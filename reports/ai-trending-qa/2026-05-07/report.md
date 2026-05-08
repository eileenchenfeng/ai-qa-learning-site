# GitHub 今日 AI Trending 测开分析（2026-05-07）

## AI 架构与趋势

### 今日结构分布（粗分类）
- AI Agent / 编排框架: 6 个

### 热门项目速览

#### 1. Hmbown/DeepSeek-TUI
- 链接：https://github.com/Hmbown/DeepSeek-TUI
- 归类：AI Agent / 编排框架
- Stars：15126
- 主要语言：Rust
- Topics：cli, deepseek, llm, rust, terminal, tui
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Coding agent for DeepSeek models that runs in your terminal
  - **Auto mode** — `--model auto` / `/model auto` chooses both the model and thinking level for each turn
  - **Thinking-mode streaming** — see DeepSeek reasoning blocks as the model works
  - **Full tool suite** — file ops, shell execution, git, web search/browse, apply-patch, sub-agents, MCP servers
  - **1M-token context** — context tracking, manual or configured compaction, and prefix-cache telemetry
  - **Three modes** — Plan (read-only explore), Agent (interactive with approval), YOLO (auto-approved)

#### 2. addyosmani/agent-skills
- 链接：https://github.com/addyosmani/agent-skills
- 归类：AI Agent / 编排框架
- Stars：31007
- 主要语言：Shell
- Topics：agent-skills, antigravity, antigravity-ide, claude-code, cursor, skills
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Production-grade engineering skills for AI coding agents.

#### 3. PriorLabs/TabPFN
- 链接：https://github.com/PriorLabs/TabPFN
- 归类：AI Agent / 编排框架
- Stars：6625
- 主要语言：Python
- Topics：data-science, foundation-models, machine-learning, tabpfn, tabular-data
- 项目特色（基于 description/README 片段的轻量提炼）：
  - ⚡ TabPFN: Foundation Model for Tabular Data ⚡
  - **Use batch prediction mode**: Each `predict` call recomputes the training set. Calling `predict` on 100 samples separately is almost 100 times slower and more expensive than a single call. If the test set is very large, split it into chunks of 1000 samples each.
  - **Avoid data preprocessing**: Do not apply data scaling or one-hot encoding when feeding data to the model.
  - **Use a GPU**: TabPFN is slow to execute on a CPU. Ensure a GPU is available for better performance.
  - **Mind the dataset size**: TabPFN works best on datasets with fewer than 100,000 samples and 2000 features. For larger datasets, we recommend looking at the Large datasets guide（https://github.com/PriorLabs/tabpfn-extensions/blob/main/examples/large_datasets/large_datasets_example.py）.
  - **TabPFN Client（https://github.com/priorlabs/tabpfn-client）**

#### 4. docusealco/docuseal
- 链接：https://github.com/docusealco/docuseal
- 归类：AI Agent / 编排框架
- Stars：15007
- 主要语言：Ruby
- Topics：document-signing, documents, e-signature, hotwired-turbo, open-source, pdf, pdf-sign, pdf-signature, ruby-on-rails, self-hosted, tailwindcss, vue
- 项目特色（基于 description/README 片段的轻量提炼）：
  - Open source DocuSign alternative. Create, fill, and sign digital documents ✍️
  - PDF form fields builder (WYSIWYG)
  - 12 field types available (Signature, Date, File, Checkbox etc.)
  - Multiple submitters per document
  - Automated emails via SMTP
  - Files storage on disk or AWS S3, Google Storage, Azure Cloud

#### 5. LearningCircuit/local-deep-research
- 链接：https://github.com/LearningCircuit/local-deep-research
- 归类：AI Agent / 编排框架
- Stars：5755
- 主要语言：Python
- Topics：academia, anthropic, arxiv, brave, deep-research, encryption, home-automation, homeserver, local, local-deep-research, local-llm, mistral
- 项目特色（基于 description/README 片段的轻量提炼）：
  - ~95% on SimpleQA (e.g. Qwen3.6-27B on a 3090). Supports all local and cloud LLMs (llama.cpp, Ollama, Google, ...). 10+ search engines - arXiv, PubMed, your private documents. Everything Local & Encrypted.
  - Does the research for you automatically
  - Searches across web, academic papers, and your own documents
  - Synthesizes everything into a report with proper citations

#### 6. InsForge/InsForge
- 链接：https://github.com/InsForge/InsForge
- 归类：AI Agent / 编排框架
- Stars：8530
- 主要语言：TypeScript
- Topics：ai, ai-agents, coding, deno, embeddings, insforge, nextjs, oauth2, pgvector, postgresql, realtime, vectors
- 项目特色（基于 description/README 片段的轻量提炼）：
  - InsForge is a Postgres-based backend with auth, storage, compute, hosting, and AI gateway. Built for coding agents.
  - **Fetch backend context**: Agents can fetch documentation and available operations for the backend primitives they use.
  - **Configure primitives**: Agents can configure backend primitives directly.
  - **Inspect backend state**: Backend state and logs are exposed through structured schemas.
  - **Authentication**: User management, authentication, and sessions
  - **Database**: Postgres relational database

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
