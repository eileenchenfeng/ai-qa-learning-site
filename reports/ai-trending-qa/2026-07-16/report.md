# GitHub 今日 AI Trending 测开分析（2026-07-16）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- 训练 / 数据: 1 个

### 热门项目速览

#### 1. Nutlope/hallmark
- 链接：https://github.com/Nutlope/hallmark
- 归类：AI Agent / 编排框架
- Stars：8884
- 主要语言：CSS
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Anti-AI-slop design skill for Claude Code, Cursor, and Codex.
  - **Claude Code**: `~/.claude/skills/hallmark/`
  - **Cursor**: `.cursor/rules/hallmark.mdc` (body of `SKILL.md`, no frontmatter)
  - **Codex**: `~/.codex/skills/hallmark/` (personal) or `.codex/skills/hallmar

#### 2. mattpocock/skills
- 链接：https://github.com/mattpocock/skills
- 归类：AI Agent / 编排框架
- Stars：172540
- 主要语言：Shell
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Skills for Real Engineers. Straight from my .claude directory.
  - Run the skills.sh installer:
  - Pick the skills you want, and which coding agents you want to install them on. **Make sure you select `/setup-matt-pocock-skills`**.
  - Run `/setup-matt-pocock-skills` in your agent. It will:
  - Ask you which issue tracker you want to use (GitHub, Linear, or local files)
  - Ask you what labels you apply to tickets when you triage them (`/triage` uses labels)

#### 3. moeru-ai/airi
- 链接：https://github.com/moeru-ai/airi
- 归类：训练 / 数据
- Stars：42573
- 主要语言：TypeScript
- Topics：ai-companion, ai-vtuber, airi, digital-life, grok-companion, live2d, neuro-sama, neurosama, openclaw, vrm, vtuber
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 💖🧸 Self hosted, you-owned Grok Companion, a container of souls of waifu, cyber livings to bring them into our worlds, wishing to achieve Neuro-sama's altitude. Capable of realtime voice chat, Minecraft, Factorio playing. Web / macOS / Windows supported.

#### 4. Dicklesworthstone/destructive_command_guard
- 链接：https://github.com/Dicklesworthstone/destructive_command_guard
- 归类：AI Agent / 编排框架
- Stars：4810
- 主要语言：Rust
- Topics：ai-agents, cli, developer-tools, git, rust, safety
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The Destructive Command Guard (dcg) is for blocking dangerous git and shell commands from being executed by agents.

#### 5. HKUDS/Vibe-Trading
- 链接：https://github.com/HKUDS/Vibe-Trading
- 归类：AI Agent / 编排框架
- Stars：23798
- 主要语言：Python
- Topics：ai-agent, algorithmic-trading, backtesting, fintech, llm, mcp, multi-agent, python, quantitative-finance, trading
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "Vibe-Trading: Your Personal Trading Agent"
  - **2026-07-15** 🧮 **Backtest correctness + Portfolio Studio core**: A 10-PR convergence pass made rebalances causal and order-independent, charged terminal close costs, reported fill-derived turnover, enforced exposure caps, and kept validation output finite and strict (#530（https://github.com/HKUDS/Vibe-Trading/pull/530）/#531（https://github.com/HKUDS/Vibe-Trading/pull/531）/#532（https://github.com/HKUDS/Vibe-Trading/pull/532）/#540（https://github.com/HKUDS/Vibe-Trading/pull/540）). Charts now reuse the run's actual data source, repeatable market queries are no longer dropped, and `.env` loads refresh cached config (#535（https://github.com/HKUDS/Vibe-Trading/pull/535）/#544（https://github.com/HKUDS/Vibe-Trading/pull/544）/#554（https://github.com/HKUDS/Vibe-Trading/pull/554）). Portfolio Studio #456（https://github.com/HKUDS/Vibe-Trading/issues/456） and config bug #541（https://github.com/HKUDS/Vibe-Trading/issues/541） are closed; provider fixes #528（https://github.com/HKUDS/Vibe-Trading/issues/528）/#529（https://github.com/HKUDS/Vibe-Trading/issues/529） closed too. Thanks @YZY0108, @santhreal, @Robin1987China, @xkam7ar, @Marnie0415, and @marichu99.
  - **2026-07-14** 🌉 **Longbridge market data + modern MCP transport + provider reliability**: Longbridge joins the historical-data fallback layer with key-gated credentials, date-window splitting, strict completeness checks, and an opt-in SDK dependency; four China-market flow tools gain verified Tushare fallbacks, and negative final equity no longer crashes backtest metrics. The MCP server now supports Streamable HTTP, `write_file` safely recovers aliased or missing path arguments, hypothesis updates reject unsupported fields, and Correlation requests are authenticated. NVIDIA NIM is now a first-class provider across Web Settings and both CLI onboarding paths, with a versioned compatibility User-Agent to address the reported 403; Web Settings now writes to the canonical `~/.vibe-trading/.env`, migrates legacy configuration, and reports permission failures clearly, fixing the DeepSeek save-time 500 (#534（https://github.com/HKUDS/Vibe-Trading/pull/534）, closes #516（https://github.com/HKUDS/Vibe-Trading/issues/516）/#524（https://github.com/HKUDS/Vibe-Trading/issues/524）; #528（https://github.com/HKUDS/Vibe-Trading/issues/528）/#529（https://github.com/HKUDS/Vibe-Trading/issues/529）). Thanks @fanfpy, @asahikiko, @santhreal, @sTunnaSu, @abhishekjaisinghani, @huangcheng, @ShiroKSH, @Meru143, @DIEGOD79, and @not-knope for the code, reports, and diagnosis.
  - **2026-07-13** 🔒 **Security hardening: all 10 external-audit findings closed + contributor batch**: every finding from the 2026-07-10 external security audit (issue #476（https://github.com/HKUDS/Vibe-Trading/issues/476）, discussion #468（https://github.com/HKUDS/Vibe-Trading/discussions/468）) is now addressed on `main` — Docker multi-stage rebuild wit

#### 6. openinterpreter/openinterpreter
- 链接：https://github.com/openinterpreter/openinterpreter
- 归类：AI Agent / 编排框架
- Stars：65558
- 主要语言：Rust
- Topics：acp, coding-agent, deepseek, kimi, qwen, rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A coding agent for low-cost models
  - Runs commands inside native sandboxing on macOS, Linux, and Windows.
  - Switches providers and models from the TUI with `/model`.
  - Inspects or switches Rust-native model harnesses with `/harness`.
  - Tests web and native apps through the built-in QA skill.
  - Runs as an Agent Client Protocol（https://agentclientprotocol.com/） agent for editors with `interpreter acp`.

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
