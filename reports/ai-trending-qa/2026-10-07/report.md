# GitHub 今日 AI Trending 测开分析（2026-10-07）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. mattpocock/skills
- 链接：https://github.com/mattpocock/skills
- 归类：AI Agent / 编排框架
- Stars：278391
- 主要语言：Shell
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Skills for Real Engineers. Straight from my .agents directory.
  - Ask you which issue tracker you want to use (GitHub, GitLab, local files, or anything else you describe)
  - Ask you what labels you apply to tickets when you triage them (`/triage` uses labels)
  - Ask you where you want to save any docs we create
  - `/grill-me` - for non-code uses
  - `/grill-with-docs` - same as `/grill-me`, but adds more goodies (see below)

#### 2. earthtojake/text-to-cad
- 链接：https://github.com/earthtojake/text-to-cad
- 归类：AI Agent / 编排框架
- Stars：18092
- 主要语言：Python
- Topics：agents, ai-agents, cad, mechanical-engineering, robotics, step, stl, stp, text-to-cad
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Give your agent CAD superpowers.
  - CAD runs through uv（https://docs.astral.sh/uv/）: check that it is installed
  - Run the commands under your agent app's heading below, or under
  - Restart the app. Its first start downloads CAD's runtime, so it needs a network

#### 3. pbakaus/impeccable
- 链接：https://github.com/pbakaus/impeccable
- 归类：AI Agent / 编排框架
- Stars：77839
- 主要语言：JavaScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The design language that makes your AI harness better at design.
  - **One setup flow.** `/impeccable init` records durable product truth in `PRODUCT.md`, so later commands know the audience, purpose, operating context, constraints, voice, and evidence without confusing those facts with surface-level visual direction.
  - **24 commands.** A shared design vocabulary with your AI: `polish`, `audit`, `critique`, `distill`, `animate`, `bolder`, `quieter`, and more.
  - **60 deterministic detector rules** plus LLM-only critique checks. The CLI and browser extension run the deterministic rules with no LLM and no API key.
  - Don't use overused fonts (Arial, Inter, system defaults)
  - Don't use gray text on colored backgrounds

#### 4. thedotmack/claude-mem
- 链接：https://github.com/thedotmack/claude-mem
- 归类：AI Agent / 编排框架
- Stars：97280
- 主要语言：TypeScript
- Topics：ai, ai-agents, ai-memory, anthropic, artificial-intelligence, chromadb, claude, claude-agent-sdk, claude-agents, claude-code, claude-code-plugin, claude-skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Persistent Context Across Sessions for Every Agent – Captures everything your agent does during sessions, compresses it with AI, and injects relevant context back into future sessions. Works with Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode + More

#### 5. ayghri/i-have-adhd
- 链接：https://github.com/ayghri/i-have-adhd
- 归类：AI Agent / 编排框架
- Stars：54523
- 主要语言：Python
- Topics：adhd, claude-, claude-code-plugin, claude-skills, developer-tools, productivity
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A skill to stop your coding agent from burying the answer. ADHD-friendly output.
  - Lead with the next action.
  - Number multi-step tasks.
  - End with one concrete next step.
  - Suppress tangents.
  - Restate state every turn.

#### 6. morluto/rea
- 链接：https://github.com/morluto/rea
- 归类：AI Agent / 编排框架
- Stars：10350
- 主要语言：TypeScript
- Topics：agent-skills, ai-agent-tools, ai-agents, binary-analysis, cli, coding-agents, cordis, ctf, decompiler, disassembler, dsh, dsh-plugin
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Reverse engineer anything with agents, from app behavior down to native binaries.

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
