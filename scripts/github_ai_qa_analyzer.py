#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""github_ai_qa_analyzer.py

目标：
- 获取 GitHub Trending（日榜/周榜/月榜）热门项目
- 过滤 AI 相关项目（基于 topics/description/README 片段的轻量规则）
- 以“资深测试开发工程师”视角生成可复用的工程化分析报告（Markdown）

输出：
- output/YYYY-MM-DD/repos.json
- output/YYYY-MM-DD/report.md

依赖：仅 Python 标准库（urllib / html.parser / json / argparse 等）
可选：设置环境变量 GITHUB_TOKEN 以提升 GitHub API 速率限制

说明：
- 默认优先使用 GitHub REST API 获取 repo 元信息与 README。
- 当 API 触发 403/429（常见于匿名速率限制或环境限制）时，会自动降级为抓取 GitHub Repo 页面 HTML
  来提取 description/topics/stars/language 等信息，以保证脚本可用性。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple


TRENDING_URL = "https://github.com/trending"
GITHUB_API = "https://api.github.com"

# 过滤 AI 项目时的关键词（可按团队偏好持续调优）
AI_KEYWORDS = {
    "ai",
    "agent",
    "agents",
    "llm",
    "gpt",
    "rag",
    "retrieval",
    "embedding",
    "chatbot",
    "transformer",
    "diffusion",
    "stable-diffusion",
    "machine-learning",
    "deep-learning",
    "pytorch",
    "tensorflow",
    "onnx",
    "inference",
    "prompt",
    "evaluation",
    "benchmark",
    "multimodal",
    "vision",
    "nlp",
}

# 粗粒度架构分类（用于趋势聚合 + 给出不同的测试建议）
ARCH_CATEGORIES: List[Tuple[str, List[str]]] = [
    (
        "AI Agent / 编排框架",
        ["agent", "agents", "workflow", "orchestration", "tool", "function calling"],
    ),
    ("RAG / 知识库", ["rag", "retrieval", "vector", "embedding", "knowledge", "index"]),
    ("评测 / Benchmark", ["evaluation", "eval", "benchmark", "leaderboard", "metrics"]),
    ("推理 / 部署", ["inference", "serving", "onnx", "triton", "vllm", "deployment"]),
    ("训练 / 数据", ["training", "finetune", "fine-tune", "dataset", "data"]),
    ("应用层 / UI", ["ui", "frontend", "web", "app", "copilot", "chat"]),
]


@dataclass
class RepoBrief:
    full_name: str  # owner/repo
    html_url: str


class TrendingParser(HTMLParser):
    """从 GitHub Trending 页面提取 repo 列表（owner/repo）。"""

    def __init__(self) -> None:
        super().__init__()
        self._in_h2 = False
        self.repos: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attrs_dict = dict(attrs)

        if tag == "h2":
            cls = attrs_dict.get("class") or ""
            # Trending 项目标题通常在 h2.h3.lh-condensed
            if "lh-condensed" in cls:
                self._in_h2 = True

        if self._in_h2 and tag == "a":
            href = attrs_dict.get("href") or ""
            # href 形如 /owner/repo
            m = re.fullmatch(r"/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", href)
            if m:
                self.repos.append(m.group(1))

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2":
            self._in_h2 = False


def _http_get(url: str, headers: Dict[str, str], timeout: int = 30) -> bytes:
    req = urllib.request.Request(url=url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _github_headers() -> Dict[str, str]:
    headers = {
        "User-Agent": "github-ai-qa-analyzer",
        "Accept": "application/vnd.github+json, application/vnd.github.mercy-preview+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    return headers


def fetch_trending_repos(since: str, top: int, language: str = "") -> List[RepoBrief]:
    params = {"since": since}
    if language:
        params["language"] = language
    url = f"{TRENDING_URL}?{urllib.parse.urlencode(params)}"

    raw = _http_get(url, headers={"User-Agent": "github-ai-qa-analyzer"})
    html = raw.decode("utf-8", errors="replace")

    parser = TrendingParser()
    parser.feed(html)

    # 去重保持顺序
    seen = set()
    repos: List[str] = []
    for r in parser.repos:
        if r not in seen:
            seen.add(r)
            repos.append(r)

    repos = repos[: max(0, top)]
    return [RepoBrief(full_name=r, html_url=f"https://github.com/{r}") for r in repos]


def _clean_int(s: str) -> Optional[int]:
    s = s.strip().replace(",", "")
    if not s:
        return None
    if not re.fullmatch(r"\d+", s):
        return None
    try:
        return int(s)
    except Exception:
        return None


def fetch_repo_meta_from_html(full_name: str) -> Dict[str, Any]:
    """当 GitHub API 不可用时，从 repo HTML 页面抓取最关键字段。"""

    url = f"https://github.com/{full_name}"
    raw = _http_get(url, headers={"User-Agent": "github-ai-qa-analyzer"})
    html = raw.decode("utf-8", errors="replace")

    # description: 优先 og:description，其次 name=description
    desc = ""
    m = re.search(r"<meta\s+property=\"og:description\"\s+content=\"([^\"]*)\"", html)
    if m:
        desc = m.group(1).strip()
    if not desc:
        m = re.search(r"<meta\s+name=\"description\"\s+content=\"([^\"]*)\"", html)
        if m:
            desc = m.group(1).strip()

    # language
    lang = ""
    m = re.search(r"itemprop=\"programmingLanguage\"[^>]*>\s*([^<]+)<", html)
    if m:
        lang = m.group(1).strip()

    # topics: href="/topics/<topic>"
    topics = []
    for t in re.findall(r"href=\"/topics/([A-Za-z0-9_.-]+)\"", html):
        if t not in topics:
            topics.append(t)

    # stars: GitHub 页面有多种渲染方式，尽量多匹配几种
    stars = None
    patterns = [
        r"id=\"repo-stars-counter-star\"[^>]*title=\"([0-9,]+)\"",
        r"id=\"repo-stars-counter-star\"[^>]*>\s*([0-9,.kK]+)\s*<",
        r"aria-label=\"([0-9,]+)\s+users\s+starred\s+this\s+repository\"",
    ]
    for p in patterns:
        m = re.search(p, html)
        if not m:
            continue
        raw_num = m.group(1).strip()
        # 处理 12.3k
        if re.fullmatch(r"\d+(\.\d+)?[kK]", raw_num):
            try:
                stars = int(float(raw_num[:-1]) * 1000)
                break
            except Exception:
                pass
        v = _clean_int(raw_num)
        if v is not None:
            stars = v
            break

    return {
        "name": full_name.split("/", 1)[-1],
        "full_name": full_name,
        "html_url": url,
        "description": desc,
        "language": lang,
        "topics": topics,
        "stargazers_count": stars,
        "_meta_source": "html",
    }


def fetch_repo_meta(full_name: str) -> Dict[str, Any]:
    url = f"{GITHUB_API}/repos/{full_name}"
    try:
        raw = _http_get(url, headers=_github_headers())
        meta = json.loads(raw.decode("utf-8"))
        meta["_meta_source"] = "api"
        return meta
    except urllib.error.HTTPError as e:
        # 403/429 常见于匿名限流或环境限制，自动降级为 HTML 抓取
        if e.code in (403, 429):
            return fetch_repo_meta_from_html(full_name)
        raise


def fetch_repo_readme_raw(full_name: str, max_chars: int = 6000) -> str:
    """优先用 API 取 raw README；若 API 被限流则返回空字符串（不阻塞）。"""

    url = f"{GITHUB_API}/repos/{full_name}/readme"
    headers = _github_headers()
    headers["Accept"] = "application/vnd.github.raw"
    try:
        raw = _http_get(url, headers=headers)
        text = raw.decode("utf-8", errors="replace")
        return text[:max_chars]
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return ""
        return ""
    except Exception:
        return ""


def _text_blob(meta: Dict[str, Any], readme: str) -> str:
    parts = []
    for k in ["name", "full_name", "description", "language"]:
        v = meta.get(k)
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
    topics = meta.get("topics") or []
    if isinstance(topics, list):
        parts.extend([str(t) for t in topics])
    if readme:
        parts.append(readme)
    return "\n".join(parts).lower()


def is_ai_repo(meta: Dict[str, Any], readme: str) -> bool:
    blob = _text_blob(meta, readme)
    return any(kw in blob for kw in AI_KEYWORDS)


def classify_arch(meta: Dict[str, Any], readme: str) -> str:
    blob = _text_blob(meta, readme)
    for cat, kws in ARCH_CATEGORIES:
        if any(kw.lower() in blob for kw in kws):
            return cat
    return "其他 / 待分类"


def sanitize_markdown_text(text: str) -> str:
    def _replace_image(match: re.Match[str]) -> str:
        alt = (match.group(1) or "").strip()
        return alt or "图片"

    def _replace_link(match: re.Match[str]) -> str:
        label = re.sub(r"\s+", " ", (match.group(1) or "").strip())
        url = (match.group(2) or "").strip()
        if url.startswith(("http://", "https://")):
            return f"{label}（{url}）" if label else url
        return label or url

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _replace_image, text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _replace_link, text)
    text = text.replace("{", r"\{").replace("}", r"\}")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def summarize_repo_feature(meta: Dict[str, Any], readme: str) -> List[str]:
    out: List[str] = []
    desc = sanitize_markdown_text((meta.get("description") or "").strip())
    if desc:
        out.append(desc)

    # 从 README 里抓取类似要点的行（粗规则：以 '-', '*', '1.' 开头）
    bullets = []
    for line in readme.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.match(r"^(-|\*|\d+\.)\s+", s):
            bullets.append(re.sub(r"^(-|\*|\d+\.)\s+", "", s).strip())
        if len(bullets) >= 6:
            break

    for b in bullets:
        b = sanitize_markdown_text(b)
        if len(b) >= 8:
            out.append(b)

    # 去重
    dedup = []
    seen = set()
    for x in out:
        k = x.lower()
        if k not in seen:
            seen.add(k)
            dedup.append(x)
    return dedup[:6]


def qa_insights_for_category(category: str) -> List[str]:
    base = [
        "将“正确性”拆成：接口契约正确 + 业务规则正确 + 模型/提示词行为可控 + 观测性可追溯。",
        "默认把 LLM 视为“不确定的外部依赖”，用 Mock/录制回放/固定种子/评测集来把测试变成确定性。",
        "把可测性当作架构能力：强制结构化输出（JSON Schema）、明确错误码、全链路 trace_id。",
    ]

    if category == "AI Agent / 编排框架":
        return base + [
            "重点测：工具调用（tool/function calling）分支覆盖、状态机/工作流回滚、长链路超时与重试策略。",
            "用 Golang Ginkgo 做后端校验：对每个工具 API 做 contract test + 幂等性测试 + 权限边界测试。",
            "把关键对话流固化成“场景回放测试”：同一输入在固定依赖下输出必须稳定（snapshot / golden）。",
        ]

    if category == "RAG / 知识库":
        return base + [
            "重点测：检索召回（Recall）与排序（Rank）——为每条问题准备‘期望命中文档集合’，做离线评测回归。",
            "把向量库当数据库测：索引构建一致性、增量写入正确性、冷热数据切换、延迟与容量压测。",
            "端到端测试要覆盖：空知识、知识过期、同义词、长文本截断、引用来源（citation）准确性。",
        ]

    if category == "评测 / Benchmark":
        return base + [
            "重点测：评测口径（metric）定义与可重复性；同一模型同一数据集结果应可复现。",
            "对评测 pipeline 做“差分测试”：数据/提示词/模型版本变化时，差异必须可解释、可追踪。",
            "把评测结果发布当作发布系统测：权限、审计、数据完整性、失败重试、幂等性。",
        ]

    if category == "推理 / 部署":
        return base + [
            "重点测：性能与稳定性——P95/P99 延迟、并发、队列积压、限流降级、OOM/泄漏。",
            "Ginkgo 侧加入压测前的“健康检查套件”：模型加载、权重一致性、GPU/CPU 资源探针。",
            "Playwright 端到端测：前端在慢请求/流式输出中不卡死、不丢 token、不重复渲染。",
        ]

    if category == "训练 / 数据":
        return base + [
            "重点测：数据链路——数据漂移监控、标注一致性、训练配置可追溯（config-as-code）。",
            "对训练脚本做“可复现实验”测试：固定随机种子/依赖版本后，关键指标应落在阈值区间。",
            "引入数据质量门禁：空值、重复、分布异常、敏感信息扫描（如适用）。",
        ]

    if category == "应用层 / UI":
        return base + [
            "重点测：用户路径与可用性——长对话、断网重连、输入法、文件上传、复制代码块等高频操作。",
            "用 Playwright 建立‘关键路径回放’：登录→创建会话→提问→流式输出→引用/工具调用结果展示。",
            "把前端埋点当作测试断言的一部分：关键交互必须产生日志/事件，方便线上回溯。",
        ]

    return base + [
        "类别不明时，先做‘接口可测性体检’：输入输出结构、错误处理、日志与追踪、可 Mock 的依赖边界。"
    ]


def actionable_steps() -> List[str]:
    return [
        "在现有自动化仓库中新建 `ai_agent_quality/` 目录，沉淀：评测集、对话回放用例、golden snapshots。",
        "为后端（Golang）增加 Ginkgo 套件：\n  - Contract tests（OpenAPI/JSON Schema）\n  - 工具 API 幂等性 + 权限边界\n  - 关键业务规则的 table-driven tests",
        "为前端/控制台增加 Playwright 套件：\n  - 关键路径回放（含流式输出断言）\n  - 断网/慢网/重试场景\n  - 可访问性（a11y）与错误提示一致性",
        "把 LLM 依赖抽象为 Provider 接口：测试环境默认 Mock（录制回放），必要时才走真实模型。",
        "建立‘变更影响面’机制：prompt/模型/检索策略/工具列表任一变化，都要触发评测回归 + 差分报告。",
    ]


def render_report(date_str: str, repos: List[Dict[str, Any]]) -> str:
    cat_count: Dict[str, int] = {}
    for r in repos:
        cat = r.get("arch_category") or "其他 / 待分类"
        cat_count[cat] = cat_count.get(cat, 0) + 1

    lines: List[str] = []
    lines.append(f"# GitHub 今日 AI Trending 测开分析（{date_str}）")
    lines.append("")

    lines.append("## AI 架构与趋势")
    lines.append("")
    if cat_count:
        lines.append("### 今日结构分布（粗分类）")
        for cat, n in sorted(cat_count.items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- {cat}: {n} 个")
        lines.append("")

    lines.append("### 热门项目速览")
    lines.append("")
    for i, r in enumerate(repos, start=1):
        lines.append(f"#### {i}. {r['full_name']}")
        lines.append(f"- 链接：{r['html_url']}")
        if r.get("arch_category"):
            lines.append(f"- 归类：{r['arch_category']}")
        if r.get("stargazers_count") is not None:
            lines.append(f"- Stars：{r['stargazers_count']}")
        if r.get("language"):
            lines.append(f"- 主要语言：{r['language']}")
        if r.get("topics"):
            lines.append(f"- Topics：{', '.join(r['topics'][:12])}")
        feats = r.get("features") or []
        if feats:
            lines.append("- 项目特色（基于 description/README 片段的轻量提炼）：")
            for f in feats[:6]:
                lines.append(f"  - {f}")
        lines.append("")

    lines.append("## 对日常 QA 工作的工程化启发（如何测试此类架构）")
    lines.append("")
    lines.append("### 1) 面向 AI Agent 产品质量的通用原则")
    lines.append("")
    lines.append("- 把 LLM 当作不可控依赖：测试要尽可能确定性（Mock/回放/固定评测集），线上靠观测性兜底。")
    lines.append("- 优先把输出结构化：JSON Schema / 受控枚举 / error code，让断言从‘主观’变成‘可自动化判定’。")
    lines.append("- 关键路径必须可回放：对话、工具调用、检索命中、模型版本，都要可复现。")
    lines.append("")

    lines.append("### 2) 按架构类型给测试策略（可直接套用）")
    lines.append("")
    for cat, _kws in ARCH_CATEGORIES + [("其他 / 待分类", [])]:
        if cat not in cat_count:
            continue
        lines.append(f"#### {cat}")
        for tip in qa_insights_for_category(cat):
            lines.append(f"- {tip}")
        lines.append("")

    lines.append("### 3) Golang Ginkgo 后端校验：最小可用模板")
    lines.append("")
    lines.append("以下片段用于说明思路（按你们的框架/路由替换即可）：")
    lines.append("")
    lines.append("```go")
    lines.append("package api_test")
    lines.append("")
    lines.append("import (")
    lines.append("  \"net/http\"")
    lines.append("  \"github.com/onsi/ginkgo/v2\"")
    lines.append("  \"github.com/onsi/gomega\"")
    lines.append(")")
    lines.append("")
    lines.append("var _ = ginkgo.Describe(\"Tool API Contract\", func() {")
    lines.append("  ginkgo.It(\"should return stable JSON schema for success\", func() {")
    lines.append("    resp, err := http.Get(\"http://localhost:8080/api/tool/foo?x=1\")")
    lines.append("    gomega.Expect(err).ToNot(gomega.HaveOccurred())")
    lines.append("    gomega.Expect(resp.StatusCode).To(gomega.Equal(http.StatusOK))")
    lines.append("    // TODO: 读取 body 做 JSON Schema 校验 / 字段断言")
    lines.append("  })")
    lines.append("})")
    lines.append("```")
    lines.append("")

    lines.append("### 4) Playwright 端到端自动化：关键路径回放模板")
    lines.append("")
    lines.append("```ts")
    lines.append("import { test, expect } from '@playwright/test';")
    lines.append("")
    lines.append("test('chat streaming should be stable', async ({ page }) => {")
    lines.append("  await page.goto('https://your-console.example.com');")
    lines.append("  // TODO: 登录")
    lines.append("")
    lines.append("  await page.getByRole('textbox', { name: '输入' }).fill('解释一下这个项目的核心能力');")
    lines.append("  await page.getByRole('button', { name: '发送' }).click();")
    lines.append("")
    lines.append("  // 关键：对流式输出做“最终一致性”断言")
    lines.append("  await expect(page.getByTestId('assistant-message').last()).toContainText('核心');")
    lines.append("});")
    lines.append("```")
    lines.append("")

    lines.append("## 可落地的行动指南（如何在现有自动化框架中应用）")
    lines.append("")
    for i, step in enumerate(actionable_steps(), start=1):
        lines.append(f"{i}. {step}")
    lines.append("")

    lines.append("---")
    lines.append("### 附：生成数据说明")
    lines.append("- 数据源：GitHub Trending +（优先）GitHub REST API；API 受限时自动降级为抓取 GitHub Repo HTML 页面")
    lines.append("- 说明：AI 过滤与分类为规则驱动，可按团队需求持续迭代；如需更智能的总结，可在此报告基础上再做人工/LLM 精炼。")

    return "\n".join(lines).rstrip() + "\n"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="GitHub AI Trending QA Analyzer (fetch + filter + report)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ap.add_argument("--since", default="daily", choices=["daily", "weekly", "monthly"], help="Trending 时间范围")
    ap.add_argument("--top", type=int, default=25, help="Trending 抓取 top N（先抓取，再过滤 AI）")
    ap.add_argument("--ai-top", type=int, default=6, help="最终输出的 AI 项目数量")
    ap.add_argument("--language", default="", help="Trending 语言筛选（如: python / go / javascript），留空表示全部")
    ap.add_argument("--date", default="", help="报告日期，格式 YYYY-MM-DD；默认取本机当天")
    ap.add_argument("--out-dir", default="output", help="输出目录")

    args = ap.parse_args()

    date_str = args.date.strip() or _dt.datetime.now().strftime("%Y-%m-%d")
    day_dir = os.path.join(args.out_dir, date_str)
    ensure_dir(day_dir)

    try:
        trending = fetch_trending_repos(since=args.since, top=args.top, language=args.language)
    except Exception as e:
        print(f"❌ 抓取 GitHub Trending 失败：{e}", file=sys.stderr)
        return 2

    # 先补全 meta（成本较低），再对通过 AI 过滤的 repo 拉 README
    metas: List[Tuple[RepoBrief, Dict[str, Any]]] = []
    for rb in trending:
        try:
            meta = fetch_repo_meta(rb.full_name)
            metas.append((rb, meta))
        except urllib.error.HTTPError as e:
            print(f"⚠️ 跳过 {rb.full_name}（repo meta HTTP {e.code}）", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 跳过 {rb.full_name}（repo meta 失败：{e}）", file=sys.stderr)

    # 初步 AI 过滤（只用 meta）
    candidates: List[Tuple[RepoBrief, Dict[str, Any]]] = []
    for rb, meta in metas:
        meta_blob = json.dumps(
            {
                "name": meta.get("name"),
                "full_name": meta.get("full_name"),
                "description": meta.get("description"),
                "language": meta.get("language"),
                "topics": meta.get("topics"),
            },
            ensure_ascii=False,
        ).lower()
        if any(kw in meta_blob for kw in AI_KEYWORDS):
            candidates.append((rb, meta))

    # 如果候选太少，再放宽：直接取 top 里最像 AI 的（用 repo 名/desc 的 ai/agent/llm 等）
    if len(candidates) < max(2, args.ai_top // 2):
        relaxed: List[Tuple[RepoBrief, Dict[str, Any]]] = []
        relaxed_kws = ["ai", "agent", "llm", "rag", "gpt", "ml"]
        for rb, meta in metas:
            blob = f"{meta.get('full_name','')}\n{meta.get('description','')}".lower()
            if any(k in blob for k in relaxed_kws):
                relaxed.append((rb, meta))
        seen = {x[0].full_name for x in candidates}
        for x in relaxed:
            if x[0].full_name not in seen:
                candidates.append(x)
                seen.add(x[0].full_name)

    candidates = candidates[: max(args.ai_top * 3, args.ai_top)]

    ai_repos: List[Dict[str, Any]] = []
    for rb, meta in candidates:
        readme = fetch_repo_readme_raw(rb.full_name)

        if not is_ai_repo(meta, readme):
            continue

        arch_cat = classify_arch(meta, readme)
        feats = summarize_repo_feature(meta, readme)

        ai_repos.append(
            {
                "full_name": rb.full_name,
                "html_url": rb.html_url,
                "description": meta.get("description"),
                "language": meta.get("language"),
                "topics": meta.get("topics") or [],
                "stargazers_count": meta.get("stargazers_count"),
                "forks_count": meta.get("forks_count"),
                "open_issues_count": meta.get("open_issues_count"),
                "arch_category": arch_cat,
                "features": feats,
                "readme_excerpt": readme[:1200],
                "_meta_source": meta.get("_meta_source"),
            }
        )

        if len(ai_repos) >= args.ai_top:
            break

    repos_path = os.path.join(day_dir, "repos.json")
    with open(repos_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "date": date_str,
                "since": args.since,
                "top": args.top,
                "ai_top": args.ai_top,
                "language": args.language,
                "repos": ai_repos,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    report_md = render_report(date_str, ai_repos)
    report_path = os.path.join(day_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print("✅ 生成完成")
    print(f"- {repos_path}")
    print(f"- {report_path}")

    if not ai_repos:
        print("\n⚠️ 本次未筛选出 AI 项目（可能是过滤规则过严或 Trending 结构变化）。")
        print("   建议：调大 --top 或减少过滤关键词限制。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
