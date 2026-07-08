# GitHub 今日 AI Trending 测开分析（2026-07-06）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. Zackriya-Solutions/meetily
- 链接：https://github.com/Zackriya-Solutions/meetily
- 归类：AI Agent / 编排框架
- Stars：17426
- 主要语言：Rust
- Topics：ai, ai-meeting-assistant, llm, local-ai, mac, meeting-minutes, meeting-notes, offline-first, ollama, parakeet, privacy-focused, privacy-tools
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Privacy first, AI meeting assistant with 4x faster Parakeet/Whisper live transcription, speaker diarization, and Ollama summarization built on Rust. 100% local processing. no cloud required. Meetily (Meetly Ai - https://meetily.ai) is the #1 Self-hosted, Open-source Ai meeting note taker for macOS & Windows.
  - Introduction
  - Why Meetily?
  - Features
  - Installation
  - Key Features in Action

#### 2. openai/codex-plugin-cc
- 链接：https://github.com/openai/codex-plugin-cc
- 归类：AI Agent / 编排框架
- Stars：25653
- 主要语言：JavaScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Use Codex from Claude Code to review code or delegate tasks.
  - `/codex:review` for a normal read-only Codex review
  - `/codex:adversarial-review` for a steerable challenge review
  - `/codex:rescue`, `/codex:transfer`, `/codex:status`, `/codex:result`, and `/codex:cancel` to delegate work, hand off sessions, and manage background jobs
  - **ChatGPT subscription (incl. Free) or OpenAI API key.**
  - Usage will contribute to your Codex usage limits. Learn more（https://developers.openai.com/codex/pricing）.

#### 3. asgeirtj/system_prompts_leaks
- 链接：https://github.com/asgeirtj/system_prompts_leaks
- 归类：AI Agent / 编排框架
- Stars：50224
- 主要语言：JavaScript
- Topics：ai, ai-agents, anthropic, awesome, chatbot, chatgpt, claude, claude-code, codex, deep-learning, education, gemini
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Extracted system prompts from Anthropic - Claude Fable 5, Opus 4.8, Claude Code, Claude Design. OpenAI - ChatGPT 5.5 Thinking, GPT 5.5 Instant, Codex. Google - Gemini 3.5 Flash, 3.1 Pro, Antigravity. xAI - Grok, Cursor, Copilot, VS Code, Perplexity, and more. Updated regularly.

#### 4. Leonxlnx/taste-skill
- 链接：https://github.com/Leonxlnx/taste-skill
- 归类：AI Agent / 编排框架
- Stars：57769
- 主要语言：JavaScript
- Topics：agent, ai, claude, claude-code, codex, coding, design, frontend, lowcode, nocode, skill, skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Taste-Skill - gives your AI good taste. stops the AI from generating boring, generic slop
  - Open a Pull Request or Issue on GitHub
  - DM @lexnlin（https://x.com/lexnlin） or @blueemi99（https://x.com/blueemi99）
  - Email us at hello@tasteskill.dev

#### 5. alirezarezvani/claude-skills
- 链接：https://github.com/alirezarezvani/claude-skills
- 归类：AI Agent / 编排框架
- Stars：20688
- 主要语言：Python
- Topics：agent-plugins, agent-skills, agentic-ai, ai-coding-agent, anthropic-claude, claude-ai, claude-code, claude-code-plugins, claude-code-skills, claude-skills, codex-skills, coding-agent-plugins
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 337 Claude Code skills & agent skills & plugins (30+ Agents, 70+ custom commands, 330+ skills, customizable references, scripts)for Claude Code, Codex, Gemini CLI, Cursor, and 8 more coding agents — engineering, marketing, product, compliance, C-level advisory, research, business operations, commercial & finance, and your daily productivity skills.
  - **SKILL.md** — structured instructions, workflows, and decision frameworks
  - **Python tools** — 593 CLI scripts (all stdlib-only, zero pip installs)
  - **Reference docs** — 711 templates, checklists, and domain-specific knowledge files

#### 6. ogulcancelik/herdr
- 链接：https://github.com/ogulcancelik/herdr
- 归类：AI Agent / 编排框架
- Stars：12208
- 主要语言：Rust
- Topics：agent, agent-orchestration, ai, ai-agents, claude-code, cli, codex, coding-agents, developer-tools, devtools, multiplexer, rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - agent multiplexer that lives in your terminal.
  - **a real terminal per agent.** you see each agent's own screen, not an app's imitation of one, so even full-screen TUIs render right.
  - **agent state at a glance.** the sidebar rolls every agent up to 🔴 blocked, 🟡 working, 🔵 done, or 🟢 idle, so you always know who needs you. zero config, no hooks required.
  - **workspaces, tabs, panes.** organize by repo or folder, click, drag, and split, mouse-native throughout.
  - **nothing dies on detach.** a background server keeps panes and agents alive; detach and reattach from any terminal, including your phone over ssh.
  - **runs anywhere.** single ~10MB rust binary, linux and macos (windows beta), no dependencies, runs inside the terminal you already use.

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
