# GitHub 今日 AI Trending 测开分析（2026-09-25）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. rohitg00/ai-engineering-from-scratch
- 链接：https://github.com/rohitg00/ai-engineering-from-scratch
- 归类：AI Agent / 编排框架
- Stars：56737
- 主要语言：Python
- Topics：agents, ai, ai-agents, ai-engineering, computer-vision, course, deep-learning, from-scratch, generative-ai, llm, machine-learning, mcp
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Learn it. Build it. Ship it for others.

#### 2. vectorize-io/hindsight
- 链接：https://github.com/vectorize-io/hindsight
- 归类：AI Agent / 编排框架
- Stars：28041
- 主要语言：Python
- Topics：agentic-ai, agents, ai-memory, memory
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Hindsight: Agent Memory That Learns
  - Memory Performance & Accuracy
  - Quick Start — server · clients · platforms · embedded
  - Adding Hindsight to Your Agent — LLM Wrapper · integrations · coding agents · MCP
  - Core Concepts — memory types · retain / recall / reflect · observations · mental models & knowledge pages · banks
  - Use Cases

#### 3. dream-num/univer
- 链接：https://github.com/dream-num/univer
- 归类：AI Agent / 编排框架
- Stars：17913
- 主要语言：TypeScript
- Topics：board, collaboration, data-table, doc, docx, excel, grid, pdf, ppt, pptx, presentation, sdk
- 项目特色（基于 description/README 片段的轻量提炼）：
  - The Office Harness for AI Agents — Spreadsheets, Docs, Slides, Canvas, Relational Tables, and PDF in one runtime.
  - Embed spreadsheet or document editing into a SaaS product, internal tool, BI workflow, or AI application.
  - Run workbook/document processing on the server with the same architecture used in the browser.
  - Compose only the features you need through plugins or start quickly with presets.
  - Extend behavior through custom plugins, commands, services, UI components, and Facade APIs.
  - Agents can generate spreadsheet-based mini-apps, such as decision-making dashboards, interactive reports, and business dashboards.

#### 4. google/ax
- 链接：https://github.com/google/ax
- 归类：AI Agent / 编排框架
- Stars：10652
- 主要语言：Go
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Google's open agentic orchestration runtime
  - repo: https://github.com/golang/go.git
  - name: golang
  - A Kubernetes cluster with **Agent Substrate** installed (see below)
  - Go（https://go.dev/doc/install） and `kubectl`
  - `ko`（https://ko.build/） (`brew install ko`) and a container registry your cluster can pull from

#### 5. NVIDIA/Model-Optimizer
- 链接：https://github.com/NVIDIA/Model-Optimizer
- 归类：AI Agent / 编排框架
- Stars：4135
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A unified library of SOTA model optimization techniques like quantization, distillation, pruning, neural architecture search, speculative decoding, etc. It compresses deep learning models for downstream deployment frameworks like TensorRT-LLM, TensorRT, vLLM, etc. to optimize inference speed.
  - [2026/09/16] **End-to-end W4A4 NVFP4 + QAD tutorial for Qwen3.6-35B-A3B**: NVFP4 W4A4 PTQ plus quantization-aware distillation, reaching up to 1.30x vLLM throughput over BF16 and 3.1x smaller checkpoints while recovering the accuracy W4A4 costs.
  - [2026/09/09] BLOG: Improving NVFP4 Accuracy with Local-Hessian Weight Scales（https://nvidia.github.io/Model-Optimizer/announcements/local-hessian.html）
  - [2026/08/24] BLOG: AutoQuantize: A Fast Automatic Mixed-Precision Assignment（https://nvidia.github.io/Model-Optimizer/announcements/autoquantize.html）
  - [2026/08/17] BLOG: Developing Nemotron 3.5 Lightning NVFP4 with QAD Using NVIDIA Model Optimizer（https://developer.nvidia.com/blog/developing-nemotron-3-5-lightning-nvfp4-with-qad-using-nvidia-model-optimizer/）: Learn how quantization-aware distillation recovers accuracy from aggressive NVFP4 quantization while reducing model size and increasing throughput.
  - [2026/06/26] BLOG: Creating the NVIDIA Nemotron 3 Ultra NVFP4 Checkpoint with NVIDIA Model Optimizer（https://developer.nvidia.com/blog/creating-the-nvidia-nemotron-3-ultra-nvfp4-checkpoint-with-nvidia-model-optimizer/）: How we quantized Nemotron 3 Ultra (550B) to NVFP4 with Model Optimizer — up to 5.9× higher decode-heavy inference throughput than GLM-5.1 754B FP4 while matching BF16 accuracy. NVFP4 Checkpoint（https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4） on Hugging Face.

#### 6. HKUDS/CLI-Anything
- 链接：https://github.com/HKUDS/CLI-Anything
- 归类：AI Agent / 编排框架
- Stars：50382
- 主要语言：Python
- 项目特色（基于 description/README 片段的轻量提炼）：
  - "CLI-Anything: Making ALL Software Agent-Native" -- CLI-Hub: https://clianything.cc/
  - **2026-05-30** 🧭 **Hermes skill** proposed (#320), adding a CLI-Anything orchestration skill with installer scripts and HARNESS fallback guidance. 🗺️ **ArcGIS Pro** was proposed for the public registry (#318) as a Windows/ArcPy CLI for cartography, geoprocessing, feature editing, and live-Pro MCP workflows.
  - **2026-05-27** 🔧 **CLI-Hub** registry date updates now handle `python -m pip` install commands (#312), improving package-date detection for registry automation.
  - **2026-05-23** 📝 **Obsidian Agent CLI** was proposed for the public registry (#307), bringing a PyPI-installed Obsidian automation CLI with persistent agent memory workflows and a pinned skill link.
  - **2026-05-21** 🔒 **Sketch CLI** token-file handling was hardened against path traversal and symlink escapes (#304).
  - **2026-05-20** 📓 **Joplin CLI** was proposed (#300) with notebooks, notes, to-dos, tags, attachments, search/sync, import/export, server/E2EE helpers, full docs, packaged skill docs, and a 134-test validation baseline.

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
