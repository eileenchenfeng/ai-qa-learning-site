# GitHub 今日 AI Trending 测开分析（2026-07-13）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. Dicklesworthstone/destructive_command_guard
- 链接：https://github.com/Dicklesworthstone/destructive_command_guard
- 归类：AI Agent / 编排框架
- Stars：3086
- 主要语言：Rust
- Topics：ai-agents, cli, developer-tools, git, rust, safety
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The Destructive Command Guard (dcg) is for blocking dangerous git and shell commands from being executed by agents.

#### 2. wonderwhy-er/DesktopCommanderMCP
- 链接：https://github.com/wonderwhy-er/DesktopCommanderMCP
- 归类：AI Agent / 编排框架
- Stars：8032
- 主要语言：TypeScript
- Topics：agent, ai, code-analysis, code-generation, gemini-cli-extension, mcp, terminal-ai, terminal-automation, vibe-coding
- 项目特色（基于 description/README 片段的轻量提炼）：
  - This is MCP server for Claude that gives it terminal control, file system search and diff file editing capabilities
  - **Use any AI model** — Claude, GPT-4.5, Gemini 2.5, or any model you prefer
  - **See file changes live** — visual file previews as AI edits your files
  - **Add custom MCPs and context** — extend with your own tools, no config files
  - **Coming soon** — skills system, dictation, background scheduled tasks, and more
  - Features

#### 3. HKUDS/Vibe-Trading
- 链接：https://github.com/HKUDS/Vibe-Trading
- 归类：AI Agent / 编排框架
- Stars：20738
- 主要语言：Python
- Topics：ai-agent, algorithmic-trading, backtesting, fintech, llm, mcp, multi-agent, python, quantitative-finance, trading
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "Vibe-Trading: Your Personal Trading Agent"
  - **2026-07-12** 🧪 **Strategy Development Manager + contributor fix batch**: the new `strategy-dev-manager` skill (#87) turns academic papers and broker research into registered factors/strategies with a persistent artifact store and automated IC/Sharpe decay monitoring — `sdm_register` / `sdm_status` / `sdm_decay_scan` drive an active → monitoring → decayed → disabled lifecycle over `~/.vibe-trading/` (#457（https://github.com/HKUDS/Vibe-Trading/pull/457）, closes #455（https://github.com/HKUDS/Vibe-Trading/issues/455）, thanks @shadowinlife). Also merged: the Correlation tab accepts bare tickers (`AAPL,SPY`) and walks the full loader fallback chain (#472（https://github.com/HKUDS/Vibe-Trading/pull/472）, closes #471（https://github.com/HKUDS/Vibe-Trading/issues/471）, thanks @yxhuang), the `local` loader honors requested intervals via OHLCV resampling (#467（https://github.com/HKUDS/Vibe-Trading/pull/467）, thanks @Shizoqua), Binance USD-M perpetual history lands with explicit `BTC-USDT-PERP` routing + execution/mark price separation as the first #462（https://github.com/HKUDS/Vibe-Trading/issues/462） slice (#470（https://github.com/HKUDS/Vibe-Trading/pull/470）, thanks @honginp), FastMCP transport imports now work across both module layouts (#469（https://github.com/HKUDS/Vibe-Trading/pull/469）, thanks @roberttidball), and Requesty is available as an OpenAI-compatible LLM gateway provider (#474（https://github.com/HKUDS/Vibe-Trading/pull/474）, thanks @Thibaultjaigu).
  - **2026-07-11** 🚀 **v0.1.11 released** (`pip install -U vibe-trading-ai`): rolls up three weeks since 0.1.10 — first-class Indian equity (NSE/BSE) backtesting, the PIT-safe fundamental factor layer (Alpha Zoo → 460), the 16-adapter IM channel runtime, end-to-end scheduled research, optional QVeris premium data, and today's contributor batch: a turnover-aware optimizer (#466（https://github.com/HKUDS/Vibe-Trading/pull/466）, thanks @Robin1987China), an `analyze_image` vision tool + NapCat DM pairing + the IM-media read fix (#464（https://github.com/HKUDS/Vibe-Trading/pull/464）/#463（https://github.com/HKUDS/Vibe-Trading/pull/463）/#465（https://github.com/HKUDS/Vibe-Trading/issues/465）, thanks @fei-moss), Longbridge Decimal serialization (#459（https://github.com/HKUDS/Vibe-Trading/pull/459）, thanks @fanfpy), and packaged-manifest count guards (#461（https://github.com/HKUDS/Vibe-Trading/pull/461）, thanks @asahikiko). Full details: CHANGELOG · release notes（https://github.com/HKUDS/Vibe-Trading/releases/tag/v0.1.11）.
  - **2026-07-10** 🇮🇳 **Indian equity (NSE/BSE) support + centralized env config**: a dedicated `IndiaEquityEngine` lands — T+1 delivery, circuit bands, and a config-driven STT/stamp/exchange/SEBI/GST cost stack — with `.NS`/`.BO` symbol routing, an opt-in read-only Shoonya/Dhan data bridge, and 255 alpha101/qlib158 factors opted into the new `equity_in` universe

#### 4. Shubhamsaboo/awesome-llm-apps
- 链接：https://github.com/Shubhamsaboo/awesome-llm-apps
- 归类：AI Agent / 编排框架
- Stars：118743
- 主要语言：Python
- Topics：agents, llms, python, rag
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 100+ AI Agent & RAG apps you can actually run — clone, customize, ship.
  - 🛠️ **Hand-built, not curated** - every template is original work, tested end-to-end before it ships.
  - 🧪 **Runs in 3 commands** - no broken `requirements.txt`, no "figure it out yourself" scaffolding.
  - 🧠 **Covers the modern AI stack** - AI Agents, Always-on Agents, Multi-agent Teams, MCP Agents, Voice AI Agents, RAG, Agent Skills, Fine-tuning.
  - 🌐 **Provider-agnostic** - switch between Claude, Gemini, GPT, Llama, Qwen, xAI and others with a config change.
  - 📚 **Step-by-step tutorials** - every featured template has a free walkthrough on Unwind AI（https://www.theunwindai.com）.

#### 5. Crosstalk-Solutions/project-nomad
- 链接：https://github.com/Crosstalk-Solutions/project-nomad
- 归类：AI Agent / 编排框架
- Stars：33864
- 主要语言：TypeScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Project N.O.M.A.D, is a self-contained, offline survival computer packed with critical tools, knowledge, and AI to keep you informed and empowered—anytime, anywhere.
  - **AI Chat with Knowledge Base** — local AI chat powered by Ollama（https://ollama.com/） or you can use OpenAI API compatible software such as LM Studio or llama.cpp, with document upload and semantic search (RAG via Qdrant（https://qdrant.tech/）)
  - **Information Library** — offline Wikipedia, medical references, ebooks, and more via Kiwix（https://kiwix.org/）
  - **Education Platform** — Khan Academy courses with progress tracking via Kolibri（https://learningequality.org/kolibri/）
  - **Offline Maps** — downloadable regional maps via ProtoMaps（https://protomaps.com）
  - **Data Tools** — encryption, encoding, and analysis via CyberChef（https://gchq.github.io/CyberChef/）

#### 6. ColeMurray/background-agents
- 链接：https://github.com/ColeMurray/background-agents
- 归类：AI Agent / 编排框架
- Stars：2299
- 主要语言：TypeScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - An open-source background agents coding system
  - Work on tasks in the background while you focus on other things
  - Access full development environments (Node.js, Python, git, browser automation, VS Code)
  - Connect from anywhere — web UI, Slack, GitHub PRs, Linear issues, or webhooks
  - Enable multiplayer sessions where multiple people can collaborate in real time
  - Create PRs with proper commit attribution to the prompting user

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
