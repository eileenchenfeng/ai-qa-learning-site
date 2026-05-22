# GitHub 今日 AI Trending 测开分析（2026-05-22）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. multica-ai/andrej-karpathy-skills
- 链接：https://github.com/multica-ai/andrej-karpathy-skills
- 归类：AI Agent / 编排框架
- Stars：143688
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A single CLAUDE.md file to improve Claude Code behavior, derived from Andrej Karpathy's observations on LLM coding pitfalls.
  - **State assumptions explicitly** — If uncertain, ask rather than guess
  - **Present multiple interpretations** — Don't pick silently when ambiguity exists
  - **Push back when warranted** — If a simpler approach exists, say so
  - **Stop when confused** — Name what's unclear and ask for clarification
  - No features beyond what was asked

#### 2. dotnet/skills
- 链接：https://github.com/dotnet/skills
- 归类：AI Agent / 编排框架
- Stars：2255
- 主要语言：C#
- Topics：agent-skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Repository for skills to assist AI coding agents with .NET and C#
  - Launch Copilot CLI or Claude Code
  - Add the marketplace:
  - Install a plugin:
  - Restart to load the new plugins
  - View available skills:

#### 3. obra/superpowers
- 链接：https://github.com/obra/superpowers
- 归类：AI Agent / 编排框架
- Stars：201793
- 主要语言：Shell
- 项目特色（基于 description/README 片段的轻量提炼）：
  - An agentic skills framework & software development methodology that works.
  - Install the plugin from Anthropic's official marketplace:
  - Register the marketplace:
  - Install the plugin from this marketplace:
  - Open the plugin search interface:
  - Search for Superpowers:

#### 4. HKUDS/CLI-Anything
- 链接：https://github.com/HKUDS/CLI-Anything
- 归类：AI Agent / 编排框架
- Stars：39232
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/
  - **2026-05-20** 🎛️ **Rekordbox CLI** merged (#252) with guarded SQLCipher write paths, backup-required forced writes, smoke coverage, and root skill sync. 📚 **Calibre CLI** merged (#223) with library/search/metadata/conversion/export workflows, 41 unit tests, real-Calibre E2E evidence, and root skill validation. 🧊 **3MF CLI** merged (#209) with mesh inspection, hole resizing, repair, comparison, and preserved triangle attributes. 🎙️ **MiniMax CLI** merged (#189) with chat/TTS workflows, JSON-safe model/voice listing, REPL quote handling, and smoke/E2E coverage. 🎮 **UEAtelier** joined the registry (#297) as an Unreal Editor MCP self-extension workbench with a Python CLI proxy.
  - **2026-05-19** 🛠️ Existing harnesses got a quality/security pass — **Zoom** downloads recordings from direct URLs (#294), **Obsidian** search now uses the Local REST API vendor content types (#289), **LibreOffice** headless conversion is more robust on macOS (#290), and XML/SVG/ODF/MLT/MusicXML/CSL parsing now routes untrusted input through `defusedxml` (#296).
  - **2026-05-18** 📈 README presentation refreshed with the Trendshift badge and centered project header polish (#285, #286), keeping the landing section focused on discovery and project momentum.
  - **2026-05-17** 🌐 **CLI-Hub** registry handling was hardened (#281) — registry entries are now copied before `_source` tagging, preventing cached or mocked registry data from being mutated in place.
  - **2026-05-16** 🔧 **n8n** received the REPL banner crash fix that later merged into main (#280), restoring the no-subcommand interactive startup path with regression coverage.

#### 5. ChromeDevTools/chrome-devtools-mcp
- 链接：https://github.com/ChromeDevTools/chrome-devtools-mcp
- 归类：AI Agent / 编排框架
- Stars：40579
- 主要语言：TypeScript
- Topics：browser, chrome, chrome-devtools, debugging, devtools, mcp, mcp-server, puppeteer
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Chrome DevTools for coding agents
  - **Get performance insights**: Uses [Chrome
  - **Advanced browser debugging**: Analyze network requests, take screenshots and
  - **Reliable automation**. Uses
  - Node.js（https://nodejs.org/） LTS（https://github.com/nodejs/Release#release-schedule） version.
  - Chrome（https://www.google.com/chrome/） current stable version or newer.

#### 6. rohitg00/ai-engineering-from-scratch
- 链接：https://github.com/rohitg00/ai-engineering-from-scratch
- 归类：AI Agent / 编排框架
- Stars：10915
- 主要语言：Python
- Topics：agents, ai, ai-agents, ai-engineering, computer-vision, course, deep-learning, from-scratch, generative-ai, llm, machine-learning, mcp
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Learn it. Build it. Ship it for others.

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
