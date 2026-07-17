# GitHub 今日 AI Trending 测开分析（2026-07-17）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. apache/ossie
- 链接：https://github.com/apache/ossie
- 归类：AI Agent / 编排框架
- Stars：954
- 主要语言：Python
- Topics：metadata, semantic
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Apache Ossie, industry wide specification effort to standardize how we exchange semantic metadata across analytics, AI and BI platforms, providing a vendor neutral, single source of truth for semantic data
  - `core-spec/` — The Ossie core specification (`spec.md`), the machine-readable schema (`spec.yaml`, `osi-schema.json`), and accompanying documentation.
  - `converters/` — Reference converters that translate between Ossie and other semantic formats (e.g., dbt, GoodData, Polaris, Salesforce).
  - `examples/` — Example semantic models, including a complete TPC-DS model.
  - `validation/` — Tooling for validating semantic models against the Ossie schema.
  - `docs/` — Project documentation and overview.

#### 2. Nutlope/hallmark
- 链接：https://github.com/Nutlope/hallmark
- 归类：AI Agent / 编排框架
- Stars：11080
- 主要语言：CSS
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Anti-AI-slop design skill for Claude Code, Cursor, and Codex.
  - **Claude Code**: `~/.claude/skills/hallmark/`
  - **Cursor**: `.cursor/rules/hallmark.mdc` (body of `SKILL.md`, no frontmatter)
  - **Codex**: `~/.codex/skills/hallmark/` (personal) or `.codex/skills/hallmar

#### 3. PostHog/posthog
- 链接：https://github.com/PostHog/posthog
- 归类：AI Agent / 编排框架
- Stars：35886
- 主要语言：Python
- Topics：ab-testing, ai-analytics, analytics, cdp, data-warehouse, experiments, feature-flags, javascript, product-analytics, python, react, session-replay
- 项目特色（基于 description/README 片段的轻量提炼）：
  - :hedgehog: PostHog is the leading platform for building self-driving products. Our developer tools – AI observability, analytics, session replay, flags, experiments, error tracking, logs, and more – capture all the context agents need to diagnose problems, uncover opportunities, and ship fixes. Steer it all from Slack, web, desktop, or the MCP.
  - Self-driving mode（https://posthog.com/docs/self-driving）: Turn signals in your product data (errors, rage clicks, failed queries, and more) into researched reports and pull requests you review and merge.
  - Product analytics（https://posthog.com/product-analytics）: Autocapture or manually instrument event-based analytics to understand user behavior and analyze data with visualization or SQL.
  - Web analytics（https://posthog.com/web-analytics）: Monitor web traffic and user sessions with a GA-like dashboard. Easily monitor conversion, web vitals, and revenue.
  - Session replays（https://posthog.com/session-replay）: Watch real user sessions of interactions with your website or mobile app to diagnose issues and understand user behavior.
  - Feature flags（https://posthog.com/feature-flags）: Safely roll out features to select users or cohorts with feature flags.

#### 4. openinterpreter/openinterpreter
- 链接：https://github.com/openinterpreter/openinterpreter
- 归类：AI Agent / 编排框架
- Stars：66030
- 主要语言：Rust
- Topics：acp, coding-agent, deepseek, kimi, qwen, rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A coding agent for open models like Kimi K3
  - Runs commands inside native sandboxing on macOS, Linux, and Windows.
  - Switches providers and models from the TUI with `/model`.
  - Inspects or switches Rust-native model harnesses with `/harness`.
  - Tests web and native apps through the built-in QA skill.
  - Runs as an Agent Client Protocol（https://agentclientprotocol.com/） agent for editors with `interpreter acp`.

#### 5. PrismML-Eng/Bonsai-demo
- 链接：https://github.com/PrismML-Eng/Bonsai-demo
- 归类：AI Agent / 编排框架
- Stars：1551
- 主要语言：Shell
- Topics：bonsai, llamacpp, llm, mlx, prism-ml, small-models
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Bonsai Demo
  - **Vision:** send photos, screenshots, and PDFs; ask about them (see VISION.md).
  - **Agentic tool calling:** native OpenAI-style `tool_calls` with full round-trips, plus MCP servers in both demo UIs (see TOOLS.md).
  - **Thinking:** a reasoning model; pick the reasoning effort per chat in the UI or budget it per request.
  - **Long context:** 256k+ token conversations.
  - **Tiny footprint:** the 1-bit Bonsai-27B packs to ~1.125 bits per weight: it fits on a modern iPhone without memory offloading. Ternary-Bonsai-27B (~1.7 bits per weight, packed into 2-bit for fast accelerated kernels) is the higher-quality option and this demo's default.

#### 6. hasaneyldrm/exercises-dataset
- 链接：https://github.com/hasaneyldrm/exercises-dataset
- 归类：AI Agent / 编排框架
- Stars：15113
- 主要语言：HTML
- Topics：dataset, exercise-database, exercises, fitness, fitness-app, gym, json, logpress, react-native, workout
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 1,324-exercise fitness dataset — animation GIFs, 180×180 thumbnails, muscle-group & equipment data, and step-by-step instructions in 6 languages. The exercise data layer behind the LogPress app.
  - 1,324 exercises with category, body-part, equipment, target and muscle-group data
  - an animation GIF + 180×180 thumbnail for every exercise (media © Gym visual（https://gymvisual.com/） — see License)
  - step-by-step instructions in 10 languages (🇬🇧 English, 🇪🇸 Spanish, 🇮🇹 Italian, 🇹🇷 Turkish, 🇷🇺 Russian, 🇨🇳 Chinese, 🇮🇳 Hindi, 🇵🇱 Polish, 🇰🇷 Korean, 🇫🇷 French)
  - the interactive browser (`index.html`) and developer setup guide (`setup.html`)
  - Data Source

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
