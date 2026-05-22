# GitHub 今日 AI Trending 测开分析（2026-05-22）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- 其他 / 待分类: 1 个

### 热门项目速览

#### 1. multica-ai/andrej-karpathy-skills
- 链接：https://github.com/multica-ai/andrej-karpathy-skills
- 归类：其他 / 待分类
- Stars：143112
- 功能特点：
  - A single CLAUDE.md file to improve Claude Code behavior, derived from Andrej Karpathy&#39;s observations on LLM coding pitfalls. - multica-ai/andrej-karpathy-skills
- 核心优势：
  - 目标清晰：从项目描述可直接定位其核心能力与落地方向
- 使用场景：
  - 用于团队学习与工程实践沉淀：复刻教程中的 demo，形成内部可复现的评测/回归用例
  - 为质量保障体系补齐‘大模型基础能力认知’与‘可测性设计模式’
- 测开视角关注点：
  - 如果是教程/实践类项目：可把其中的 demo 固化为内部‘能力基线’与回归集（例如提示词、RAG、评测口径的最小闭环）。
  - 用它来统一团队对 LLM 行为与误差的理解：减少‘主观评审’，增加可自动化度量（评分、命中率、拒答率等）。

#### 2. dotnet/skills
- 链接：https://github.com/dotnet/skills
- 归类：AI Agent / 编排框架
- Stars：2185
- 主要语言：C#
- Topics：agent-skills
- 功能特点：
  - Repository for skills to assist AI coding agents with .NET and C#
- 核心优势：
  - 目标清晰：从项目描述可直接定位其核心能力与落地方向
- 使用场景：
  - 构建/编排多步骤 AI Agent 工作流（工具调用、计划/执行、状态管理）
  - 为业务系统接入‘可控的’自动化能力：将外部动作收敛为工具 API（便于做契约与权限测试）
- 测开视角关注点：
  - 优先把 agent 的‘动作空间’收敛为工具 API：每个工具都应该有契约（schema）、错误码、权限边界与幂等性测试。
  - 对‘计划/执行/反思/重试’等阶段引入 trace_id + 事件流日志：测试既能断言结果，也能断言过程（分支覆盖/回滚是否正确）。
  - 为关键对话/任务流建立回放用例（golden/snapshot）：固定依赖（检索/工具/模型版本）后，输出应稳定在可接受差异内。

#### 3. obra/superpowers
- 链接：https://github.com/obra/superpowers
- 归类：AI Agent / 编排框架
- Stars：201482
- 功能特点：
  - An agentic skills framework &amp; software development methodology that works. - obra/superpowers
- 核心优势：
  - 目标清晰：从项目描述可直接定位其核心能力与落地方向
- 使用场景：
  - 构建/编排多步骤 AI Agent 工作流（工具调用、计划/执行、状态管理）
  - 为业务系统接入‘可控的’自动化能力：将外部动作收敛为工具 API（便于做契约与权限测试）
- 测开视角关注点：
  - 优先把 agent 的‘动作空间’收敛为工具 API：每个工具都应该有契约（schema）、错误码、权限边界与幂等性测试。
  - 对‘计划/执行/反思/重试’等阶段引入 trace_id + 事件流日志：测试既能断言结果，也能断言过程（分支覆盖/回滚是否正确）。
  - 为关键对话/任务流建立回放用例（golden/snapshot）：固定依赖（检索/工具/模型版本）后，输出应稳定在可接受差异内。

#### 4. HKUDS/CLI-Anything
- 链接：https://github.com/HKUDS/CLI-Anything
- 归类：AI Agent / 编排框架
- Stars：39106
- 功能特点：
  - &quot;CLI-Anything: Making ALL Software Agent-Native&quot; -- CLI-Hub: https://clianything.cc/ - HKUDS/CLI-Anything
- 核心优势：
  - 目标清晰：从项目描述可直接定位其核心能力与落地方向
- 使用场景：
  - 构建/编排多步骤 AI Agent 工作流（工具调用、计划/执行、状态管理）
  - 为业务系统接入‘可控的’自动化能力：将外部动作收敛为工具 API（便于做契约与权限测试）
- 测开视角关注点：
  - 优先把 agent 的‘动作空间’收敛为工具 API：每个工具都应该有契约（schema）、错误码、权限边界与幂等性测试。
  - 对‘计划/执行/反思/重试’等阶段引入 trace_id + 事件流日志：测试既能断言结果，也能断言过程（分支覆盖/回滚是否正确）。
  - 为关键对话/任务流建立回放用例（golden/snapshot）：固定依赖（检索/工具/模型版本）后，输出应稳定在可接受差异内。

#### 5. ChromeDevTools/chrome-devtools-mcp
- 链接：https://github.com/ChromeDevTools/chrome-devtools-mcp
- 归类：AI Agent / 编排框架
- Stars：40474
- Topics：debugging, chrome, browser, chrome-devtools, mcp, devtools, puppeteer, mcp-server
- 功能特点：
  - Chrome DevTools for coding agents. Contribute to ChromeDevTools/chrome-devtools-mcp development by creating an account on GitHub.
- 核心优势：
  - 目标清晰：从项目描述可直接定位其核心能力与落地方向
- 使用场景：
  - 构建/编排多步骤 AI Agent 工作流（工具调用、计划/执行、状态管理）
  - 为业务系统接入‘可控的’自动化能力：将外部动作收敛为工具 API（便于做契约与权限测试）
- 测开视角关注点：
  - 优先把 agent 的‘动作空间’收敛为工具 API：每个工具都应该有契约（schema）、错误码、权限边界与幂等性测试。
  - 对‘计划/执行/反思/重试’等阶段引入 trace_id + 事件流日志：测试既能断言结果，也能断言过程（分支覆盖/回滚是否正确）。
  - 为关键对话/任务流建立回放用例（golden/snapshot）：固定依赖（检索/工具/模型版本）后，输出应稳定在可接受差异内。

#### 6. rohitg00/ai-engineering-from-scratch
- 链接：https://github.com/rohitg00/ai-engineering-from-scratch
- 归类：AI Agent / 编排框架
- Stars：10694
- Topics：python, nlp, rust, machine-learning, tutorial, typescript, course, reinforcement-learning, ai, computer-vision, deep-learning, mcp
- 功能特点：
  - Learn it. Build it. Ship it for others. Contribute to rohitg00/ai-engineering-from-scratch development by creating an account on GitHub.
- 核心优势：
  - 产品化形态明确：适合沉淀 Playwright 关键路径回放与可用性回归
- 使用场景：
  - 构建/编排多步骤 AI Agent 工作流（工具调用、计划/执行、状态管理）
  - 为业务系统接入‘可控的’自动化能力：将外部动作收敛为工具 API（便于做契约与权限测试）
- 测开视角关注点：
  - 优先把 agent 的‘动作空间’收敛为工具 API：每个工具都应该有契约（schema）、错误码、权限边界与幂等性测试。
  - 对‘计划/执行/反思/重试’等阶段引入 trace_id + 事件流日志：测试既能断言结果，也能断言过程（分支覆盖/回滚是否正确）。
  - 为关键对话/任务流建立回放用例（golden/snapshot）：固定依赖（检索/工具/模型版本）后，输出应稳定在可接受差异内。

## 对日常 QA 工作的工程化启发（如何测试此类架构）

### 1) 面向 AI Agent 产品质量的通用原则

- 把 LLM 当作不可控依赖：测试要尽可能确定性（Mock/回放/固定评测集），线上靠观测性兜底。
- 优先把输出结构化：JSON Schema / 受控枚举 / error code，让断言从‘主观’变成‘可自动化判定’。
- 关键路径必须可回放：对话、工具调用、检索命中、模型版本，都要可复现。

### 2) 按架构类型给测试策略（可直接套用）

#### AI Agent / 编排框架
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：工具调用（tool/function calling）分支覆盖、状态机/工作流回滚、长链路超时与重试策略。
- 用 Golang Ginkgo 做后端校验：对每个工具 API 做 contract test + 幂等性测试 + 权限边界测试。
- 把关键对话流固化成“场景回放测试”：同一输入在固定依赖下输出必须稳定（snapshot / golden）。

#### 其他 / 待分类
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 类别不明时，先做‘接口可测性体检’：输入输出结构、错误处理、日志与追踪、可 Mock 的依赖边界。

### 3) Golang Ginkgo 后端校验：最小可用模板

以下片段用于说明思路（按你们的框架/路由替换即可）：

```go
package api_test

import (
  "net/http"
  "github.com/onsi/ginkgo/v2"
  "github.com/onsi/gomega"
)

var _ = ginkgo.Describe("Tool API Contract", func() {
  ginkgo.It("should return stable JSON schema for success", func() {
    resp, err := http.Get("http://localhost:8080/api/tool/foo?x=1")
    gomega.Expect(err).ToNot(gomega.HaveOccurred())
    gomega.Expect(resp.StatusCode).To(gomega.Equal(http.StatusOK))
    // TODO: 读取 body 做 JSON Schema 校验 / 字段断言
  })
})
```

### 4) Playwright 端到端自动化：关键路径回放模板

```ts
import { test, expect } from '@playwright/test';

test('chat streaming should be stable', async ({ page }) => {
  await page.goto('https://your-console.example.com');
  // TODO: 登录

  await page.getByRole('textbox', { name: '输入' }).fill('解释一下这个项目的核心能力');
  await page.getByRole('button', { name: '发送' }).click();

  // 关键：对流式输出做“最终一致性”断言
  await expect(page.getByTestId('assistant-message').last()).toContainText('核心');
});
```

## 可落地的行动指南（如何在现有自动化框架中应用）

1. 在现有自动化仓库中新建 `ai_agent_quality/` 目录，沉淀：评测集、对话回放用例、golden snapshots。
2. 为后端（Golang）增加 Ginkgo 套件：
  - Contract tests（OpenAPI/JSON Schema）
  - 工具 API 幂等性 + 权限边界
  - 关键业务规则的 table-driven tests
3. 为前端/控制台增加 Playwright 套件：
  - 关键路径回放（含流式输出断言）
  - 断网/慢网/重试场景
  - 可访问性（a11y）与错误提示一致性
4. 把 LLM 依赖抽象为 Provider 接口：测试环境默认 Mock（录制回放），必要时才走真实模型。
5. 建立‘变更影响面’机制：prompt/模型/检索策略/工具列表任一变化，都要触发评测回归 + 差分报告。

---
### 附：生成数据说明
- 数据源：GitHub Trending +（优先）GitHub REST API；API 受限时自动降级为抓取 GitHub Repo HTML 页面
- 说明：AI 过滤与分类为规则驱动，可按团队需求持续迭代；如需更智能的总结，可在此报告基础上再做人工/LLM 精炼。
