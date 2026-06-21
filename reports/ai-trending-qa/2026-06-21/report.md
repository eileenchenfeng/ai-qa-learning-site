# GitHub 今日 AI Trending 测开分析（2026-06-21）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- RAG / 知识库: 1 个

### 热门项目速览

#### 1. palmier-io/palmier-pro
- 链接：https://github.com/palmier-io/palmier-pro
- 归类：AI Agent / 编排框架
- Stars：3645
- 主要语言：Swift
- Topics：ai-video, claude, macos, mcp, seedance2, swift, video-editor
- 项目特色（基于 description/README 片段的轻量提炼）：
  - macOS video editor built for AI
  - **Discord:** Join the community on **Discord（https://discord.com/invite/SMVW6pKYmg）**.
  - **Twitter / X:** Follow **@Palmier_io（https://x.com/Palmier_io）** for updates and announcements.
  - **Instagram:** Follow @palmier.io（https://www.instagram.com/palmier.io）
  - **Feedback &amp; Support:** Create a Github Issue（https://github.com/palmier-io/palmier-pro/issues） or email us at founders@palmier.io

#### 2. calesthio/OpenMontage
- 链接：https://github.com/calesthio/OpenMontage
- 归类：AI Agent / 编排框架
- Stars：7208
- 主要语言：Python
- Topics：agent, agentic-ai, ai, claude, copilot, cursor, elevenlabs, ffmpeg, flux, image-generation, open-source, openai
- 项目特色（基于 description/README 片段的轻量提炼）：
  - World's first open-source, agentic video production system. 12 pipelines, 52 tools, 500+ agent skills. Turn your AI coding assistant into a full video production studio.
  - **Paste a reference video**
  - **The agent analyzes transcript, pacing, scenes, keyframes, and style**
  - **You get 2-3 differentiated concepts, an honest tool path, cost estimates, and a sample before full production**
  - **What it keeps** from the reference: pacing, hook style, structure, tone
  - **What it changes**: topic, visual treatment, angle, narration approach

#### 3. DeusData/codebase-memory-mcp
- 链接：https://github.com/DeusData/codebase-memory-mcp
- 归类：AI Agent / 编排框架
- Stars：9519
- 主要语言：C
- Topics：aider, ast, claude-code, code-analysis, code-intelligence, codex, cursor, cypher, developer-tools, gemini-cli, graph-visualization, kilocode
- 项目特色（基于 description/README 片段的轻量提炼）：
  - High-performance code intelligence MCP server. Indexes codebases into a persistent knowledge graph — average repo in milliseconds. 158 languages, sub-ms queries, 99% fewer tokens. Single static binary, zero dependencies.
  - **Extreme indexing speed** — Linux kernel (28M LOC, 75K files) in 3 minutes. RAM-first pipeline: LZ4 compression, in-memory SQLite, fused Aho-Corasick pattern matching. Memory released after indexing.
  - **Plug and play** — single static binary for macOS (arm64/amd64), Linux (arm64/amd64), and Windows (amd64). No Docker, no runtime dependencies, no API keys. Download → `install` → restart agent → done.
  - **158 languages** — vendored tree-sitter grammars compiled into the binary. Nothing to install, nothing that breaks.
  - **120x fewer tokens** — 5 structural queries: ~3,400 tokens vs ~412,000 via file-by-file search. One graph query replaces dozens of grep/read cycles.
  - **11 agents, one command** — `install` auto-detects Claude Code, Codex CLI, Gemini CLI, Zed, OpenCode, Antigravity, Aider, KiloCode, VS Code, OpenClaw, and Kiro — configures MCP entries, instruction files, and pre-tool hooks for each.

#### 4. google-research/timesfm
- 链接：https://github.com/google-research/timesfm
- 归类：AI Agent / 编排框架
- Stars：24611
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - TimesFM (Time Series Foundation Model) is a pretrained time-series foundation model developed by Google Research for time-series forecasting.
  - All checkpoints:
  - Google Research blog（https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/）.
  - TimesFM in Google 1P Products:
  - BigQuery ML（https://cloud.google.com/bigquery/docs/timesfm-model）: Enterprise level SQL queries for scalability and reliability.
  - Google Sheets（https://workspaceupdates.googleblog.com/2026/02/forecast-data-in-connected-sheets-BigQueryML-TimesFM.html）: For your daily spreadsheet.

#### 5. twentyhq/twenty
- 链接：https://github.com/twentyhq/twenty
- 归类：AI Agent / 编排框架
- Stars：50911
- 主要语言：TypeScript
- Topics：crm, crm-system, customer, good-first-issue, graphql, hacktoberfest, javascript, marketing, monorepo, nestjs, open-source, postgresql
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The open alternative to Salesforce, designed for AI.

#### 6. Kong/insomnia
- 链接：https://github.com/Kong/insomnia
- 归类：RAG / 知识库
- Stars：39384
- 主要语言：TypeScript
- Topics：api, api-client, api-design, curl, electron-app, graphql, grpc, http-client, rest-api, websockets
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The open-source, cross-platform API client for GraphQL, REST, WebSockets, SSE and gRPC. With Cloud, Local and Git storage.
  - **Debug APIs** using the most popular protocols and formats.
  - **Design APIs** using the native OpenAPI editor and visual preview.
  - **Test APIs** using native test suites and collection runner.
  - **Mock APIs** using a cloud or self-hosted mocking server.
  - **Build CI/CD pipelines** using the native Insomnia CLI for linting and testing.

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

#### RAG / 知识库
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：检索召回（Recall）与排序（Rank）——为每条问题准备‘期望命中文档集合’，做离线评测回归。
- 把向量库当数据库测：索引构建一致性、增量写入正确性、冷热数据切换、延迟与容量压测。
- 端到端测试要覆盖：空知识、知识过期、同义词、长文本截断、引用来源（citation）准确性。

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
