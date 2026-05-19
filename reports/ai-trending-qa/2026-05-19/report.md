# GitHub 今日 AI Trending 测开分析（2026-05-19）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 5 个
- 推理 / 部署: 1 个

### 热门项目速览

#### 1. tinyhumansai/openhuman
- 链接：https://github.com/tinyhumansai/openhuman
- 归类：AI Agent / 编排框架
- Stars：17952
- 主要语言：Rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Your Personal AI super intelligence. Private, Simple and extremely powerful.
  - **Simple, UI-first & Human** A clean desktop experience and short onboarding paths take you from install to a working agent in a few clicks — no config-first setup, no terminal required. The agent has a face（https://tinyhumans.gitbook.io/openhuman/features/mascot）: a desktop mascot that speaks, reacts to its surroundings, joins your Google Meets（https://tinyhumans.gitbook.io/openhuman/features/mascot/meeting-agents） as a real participant, remembers you across weeks, and keeps thinking in the background even when you've stopped typing.
  - **118+ third-party integrations（https://tinyhumans.gitbook.io/openhuman/features/integrations） with auto-fetch（https://tinyhumans.gitbook.io/openhuman/features/obsidian-wiki/auto-fetch）**: plug into Gmail, Notion, GitHub, Slack, Stripe, Calendar, Drive, Linear, Jira and the rest of your stack with **one-click OAuth**. Every connection is exposed to the agent as a typed tool, and every twenty minutes the core walks each active connection and pulls fresh data into the memory tree（https://tinyhumans.gitbook.io/openhuman/features/integrations/auto-fetch）. No prompts, no polling loops you have to write, so the agent already has tomorrow's context this morning.
  - **Memory Tree（https://tinyhumans.gitbook.io/openhuman/features/memory-tree） + Obsidian Wiki（https://tinyhumans.gitbook.io/openhuman/features/obsidian-wiki）**: a local-first knowledge base built from your data and your activity. Everything you connect is canonicalized into ≤3k-token Markdown chunks, scored, and folded into hierarchical summary trees stored in **SQLite on your machine**. The same chunks land as `.md` files in an Obsidian-compatible vault you can open, browse and edit, inspired by Karpathy's obsidian-wiki workflow（https://x.com/karpathy/status/2039805659525644595）.
  - **Batteries included**: web search, a web-fetch scraper（https://tinyhumans.gitbook.io/openhuman/features/native-tools）, a full coder toolset (filesystem, git, lint, test, grep), and native voice（https://tinyhumans.gitbook.io/openhuman/features/voice） (STT in, ElevenLabs TTS out, mascot lip-sync, live Google Meet agent) are wired in by default. Model routing（https://tinyhumans.gitbook.io/openhuman/features/model-routing） sends each task to the right LLM (reasoning, fast, or vision) under one subscription. No "install a plugin to read files" friction. Optional local AI via Ollama（https://tinyhumans.gitbook.io/openhuman/features/model-routing/local-ai） for on-device workloads.
  - **Smart token compression (TokenJuice)（https://tinyhumans.gitbook.io/openhuman/features/token-compression）**: every tool call, scrape result, email body, and search payload is run t

#### 2. Imbad0202/academic-research-skills
- 链接：https://github.com/Imbad0202/academic-research-skills
- 归类：AI Agent / 编排框架
- Stars：12305
- 主要语言：Python
- Topics：academic-pipeline, academic-writing, ai-research, claude, claude-code, literature-review, peer-review, prompt-engineering
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Academic Research Skills for Claude Code: research → write → review → revise → finalize
  - Claude Code（https://claude.ai/install.sh） (latest; plugin packaging requires recent versions)
  - `ANTHROPIC_API_KEY` exported, or set on first `claude` run
  - *Optional:* Pandoc for DOCX, tectonic + Source Han Serif TC for APA 7.0 PDF (Markdown output works without either)

#### 3. HKUDS/CLI-Anything
- 链接：https://github.com/HKUDS/CLI-Anything
- 归类：AI Agent / 编排框架
- Stars：36852
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/
  - **2026-04-18** 🧩 **All SKILL.md files are now being unified under the top-level `skills/` directory** — every CLI skill can be installed from one canonical source with `npx skills add HKUDS/CLI-Anything --skill <skill-name> -g -y`. We also added root-skill validation CI, synced contribution / PR docs and REPL skill-path hints to the new layout, and refreshed the **CLI-Hub** install-first frontend around the new `npx skills` flow.
  - **2026-04-17** 🌐 **CLI-Hub** received another install UX pass — public registry metadata and skill coverage were tightened, visit counting was corrected, and the web hub was further refined. 🧪 **Shotcut** render output duration was fixed (#92). 📝 **SKILL** contribution paths were corrected for the new docs flow (#224), and the skill generator now safely handles empty intros (#203).
  - **2026-04-16** 🗺️ **QGIS CLI** merged (#207) — a full GIS / map authoring harness landed. 🧬 **UniMol Tools CLI** merged (#219) for molecular modeling workflows. 🌐 **CLI-Hub** also added more public CLIs, including **py4csr**, refreshed its generated meta-skill, corrected SKILL contribution docs, and fixed `apt-get` package extraction in skill generation (#204).
  - **2026-04-16** 📈 **Unreal Insights CLI** expanded — added background capture session control (`capture start/status/snapshot/stop`), engine-root-matched `UnrealInsights.exe` resolution/build flows, and refreshed docs/tests for the new orchestration workflow.
  - **2026-04-15** 🌐 **CLI-Hub** updated to **v0.2.0** — the PyPI package now supports public CLIs from multiple install sources (`pip`, `npm`, `brew`, bundled/system tools), backed by a new `public_registry.json`. The Hub frontend was redesigned with separate **CLI-Anything CLIs** and **Public CLIs** decks, and live end-to-end checks now cover real install, update, and uninstall flows across both pip and npm packages.

#### 4. K-Dense-AI/scientific-agent-skills
- 链接：https://github.com/K-Dense-AI/scientific-agent-skills
- 归类：AI Agent / 编排框架
- Stars：24505
- 主要语言：Python
- Topics：agent-skills, ai-scientist, bioinformatics, chemoinformatics, claude, claude-skills, claudecode, clinical-research, computational-biology, data-analysis, drug-discovery, genomics
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A set of ready to use Agent Skills for research, science, engineering, analysis, finance and writing.
  - 🧬 Bioinformatics & Genomics - Sequence analysis, single-cell RNA-seq, gene regulatory networks, variant annotation, phylogenetic analysis
  - 🧪 Cheminformatics & Drug Discovery - Molecular property prediction, virtual screening, ADMET analysis, molecular docking, lead optimization
  - 🔬 Proteomics & Mass Spectrometry - LC-MS/MS processing, peptide identification, spectral matching, protein quantification
  - 🏥 Clinical Research & Precision Medicine - Clinical trials, pharmacogenomics, variant interpretation, drug safety, clinical decision support, treatment planning
  - 🧠 Healthcare AI & Clinical ML - EHR analysis, physiological signal processing, medical imaging, clinical prediction models

#### 5. supertone-inc/supertonic
- 链接：https://github.com/supertone-inc/supertonic
- 归类：推理 / 部署
- Stars：8443
- 主要语言：Swift
- Topics：cpp, csharp, flutter, go, ios, java, lightweight, multilingual, nodejs, on-device, onnx, onnxruntime
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Lightning-Fast, On-Device, Multilingual TTS — running natively via ONNX.
  - ⚡ **Blazingly Fast** — Low-latency, real-time synthesis across desktop, browser, mobile, and edge — fast enough to turn an entire webpage into audio in under a second
  - 🌍 **31-Language Multilingual** — Synthesize directly from text across 31 languages, or pass `lang="na"` to let Supertonic process the text language-agnostically when you don't know the input language — no separate language adapters needed
  - 🪶 **99M-Parameter Open-Weight Model** — A compact, fully open-weight checkpoint — a fraction of the size of 0.7B–2B class open TTS systems — for smaller downloads, faster cold starts, and lower memory footprint
  - 📱 **Edge-Device Ready** — Runs locally on desktop, mobile, browsers, and resource-constrained hardware like Raspberry Pi or e-readers, with zero network dependency, complete privacy, and no GPU required
  - 🔊 **44.1kHz High-Quality Audio** — Outputs studio-grade 44.1kHz 16-bit WAV directly, ready for production playback without any external upsampler

#### 6. ggml-org/llama.cpp
- 链接：https://github.com/ggml-org/llama.cpp
- 归类：AI Agent / 编排框架
- Stars：111141
- 主要语言：C++
- Topics：ggml
- 项目特色（基于 description/README 片段的轻量提炼）：
  - LLM inference in C/C++
  - Changelog for `libllama` API（https://github.com/ggml-org/llama.cpp/issues/9289）
  - Changelog for `llama-server` REST API（https://github.com/ggml-org/llama.cpp/issues/9291）
  - **Hugging Face cache migration: models downloaded with `-hf` are now stored in the standard Hugging Face cache directory, enabling sharing with other HF tools.**
  - **guide : using the new WebUI of llama.cpp（https://github.com/ggml-org/llama.cpp/discussions/16938）**
  - guide : running gpt-oss with llama.cpp（https://github.com/ggml-org/llama.cpp/discussions/15396）

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

#### 推理 / 部署
- 将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。
- 默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。
- 把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。
- 重点测：性能与稳定性——P95/P99 延迟、并发、队列积压、限流降级、OOM/泄漏。
- Ginkgo 侧加入压测前的“健康检查套件”：模型加载、权重一致性、GPU/CPU 资源探针。
- Playwright 端到端测：前端在慢请求/流式输出中不卡死、不丢 token、不重复渲染。

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
