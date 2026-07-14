# GitHub 今日 AI Trending 测开分析（2026-07-14）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- 训练 / 数据: 1 个

### 热门项目速览

#### 1. HKUDS/Vibe-Trading
- 链接：https://github.com/HKUDS/Vibe-Trading
- 归类：AI Agent / 编排框架
- Stars：21950
- 主要语言：Python
- Topics：ai-agent, algorithmic-trading, backtesting, fintech, llm, mcp, multi-agent, python, quantitative-finance, trading
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "Vibe-Trading: Your Personal Trading Agent"
  - **2026-07-13** 🔒 **Security hardening: all 10 external-audit findings closed + contributor batch**: every finding from the 2026-07-10 external security audit (issue #476（https://github.com/HKUDS/Vibe-Trading/issues/476）, discussion #468（https://github.com/HKUDS/Vibe-Trading/discussions/468）) is now addressed on `main` — Docker multi-stage rebuild with digest-pinned images, an AST-hardened backtest sandbox blocking network/subprocess/eval/os.environ/unsafe-open (including inside nested function bodies), short-lived single-use SSE auth tickets, hardened Compose (read-only rootfs, dropped capabilities, resource limits), auth + rate limiting on `/correlation`, security headers, hash-locked dependencies, and more. Also merged: opt-in **TAP mode** for Alpaca key isolation (#377（https://github.com/HKUDS/Vibe-Trading/pull/377）, thanks @0xZKnw), realized portfolio turnover surfaced in backtest metrics (#478（https://github.com/HKUDS/Vibe-Trading/pull/478）, thanks @Robin1987China), a **Frazzini-Pedersen betting-against-beta** academic factor (Alpha Zoo → 461, #480（https://github.com/HKUDS/Vibe-Trading/pull/480）, thanks @YogeshModi24), a look-ahead-bias fix across all 5 portfolio optimizers (#487（https://github.com/HKUDS/Vibe-Trading/pull/487）, thanks @YZY0108), and two preflight/provider-config fixes (#479（https://github.com/HKUDS/Vibe-Trading/pull/479）/#484（https://github.com/HKUDS/Vibe-Trading/pull/484）, closes #477（https://github.com/HKUDS/Vibe-Trading/issues/477）/#482（https://github.com/HKUDS/Vibe-Trading/issues/482）, thanks @ananaymital/@Bortlesboat).
  - **2026-07-12** 🧪 **Strategy Development Manager + contributor fix batch**: the new `strategy-dev-manager` skill (#87) turns academic papers and broker research into registered factors/strategies with a persistent artifact store and automated IC/Sharpe decay monitoring — `sdm_register` / `sdm_status` / `sdm_decay_scan` drive an active → monitoring → decayed → disabled lifecycle over `~/.vibe-trading/` (#457（https://github.com/HKUDS/Vibe-Trading/pull/457）, closes #455（https://github.com/HKUDS/Vibe-Trading/issues/455）, thanks @shadowinlife). Also merged: the Correlation tab accepts bare tickers (`AAPL,SPY`) and walks the full loader fallback chain (#472（https://github.com/HKUDS/Vibe-Trading/pull/472）, closes #471（https://github.com/HKUDS/Vibe-Trading/issues/471）, thanks @yxhuang), the `local` loader honors requested intervals via OHLCV resampling (#467（https://github.com/HKUDS/Vibe-Trading/pull/467）, thanks @Shizoqua), Binance USD-M perpetual history lands with explicit `BTC-USDT-PERP` routing + execution/mark price separation as the first #462（https://github.com/HKUDS/Vibe-Trading/issues/462） slice (#470（https://github.com/HKUDS/Vibe-Trading/pull/470）, thanks @honginp), FastMCP transport imports now work across both module layouts (#469（https://github.com/HKUDS/Vibe-Trading/pull/469）, t

#### 2. moeru-ai/airi
- 链接：https://github.com/moeru-ai/airi
- 归类：训练 / 数据
- Stars：41994
- 主要语言：TypeScript
- Topics：ai-companion, ai-vtuber, airi, digital-life, grok-companion, live2d, neuro-sama, neurosama, openclaw, vrm, vtuber
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 💖🧸 Self hosted, you-owned Grok Companion, a container of souls of waifu, cyber livings to bring them into our worlds, wishing to achieve Neuro-sama's altitude. Capable of realtime voice chat, Minecraft, Factorio playing. Web / macOS / Windows supported.

#### 3. Shubhamsaboo/awesome-llm-apps
- 链接：https://github.com/Shubhamsaboo/awesome-llm-apps
- 归类：AI Agent / 编排框架
- Stars：119804
- 主要语言：Python
- Topics：agents, llms, python, rag
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 100+ AI Agent & RAG apps you can actually run — clone, customize, ship.
  - 🛠️ **Hand-built, not curated** - every template is original work, tested end-to-end before it ships.
  - 🧪 **Runs in 3 commands** - no broken `requirements.txt`, no "figure it out yourself" scaffolding.
  - 🧠 **Covers the modern AI stack** - AI Agents, Always-on Agents, Multi-agent Teams, MCP Agents, Voice AI Agents, RAG, Agent Skills, Fine-tuning.
  - 🌐 **Provider-agnostic** - switch between Claude, Gemini, GPT, Llama, Qwen, xAI and others with a config change.
  - 📚 **Step-by-step tutorials** - every featured template has a free walkthrough on Unwind AI（https://www.theunwindai.com）.

#### 4. Nutlope/hallmark
- 链接：https://github.com/Nutlope/hallmark
- 归类：AI Agent / 编排框架
- Stars：5303
- 主要语言：CSS
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Anti-AI-slop design skill for Claude Code, Cursor, and Codex.
  - **Claude Code**: `~/.claude/skills/hallmark/`
  - **Cursor**: `.cursor/rules/hallmark.mdc` (body of `SKILL.md`, no frontmatter)
  - **Codex**: `~/.codex/skills/hallmark/` (personal) or `.codex/skills/hallmar

#### 5. Graphify-Labs/graphify
- 链接：https://github.com/Graphify-Labs/graphify
- 归类：AI Agent / 编排框架
- Stars：84948
- 主要语言：Python
- Topics：antigravity, claude-code, codex, gemini, graphrag, knowledge-graph, leiden, openclaw, rag, skills, tree-sitter
- 项目特色（基于 description/README 片段的轻量提炼）：
  - AI coding assistant skill (Claude Code, Codex, OpenCode, Cursor, Gemini CLI, and more). Turn any folder of code, SQL schemas, R scripts, shell scripts, docs, papers, images, or videos into a queryable knowledge graph. App code + database schema + infrastructure in one graph.
  - **Code maps for free, fully local.** Code is parsed with tree-sitter AST: deterministic, no LLM, nothing leaves your machine. (Docs, PDFs, images and video use your assistant's model, or a configured API key, for a semantic pass.)
  - **Every edge is explained.** Each connection is tagged `EXTRACTED` (explicit in the source) or `INFERRED` (resolved by graphify), so you can tell what was read directly from what was inferred.
  - **Not a vector index.** No embeddings, no vector store: a real graph you traverse. Ask a question, trace the path between two things, or explain one concept.

#### 6. hasaneyldrm/exercises-dataset
- 链接：https://github.com/hasaneyldrm/exercises-dataset
- 归类：AI Agent / 编排框架
- Stars：12744
- 主要语言：HTML
- Topics：dataset, exercise-database, exercises, fitness, fitness-app, gym, json, logpress, react-native, workout
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 1,324-exercise fitness dataset — animation GIFs, 180×180 thumbnails, muscle-group & equipment data, and step-by-step instructions in 6 languages. The exercise data layer behind the LogPress app.
  - 1,324 exercises with category, body-part, equipment, target and muscle-group data
  - an animation GIF + 180×180 thumbnail for every exercise (media © Gym visual（https://gymvisual.com/） — see License)
  - step-by-step instructions in 9 languages (🇬🇧 English, 🇪🇸 Spanish, 🇮🇹 Italian, 🇹🇷 Turkish, 🇷🇺 Russian, 🇨🇳 Chinese, 🇮🇳 Hindi, 🇵🇱 Polish, 🇰🇷 Korean)
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

#### 训练 / 数据
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：数据链路——数据漂移监控、标注一致性、训练配置可追溯（config-as-code）。
- 对训练脚本做“可复现实验”测试：固定随机种子/依赖版本后，关键指标应落在阈值区间。
- 引入数据质量门禁：空值、重复、分布异常、敏感信息扫描（如适用）。

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
