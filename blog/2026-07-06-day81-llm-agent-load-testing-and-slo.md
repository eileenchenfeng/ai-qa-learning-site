---
title: "每日 AI 学习笔记｜Day 81：LLM Agent 性能压测与 SLO 验证实战"
date: 2026-07-06
authors: [xiaoai]
tags: [learning-notes, AI, QA, load-testing, k6, observability]
---

今天把“性能压测”从传统 API 压测推进到 **LLM/Agent 场景**：不仅要压 QPS，更要压 **长链路、流式输出、工具调用、外部副作用**，最终落到“能否达成 SLO”。

{/* truncate */}

## 核心总结

- **把 Agent 当“有状态的业务编排器”来压**：压测对象不是某个接口，而是“用户发起 → Agent 推理/规划 → 多工具调用 → 产出可观测结果”的完整链路。
- **先定 SLO 再写压测**：例如 *P95 首 token < 2s，P99 全量完成 < 30s，错误率 < 0.5%，外部副作用幂等一致*。没有 SLO 的压测只是在“测个热闹”。
- **关键指标必须分层**：入口（HTTP/WS）、模型层（推理耗时/排队）、编排层（tool 调用耗时与失败）、外部系统（写入成功率/补偿）、客户端体验（首 token / token 速率 / cancel 生效）。
- **负载模型要贴近真实用户**：突发（会议前）、潮汐（上下班）、混合请求（短问答 + 长任务 + 多工具）比“固定并发打满”更能暴露问题。
- **压测验收要包含“可回放证据”**：每个压测请求最好有 `request_id`，能在日志/trace 中一键定位，压测报告能回答“慢在哪一段”。

## 1. LLM/Agent 压测与传统 API 压测的 4 个本质差异

1. **请求时长更长、尾延迟更重要**：LLM/Agent 的 P99 常常比 P50 高一个数量级。优化目标要盯住 tail。
2. **输出是“流”而不是一次性 JSON**：用户体验关键是 **首 token 延迟（TTFT）** 与 **token 速率（TPS）**，而不仅是总耗时。
3. **链路包含多次外部调用与副作用**：tool 调用可能触发 DB 写、发消息、创建工单等。压测必须保证 **幂等** 与 **环境隔离**。
4. **“成功”不等于“可用”**：接口 200 但内容为空、被截断、推理降级、工具失败后静默兜底，都可能让用户体验变差。

## 2. 先把 SLO 写清楚：建议的验收口径

以“对话式 Agent（含工具调用）”为例，给一个可落地的 SLO 模板（你可以按业务改数值）：

- **可用性**：成功率 ≥ 99.5%（成功定义：最终产出符合 schema，且关键 tool 调用成功/或有明确可解释降级）
- **性能**：
  - P95 **TTFT** < 2s
  - P99 **E2E 完成耗时** < 30s（长任务可分级：短问答 < 8s，长任务 < 60s）
- **稳定性**：
  - 5xx + 超时比例 < 0.5%
  - tool 调用失败（可重试类）最终恢复成功率 ≥ 99%
- **资源成本**（可选但强烈建议）：
  - 单请求平均 token 成本、GPU/CPU 占用上限、队列等待时间上限
- **一致性**：
  - 对同一 `idempotency_key` 重放，外部副作用只发生一次；取消请求生效后不再产生新副作用

## 3. E2E 场景设计：把压测用例写成“真实用户任务”

> 下面所有压测都按 E2E 端到端场景组织：每个场景从用户触发开始，最终验证可观测结果（日志/trace/外部状态）。单点断言下沉到步骤的“预期中间状态/最终✅”。

### 场景 A：高频短问答（对话体验基线）

**用户故事：** 用户在工位连续问 20 个短问题（无工具调用），要求快速出首 token。

**链路：** user → chat → llm stream → client render

**验证点：**
- ✅ P95 TTFT < 2s
- ✅ P99 完成 < 8s
- ✅ 流式输出不断流（无长时间空窗）

### 场景 B：长任务 + 多工具调用（编排与外部依赖）

**用户故事：** 用户发起“生成测试计划并同步到工单系统”，Agent 需要：规划 → 调用 3 个 tool（检索需求/生成用例/创建工单）→ 返回最终链接。

**验证点：**
- ✅ 每次 tool 调用都有 trace span，可分解耗时
- ✅ 失败时有明确错误与可恢复策略（重试/降级/人工兜底）
- ✅ 外部工单只创建一次（幂等）

### 场景 C：用户取消（Cancel）

**用户故事：** 用户发起长任务后 3 秒取消，系统应停止生成与后续 tool 调用。

**验证点：**
- ✅ cancel 到生效（不再输出新 token）< 500ms
- ✅ cancel 生效后不再产生外部副作用

## 4. 工程实战：用 k6 写一个“Agent E2E 压测脚本”（可运行）

下面示例假设你的服务有一个 HTTP 接口：
- `POST /v1/agent/run`：同步返回 JSON（非流式）
- 或 `POST /v1/agent/stream`：SSE/HTTP chunk 流式输出（示例里用非流式更通用）

你只需要把 `BASE_URL` 和鉴权头改成自己的。

### 4.1 k6 脚本：分场景 + SLO 阈值 + request_id 可回放

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    short_qa: {
      executor: 'constant-arrival-rate',
      rate: 10,
      timeUnit: '1s',
      duration: '3m',
      preAllocatedVUs: 20,
      maxVUs: 100,
      tags: { scenario: 'short_qa' },
    },
    tool_chain: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '1s',
      stages: [
        { target: 5, duration: '2m' },
        { target: 10, duration: '3m' },
        { target: 0, duration: '1m' },
      ],
      preAllocatedVUs: 30,
      maxVUs: 200,
      tags: { scenario: 'tool_chain' },
      startTime: '10s',
    },
  },
  thresholds: {
    // 入口 E2E 耗时阈值（可按场景拆更细）
    http_req_failed: ['rate<0.005'],
    http_req_duration: ['p(95)<2000', 'p(99)<30000'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const TOKEN = __ENV.TOKEN || 'replace_me';

function headers(requestId) {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${TOKEN}`,
      'X-Request-Id': requestId,
      // 建议服务端支持幂等键：同 key 重放不产生重复副作用
      'Idempotency-Key': requestId,
    },
    tags: { request_id: requestId },
    timeout: '60s',
  };
}

export default function () {
  const scenario = __ENV.K6_SCENARIO || (__ITER % 2 === 0 ? 'short_qa' : 'tool_chain');
  const requestId = `${scenario}-${__VU}-${__ITER}-${Date.now()}`;

  let payload;
  if (scenario === 'short_qa') {
    payload = {
      input: '用一句话解释什么是幂等，并给出一个测试验证点。',
      tools: [],
      stream: false,
    };
  } else {
    payload = {
      input: '生成一个针对“Agent 取消与补偿”的 E2E 测试计划，并返回 JSON。',
      tools: ['search', 'testcase_generator', 'ticket_create'],
      stream: false,
    };
  }

  const res = http.post(`${BASE_URL}/v1/agent/run`, JSON.stringify(payload), headers(requestId));

  // 预期中间状态：接口可用
  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // 预期中间状态：有可解析的 JSON
  let body;
  try {
    body = res.json();
  } catch (e) {
    body = null;
  }

  // ✅ 最终验证点：输出结构符合预期（示例字段按你的协议改）
  check(body, {
    'has output': (b) => b && (b.output || b.result),
    'has request_id echo': (b) => b && (b.request_id || b.trace_id || b.meta),
  });

  // 模拟用户思考间隔
  sleep(Math.random() * 1.5);
}
```

运行：

```bash
# 安装 k6（示例：macOS）
# brew install k6

BASE_URL="https://your-service" TOKEN="your-token" k6 run script.js
```

### 4.2 关键工程建议：让压测“能定位”

- 服务端把 `X-Request-Id` 写入日志，并在响应里回显（例如 `request_id` / `trace_id`）。
- 对每次 tool 调用打 span（OpenTelemetry）并带上 `request_id`：压测发现慢了，能一键定位到“LLM 慢 / tool 慢 / DB 慢 / 下游限流”。
- 对有副作用的 tool 强制幂等：`Idempotency-Key` → DB 唯一索引 / 去重表。

## 5. 课后思考题

1. 你的业务里“成功”的定义是什么？接口 200 算成功吗，还是需要 tool 全部完成才算？
2. 如果引入流式输出，TTFT 和总耗时哪个更能代表用户体验？你会怎么定义并监控？
3. 取消（cancel）发生在“不可逆边界”之后，你的系统是选择补偿还是提示用户不可取消？对应的测试如何设计？
4. 在压测环境中，如何避免压测对真实线上数据产生污染？（比如隔离租户、mock 下游、只读账号、写入落沙箱）

## 6. 今日小结

今天的关键收获是：**Agent 压测要从“压接口”升级成“压业务链路”**。先写清 SLO，再用贴近真实用户任务的 E2E 场景去压，并且让每个请求都可回放、可定位。这样压测结果才不仅是一个数字，而是可驱动工程优化的证据链。