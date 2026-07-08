# GitHub 今日 AI Trending 测开分析（2026-07-08）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- RAG / 知识库: 1 个

### 热门项目速览

#### 1. MadsLorentzen/ai-job-search
- 链接：https://github.com/MadsLorentzen/ai-job-search
- 归类：AI Agent / 编排框架
- Stars：11492
- 主要语言：TypeScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - AI-powered job application framework built on Claude Code. Fork it, fill in your profile, and let Claude evaluate jobs, tailor CVs, write cover letters, and prepare you for interviews.
  - Claude Code（https://claude.com/claude-code） (CLI)
  - Python 3.10+
  - Bun（https://bun.sh） (for Danish job search CLI tools)
  - LaTeX distribution with `lualatex` and `xelatex`: TeX Live（https://tug.org/texlive/） or MiKTeX（https://miktex.org/）. The CV compiles with `lualatex` (pdflatex often fails on modern MiKTeX installs with `fontawesome5` font-expansion errors); the cover letter compiles with `xelatex` because `cover.cls` requires `fontspec`.
  - Optional: `pdftotext` from poppler（https://poppler.freedesktop.org/） (macOS: `brew install poppler`, Debian/Ubuntu: `apt install poppler-utils`, Windows: `choco install poppler`) — used by `/apply`'s ATS parseability check on the compiled CV. If missing, the check degrades gracefully to a visual keyword review.

#### 2. Zackriya-Solutions/meetily
- 链接：https://github.com/Zackriya-Solutions/meetily
- 归类：AI Agent / 编排框架
- Stars：20907
- 主要语言：Rust
- Topics：ai, ai-meeting-assistant, llm, local-ai, mac, meeting-minutes, meeting-notes, offline-first, ollama, parakeet, privacy-focused, privacy-tools
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Privacy first, AI meeting assistant with 4x faster Parakeet/Whisper live transcription, speaker diarization, and Ollama summarization built on Rust. 100% local processing. no cloud required. Meetily (Meetly Ai - https://meetily.ai) is the #1 Self-hosted, Open-source Ai meeting note taker for macOS & Windows.
  - Introduction
  - Why Meetily?
  - Features
  - Installation
  - Key Features in Action

#### 3. addyosmani/agent-skills
- 链接：https://github.com/addyosmani/agent-skills
- 归类：AI Agent / 编排框架
- Stars：72311
- 主要语言：JavaScript
- Topics：agent-skills, antigravity, claude-code, codex, cursor, skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Production-grade engineering skills for AI coding agents.

#### 4. asgeirtj/system_prompts_leaks
- 链接：https://github.com/asgeirtj/system_prompts_leaks
- 归类：AI Agent / 编排框架
- Stars：53168
- 主要语言：JavaScript
- Topics：ai, ai-agents, anthropic, awesome, chatbot, chatgpt, claude, claude-code, codex, deep-learning, education, gemini
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Extracted system prompts from Anthropic - Claude Fable 5, Opus 4.8, Claude Code, Claude Design. OpenAI - ChatGPT 5.5 Thinking, GPT 5.5 Instant, Codex. Google - Gemini 3.5 Flash, 3.1 Pro, Antigravity. xAI - Grok, Cursor, Copilot, VS Code, Perplexity, and more. Updated regularly.

#### 5. TencentCloud/CubeSandbox
- 链接：https://github.com/TencentCloud/CubeSandbox
- 归类：AI Agent / 编排框架
- Stars：8528
- 主要语言：Rust
- Topics：agents, container, sandbox
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Instant, Concurrent, Secure & Lightweight Sandbox for AI Agents.

#### 6. steipete/CodexBar
- 链接：https://github.com/steipete/CodexBar
- 归类：RAG / 知识库
- Stars：17074
- 主要语言：Swift
- Topics：ai, claude-code, codex, swift
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Show usage stats for OpenAI Codex and Claude Code, without having to login.
  - **Plan around resets.** Per-provider session, weekly, and monthly windows with countdowns to the next reset — stop guessing whether to start that long task.
  - **Credits, spend, and cost scans.** Credit balances, Admin API spend dashboards, provider billing summaries, and local cost scans where the source exposes enough detail.
  - **Live status.** Provider status polling surfaces incident badges in the menu and an indicator overlay on the bar icon.
  - **Privacy-first.** Reuses existing provider sessions — OAuth, device flow, API keys, browser cookies, local files — so no passwords are stored.
  - macOS 14+ (Sonoma)

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
