#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate daily Feishu Interactive Cards (schema 2.0).

目标
- 将“GitHub Trending 测开报告 / AI 早报 / 每日 AI 学习笔记”的飞书通知统一改为 Card v2（interactive）。
- 默认只生成 card.json（dry-run），不真实发送。

为什么放在仓库内？
- GitHub Actions 负责生成/提交 blog 与 reports；
- 这份脚本负责把“已生成的内容”做成高可读卡片，便于通过任何渠道（Aime 定时任务/本地/其他 pipeline）发送到飞书群。

使用示例
1) Dry-run 生成卡片 JSON（默认）
   python3 scripts/feishu_daily_cards.py --date 2026-04-23 --out temp/daily_cards_2026-04-23.json

2) 生成 + 发送到群（需要 include_secrets=true 的 bash 环境）
   python3 scripts/feishu_daily_cards.py \
     --date 2026-04-23 \
     --chat-id oc_xxx \
     --send

注意
- 本脚本只负责生成与发送“每日内容卡片”，不触碰 wechat_publisher 目录。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from feishu_cardkit import build_card, button, caption, column, column_set, hr, md


DEFAULT_SITE_URL = "https://15606518796-cyber.github.io/ai-qa-learning-site"


@dataclass
class BlogPost:
    date: str  # YYYY-MM-DD
    file_path: Path
    title: str
    slug: str

    @property
    def url(self) -> str:
        site = os.environ.get("AI_QA_SITE_URL", "").strip() or DEFAULT_SITE_URL
        yyyy, mm, dd = self.date.split("-", 2)
        return f"{site}/blog/{yyyy}/{mm}/{dd}/{self.slug}"


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _parse_front_matter_title(md_text: str) -> str:
    # extremely small front-matter parser: title: "..." or title: ...
    # only look at the first 60 lines.
    head = "\n".join(md_text.splitlines()[:60])
    m = re.search(r"^title:\s*(.+)$", head, flags=re.MULTILINE)
    if not m:
        return ""
    raw = m.group(1).strip()
    # strip quotes
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1]
    return raw.strip()


def _slug_from_filename(date: str, filename: str) -> str:
    # filename: 2026-04-23-day11-agent-architecture.md -> day11-agent-architecture
    base = filename
    if base.endswith(".md"):
        base = base[:-3]
    prefix = f"{date}-"
    if base.startswith(prefix):
        return base[len(prefix) :]
    return base


def find_blog_post(repo_root: Path, *, date: str, kind: str) -> Optional[BlogPost]:
    # kind:
    # - morning: {date}-ai-morning-post.md
    # - trending: {date}-github-trending-ai-qa.md
    # - learning: {date}-day*.md (first match)

    blog_dir = repo_root / "blog"
    if kind == "morning":
        fp = blog_dir / f"{date}-ai-morning-post.md"
        candidates = [fp]
    elif kind == "trending":
        fp = blog_dir / f"{date}-github-trending-ai-qa.md"
        candidates = [fp]
    elif kind == "learning":
        candidates = sorted(blog_dir.glob(f"{date}-day*.md"))
    else:
        return None

    for p in candidates:
        if not p.exists():
            continue
        text = _read_text(p)
        title = _parse_front_matter_title(text) or p.stem
        slug = _slug_from_filename(date, p.name)
        return BlogPost(date=date, file_path=p, title=title, slug=slug)

    return None


def extract_trending_top_repos(blog_text: str, limit: int = 6) -> List[Tuple[str, str]]:
    """Extract (repo_full_name, url) from a github trending blog post.

    We match patterns like:
    #### 1. owner/repo
    - 链接：https://github.com/owner/repo
    """

    lines = blog_text.splitlines()
    out: List[Tuple[str, str]] = []

    heading_re = re.compile(r"^(#{3,5})\\s+\\d+\\.\\s+([^\\s]+/[^\\s]+)\\s*$")
    url_re = re.compile(r"^(#{3,5})\\s+\\d+\\.\\s+([^\\s]+/[^\\s]+)\\s*$")

    i = 0
    while i < len(lines) and len(out) < limit:
        m = heading_re.match(lines[i].strip())
        if not m:
            i += 1
            continue

        repo = m.group(2).strip()
        url = ""

        # Search next ~12 lines for the URL field
        for j in range(i + 1, min(i + 13, len(lines))):
            m2 = url_re.match(lines[j].strip())
            if m2:
                url = m2.group(1).strip()
                break

        if repo and url:
            out.append((repo, url))

        i += 1

    return out



def _extract_section_by_keywords(md_text: str, keywords: List[str]) -> str:
    """Extract a section body by heading keywords (level-2 headings).

    If none of the keywords match, fall back to the first level-2 heading.
    """

    lines = md_text.splitlines()
    start_idx: Optional[int] = None

    # Prefer headings that contain any of the keywords
    if keywords:
        for i, line in enumerate(lines):
            if line.startswith("##"):
                title = line.lstrip("#").strip()
                if any(kw in title for kw in keywords):
                    start_idx = i
                    break

    # Fallback: first level-2 heading
    if start_idx is None:
        for i, line in enumerate(lines):
            if line.startswith("## "):
                start_idx = i
                break

    if start_idx is None:
        return ""

    end_idx = len(lines)
    for j in range(start_idx + 1, len(lines)):
        if lines[j].startswith("## "):
            end_idx = j
            break

    body_lines = lines[start_idx + 1 : end_idx]
    return "\n".join(body_lines).strip()



def _extract_bullets_from_section(md_text: str, keywords: List[str], max_items: int = 4) -> List[str]:
    """Return up to max_items bullet lines ("- xxx") from a section.

    This normalizes numbered lists ("1. xxx") / "- xxx" / "* xxx" into
    markdown bullets, so they can be rendered consistently in Feishu markdown.
    """

    section = _extract_section_by_keywords(md_text, keywords)
    if not section:
        return []

    bullets: List[str] = []
    for raw in section.splitlines():
        s = raw.strip()
        if not s:
            continue

        # Match "1. xxx" / "1) xxx" style
        m = re.match(r"^(\d+[\.)]\s+)(.+)$", s)
        if m:
            content = m.group(2).strip()
        elif s.startswith(('-', '*')):
            content = s.lstrip('-*').strip()
        else:
            continue

        if not content:
            continue

        bullets.append(f"- {content}")
        if len(bullets) >= max_items:
            break

    return bullets



def extract_learning_key_points(md_text: str, max_items: int = 4) -> List[str]:
    """Extract 2-4 key conclusions from a daily learning note.

    优先策略：
    - 找到包含“核心结论 / TL;DR”等关键词的小节
    - 如果没有，则回退到第一节正文的小结 bullets
    """

    # 优先使用 "核心结论" / "TL;DR" 等关键词
    bullets = _extract_bullets_from_section(md_text, ["核心结论", "TL;DR"], max_items=max_items)
    if bullets:
        return bullets

    # 回退到第一节（通常是当日主干内容）
    bullets = _extract_bullets_from_section(md_text, [], max_items=max_items)
    return bullets



def extract_trending_key_takeaways(md_text: str, max_items: int = 4) -> List[str]:
    """Extract 2-4 key QA takeaways from the GitHub Trending report.

    优先从“今天最值得带回团队讨论的 X 个方向”段落中提炼编号列表；
    若未找到，则回退到“对日常 QA 工作的工程化启发”小节。"""

    lines = md_text.splitlines()
    bullets: List[str] = []
    start_idx: Optional[int] = None

    for i, line in enumerate(lines):
        if "最值得带回" in line or "重点观察" in line:
            start_idx = i + 1
            break

    if start_idx is not None:
        for raw in lines[start_idx:]:
            s = raw.strip()
            if not s and bullets:
                break
            m = re.match(r"^(\d+)[\.)]\s+(.+)$", s)
            if not m:
                # 允许使用 "- " 补充上一条的补充说明
                if bullets and s.startswith(('-', '*')):
                    bullets[-1] += " " + s.lstrip('-*').strip()
                elif bullets:
                    break
                continue
            content = m.group(2).strip()
            if not content:
                continue
            bullets.append(f"- {content}")
            if len(bullets) >= max_items:
                break

    if bullets:
        return bullets

    # 回退：从“对日常 QA 工作的工程化启发”小节提炼 bullets
    bullets = _extract_bullets_from_section(md_text, ["工程化启发", "QA 工作"], max_items=max_items)
    return bullets



def extract_trending_action_points(md_text: str, max_items: int = 3) -> List[str]:
    """Extract 2-3 concrete action suggestions from the Trending report.

    主要从“可落地的行动指南”小节中抓取 bullets，用作“建议动作”。"""

    return _extract_bullets_from_section(md_text, ["可落地的行动指南"], max_items=max_items)



def build_daily_card(*, repo_root: Path, date: str) -> Dict[str, Any]:
    morning = find_blog_post(repo_root, date=date, kind="morning")
    trending = find_blog_post(repo_root, date=date, kind="trending")
    learning = find_blog_post(repo_root, date=date, kind="learning")

    missing = [
        name
        for name, v in [("AI 早报", morning), ("GitHub Trending 测开分析", trending), ("每日 AI 学习笔记", learning)]
        if v is None
    ]

    header_title = f"📮 每日 AI 内容摘要（{date}）"

    elements: List[Dict[str, Any]] = []

    if missing:
        elements.append(
            md(
                "⚠️ **本次卡片为部分内容**\n"
                + "以下内容在仓库 blog/ 中未找到对应文件：\n"
                + "\n".join([f"- {x}" for x in missing])
            )
        )
        elements.append(hr())

    # 1) 每日 AI 学习笔记：直接给出 2~4 条核心结论
    if learning:
        learning_text = _read_text(learning.file_path)
        learning_points = extract_learning_key_points(learning_text, max_items=4)

        lines: List[str] = [
            "#### 📚 今日学习结论",
            f"**{learning.title}**",
            "",
        ]
        if learning_points:
            lines.extend(learning_points)
        else:
            lines.append("（暂未从正文中自动提炼出结论，建议点击下方按钮查看全文）")

        elements.append(md("\n".join(lines)))

    # 2) GitHub Trending 测开分析：提炼趋势结论 + QA 启发 + 建议动作
    if trending:
        if elements:
            elements.append(hr())

        trending_text = _read_text(trending.file_path)
        qa_points = extract_trending_key_takeaways(trending_text, max_items=4)
        action_points = extract_trending_action_points(trending_text, max_items=3)

        lines = [
            "#### 🧪 GitHub Trending QA 启发",
            f"**{trending.title}**",
            "",
        ]

        if qa_points:
            lines.extend(qa_points)

        if action_points:
            lines.append("")
            lines.append("**建议动作（节选）：**")
            lines.extend(action_points)

        if not qa_points and not action_points:
            lines.append("（暂未从正文中自动提炼出 QA 启发，建议点击下方按钮查看全文）")

        elements.append(md("\n".join(lines)))

    # 3) AI 早报：简要点名，作为补充信息
    if morning:
        if elements:
            elements.append(hr())
        elements.append(
            md(
                "#### ☀️ 今日 AI 早报\n"
                + f"- {morning.title}"
            )
        )

    # 4) 全文链接与按钮（作为次要信息）
    link_lines: List[str] = []
    btns: List[Dict[str, Any]] = []

    if morning:
        link_lines.append(f"- [AI 早报]({morning.url})")
        btns.append(button(text="打开 AI 早报", url=morning.url, style="default"))

    if learning:
        link_lines.append(f"- [每日 AI 学习笔记]({learning.url})")
        btns.append(button(text="打开学习笔记", url=learning.url, style="primary"))

    if trending:
        link_lines.append(f"- [GitHub Trending 测开分析]({trending.url})")
        btns.append(button(text="打开 Trending 分析", url=trending.url, style="default"))

    if link_lines:
        elements.append(hr())
        elements.append(md("#### 🔗 查看完整内容\n" + "\n".join(link_lines)))
        if btns:
            elements.append(hr())
            elements.extend(btns)

    elements.append(hr())
    elements.append(caption("Aime 自动生成 | 卡片类型：Interactive Card v2（schema 2.0）"))

    return build_card(title=header_title, template="blue", elements=elements, card_name="DailyAiContent")


def _try_read_default_chat_id(repo_root: Path) -> str:
    # 默认复用 HTL 监听器同一群（CICD测试通知群）
    # workspace_root/htl_feishu_listener/state.json
    state = repo_root.parent / "htl_feishu_listener" / "state.json"
    if not state.exists():
        return ""

    try:
        obj = json.loads(state.read_text(encoding="utf-8"))
        v = str(obj.get("chat_id") or "").strip()
        if v.startswith("oc_"):
            return v
        return ""
    except Exception:
        return ""


def send_card_via_im_send(*, workspace_root: Path, chat_id: str, cardkit: Dict[str, Any]) -> None:
    """Send the card to a Feishu group.

    This function relies on inner_skills/feishu-im-send/scripts/im_send.py.
    It will:
    1) create_card -> card_id
    2) send chat_id interactive card_id --id-type=chat_id
    """

    tool = workspace_root / "inner_skills" / "feishu-im-send" / "scripts" / "im_send.py"
    if not tool.exists():
        raise RuntimeError(f"im_send.py not found: {tool}")

    # Write a temp json file for create_card (less escaping pain)
    temp_dir = workspace_root / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = temp_dir / "daily_ai_content_card.json"
    tmp_path.write_text(json.dumps(cardkit, ensure_ascii=False, indent=2), encoding="utf-8")

    import subprocess

    p1 = subprocess.run([sys.executable, str(tool), "create_card", str(tmp_path)], capture_output=True, text=True)
    if p1.returncode != 0:
        raise RuntimeError(f"create_card failed\nSTDOUT:\n{p1.stdout}\nSTDERR:\n{p1.stderr}")

    m = re.search(r'card_id["\'\'" ]*:["\'\'" ]*(\d+)', p1.stdout)
    if not m:
        raise RuntimeError(f"create_card succeeded but card_id not found. raw=\n{p1.stdout}")

    card_id = m.group(1)

    p2 = subprocess.run(
        [sys.executable, str(tool), "send", chat_id, "interactive", card_id, "--id-type=chat_id"],
        capture_output=True,
        text=True,
    )
    if p2.returncode != 0:
        raise RuntimeError(f"send failed\nSTDOUT:\n{p2.stdout}\nSTDERR:\n{p2.stderr}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--out", default="", help="可选：输出 card JSON 文件路径")
    ap.add_argument("--chat-id", default="", help="目标飞书群 chat_id（oc_xxx）。不传则尝试读取 ../htl_feishu_listener/state.json")
    ap.add_argument("--send", action="store_true", help="真实发送到飞书群（默认不发送，仅 dry-run 生成 JSON）")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    workspace_root = repo_root.parent

    cardkit = build_daily_card(repo_root=repo_root, date=args.date)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(cardkit, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] wrote: {out_path}")

    # default: dry-run only
    if not args.send:
        print("[DRY-RUN] card generated. use --send to send to Feishu.")
        return 0

    chat_id = (args.chat_id or "").strip() or _try_read_default_chat_id(repo_root)
    if not chat_id:
        raise RuntimeError("chat_id is required for --send. pass --chat-id oc_xxx or ensure ../htl_feishu_listener/state.json exists")

    send_card_via_im_send(workspace_root=workspace_root, chat_id=chat_id, cardkit=cardkit)
    print(f"[OK] sent to chat_id={chat_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
