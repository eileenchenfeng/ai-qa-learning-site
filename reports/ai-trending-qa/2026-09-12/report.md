# GitHub 今日 AI Trending 测开分析（2026-09-12）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. ayghri/i-have-adhd
- 链接：https://github.com/ayghri/i-have-adhd
- 归类：AI Agent / 编排框架
- Stars：42169
- 主要语言：Python
- Topics：adhd, claude-, claude-code-plugin, claude-skills, developer-tools, productivity
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A skill to stop your coding agent from burying the answer. ADHD-friendly output.
  - Lead with the next action.
  - Number multi-step tasks.
  - End with one concrete next step.
  - Suppress tangents.
  - Restate state every turn.

#### 2. melgarafael/DeskcommCRM
- 链接：https://github.com/melgarafael/DeskcommCRM
- 归类：AI Agent / 编排框架
- Stars：1421
- 主要语言：TypeScript
- Topics：ai, ai-agents, chatbot, crm, customer-support, ecommerce, lgpd, mcp, multi-tenant, nextjs, nuvemshop, open-source
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open-source AI sales OS — self-hosted CRM with native AI agents + WhatsApp (WAHA). Open alternative to Kommo, Octadesk & Intercom for any business that sells by chat. MCP-ready, multi-tenant, LGPD.
  - Gera todos os segredos técnicos sozinho (você não inventa senha nenhuma).
  - Cria as extensões do Postgres e aplica o schema completo (`supabase/baseline.sql`).
  - Cria o primeiro admin com o e-mail e a senha que você escolheu.
  - Sobe a stack inteira com **HTTPS automático** e confere a saúde no fim.
  - Instala o **cron das automações** (sem ele, as regras QUANDO/SE/ENTÃO ficam paradas na fila)

#### 3. vastsa/PI-Desktop
- 链接：https://github.com/vastsa/PI-Desktop
- 归类：AI Agent / 编排框架
- Stars：2837
- 主要语言：TypeScript
- Topics：ai-agent, coding-agent, desktop-app, electron, global, i18n, local-first, mcp, pi, pi-agent, pi-desktop, plugins
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Local-first AI coding agent desktop: Electron + Rust host core + pi Agent Harness + user-installable plugins
  - **Connect a model**
  - **Open a project**
  - **Pick Agent, Plan, or Goal**
  - **Review the result**
  - codebase exploration

#### 4. armory3d/armorpaint
- 链接：https://github.com/armory3d/armorpaint
- 归类：AI Agent / 编排框架
- Stars：4758
- 主要语言：C
- Topics：3d, armorpaint, painting, texturing, tool
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Graphics Creation Tools

#### 5. alsk1992/CloddsBot
- 链接：https://github.com/alsk1992/CloddsBot
- 归类：AI Agent / 编排框架
- Stars：2210
- 主要语言：TypeScript
- Topics：agi, ai, arbitrage, claude, crypto, defi, ethereum, futures, hft, hyperliquid, kalshi, polymarket
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open Source AI trading agent that operates autonomously across 1000+ markets - Polymarket, Kalshi, Binance, Hyperliquid, Solana DEXs, 5 EVM chains. Scans for edge, executes instantly, manages risk while you sleep. Agent commerce protocol for machine-to-machine payments. Self-hosted. Built on Claude.
  - Install the latest GitHub Release → `clodds onboard`
  - Onboarding wizard walks through credentials setup
  - Fetches live 15-minute BTC prediction markets from Polymarket (in real-time)
  - One command away from trading
  - Claude-style sidebar with 4 tabs: Chats, Projects, Artifacts, Code

#### 6. nashsu/llm_wiki
- 链接：https://github.com/nashsu/llm_wiki
- 归类：AI Agent / 编排框架
- Stars：18814
- 主要语言：TypeScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - LLM Wiki is a cross-platform desktop application that turns your documents into an organized, interlinked knowledge base — automatically. Instead of traditional RAG (retrieve-and-answer from scratch every time), the LLM incrementally builds and maintains a persistent wiki from your sources。
  - **Two-Step Chain-of-Thought Ingest** — LLM analyzes first, then generates wiki pages with source traceability and incremental cache
  - **Multimodal Image Ingestion** — extract embedded images from PDFs, generate factual captions with a vision LLM, surface them in image-aware search results with lightbox preview and jump-to-source
  - **Multi-format Document Parsing** — ingest PDF, Office documents, EPUB/MOBI, Org mode, images, media, web clips, and batches of URLs, with built-in, cloud, or local MinerU PDF processing
  - **Flexible Model Configuration** — configure models per project, route Chat and Ingest independently, and manage custom providers, headers, and streaming output
  - **Source-grounded Retrieval** — use Read Sources Only mode to answer exclusively from original imported material

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
