# GitHub 今日 AI Trending 测开分析（2026-06-02）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- 应用层 / UI: 1 个

### 热门项目速览

#### 1. microsoft/markitdown
- 链接：https://github.com/microsoft/markitdown
- 归类：AI Agent / 编排框架
- Stars：139044
- 主要语言：Python
- Topics：autogen, autogen-extension, langchain, markdown, microsoft-office, openai, pdf
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Python tool for converting files and office documents to Markdown.
  - PowerPoint
  - Images (EXIF metadata and OCR)
  - Audio (EXIF metadata and speech transcription)

#### 2. nesquena/hermes-webui
- 链接：https://github.com/nesquena/hermes-webui
- 归类：AI Agent / 编排框架
- Stars：11579
- 主要语言：Python
- Topics：agent, ai-agents, hermes, hermes-agent, nous-research
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Hermes WebUI: The best way to use Hermes Agent from the web or from your phone!
  - Why Hermes — what it is and how it compares
  - Quick start — clone + `bootstrap.py` / `start.sh` / `ctl.sh`
  - Features — chat, sessions, workspace, voice, profiles, security, themes, panels, mobile
  - Configuration & access — auto-discovery, overrides, remote/Tailscale/phone, manual launch
  - Docker — single- and multi-container deploys

#### 3. supermemoryai/supermemory
- 链接：https://github.com/supermemoryai/supermemory
- 归类：AI Agent / 编排框架
- Stars：24112
- 主要语言：TypeScript
- Topics：agent-memory, ai-memory, cloudflare-kv, cloudflare-pages, cloudflare-workers, drizzle-orm, memory, postgres, remix, tailwindcss, typescript, vite
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Memory engine and app that is extremely fast, scalable. The Memory API for the AI era.
  - Openclaw plugin: https://github.com/supermemoryai/openclaw-supermemory
  - Claude code plugin: https://github.com/supermemoryai/claude-supermemory
  - OpenCode plugin: https://github.com/supermemoryai/opencode-supermemory
  - Hermes agent (Supermemory memory provider): https://github.com/NousResearch/hermes-agent
  - **You talk to your AI normally.** Share preferences, mention projects, discuss problems.

#### 4. harry0703/MoneyPrinterTurbo
- 链接：https://github.com/harry0703/MoneyPrinterTurbo
- 归类：应用层 / UI
- Stars：77116
- 主要语言：Python
- Topics：ai, automation, chatgpt, moviepy, python, shortvideo, tiktok
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 利用AI大模型，一键生成高清短视频 Generate short videos with one click using AI LLM.
  - [x] 完整的 **MVC架构**，代码 **结构清晰**，易于维护，支持 `API` 和 `Web界面`
  - [x] 支持视频文案 **AI自动生成**，也可以**自定义文案**
  - [x] 支持多种 **高清视频** 尺寸
  - [x] 竖屏 9:16，`1080x1920`
  - [x] 横屏 16:9，`1920x1080`

#### 5. D4Vinci/Scrapling
- 链接：https://github.com/D4Vinci/Scrapling
- 归类：AI Agent / 编排框架
- Stars：58297
- 主要语言：Python
- Topics：ai, ai-scraping, automation, crawler, crawling, crawling-python, data, data-extraction, mcp, mcp-server, playwright, python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 🕷️ An adaptive Web Scraping framework that handles everything from a single request to a full-scale crawl!

#### 6. pbakaus/impeccable
- 链接：https://github.com/pbakaus/impeccable
- 归类：AI Agent / 编排框架
- Stars：32923
- 主要语言：JavaScript
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The design language that makes your AI harness better at design.
  - **7 domain reference files** (view source). Typography, color, motion, spatial, interaction, responsive, UX writing. Load on every command, alongside a brand-vs-product register that adjusts the defaults.
  - **23 commands.** A shared design vocabulary with your AI: `polish`, `audit`, `critique`, `distill`, `animate`, `bolder`, `quieter`, and more.
  - **27 deterministic anti-pattern rules** plus a 12-rule LLM critique pass. CLI and browser extension run the deterministic ones with no LLM and no API key. Each is tied to specific design guidance the skill teaches against.
  - Don't use overused fonts (Arial, Inter, system defaults)
  - Don't use gray text on colored backgrounds

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

#### 应用层 / UI
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：用户路径与可用性——长对话、断网重连、输入法、文件上传、复制代码块等高频操作。
- 用 Playwright 建立‘关键路径回放’：登录→创建会话→提问→流式输出→引用/工具调用结果展示。
- 把前端埋点当作测试断言的一部分：关键交互必须产生日志/事件，方便线上回溯。

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
