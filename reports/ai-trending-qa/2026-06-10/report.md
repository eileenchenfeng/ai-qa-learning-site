# GitHub 今日 AI Trending 测开分析（2026-06-10）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 4 个
- RAG / 知识库: 1 个
- 应用层 / UI: 1 个

### 热门项目速览

#### 1. mvanhorn/last30days-skill
- 链接：https://github.com/mvanhorn/last30days-skill
- 归类：AI Agent / 编排框架
- Stars：37793
- 主要语言：Python
- Topics：ai-prompts, ai-skill, bluesky, claude, claude-code, clawhub, deep-research, hackernews, instagram, openclaw, polymarket, recency
- 项目特色（基于 description/README 片段的轻量提炼）：
  - AI agent skill that researches any topic across Reddit, X, YouTube, HN, Polymarket, and the web - then synthesizes a grounded summary

#### 2. RyanCodrai/turbovec
- 链接：https://github.com/RyanCodrai/turbovec
- 归类：RAG / 知识库
- Stars：10351
- 主要语言：Python
- Topics：ann, avx512, embedding, embeddings, faiss, nearest-neighbor, neon, python, quant, quantization, rag, rust
- 项目特色（基于 description/README 片段的轻量提炼）：
  - A vector index built on TurboQuant, written in Rust with Python bindings
  - **Online ingest.** Add vectors, they're indexed — no train step, no parameter tuning, no rebuilds as the corpus grows.
  - **Faster than FAISS.** Hand-written NEON (ARM) and AVX-512BW (x86) kernels beat FAISS IndexPQFastScan by 12–20% on ARM and match-or-beat it on x86.
  - **Filter at search time.** Pass an id allowlist (or a slot bitmask) to `search()` and the kernel honours it directly. You always get up to `k` results from the allowed set — no over-fetching, no recall hit on selective filters.
  - **Pure local.** No managed service, no data leaving your machine or VPC. Pair with any open-source embedding model for a fully air-gapped RAG stack.
  - LangChain — `pip install turbovec[langchain]` · replaces `langchain_core.vectorstores.InMemoryVectorStore`

#### 3. roboflow/supervision
- 链接：https://github.com/roboflow/supervision
- 归类：AI Agent / 编排框架
- Stars：43132
- 主要语言：Python
- Topics：classification, coco, computer-vision, deep-learning, hacktoberfest, image-processing, instance-segmentation, low-code, machine-learning, metrics, object-detection, oriented-bounding-box
- 项目特色（基于 description/README 片段的轻量提炼）：
  - We write your reusable computer vision tools. 💜
  - inference

#### 4. opencv/opencv
- 链接：https://github.com/opencv/opencv
- 归类：应用层 / UI
- Stars：88721
- 主要语言：C++
- Topics：c-plus-plus, computer-vision, deep-learning, image-processing, opencv
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open Source Computer Vision Library
  - Homepage: <https://opencv.org>
  - Courses: <https://opencv.org/courses>
  - Docs: <https://docs.opencv.org/4.x/>
  - Q&A forum: <https://forum.opencv.org>
  - previous forum (read only): <http://answers.opencv.org>

#### 5. aaif-goose/goose
- 链接：https://github.com/aaif-goose/goose
- 归类：AI Agent / 编排框架
- Stars：48558
- 主要语言：Rust
- Topics：acp, ai, ai-agents, mcp
- 项目特色（基于 description/README 片段的轻量提炼）：
  - an open source, extensible AI agent that goes beyond code suggestions - install, execute, edit, and test with any LLM
  - Quickstart（https://goose-docs.ai/docs/quickstart）
  - Installation（https://goose-docs.ai/docs/getting-started/installation）
  - Tutorials（https://goose-docs.ai/docs/category/tutorials）
  - Documentation（https://goose-docs.ai/docs/category/getting-started）
  - Governance（https://github.com/aaif-goose/goose/blob/main/GOVERNANCE.md）

#### 6. Andyyyy64/whichllm
- 链接：https://github.com/Andyyyy64/whichllm
- 归类：AI Agent / 编排框架
- Stars：4185
- 主要语言：Python
- Topics：ai, apple-silicon, benchmarks, cli, command-line-tool, gguf, gpu, huggingface, inference, llm, local-llm, ollama
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Find the local LLM that actually runs and performs best on your hardware. Ranked by real, recency-aware benchmarks, not parameter count. One command, run it instantly.
  - **Evidence-based ranking, not a size heuristic** — The top pick is
  - **Recency-aware** — Stale leaderboards are demoted along each model's
  - **Evidence-graded and guarded** — Every score is tagged
  - **Architecture-aware estimates** — VRAM = weights + GQA KV cache +
  - **One command, scriptable** — `whichllm` prints the answer; add

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
