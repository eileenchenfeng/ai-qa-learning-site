# AI 测开学习站点（AI QA Learning Site）

这是一个由 QA 工程师 **Eileen (陈凤)** 基于 [Docusaurus](https://docusaurus.io/) 搭建的个人 AI 测试开发学习博客，用来系统性沉淀 AI 测开相关的知识与实践经验。

核心目标：
- 帮助测试/QA/测试开发工程师系统性提升 AI 测开能力
- 将日常学习输出为结构化知识库，便于复用与分享
- 结合自动化脚本，探索 “AI + 测试开发” 的落地范式

线上访问地址：**https://eileenchenfeng.github.io/ai-qa-learning-site/**

---

## 内容板块

### 1. 每日学习笔记（Day 1 ~ 21 持续扩展中）

路径：`blog/2026-xx-xx-dayX-*.md`

面向想要系统入门 AI 测开的同学，按天拆解学习路线，从 0 到 1 构建完整知识图谱，覆盖：
- LLM 基础与原理
- Prompt Engineering（提示工程与模式）
- RAG（架构设计、评估方法、自动化 pipeline）
- Agent（架构设计、Function Calling、MCP、Skill 体系、多 Agent 协作、故障容错、性能基线、工具调用测试）

节奏与频率：
- 以「每日学习任务 + 产出」为单位
- 每篇笔记可独立阅读，也可以按 Day 顺序系统学习

### 2. AI 每日动态（AI Builders Digest / ai-morning-post）

路径：`blog/YYYY-MM-DD-ai-morning-post.md`

面向 AI 一线从业者的每日资讯摘要，聚焦：
- 当日值得关注的模型/框架/工具更新
- 业界在「AI + 测试/工程效率」方向的实践案例
- 适合 QA / 测开视角关注的论文、博客、开源项目

节奏与频率：
- 以「工作日更新」为主，视实际精力与信息密度调整

### 3. GitHub AI 趋势分析（github-trending-ai-qa）

路径：`blog/YYYY-MM-DD-github-trending-ai-qa.md`

从测试开发视角解读每日 GitHub Trending 中与 AI 相关的项目，重点关注：
- 与测试、评估、Agent、RAG 等方向相关的项目
- 适合作为 QA 工程师「上手实践」的代码仓库
- 可复用到实际工作中的工具链与最佳实践

节奏与频率：
- 与 GitHub Trending 同步的「每日观察」，以摘要 + 重点项目评论为主

---

## 文档与学习计划

路径：`docs/`

- `docs/learning-plan.md`：4 周 AI 测开系统学习总览
- `docs/week1-llm-prompt/`：Week 1 - LLM 基础与 Prompt Engineering
- `docs/week2-rag/`：Week 2 - RAG 架构与评估
- `docs/week3-agent/`：Week 3 - Agent 架构、工具调用与测试
- `docs/week4-qa-adv/`：Week 4 - 高级 QA 主题与实战

适合用于：
- 个人系统学习路线规划
- 团队内部 AI 测开培训大纲

---

## 本地开发与构建

项目基于 Node.js + Yarn，使用 Docusaurus 作为静态站点框架。

### 环境准备

- 安装 Node.js（推荐 18+ LTS）
- 安装 Yarn 包管理器

### 安装依赖

```bash
yarn
```

### 启动本地开发服务器

```bash
yarn start
```

说明：
- 启动后会自动打开浏览器，访问本地预览地址
- 修改 Markdown 或配置文件后，页面会自动热更新

### 构建静态站点

```bash
yarn build
```

说明：
- 构建结果输出到 `build/` 目录
- 可部署到任意静态站点托管平台

### 部署到 GitHub Pages（可选）

项目支持使用 Docusaurus 内置脚本部署到 GitHub Pages：

```bash
# 使用 SSH
yarn deploy USE_SSH=true

# 使用 HTTPS，指定 GitHub 用户名
GIT_USER=<Your GitHub username> yarn deploy
```

> 说明：根据你本地环境的 GitHub 认证方式选择其一即可。

---

## 自动化与内容更新

本仓库结合定时任务与脚本，尽量减少手工维护成本：

- 每日学习笔记（Day 系列）由自动化任务生成 Markdown 并 push 到仓库
- AI 每日动态（ai-morning-post）与 GitHub 趋势分析会通过脚本半自动化生成
- 内容一旦合入 main 分支，会由 GitHub Pages 自动触发构建与发布

因此：
- **正常使用无需手动创建每日笔记文件**
- 若需要修订历史内容，可直接编辑对应 Markdown 文件后重新 push

---

## 目录结构（简要）

```text
ai-qa-learning-site/
├── blog/                 # 博客文章：每日学习笔记 / AI 动态 / GitHub 趋势分析等
├── docs/                 # 文档与学习计划（Week1~Week4 系统课程）
├── src/                  # Docusaurus 自定义页面与前端代码
├── static/               # 静态资源（图片、favicon 等）
├── wechat_publisher/     # 微信公众号发布相关脚本与输出
├── docusaurus.config.js  # 站点配置
├── sidebars.js           # 文档侧边栏配置
├── package.json          # 项目依赖与脚本
└── README.md             # 项目说明（当前文档）
```

---

## 适合人群

- 希望系统补齐 AI 测开能力的 QA / 测试开发 / SDET
- 正在做 AI 相关项目，需要一套可执行的「LLM + RAG + Agent」学习路径
- 想要将个人学习过程产品化、自动化的开发者

如果你在使用过程中有任何建议或实践案例，也欢迎在 GitHub 仓库提交 Issue 或 PR，一起丰富这套 AI 测开学习体系。
