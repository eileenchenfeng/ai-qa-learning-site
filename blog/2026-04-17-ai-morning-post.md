---
title: AI 早报（2026-04-17）：GitHub Trending × AI Builders Digest
authors: [xiaoai]
tags: [AI, github-trending, builders-digest, QA]
date: 2026-04-17
---

今天的早报分两部分：
1) GitHub Trending：从测试开发（QA/测开）视角，提炼 AI 项目形态与可落地的工程化测试启发。
2) AI Builders Digest：追踪建造者动态（仅基于中心化 feed JSON 做整理/摘要；不访问外链，不杜撰）。

> ⚠️ 本文为补发内容。当前脚本会基于补发时可获取到的实时数据源生成内容，不保证完全还原该日期当天的 GitHub Trending / Feed 快照。

{/* truncate */}

## GitHub Trending（测开视角）

### AI 架构与趋势

#### 今日结构分布（粗分类）
- AI Agent / 编排框架: 8 个

#### 热门项目速览

##### 1. Fincept-Corporation/FinceptTerminal
- 链接：https://github.com/Fincept-Corporation/FinceptTerminal
- 归类：AI Agent / 编排框架
- Stars：11681
- 主要语言：Python
- Topics：bloomberg-terminal, contributions-welcome, finance, financial-markets, foss, good-first-issue, help-wanted, investing, investment, investment-research, machine-learning, opensource
- 项目特色（基于 description/README 片段的轻量提炼）：
  - FinceptTerminal is a modern finance application offering advanced market analytics, investment research, and economic data tools, designed for interactive exploration and data-driven decision-making in a user-friendly environment.

##### 2. thunderbird/thunderbolt
- 链接：https://github.com/thunderbird/thunderbolt
- 归类：AI Agent / 编排框架
- Stars：3492
- 主要语言：TypeScript
- Topics：ai, ai-agents, llms, on-device-ai
- 项目特色（基于 description/README 片段的轻量提炼）：
  - AI You Control: Choose your models. Own your data. Eliminate vendor lock-in.
  - 🌐 Available on all major desktop and mobile platforms: web, iOS, Android, Mac, Linux, and Windows.
  - 🧠 Compatible with frontier, local, and on-prem models.
  - 🙋 Enterprise features, support, and FDEs available.
  - We're actively working on our docs, community, and roadmap. For now, the best way to get in touch is to File an issue（https://github.com/thunderbird/thunderbolt/issues）.
  - **Development**: The development guide will help you get started.

##### 3. zilliztech/claude-context
- 链接：https://github.com/zilliztech/claude-context
- 归类：AI Agent / 编排框架
- Stars：6642
- 主要语言：TypeScript
- Topics：agent, agentic-rag, ai-coding, claude-code, code-generation, code-search, cursor, embedding, gemini-cli, mcp, merkle-tree, nodejs
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Code search MCP for Claude Code. Make entire codebase the context for any coding agent.
  - Node.js >= 20.0.0 and < 24.0.0
  - Create or edit the `~/.codex/config.toml` file.
  - Add the following configuration:
  - Save the file and restart Codex CLI to apply the changes.
  - Create or edit the `~/.gemini/settings.json` file.

##### 4. ruvnet/RuView
- 链接：https://github.com/ruvnet/RuView
- 归类：AI Agent / 编排框架
- Stars：48916
- 主要语言：Rust
- Topics：agentic-ai, densepose, esp32, firmware, mcu, mincut, monitoring, pose-estimation, rf, self, self-learning, wifi
- 项目特色（基于 description/README 片段的轻量提炼）：
  - π RuView: WiFi DensePose turns commodity WiFi signals into real-time human pose estimation, vital sign monitoring, and presence detection — all without a single pixel of video.
  - **Presence and occupancy** — detect people through walls, count them, track entries and exits
  - **Vital signs** — breathing rate and heart rate, contactless, while sleeping or sitting
  - **Activity recognition** — walking, sitting, gestures, falls — from temporal CSI patterns
  - **Environment mapping** — RF fingerprinting identifies rooms, detects moved furniture, spots new objects
  - **Sleep quality** — overnight monitoring with sleep stage classification and apnea screening

##### 5. microsoft/ai-agents-for-beginners
- 链接：https://github.com/microsoft/ai-agents-for-beginners
- 归类：AI Agent / 编排框架
- Stars：57756
- 主要语言：Jupyter Notebook
- Topics：agentic-ai, agentic-framework, agentic-rag, ai-agents, ai-agents-framework, autogen, generative-ai, semantic-kernel
- 项目特色（基于 description/README 片段的轻量提炼）：
  - 12 Lessons to Get Started Building AI Agents

##### 6. dayanch96/YTLite
- 链接：https://github.com/dayanch96/YTLite
- 归类：AI Agent / 编排框架
- Stars：4846
- 主要语言：Logos
- Topics：downloader, ios, jailbreak, sponsorblock, tweak, youtube
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A flexible enhancer for YouTube on iOS
  - Screenshots
  - Main Features
  - How to build a YouTube Plus app using GitHub Actions
  - Supported YouTube Version

##### 7. HKUDS/RAG-Anything
- 链接：https://github.com/HKUDS/RAG-Anything
- 归类：AI Agent / 编排框架
- Stars：16924
- 主要语言：Python
- Topics：multi-modal-rag, retrieval-augmented-generation
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "RAG-Anything: All-in-One RAG Framework"
  - [X] [2025.10]🎯📢 🚀 We have released the technical report of RAG-Anything（http://arxiv.org/abs/2510.12323）. Access it now to explore our latest research findings.
  - [X] [2025.08]🎯📢 🔍 RAG-Anything now features **VLM-Enhanced Query** mode! When documents include images, the system seamlessly integrates them into VLM for advanced multimodal analysis, combining visual and textual context for deeper insights.
  - [X] [2025.07]🎯📢 RAG-Anything now features a context configuration module, enabling intelligent integration of relevant contextual information to enhance multimodal content processing.
  - [X] [2025.07]🎯📢 🚀 RAG-Anything now supports multimodal query capabilities, enabling enhanced RAG with seamless processing of text, images, tables, and equations.
  - [X] [2025.07]🎯📢 🎉 RAG-Anything has reached 1k🌟 stars on GitHub! Thank you for your incredible support and valuable contributions to the project.

##### 8. sansan0/TrendRadar
- 链接：https://github.com/sansan0/TrendRadar
- 归类：AI Agent / 编排框架
- Stars：53690
- 主要语言：Python
- Topics：ai, bark, data-analysis, docker, hot-news, llm, mail, mcp, mcp-server, news, ntfy, python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - ⭐AI-driven public opinion & trend monitor with multi-platform aggregation, RSS, and smart alerts.🎯 告别信息过载，你的 AI 舆情监控助手与热点筛选工具！聚合多平台热点 + RSS 订阅，支持关键词精准筛选。AI 智能筛选新闻 + AI 翻译 + AI 分析简报直推手机，也支持接入 MCP 架构，赋能 AI 自然语言对话分析、情感洞察与趋势预测等。支持 Docker ，数据本地/云端自持。集成微信/飞书/钉钉/Telegram/邮件/ntfy/bark/slack 等渠道智能推送。
  - 感谢**为项目点 star** 的观众们，**fork** 你所欲也，**star** 我所欲也，两者得兼😍是对开源精神最好的支持
  - **前往 newsnow 项目（https://github.com/ourongxing/newsnow） 点 star 支持**
  - Docker 部署时，请合理控制推送频率，勿竭泽而渔
  - 小众软件（https://mp.weixin.qq.com/s/fvutkJ_NPUelSW9OGK39aA） - 开源软件推荐平台
  - LinuxDo 社区（https://linux.do/） - 技术爱好者的聚集地

### 对日常 QA 工作的工程化启发（如何测试此类架构）

#### 1) 面向 AI Agent 产品质量的通用原则

- 把 LLM 当作不可控依赖：测试要尽可能确定性（Mock/回放/固定评测集），线上靠观测性兜底。
- 优先把输出结构化：JSON Schema / 受控枚举 / error code，让断言从‘主观’变成‘可自动化判定’。
- 关键路径必须可回放：对话、工具调用、检索命中、模型版本，都要可复现。

#### 2) 按架构类型给测试策略（可直接套用）

##### AI Agent / 编排框架
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：工具调用（tool/function calling）分支覆盖、状态机/工作流回滚、长链路超时与重试策略。
- 用 Golang Ginkgo 做后端校验：对每个工具 API 做 contract test + 幂等性测试 + 权限边界测试。
- 把关键对话流固化成“场景回放测试”：同一输入在固定依赖下输出必须稳定（snapshot / golden）。

#### 3) Golang Ginkgo 后端校验：最小可用模板

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

#### 4) Playwright 端到端自动化：关键路径回放模板

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

### 可落地的行动指南（如何在现有自动化框架中应用）

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
#### 附：生成数据说明
- 数据源：GitHub Trending +（优先）GitHub REST API；API 受限时自动降级为抓取 GitHub Repo HTML 页面
- 说明：AI 过滤与分类为规则驱动，可按团队需求持续迭代；如需更智能的总结，可在此报告基础上再做人工/LLM 精炼。

## AI Builders Digest

AI Builders Digest — 2026-04-17

## X / TWITTER

### Swyx (achieve ambition with intentionality, intensity, integrity & insanity.

affiliations:
- dxtipshq 
- cognition
- temporalio
- aidotengineer
- latentspacepod)
- give us back Sky https://t.co/YIjHaa0jMR
- the Codex x skybysoftware acquisition may have been one of the best openai deals made in the last year. I've been waiting for "real" computer use since romainhuet demoed the ChatGPT App with 4o Vision at AIEWF 2024... and only now it's really, actually rolling out in a usable fashion.
- and dexhorthy is quoting Z/L continuum in AIE Miami!! https://t.co/0KdjCJfZ8a idea catching on altryne https://t.co/O2Q4OImv1k

链接：https://x.com/swyx/status/2046388765820661939 · https://x.com/swyx/status/2046362691606855700 · https://x.com/swyx/status/2046222691418439689

### Josh Woodward (VP, Google GoogleLabs GeminiApp GoogleAIStudio)
- Welcome back Ben! Can’t wait to see what you build! https://t.co/qWkdBgrksp

链接：https://x.com/joshwoodward/status/2046361644029378731

### Peter Yang (Practical AI tutorials and interviews for busy people | Join 140K+ readers at https://t.co/XYKTmGVH14 | Product at Roblox)
- The only thing more fun than coding with agents is designing with agents
- I feel like Codex's gap in frontend design skills can be easily made up if you use an AI design tool. My favorite is tomkrcha's Pencil
- The more innovative the company the less of a "2026 roadmap" it actually has. https://t.co/LR4ObKvt97

链接：https://x.com/petergyang/status/2046434474603446535 · https://x.com/petergyang/status/2046434019307561342 · https://x.com/petergyang/status/2046433025337315651

### Nan Yu (head of product linear)
- When is Venmo gonna finally turn off that feature that lets me see when two of my mutual friends are hooking up?

链接：https://x.com/thenanyu/status/2046317076164350411

### Amjad Masad (ceo replit. civilizationist)
- Fairuz is the star of Kanye’s new album https://t.co/u8oIL4wEG3

链接：https://x.com/amasad/status/2046443294104883693

### Guillermo Rauch (vercel CEO)
- I’m so encouraged by the way our team and industry peers have shown up to protect the internet. We’ve now shipped over 20 product improvements across Dashboard and CLI to help your security posture. Easier to set up MFA, audit your Environment Variables, Activity logs and more https://t.co/5Qi2NEvUhw
- Getting lots of questions about how to learn more about the incident. We're actively maintaining the security bulletin. That's the source. The bulletin includes security best practices to take out of an abundance of caution. To reiterate, we directly contacted all Vercel customers that we believe to be impacted by the IOC shared in the bulletin. One misconception we've seen that I need to call out. Deletion (e.g.: of an env var, project, account…) does not imply Rotation. Rotating keys means *invalidating* the previous value with the vendor/service you're using, and getting a new one. Do that. i.e.: if you only delete the resource on the Vercel side, the associated key can "live on" with the other provider, and be mis-used https://t.co/VJfx1ODUM8

链接：https://x.com/rauchg/status/2046406894269747668 · https://x.com/rauchg/status/2046305710120829374

### Alex Albert (Research AnthropicAI. Opinions are my own!)
- Jack's young money blog had a big impact on me when I was in college and navigating what I wanted to do post-grad. If you are in your teens/20s and trying to figure out how to think about life, this book will offer you some good ideas. https://t.co/8Z1rpUzd36

链接：https://x.com/alexalbert__/status/2046277525207466003

### Aaron Levie (ceo box - your business lives in content. unleash it with AI)
- The jump from working with a chatbot to having an agent that actually helps automate a process requires a real amount of work. Most companies will need to have dedicated people that are responsible for bringing automation to their teams, instead of leaving this up to every individual employee. Partly because the work is more technical than we imagine today, and partly because it’s just hard to do this as a side project. The job spec is to map out new workflows with agents, implement new systems to deploy agents, make sure the agent has all the right (up to date) context to work with, wiring up internal systems to connect to the agents, creating evals for the agents, figuring out where the human is in the loop, managing the system when there are new upgrades, helping with the change management of the existing business process, and so on. These jobs may come from IT or engineering, or live directly in the business function itself. They’ll be called different things depending on the company, and in some sense it’s the future of software engineering that you’ll see a huge growth of in non-tech companies. Most companies will have to be hiring for this now or in the future, and it’s another example of the kind of new jobs that will be created in AI.

链接：https://x.com/levie/status/2046397816755634340

### Ryo Lu (Design Cursor_ai. Early NotionHQ, Stripe, built startups. I make a world where anyone can make software. Aspiring k-pop idol.)
- we love a clean start https://t.co/QgFKXyZZEI

链接：https://x.com/ryolu_/status/2046246973783859559

### Garry Tan (President & CEO ycombinator —Founder garryslist—Creator of GStack & GBrain—designer/engineer who helps founders—SF Dem accelerating the boom loop)
- All of these people need to start startups at Y Combinator https://t.co/RY70TxT5US
- I wrote my friend chrysb a quick note on how to implement GBrain style migrations for people who upgrade to new GBrain versions and want their setups to stay in sync as the core setup changes This is for Alphaclaw but I think could be for any plugin or layer in the OpenClaw/Hermes ecosystem https://t.co/5GrG5RWfCH
- Someone figured out my secret 👀 https://t.co/jWLX6F30GQ

链接：https://x.com/garrytan/status/2046465101759500767 · https://x.com/garrytan/status/2046464315918864385 · https://x.com/garrytan/status/2046459740210036938

### Matt Turck (VC at FirstMarkCap.  Host: MAD Podcast; Organizer: Data Driven NYC, Author: MAD Landscape.)
- One head-scratching idea that gets repeated endlessly: the new TAM for AI is the size of the human labor market, dollar-for-dollar. Many trillions! Just for like any labor automation technology in history, the price of AI services will be the marginal cost + a normal margin.

链接：https://x.com/mattturck/status/2046284478151086178

### Zara Zhang (Builder. Dangerously skips permissions. Harvard’17. GitHub: https://t.co/KCuEajezlL YouTube: https://t.co/8xzbGWtf6w)
- Agents speak HTML as their native language Let agents express themselves in their native language (for similar reasons, agents produce much better looking slides in HTML than in XML) https://t.co/vGAPawGNgu

链接：https://x.com/zarazhangrui/status/2046454622852657264

### Nikunj Kothari (partner fpvventures - investing in seed/A. previous: early hire meter, opendoor, atlassian & others. love shimoleejhaveri + 👦👧)
- This is easily the best podcast episode I’ve heard this year.. Genuine, kind, authentic. Absolutely incredible storytelling. I aspire to have the range of stories that JaredBWeinstein shared on the pod. jacksondahl &amp; DialecticPod always crush but this was special 👏 https://t.co/EGzdrhzwKE
- Every Indian in the US is T-3 hours away from their parents waking up, reading the news and messaging them “why are you not the ceo of Apple huh”

链接：https://x.com/nikunj/status/2046465709438582945 · https://x.com/nikunj/status/2046373243070939360

### Peter Steinberger (Polyagentmorous ClawFather. Came back from retirement to mess with AI and help a lobster take over the world.
OpenClaw🦞 + OpenAI)
- 🗃️ wacli 0.6.0 is out! Big security + reliability sweep for WhatsApp CLI. Hardens SQLite/store path handling, sanitizes search queries, recovers sync/media panics, adds WACLI_STORE_DIR, and improves SIGINT exits. https://t.co/VabuMQgps5 props sdinakar7 for doing the work!
- 🧭 gog 0.13 is out! Gmail forwarding with notes + attachments, autoreplies, full-body search, Markdown uploads to Google Docs, rendered Slides thumbnails, Sheets chart editing, secondary calendars, commenter-only Drive shares, and safer no-send controls. https://t.co/7nQoJaa0Ti
- Kudos to the folks from Tencent for working with us and providing evals to improve OpenClaw's harness performance! We're also working with them to bring fixes/improvements back to the open source repo. Great option for folks not comfortable with the terminal. https://t.co/sbmx7CMLB7

链接：https://x.com/steipete/status/2046375922031321401 · https://x.com/steipete/status/2046356596683411924 · https://x.com/steipete/status/2046259696722465113

### Dan Shipper (ceo every | the only subscription you need to stay at the edge of AI)
- media is cool again! https://t.co/bf7HSf4G8n
- two agents are better than one
- Opus 4.7 does good code reviews

链接：https://x.com/danshipper/status/2046272643133825458 · https://x.com/danshipper/status/2046231280430240141 · https://x.com/danshipper/status/2046224034619125871

### Sam Altman (AI is cool i guess)
- Tim Cook is a legend. I am very thankful for everything he has done and I am very thankful for Apple.
- The internal working name for this was "telepathy", and it feels like it. https://t.co/9LAUTaaYAe

链接：https://x.com/sama/status/2046330825265086712 · https://x.com/sama/status/2046330082726384051

### Claude (Claude is an AI assistant built by anthropicai to be safe, accurate, and secure. Talk to Claude on https://t.co/ZhTwG8d1e5 or download the app.)
- Available now on all paid plans. Update or download the Claude app to try it in Cowork: https://t.co/hwPB3zlk0w
- Everything you build is saved to the new Live Artifacts tab, with version history. Come back tomorrow or next month, from any session, and pick up where you left off.
- In Cowork, Claude can now build live artifacts: dashboards and trackers connected to your apps and files. Open one any time and it refreshes with current data. https://t.co/oru97zRn8L

链接：https://x.com/claudeai/status/2046328622869344429 · https://x.com/claudeai/status/2046328621611065668 · https://x.com/claudeai/status/2046328619249684989

## OFFICIAL BLOGS

### blog — Preparing your security program for AI-accelerated offense
- Earlier this week, we announced Project Glasswing—our urgent attempt to put the strong cybersecurity capabilities of our newest frontier model, Claude Mythos Preview, to use for defensive purposes. In the announcement —and the accompanying technical blog post —we described how AI models are rapidly reducing the required resources, time, and skill required to find and exploit vulnerabilities in software. With an eye on the lightning-fast progress of AI, we also noted that it will not be long before models of similar capability levels are widely available. Within the next 24 months, vast numbers of bugs that sat unnoticed in code, possibly for years, will be found by AI models and chained into working exploits. Indeed, it is already the case that publicly available, sub-Mythos-level models can find serious vulnerabilities that traditional reviews have missed for long periods of time. Thankfully, this works both ways: although attackers can use AI to move faster, so can defenders who adopt AI tools to secure themselves. In this post, we offer security recommendations and practical tips based on what our security teams and researchers have observed and learned from using frontier AI models to secure real codebases and systems. We hope security teams and others will find this advice useful as we enter the age of AI-driven cybersecurity. Many of the pieces of advice below are already part of the existing security consensus; we have prioritized them according to which controls we have seen hold and which we have seen degrade. If your organization reports against SOC 2 and ISO 27001, these will map directly onto controls you are already tracking. We’ll update this guidance as we and our Project Glasswing partners continue our cybersecurity work. What to do now 1. Close your patch gap AI models are very effective at recognizing the signatures of known, already-patched vulnerabilities in unpatched systems. Reversing a patch into a working exploit is exactly the kind of mechanical analysis at which these models excel. This means that the window between a patch being published and an exploit becoming available is shrinking. Patch everything on the CISA Known Exploited Vulnerabilities (KEV) catalog immediately. This catalog contains vulnerabilities that are confirmed to be under active exploitation. Anything on this list which is reachable from a network should be treated as an emergency. Use EPSS to prioritize the rest. Exploit Prediction Scoring System (EPSS) provides a daily-updated probability that a given Common Vulnerability and Exposure (CVE) will be exploited in the next 30 days. Patching the KEV list first and then everything above a chosen EPSS threshold will help you turn thousands of open CVEs into a manageable queue. Reduce time-to-patch on internet-exposed systems. We recommend patching internet-facing applications within 24 hours of an exploit becoming available, and within days for other vulnerabilities. Automate patch deployment and reboots where the risk of an automated update causing an outage is acceptable. Manual approval steps add delay, and delay is now the primary risk. Practical tip: Most cloud and OS vendors already ship patch automation; enabling it is often a simple configuration change. For container images and dependency manifests, several open-source scanners run as a single continuous integration step and annotate CVEs with data from the KEV catalogue and EPSS, so prioritization is built in. 2. Prepare to handle a much higher volume of vulnerability reports Over approximately the next two years, the processes you use to receive, prioritize, and fix vulnerabilities (both in your own code and in the software you buy from vendors) will be under far more pressure than they are today. Your Vulnerability Management process should plan for many more patches, from vendors and upstream. Plan for an order-of-magnitude increase in finding volume. Aspects like intake, triage, and remediation tracking need to keep pace with the increasing numbers of vulnerabilities being exposed. If your security meetings are still built around a spreadsheet and a weekly meeting, it’s unlikely that you’ll keep up. It’s worth considering some amount of automation—with, of course, humans in the loop, to assist with the sheer volume here. Check the security of your open-source dependencies. Most software supply chains are mostly open source. Most open-source projects have no service-level agreement or commitment to maintain a high level of security. OpenSSF Scorecard automatically scores every dependency on signals like branch protection, fuzzing coverage, signed releases, and maintainer activity. It runs in CI and helps to identify unmaintained packages. Apply the same expectations to your vendors. Your third-party risk management process should ask suppliers how they are themselves preparing for accelerated exploit timelines and whether they are scanning their own code. ‍ Practical tip: Look into open source software and third-party services that evaluate the reachability of vulnerable code. Build automated processes that continuously deliver new software updates to your IT and production infrastructure, by doing regression testing on updates to gain confidence that you can deploy them quickly. Above we mentioned automation of these processes. There are a number of important ways that AI can assist: Speeding up triage. Triage is a bottleneck, because it requires expert review and classification. A frontier model can deduplicate findings against an existing backlog, use its knowledge of your assets to estimate exposure, and draft remediation tickets where the affected code paths are pre-identified. Check your dependencies for redundancy. Most large codebases accumulate multiple libraries doing the same job (several HTTP clients; several JSON parsers). This gives attackers more opportunity, all for no functional gain on your part. Pointing an LLM at a lockfile and asking which dependencies overlap (and what migration and consolidation would look like) is a one-hour exercise that often pays off. AI upgrade automation. Frontier models are increasingly capable of generating patches to include alongside vulnerability reports. When the report is clear and thorough, maybe even with a proof-of-concept, the model can directly test the patch to confirm that the exploit path is closed. It can also directly automate the process of accepting the upstream patch, validating that the upgrade doesn’t break tests or internal systems. AI vendoring . Some small dependencies will score poorly on the OpenSSF Scorecard—perhaps because they’re not actively maintained. You shouldn’t continue to rely on these; instead, you should consider having an LLM write its own code to reimplement the functionality you actually use. 3. Find bugs before you ship them Prevention is always better than cure. You should assume that bugs that reach production will eventually be found, so your security testing needs to happen well before. Add static analysis and AI-assisted code review to your continuous integration pipeline, and block merges on high-confidence findings. If false positives make this impractical, you should keep the check, but address the tooling. The OWASP Application Security Verification Standard defines what “passing” a test looks like at three different levels of rigor. Add automated penetration testing to your continuous delivery pipeline. You can run the same scanning for staging that attackers will run against your production systems. Secure the build pipeline. An attacker who can inject code between commit and deployment does not need to find a vulnerability. The SLSA security framework provides a graded path: lower levels establish which commit produced which artifact, and higher levels make the build itself verifiable. Adopt Secure by Design practices. CISA’s pledge commitments (multi-factor authentication by default; no default passwords; transparent vulnerability reporting) are a reasonable minimum bar. Prefer memory-safe languages for new code. A large share of severe vulnerabilities are memory-safety bugs that do not occur in Rust, Go, or managed runtimes. CISA, the NSA, and the NCSC have published useful roadmaps . Existing C/C++ code does not need to be rewritten, but new C/C++ code should require a justification. AI assisted rewrites are increasingly viable, as well. Practical tip: Static application security testing (SAST) tooling that runs as a CI action with OWASP Top 10 and language-specific rule sets is widely available, both open-source and built into code hosting platforms (CodeQL on GitHub being the most common starting point). To assess build provenance, OpenSSF publishes a reusable workflow that produces SLSA Level 3 attestations from GitHub Actions; adopting it is significantly less work than the SLSA spec suggests. As before, there are some clear opportunities for accelerating this work with AI: AI vulnerability scanning. The logic here is straightforward: you should scan your own code and systems with the same kind of model an attacker would use, before they do. This approach just requires an isolated agent, a verification step to filter noise, and a path into your existing triage process. You can do this with an LLM today. If you implement one thing from this section, implement this. Patch generation. When SAST or a scanner produces a finding, a frontier model can usually propose a patch for it. This does not remove the need for review, but it changes the developer’s job from “understand the bug and write a fix” to “verify a proposed fix is correct.” The latter is faster. The same approach applies to memory-safe migration: LLMs can port a self-contained C module to Rust with tests; a reviewer can validate the equivalence rather than writing the whole thing from scratch. 4. Find the vulnerabilities already in your code Patching addresses known vulnerabilities in software you depend on. But your own codebase contains unknown ones. Most long-running production code has been reviewed by humans many times, but has never been examined by a frontier model, and that kind of analysis tends to surface new, previously-overlooked issues . Proactively scanning can identify vulnerabilities that are within the reach of modern LLMs before attackers discover them themselves. Prioritize by exposure. Start with code that parses untrusted input, enforces an authentication or authorization decision, or is reachable from the internet. These are the paths where a finding is most likely to matter. Include legacy code. Code that predates current review practices, or whose original authors have moved on, often has the least recent scrutiny. That’s where you have the most to gain from a fresh pass. Budget for remediation. A well-structured model scan of older code typically produces fewer findings than a SAST rollout, but a higher share of them are real. Plan engineering time to fix the bugs. Practical tip: Pick one internet-facing service with few current owners and scan its input handling and auth logic. Run the agent in isolation and add a verification step so you’re acting on confirmed findings. One service done properly is a reasonable basis for estimating what a broader program will cost. 5. Design for breach Attackers will try to get a foothold somewhere. You need to limit what they can reach from there. Mitigations whose value comes from friction—making an attack tedious —rather than a hard barrier (extra pivot hops, rate limits, non-standard ports, SMS-based MFA) are much less effective against an adversary that can grind through those tedious steps. Our recommendations below favor controls that hold even when the attacker has unlimited patience: hardware-bound credentials, expiring tokens, and network paths that do not exist rather than paths that are merely inconvenient. Adopt zero trust architecture. Authenticate and authorize every request between services as if it came from the internet. CISA&#x27;s Zero Trust Maturity Model and the NCSC&#x27;s zero trust principles both provide staged adoption paths. Tie access to verified hardware rather than credentials. Production systems and sensitive internal tools should only be reachable from managed employee devices with attested hardware identity, paired with phishing-resistant 2FA (FIDO2 or passkeys). Stolen credentials alone should never be sufficient to gain access. Even calls between production services should be rooted in hardware identity. Isolate services by identity. A compromised build server should not be able to query production databases. A compromised laptop should not be able to reach build infrastructure. Enforce this at the receiving end: every workload should carry its own cryptographic identity, and each service should accept connections only from the specific callers of its policy names. Network segmentation can still reduce blast radius and noise, but it is a backstop. Replace long-lived secrets with short-lived tokens. Static API keys, embedded credentials, and shared service-account passwords are among the first things an attacker with model-assisted code analysis will find. Use short-lived, narrowly-scoped tokens issued by an identity provider. Practical tip: Full zero-trust is a multi-year program, but an identity-aware access proxy puts device-verified, MFA-gated access in front of internal services without having to fundamentally change their architecture. Each major cloud provider offers a native option, and several open-source and commercial alternatives exist for on-premises or multi-cloud environments. For secrets, every major cloud has a managed secrets store; moving the single most widely-shared credential into one and rotating it is a useful forcing function for the rest. 6. Reduce and inventory what you expose This section is based on two important principles. First, you cannot defend systems you don’t know about. Second, the smaller the exposed surface, the less there is to attack. Maintain a current inventory of every internet-facing host, service, and API endpoint in your systems. Attackers can run automated reconnaissance; your inventory should be at least as accurate. Include these systems in your pentests and red-teaming. Decommission unused systems. Legacy services with no clear owner are typically also unpatched. Minimize what each service exposes. Default-deny network ingress and limit API surface area to what is actually required. Practical tip: Internet-wide scan indexes are publicly searchable; querying one for your own IP ranges and domains shows you what an attacker’s reconnaissance sees. For cloud assets, native inventory tools (AWS Config, Azure Resource Graph, GCP Asset Inventory) already exist; the work is in querying them. AI can help directly here, too: Pruning stale code and systems. Identifying unused code is tedious—but as noted above, AI models are good at tedious tasks. A model with read access to a codebase and traffic logs can list endpoints that have no callers and have not received traffic; from there, it can explain what removing each one would affect. Autonomous external red-teaming. Point an AI offensive agent at your own perimeter from the outside, with no credentials and no source access. Then, let it do what an attacker would: work out what is reachable, fingerprint it, and attempt to chain what it finds into a foothold. This kind of automated red-teaming can catch things source scanning doesn’t see: forgotten hosts, exposed management interfaces, default credentials, and misconfigured storage. Run it on the same cadence as your inventory refresh. 7. Shorten your incident response time Exploits can appear within hours of a patch. Response processes that take days are too slow. Here are some ideas for how to reduce your incident response time: Put a model at the front of your alert queue. Every inbound alert should get an automated first-pass investigation before a human sees it. This kind of “triage agent” with read-only access to your Security Information and Event Management (SIEM) platform and a well-scoped set of query tools can direct your attention to the alerts that need human judgement most. Put instrument dwell time and coverage before anything else. These are the two metrics that AI automation has the greatest ability to move; both matter most when exploit windows shorten. Automate the bookkeeping around incidents. During an active incident, models should be taking notes, capturing artifacts, pursuing parallel investigation tracks, and drafting the postmortem and root-cause analysis. On the other hand, humans should be making the containment calls, disclosure calls, and customer-comms calls. Human decision speed during an incident should never be rate-limited on aspects that would be better handed to an AI, like evidence collection or write-ups. Let models drive the detection flywheel. Ingesting threat intelligence , generating candidate detections, hunting for matches, and tuning what fires are all now within reach of frontier models, who can run the process end-to-end. Run a tabletop for five simultaneous incidents. The standard exercise assumes one critical CVE with a working exploit hits on a Monday. Given the improved AI capabilities we’re seeing, this might be unwise. To truly stress-test your responses, you should run the version where five incidents hit in the same week. Map detection coverage against MITRE ATT&CK . ATT&CK provides a standard vocabulary of attacker techniques that most detection tools already use. Knowing which techniques you can detect (and which you can’t), is more useful than a general goal to “improve detection.” You should prioritize coverage for lateral movement and credential access. Establish emergency change procedures in advance. A two-week change-approval cycle for production patches is itself a security risk. The same applies to emergency containment actions (like taking a service offline, rotating a credential, or blocking a network path). You should decide in advance who can authorize these and how fast. Practical tip: Pick one noisy rule with a known-high false positive rate. Wire a frontier model into its alert stream with read-only access to the underlying data, and have it produce a structured disposition for every firing. Measure agreement against a human reviewer for two weeks. If the agreement rate is tolerable, expand to the next rule. It’s not worth trying to automate the whole queue at once. Separately, Atomic Red Team is an open-source library of small, safe tests mapped to ATT&CK techniques; running a handful and checking which ones your existing logging actually detected is a one-afternoon exercise that produces a concrete coverage map. Here are some ways AI can assist with response times: First-pass triage at 100% coverage. A well-scoped triage agent can investigate every alert (where humans might look only at those above a given severity threshold), and produce a structured disposition a human can accept, reject, or escalate. The mechanism that makes this work is giving your model a minimal tool set (query, think, report), letting it choose its own investigation strategy, and measuring the output against operational metrics. Incident scribe and parallel investigator. During an active incident, a model can take contemporaneous notes, timestamp artifacts as they are collected, pursue independent investigation tracks the responder has not gotten to yet, and draft the postmortem from the transcript once the incident closes. This is the least glamorous application of frontier models to security work—but it’s probably the highest-impact one. Proactive hunting against your own environment. The same kind of agent that can find vulnerabilities in source code can hunt for misconfigurations and indicators of compromise across your telemetry. You can run it on the same cadence as your external attack-surface scan. Advice for submitting vulnerability reports to others If you are scanning code—your own dependencies, open-source projects, or vendor products—and reporting findings upstream, the quality of those reports determines whether anyone acts on them. Open-source maintainers are already receiving large volumes of low-quality automated reports, and many have started ignoring anything that looks AI-generated. Adding to that volume without adding signal makes the problem worse for everyone, including you. A report should be sent only when a human has verified it and is willing to put their name on it. Concretely: State the bug and its impact in plain language. A maintainer should be able to understand what is wrong and why it matters from the first paragraph, without running anything. Walk through the code path. Show where the input enters, where it is mishandled, and where the consequence occurs. This is the part that distinguishes a real finding from a pattern match. Provide a working reproduction. A proof-of-concept the maintainer can run, or a test case that fails, is more credible than any amount of explanation. Include a proposed patch you would accept if you were the maintainer. A patch demonstrates that the reporter understands the codebase well enough to fix the problem in a way that fits the project’s conventions. Disclose AI involvement upfront. If a model found the bug or drafted the report, say so in the first line. Maintainers will find out anyway; concealing it costs more credibility than disclosing it. Defer to the maintainer&#x27;s judgment. If they decline the report, you should make peace with that. The goodwill from being easy to work with is worth more than winning an argument over one bug. Practical tip: A useful self-check before sending a vulnerability report is to close the editor and explain the bug from memory. If you cannot describe what goes wrong without referring back to the model output, you do not understand it well enough to report it. If you don’t have a security team Most of the above advice assumes that your organization has a dedicated security function. If you are a small organization, a solo developer, or an open-source maintainer, the same risks apply but the actions are simpler: Turn on automatic updates for your operating system, browser, and every application that offers it. This is the single most effective action available and requires no ongoing effort. Prefer managed services over self-hosting. Letting a provider with a security team run the database, authentication, and email shifts the patching burden to them. The cost of a managed service like this is almost always lower than the cost of one incident. Use passkeys or hardware security keys on every account that supports them. SMS codes can be intercepted and passwords get reused; a hardware key cannot be phished. Enable the free security tooling on your code host. GitHub&#x27;s Dependabot, secret scanning, and CodeQL are free for public repositories and catch a meaningful share of what enterprise tools catch. Enabling them takes minutes. If you maintain an open-source project, publish a SECURITY.md stating who to contact and what to expect when they’re contacted. AI-assisted scanning means you will receive more vulnerability reports than before. Some will be valuable; some will be automated noise. A clear intake process helps you tell them apart, and signals to good-faith reporters that their effort will not be wasted. Topic Reference Patch prioritization CISA KEV Catalog , FIRST EPSS , CISA BOD 22-01 Baseline controls ACSC Essential Eight , CISA CPGs , CIS Controls v8 , NCSC 10 Steps Secure development NIST SSDF (SP 800-218) , OWASP ASVS , OWASP SAMM , CISA Secure by Design Memory safety CISA/NSA Memory Safe Roadmaps Supply chain & build integrity SLSA , OpenSSF Scorecards , CISA SBOM resources , NIST SP 800-161 Zero trust CISA Zero Trust Maturity Model , NIST SP 800-207 , NCSC Zero Trust Principles Detection & response MITRE ATT&CK , MITRE D3FEND Program framework NIST Cybersecurity Framework 2.0 , NCSC Cyber Assessment Framework Acknowledgements This article was written by members of Anthropic’s Security Engineering and Research teams, including Donny Greenberg, Jason Clinton, Michael Moore, Abel Ribbink, and Jackie Bow, with contributions from Jannet Park, Gabby Curtis, and Stuart Ritchie.
- 链接：https://claude.com/blog/preparing-your-security-program-for-ai-accelerated-offense

## PODCASTS

### No Priors — The Agentic Economy: How AI Agents Will Transform the Financial System with Circle Co-Founder and CEO Jeremy Allaire
- 链接：https://www.youtube.com/watch?v=eyobeqMdbeI

---
Generated through the Follow Builders skill: https://github.com/zarazhangrui/follow-builders
