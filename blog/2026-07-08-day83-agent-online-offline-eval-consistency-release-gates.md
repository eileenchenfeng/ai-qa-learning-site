---
title: "每日 AI 学习笔记｜Day 83：Agent 线上离线评测一致性与发布门禁"
date: 2026-07-08
authors: [xiaoai]
tags: [learning-notes, AI, QA, evalops, release-gate, online-eval, offline-eval, cicd]
---

# 每日 AI 学习笔记｜Day 83：Agent 线上离线评测一致性与发布门禁

## 核心总结

今天的主题是 **Agent 线上离线评测一致性与发布门禁**。如果说 Day 82 解决的是“评测数据集怎么建设和版本化”，那今天要解决的是另一件更容易出事故的事：**为什么离线分数很好，上线以后还是会翻车**。

对资深测试开发来说，真正难的不是把 eval 跑起来，而是让离线评测、预发验证、线上观测和发布拦截共享同一套质量语言。只有当 `case_id`、`dataset_version`、`runner_version`、`trace_id` 和线上故障证据能串起来，团队才知道一次发布到底是模型退化、工具漂移、环境差异，还是评测本身失真。

- **离线高分不等于线上可用**：真实环境还会叠加权限差异、缓存命中、外部限流、流量分布变化和不可控依赖延迟。
- **发布门禁要看 E2E 业务链路**：从用户触发，到 Agent 规划、工具调用、外部状态写入、最终可观测结果，都要被校验，而不是只看答案文本像不像。
- **一致性的关键是“同一条样本跨环境可追踪”**：每次评测都要带上稳定 `case_id`、请求级 `trace_id` 和环境标签，便于线上线下对账。
- **门禁规则必须分层**：P0 核心场景、负样本、安全场景、成本指标和时延指标不应该混成一个平均分。
- **线上反馈要反哺离线集**：灰度故障、真实投诉、回滚案例要回收进 dataset，不然离线评测会越来越“像考试题”，越来越不像真实业务。

{/* truncate */}

## 1. 为什么离线评测通过了，线上还是会出问题

很多团队已经能在 CI 里自动跑 eval，分数也不低，但问题往往出在发布后的前几小时。根因通常不是“模型突然变笨”，而是离线环境默认帮你抹平了很多现实约束。

常见差异包括：离线环境用的是固定 prompt 和固定上下文，线上却有多轮会话残留；离线调用的是 mock tool，线上调用的是真实下游；离线没有权限裁剪，线上则存在用户角色差异；离线用的是稳定数据快照，线上命中的却是实时变化的数据。

<callout icon="bulb" bgc="3">
**判断标准：** 一套评测体系是否可信，不看它能否给出一个漂亮的总分，而看它能否解释“线上失败为什么没在离线被拦住”。
</callout>

## 2. 先统一口径：线上离线一致性到底在对齐什么

一致性不是要求线上结果和离线结果逐字相同，而是要求关键业务行为在不同环境下保持可解释、可比较、可追踪。

<table header-row="true" col-widths="170,250,260,220">
  <tr>
    <td>对齐维度</td>
    <td>离线评测关注点</td>
    <td>线上验证关注点</td>
    <td>推荐门禁方式</td>
  </tr>
  <tr>
    <td>任务结果</td>
    <td>最终输出是否满足 rubric</td>
    <td>用户是否得到可执行、可追溯结果</td>
    <td>P0 样本必须通过</td>
  </tr>
  <tr>
    <td>工具链路</td>
    <td>是否调用正确工具、参数是否完整</td>
    <td>工具是否真实执行成功、是否出现重试/降级</td>
    <td>记录工具轨迹并做外部断言</td>
  </tr>
  <tr>
    <td>权限与安全</td>
    <td>越权样本应拒绝或澄清</td>
    <td>不同角色下是否仍能守住边界</td>
    <td>负样本误通过直接阻断</td>
  </tr>
  <tr>
    <td>性能与成本</td>
    <td>离线平均耗时、token 成本</td>
    <td>真实流量下的 P95/P99 与资源波动</td>
    <td>SLO/SLA 双阈值</td>
  </tr>
  <tr>
    <td>可观测性</td>
    <td>case_id、trace_id 是否齐全</td>
    <td>日志、trace、审计记录能否串联</td>
    <td>无追踪信息视为不合格</td>
  </tr>
</table>

## 3. E2E 场景：一次发布前的真实质量门禁链路

下面用一个贴近测开团队的场景说明“线上离线一致性”怎么真正落地。

**用户故事：** 团队要上线一个“自动解析需求、生成 Ginkgo E2E 用例、同步到测试平台并创建回归任务”的 Agent 能力。发布前，系统需要先跑离线回归，再跑预发沙箱验证，最后在灰度期间对真实流量抽样复验。

**链路：** 开发提交 PR → CI 构建版本 → 拉取稳定 dataset → 执行离线 E2E eval → 部署预发 → 跑沙箱工具链验证 → 灰度抽样真实请求 → 对比线上线下差异 → 满足门禁后继续放量。

**预期中间状态：**

1. 每个 case 都带稳定 `case_id`，每次执行都带新的 `run_id` 和 `trace_id`。
2. 预发环境的写操作全部落到沙箱空间，避免污染真实平台。
3. 关键 tool 调用、参数、返回码、重试次数都能在 trace 中看到。
4. 如果线上和离线结果不一致，报告能区分是环境差异、依赖漂移还是评测规则问题。
5. 灰度期抽样请求能回收为候选样本，进入下一版 dataset。

**最终验证点（✅）：**

- ✅ `p0_pass_rate == 100%`，且无新增 P0 失败样本。
- ✅ `negative_false_accept_rate == 0%`，越权或缺参写操作必须被拒绝或澄清。
- ✅ 预发沙箱中的外部状态与预期一致，例如测试任务成功创建且只创建一次。
- ✅ 灰度期 `online_offline_mismatch_rate` 不超过阈值，例如 < 3%。
- ✅ 任一失败样本都能定位到 `dataset_version`、`agent_version`、`runner_version` 和 `trace_id`。

## 4. 工程实践一：Python 编排发布门禁（可运行）

下面示例实现一个简化版 gate runner：先跑离线评测，再读取线上抽样结果，对不一致率做拦截。你可以直接保存为 `evalops/release_gate.py` 运行。

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvalSummary:
    overall_score: float
    p0_pass_rate: float
    negative_false_accept_rate: float
    dataset_version: str


@dataclass
class OnlineCheckSummary:
    sampled_cases: int
    mismatch_rate: float
    p95_latency_ms: int


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_offline_summary(path: Path) -> EvalSummary:
    data = load_json(path)
    return EvalSummary(
        overall_score=data["overall_score"],
        p0_pass_rate=data["p0_pass_rate"],
        negative_false_accept_rate=data["negative_false_accept_rate"],
        dataset_version=data["dataset_version"],
    )


def load_online_summary(path: Path) -> OnlineCheckSummary:
    data = load_json(path)
    return OnlineCheckSummary(
        sampled_cases=data["sampled_cases"],
        mismatch_rate=data["mismatch_rate"],
        p95_latency_ms=data["p95_latency_ms"],
    )


def evaluate_gate(offline: EvalSummary, online: OnlineCheckSummary) -> tuple[bool, list[str]]:
    reasons: list[str] = []

    if offline.p0_pass_rate < 1.0:
        reasons.append(f"P0 样本未全通过: {offline.p0_pass_rate:.2%}")
    if offline.negative_false_accept_rate > 0:
        reasons.append(
            f"负样本误通过率不为 0: {offline.negative_false_accept_rate:.2%}"
        )
    if online.sampled_cases < 20:
        reasons.append(f"线上抽样量不足: {online.sampled_cases}")
    if online.mismatch_rate > 0.03:
        reasons.append(f"线上离线不一致率过高: {online.mismatch_rate:.2%}")
    if online.p95_latency_ms > 3000:
        reasons.append(f"线上 P95 时延超阈值: {online.p95_latency_ms}ms")

    return len(reasons) == 0, reasons


def main() -> None:
    offline = load_offline_summary(Path("artifacts/offline_eval_summary.json"))
    online = load_online_summary(Path("artifacts/online_shadow_summary.json"))

    ok, reasons = evaluate_gate(offline, online)
    result = {
        "passed": ok,
        "dataset_version": offline.dataset_version,
        "offline": offline.__dict__,
        "online": online.__dict__,
        "reasons": reasons,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```

示例输入：

```json
// artifacts/offline_eval_summary.json
{
  "dataset_version": "v2026.07.08",
  "overall_score": 0.91,
  "p0_pass_rate": 1.0,
  "negative_false_accept_rate": 0.0
}
```

```json
// artifacts/online_shadow_summary.json
{
  "sampled_cases": 36,
  "mismatch_rate": 0.027,
  "p95_latency_ms": 2400
}
```

运行方式：

```bash
python evalops/release_gate.py
```

这个脚本的价值不在于逻辑复杂，而在于它把“离线分数、线上抽样、性能阈值”合并成了同一个放行决策。

## 5. 工程实践二：Golang + Ginkgo 校验关键外部状态

如果你的 Agent 最终会创建任务、写测试平台、发通知，仅看返回文本还不够。下面的 Ginkgo 用例示例演示如何对外部状态做最终校验。

```go
package e2e_test

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type GateResponse struct {
    TraceID   string `json:"trace_id"`
    TaskID    string `json:"task_id"`
    FinalText string `json:"final_text"`
}

type TaskDetail struct {
    ID        string `json:"id"`
    Status    string `json:"status"`
    Scenario  string `json:"scenario"`
    TraceID   string `json:"trace_id"`
}

var _ = Describe("Agent 发布门禁 E2E", func() {
    It("生成测试计划并创建回归任务后，外部状态应可对账", func() {
        resp, err := http.Post("http://localhost:8080/v1/agent/release-gate", "application/json", nil)
        Expect(err).NotTo(HaveOccurred())
        Expect(resp.StatusCode).To(Equal(http.StatusOK))

        var gateResp GateResponse
        Expect(json.NewDecoder(resp.Body).Decode(&gateResp)).To(Succeed())
        Expect(gateResp.TraceID).NotTo(BeEmpty())
        Expect(gateResp.TaskID).NotTo(BeEmpty())

        client := &http.Client{Timeout: 3 * time.Second}
        req, err := http.NewRequest(http.MethodGet, fmt.Sprintf("http://localhost:8081/tasks/%s", gateResp.TaskID), nil)
        Expect(err).NotTo(HaveOccurred())

        detailResp, err := client.Do(req)
        Expect(err).NotTo(HaveOccurred())
        Expect(detailResp.StatusCode).To(Equal(http.StatusOK))

        var detail TaskDetail
        Expect(json.NewDecoder(detailResp.Body).Decode(&detail)).To(Succeed())

        Expect(detail.Status).To(Equal("created"))
        Expect(detail.Scenario).To(Equal("release-gate"))
        Expect(detail.TraceID).To(Equal(gateResp.TraceID))
        Expect(gateResp.FinalText).To(ContainSubstring("测试计划"))
    })
})
```

这类 E2E 用例的重点是：从用户触发开始，一直验证到“外部系统里确实出现了正确结果”，而不是把测试停在 Agent 返回 200。

## 6. 如何设计可落地的门禁分层

发布门禁最怕两件事：一是过于宽松，拦不住高风险问题；二是过于僵硬，导致团队为了过门禁而把规则做成摆设。

一个更稳妥的分层方式通常是：

- **硬门禁**：P0 核心路径失败、负样本误通过、安全违规、幂等失效，直接阻断。
- **软门禁**：整体分数轻微下降、部分长尾样本波动、少量非关键 mismatch，允许人工复核后继续。
- **观察指标**：线上抽样量、token 成本、P95/P99 变化、工具重试率，先告警，再决定是否升级为门禁。

<callout icon="bulb" bgc="4">
**实践建议：** 刚开始建设门禁时，不要一次把所有指标都设成阻断项。先把真正会造成线上事故的那几类问题做成硬门禁，其余先观察两周，再决定是否收紧。
</callout>

## 7. 让线上反馈真正反哺离线集

很多团队的 eval dataset 一开始质量不错，几个月后却越来越失真。原因往往不是没人维护，而是线上反馈没有形成稳定回收机制。

推荐至少回收 4 类材料：灰度失败 case、用户投诉 case、回滚前后差异 case，以及线上抽样发现的高 mismatch case。每次回收都要补充失败原因、环境标签和修复后验证结果，避免只收一段 prompt，却丢掉上下文和外部状态。

如果线上出现过“离线能过、线上翻车”的事故，这个 case 应该升级成高优先级样本，并进入下一版稳定 dataset。否则同类问题通常还会再来一次。

## 8. 课后思考题

1. 你现在团队里的发布门禁，拦的是“模型输出错了”，还是“真实业务链路不可用”？
2. 如果线上和离线结果不一致，你的第一反应能快速区分是环境差异、数据漂移还是评测规则失真吗？
3. 对有写操作的 Agent，你们是否已经把幂等、审计日志、trace_id 和外部断言串在一起？
4. 现有 dataset 中，有多少样本来自真实线上故障，而不是人工想象出来的题目？

## 9. 今日小结

今天最关键的收获是：**Agent 质量门禁不是“跑一次离线 eval”就结束，而是要把离线评测、预发验证、灰度抽样和线上反馈接成一条闭环。** 只有当样本、执行、观测和发布决策共用同一套追踪信息，团队才有能力在版本变更时既快又稳地放量。