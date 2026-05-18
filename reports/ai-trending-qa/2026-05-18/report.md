# GitHub 今日 AI Trending 测开分析（2026-05-18）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. tinyhumansai/openhuman
- 链接：https://github.com/tinyhumansai/openhuman
- 归类：AI Agent / 编排框架
- Stars：14011
- 主要语言：Rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Your Personal AI super intelligence. Private, Simple and extremely powerful.
  - **Simple, UI-first & Human** A clean desktop experience and short onboarding paths take you from install to a working agent in a few clicks — no config-first setup, no terminal required. The agent has a face（https://tinyhumans.gitbook.io/openhuman/features/mascot）: a desktop mascot that speaks, reacts to its surroundings, joins your Google Meets（https://tinyhumans.gitbook.io/openhuman/features/mascot/meeting-agents） as a real participant, remembers you across weeks, and keeps thinking in the background even when you've stopped typing.
  - **118+ third-party integrations（https://tinyhumans.gitbook.io/openhuman/features/integrations） with auto-fetch（https://tinyhumans.gitbook.io/openhuman/features/obsidian-wiki/auto-fetch）**: plug into Gmail, Notion, GitHub, Slack, Stripe, Calendar, Drive, Linear, Jira and the rest of your stack with **one-click OAuth**. Every connection is exposed to the agent as a typed tool, and every twenty minutes the core walks each active connection and pulls fresh data into the memory tree（https://tinyhumans.gitbook.io/openhuman/features/integrations/auto-fetch）. No prompts, no polling loops you have to write, so the agent already has tomorrow's context this morning.
  - **Memory Tree（https://tinyhumans.gitbook.io/openhuman/features/memory-tree） + Obsidian Wiki（https://tinyhumans.gitbook.io/openhuman/features/obsidian-wiki）**: a local-first knowledge base built from your data and your activity. Everything you connect is canonicalized into ≤3k-token Markdown chunks, scored, and folded into hierarchical summary trees stored in **SQLite on your machine**. The same chunks land as `.md` files in an Obsidian-compatible vault you can open, browse and edit, inspired by Karpathy's obsidian-wiki workflow（https://x.com/karpathy/status/2039805659525644595）.
  - **Batteries included**: web search, a web-fetch scraper（https://tinyhumans.gitbook.io/openhuman/features/native-tools）, a full coder toolset (filesystem, git, lint, test, grep), and native voice（https://tinyhumans.gitbook.io/openhuman/features/voice） (STT in, ElevenLabs TTS out, mascot lip-sync, live Google Meet agent) are wired in by default. Model routing（https://tinyhumans.gitbook.io/openhuman/features/model-routing） sends each task to the right LLM (reasoning, fast, or vision) under one subscription. No "install a plugin to read files" friction. Optional local AI via Ollama（https://tinyhumans.gitbook.io/openhuman/features/model-routing/local-ai） for on-device workloads.
  - **Smart token compression (TokenJuice)（https://tinyhumans.gitbook.io/openhuman/features/token-compression）**: every tool call, scrape result, email body, and search payload is run through a token compression layer before it touches any LLM Model. HTML is converted to Markdown, long URLs are shortened, and verbose tool output is deduped and summarised via a configurable rule overlay etc... CJK, emoji, and other mu

#### 2. HKUDS/CLI-Anything
- 链接：https://github.com/HKUDS/CLI-Anything
- 归类：AI Agent / 编排框架
- Stars：35867
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/
  - **2026-04-18** 🧩 **All SKILL.md files are now being unified under the top-level `skills/` directory** — every CLI skill can be installed from one canonical source with `npx skills add HKUDS/CLI-Anything --skill <skill-name> -g -y`. We also added root-skill validation CI, synced contribution / PR docs and REPL skill-path hints to the new layout, and refreshed the **CLI-Hub** install-first frontend around the new `npx skills` flow.
  - **2026-04-17** 🌐 **CLI-Hub** received another install UX pass — public registry metadata and skill coverage were tightened, visit counting was corrected, and the web hub was further refined. 🧪 **Shotcut** render output duration was fixed (#92). 📝 **SKILL** contribution paths were corrected for the new docs flow (#224), and the skill generator now safely handles empty intros (#203).
  - **2026-04-16** 🗺️ **QGIS CLI** merged (#207) — a full GIS / map authoring harness landed. 🧬 **UniMol Tools CLI** merged (#219) for molecular modeling workflows. 🌐 **CLI-Hub** also added more public CLIs, including **py4csr**, refreshed its generated meta-skill, corrected SKILL contribution docs, and fixed `apt-get` package extraction in skill generation (#204).
  - **2026-04-16** 📈 **Unreal Insights CLI** expanded — added background capture session control (`capture start/status/snapshot/stop`), engine-root-matched `UnrealInsights.exe` resolution/build flows, and refreshed docs/tests for the new orchestration workflow.
  - **2026-04-15** 🌐 **CLI-Hub** updated to **v0.2.0** — the PyPI package now supports public CLIs from multiple install sources (`pip`, `npm`, `brew`, bundled/system tools), backed by a new `public_registry.json`. The Hub frontend was redesigned with separate **CLI-Anything CLIs** and **Public CLIs** decks, and live end-to-end checks now cover real install, update, and uninstall flows across both pip and npm packages.

#### 3. calcom/cal.diy
- 链接：https://github.com/calcom/cal.diy
- 归类：AI Agent / 编排框架
- Stars：43370
- 主要语言：TypeScript
- Topics：next-auth, nextjs, open-source, postgresql, prisma, t3-stack, tailwindcss, trpc, turborepo, typescript, zod
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Scheduling infrastructure for absolutely everyone.
  - **No enterprise features** — Teams, Organizations, Insights, Workflows, SSO/SAML, and other EE-only features have been removed
  - **No license key required** — Everything works out of the box, no Cal.com account or license needed
  - **100% open source** — The entire codebase is licensed under MIT, no "Open Core" split
  - **Community-maintained** — Contributions are welcome and go directly into this project (see CONTRIBUTING.md)
  - Next.js（https://nextjs.org/）

#### 4. Anil-matcha/Open-Generative-AI
- 链接：https://github.com/Anil-matcha/Open-Generative-AI
- 归类：AI Agent / 编排框架
- Stars：15292
- 主要语言：JavaScript
- Topics：ai-art-generator, ai-image-generation, ai-video-generation, creative-tools, flux-1, generative-ai, image-to-video, javascript, kling-ai, midjourney-alternative, muapi, open-source
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open-source alternative to AI video platforms — Free AI image & video generation studio with 200+ models (Flux, Midjourney, Kling, Sora, Veo). No content filters. Self-hosted, MIT licensed.
  - Try to open the app — macOS will block it
  - Go to **System Settings → Privacy & Security**
  - Scroll down to find _"Open Generative AI was blocked"_
  - Click **Open Anyway** → **Open**
  - Click **More info** on the SmartScreen dialog

#### 5. BigBodyCobain/Shadowbroker
- 链接：https://github.com/BigBodyCobain/Shadowbroker
- 归类：AI Agent / 编排框架
- Stars：7223
- 主要语言：Python
- Topics：air-force-one, airforce1, asdb, cctv, cctv-cameras, cctv-surveillance, earthquake-visualization, elonjet, osint, osint-resources, osint-tool, sattelite
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open-source intelligence for the global theater. Track everything from the corporate/private jets of the wealthy, and spy satellites, to seismic events in one unified interface. Hook an AI agent up to have it parse through data and find previously unseen correlations. The knowledge is available to all but rarely aggregated in the open, until now.
  - **Track Air Force One**, the private jets of billionaires and dictators, and every military tanker, ISR, and fighter broadcasting ADS-B. Air Force One and all of the accompanying Presidential/Vice Presidential planes are highlighted and monitored from the moment they leave the ground.
  - **Connect an AI agent as a co-analyst** through ShadowBroker's HMAC-signed agentic command channel — supports OpenClaw and any other agent that speaks the protocol (Claude, GPT, LangChain, custom). The agent gets full read/write access to all 35+ data layers, pin placement, map control, SAR ground-change, mesh networking, and alert delivery. It sees everything the operator sees and can take actions on the map in real time.
  - **Communicate on the InfoNet testnet** — The first decentralized intelligence mesh built into an OSINT tool. Obfuscated messaging with gate personas, Dead Drop peer-to-peer exchange, and a built-in terminal CLI. No accounts, no signup. Privacy is not guaranteed yet — this is an experimental testnet — but the protocol is live and being hardened.
  - **Right-click anywhere on Earth** for a country dossier (head of state, population, languages), Wikipedia summary, and the latest Sentinel-2 satellite photo at 10m resolution
  - **Click a KiwiSDR node** and tune into live shortwave radio directly in the dashboard. Click a police scanner feed and eavesdrop in one click.

#### 6. tech-leads-club/agent-skills
- 链接：https://github.com/tech-leads-club/agent-skills
- 归类：AI Agent / 编排框架
- Stars：3636
- 主要语言：TypeScript
- Topics：agent, ai, antigravity, claude-code, copilot, cursor, skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The secure, validated skill registry for professional AI coding agents. Extend Antigravity, Claude Code, Cursor, Copilot and more with absolute confidence.
  - ✨ What are Skills?
  - 🛡️ Security & Trust
  - 🤖 Supported Agents
  - 🌟 Featured Skills
  - 🚀 Quick Start

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
