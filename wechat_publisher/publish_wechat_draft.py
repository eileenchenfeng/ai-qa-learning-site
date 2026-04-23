#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""WeChat Official Account Auto Publisher (Route B)

目标：把 Markdown 摘要转换为适合微信公众号的内联样式 HTML，并完成：
- 动态封面生成（本地 PIL）+ 上传获取 thumb_media_id
- 创建草稿（draft/add）
- 发送预览（message/mass/preview）
- 正式发表（freepublish/submit，可选等待发布结果）

安全约束：
- 不从 MEMORY.md 读取 AppID/AppSecret
- 不在任何可持久化文件（例如 state.json / README / MEMORY.md）里硬编码微信号等敏感信息
  - AppID/AppSecret：建议放在 .env 或环境变量
  - 预览微信号 touser：仅通过命令参数或环境变量传入，不写入 state.json

使用：
  python3 wechat_publisher/publish_wechat_draft.py --help

依赖：见 wechat_publisher/requirements.txt
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import typer
from bs4 import BeautifulSoup
from markdown import markdown as md_to_html
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# ----------------------------
# Constants / Defaults
# ----------------------------

DEFAULT_OUTPUT_DIR = Path("wechat_publisher/output")
DEFAULT_STATE_PATH = Path("wechat_publisher/state.json")

# 微信推荐封面比例常见为 2.35:1（例如 900x383）。
DEFAULT_COVER_SIZE = (900, 383)

# Shared styles for URL boxes (replacing clickable <a> buttons)
URL_LABEL_STYLE = "margin-top: 12px; margin-bottom: 4px; font-size: 13px; color: #64748b; font-weight: 700;"
URL_BOX_STYLE = (
    "background: #f8fafc;"
    "border: 1px solid #e2e8f0;"
    "border-radius: 8px;"
    "padding: 10px 14px;"
    "font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;"
    "font-size: 12px;"
    "color: #1e293b;"
    "word-break: break-all;"
    "line-height: 1.5;"
)


# ----------------------------
# Utilities
# ----------------------------


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_json_dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(read_text(path))
    except Exception:
        return {}


def sha1_short(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def truncate_utf8_bytes(s: str, max_bytes: int) -> str:
    """Truncate a string to fit into max UTF-8 bytes."""
    b = s.encode("utf-8")
    if len(b) <= max_bytes:
        return s

    cut = b[:max_bytes]
    while cut:
        try:
            decoded = cut.decode("utf-8")
            return decoded.rstrip() + "…"
        except UnicodeDecodeError:
            cut = cut[:-1]
    return "…"


def truncate_chars(s: str, max_chars: int) -> str:
    """Truncate a string to fit into max characters."""
    if len(s) <= max_chars:
        return s
    return s[:max_chars].rstrip() + "…"


def strip_markdown_to_plain(md_text: str) -> str:
    """Very lightweight markdown -> plain text, used for digest."""
    text = md_text
    # Strip some common markdown
    text = re.sub(r"`{1,3}.*?`{1,3}", " ", text, flags=re.S)
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", text)
    text = re.sub(r"[*_~]{1,}", "", text)  # remove formatting
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for it in items:
        k = (it or "").strip()
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


def truncate_chars_with_dots(s: str, max_chars: int) -> str:
    """把字符串截断到 max_chars 字符以内，并强制以 "..." 结尾。

    说明：这里用三个点 "..."（而不是省略号 "…"），以匹配公众号摘要里更常见的展示效果。
    """

    s = (s or "").strip()
    if max_chars <= 0:
        return ""
    if max_chars <= 3:
        return "." * max_chars

    # 清理已有的结尾省略号
    s = s.rstrip("…")
    if s.endswith("..."):
        s = s[:-3].rstrip()

    if len(s) <= max_chars - 3:
        return s.rstrip("，,。．.；;、 ") + "..."

    base = s[: max_chars - 3].rstrip()
    base = base.rstrip("，,。．.；;、 ")
    return base + "..."


def _is_digest_meta_line(line: str) -> bool:
    """判定某一行是否更像“元信息/脚注”，不适合作为摘要来源。"""

    s = (line or "").strip()
    if not s:
        return True

    # 标题行不作为正文
    if s.startswith("#"):
        return True

    # 过滤常见 meta：关键词/链接/URL
    if re.search(r"(英文关键词|关键词)\s*[:：]", s):
        return True
    if re.search(r"(原文链接|视频链接|链接)\s*[:：]", s) and ("http://" in s or "https://" in s):
        return True
    if s.startswith("http://") or s.startswith("https://"):
        return True

    return False


def _extract_first_paragraph_under_each_h3(md_text: str) -> List[str]:
    """遍历 Markdown，提取每个 ### 标题下的“第一段正文”。

    注意：这里的“第一段正文”指的是：
    - 跳过空行/元信息行（关键词、链接等）
    - 从第一个有效正文行开始
    - 直到遇到空行（段落结束）为止
    并且：同一个 ### 小节只取第一段，后续段落/列表不再继续抓。
    """

    paragraphs: List[str] = []

    in_h3 = False
    collecting = False
    got_first_paragraph = False
    buf: List[str] = []

    def flush_buf() -> None:
        nonlocal buf, collecting, got_first_paragraph
        text = " ".join([b.strip() for b in buf if b.strip()]).strip()
        if text:
            paragraphs.append(text)
        buf = []
        collecting = False
        got_first_paragraph = True

    for raw in (md_text or "").splitlines():
        line = (raw or "").rstrip()
        stripped = line.strip()

        # H3：开启一个新小节
        if re.match(r"^\s*###\s+(.+?)\s*$", stripped):
            if in_h3 and collecting and not got_first_paragraph:
                flush_buf()
            in_h3 = True
            collecting = False
            got_first_paragraph = False
            buf = []
            continue

        if not in_h3:
            continue

        # 遇到更高层级标题（##），当前 h3 小节结束
        if re.match(r"^\s*##\s+", stripped):
            if collecting and not got_first_paragraph:
                flush_buf()
            in_h3 = False
            continue

        # 同一个 h3 已经拿到第一段了：忽略后续内容，直到下一个标题
        if got_first_paragraph:
            continue

        # 尚未开始收集：找到第一行有效正文
        if not collecting:
            if not stripped:
                continue
            if _is_digest_meta_line(stripped):
                continue
            collecting = True

        # 正在收集第一段，空行意味着段落结束
        if collecting and not stripped:
            flush_buf()
            continue

        if collecting:
            buf.append(stripped)

    # EOF flush
    if in_h3 and collecting and not got_first_paragraph:
        flush_buf()

    return paragraphs


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def _is_meaningful_cn_phrase(text: str) -> bool:
    """摘要短句过滤：避免只有“了/的”等虚词也被当作有效要点。"""

    s = (text or "").strip()
    if not s:
        return False

    cn_chars = re.findall(r"[\u4e00-\u9fff]", s)
    if len(cn_chars) < 2:
        return False

    stop = set("的了呢吧呀啊着在让与和及并从把要会能也还对将被给跟等们")
    # 若中文字符几乎全是停用虚词，则判为无效
    if all(ch in stop for ch in cn_chars):
        return False

    return True


def _is_ascii_alnum(ch: str) -> bool:
    return bool(re.match(r"[A-Za-z0-9]", (ch or "")[:1]))


def _strip_spoken_prefix(text: str) -> str:
    """去掉常见的“口语化引述前缀”，让摘要更像“内容要点”。

    例：
    - "他强调：企业要真正跑起来 agent..." -> "企业要真正跑起来 agent..."
    - "连续分享了 OpenClaw 与周边工具更新..." -> "OpenClaw 与周边工具更新..."
    """

    s = (text or "").strip()
    if not s:
        return ""

    # 先去掉引号/括号等可能包裹在句首的符号
    s = s.lstrip("\"'“”‘’（()【[]-—•*·/ ")

    # 常见“口语化引述”动词/短语
    spoken_prefixes = [
        "他强调",
        "她强调",
        "他提到",
        "她提到",
        "他提及",
        "她提及",
        "他表示",
        "她表示",
        "他指出",
        "她指出",
        "他认为",
        "她认为",
        "他解释",
        "她解释",
        "他建议",
        "她建议",
        "他提醒",
        "她提醒",
        "他总结",
        "她总结",
        "他介绍",
        "她介绍",
        "他分享",
        "她分享",
        "他转发",
        "她转发",
        "他点评",
        "她点评",
        "他发布",
        "她发布",
        "他发布了",
        "她发布了",
        "他转发了",
        "她转发了",
        "他点评了",
        "她点评了",
        "他转发/点评了",
        "她转发/点评了",
        "他给了",
        "她给了",
        "分享了",
        "连续分享了",
        "并分享了",
        "继续分享了",
        "进一步分享了",
        "发布了",
        "转发了",
        "点评了",
        "表示",
        "指出",
        "强调",
        "提到",
        "提及",
        "认为",
        "总结",
        "结论",
        "要点",
        "一句话点题",
        "The Takeaway",
        "Takeaway",
        "今日摘要",
    ]

    # 循环剥离，避免出现“他强调：他指出：...”这种套娃
    for _ in range(3):
        before = s

        # 形如："某某（人名/他/她/嘉宾）强调：..."
        # 更泛化的“口语引述句首”：
        # - 可带人名/身份（如“Box CEO Aaron Levie”/“嘉宾”/“他”/“她”）
        # - 可带副词（如“还”“也”“进一步”）
        # - 可带冒号/逗号
        s = re.sub(
            r"^(?:[\u4e00-\u9fffA-Za-z0-9·•\-\s]{1,30})?"
            r"(?:还|也|再次|继续|进一步|特别)?"
            r"(?:强调|提到|提及|表示|指出|认为|解释|建议|提醒|总结|介绍|分享|发布|转发|点评)"
            r"(?:了)?\s*[：:，,]\s*",
            "",
            s,
        ).strip()

        # 形如："连续分享了 ..."（不一定带冒号）
        for p in spoken_prefixes:
            s = re.sub(rf"^{re.escape(p)}\s*[：:，,]?\s*", "", s).strip()

        if s == before:
            break

    return s.strip()


def _extract_core_phrase_from_paragraph(paragraph: str, *, slice_len: int = 12) -> str:
    """从一段正文中提取“内容核心点短句”。

    规则（对齐需求）：
    1) 去掉口语化前缀（如“他强调：”“他提到”“连续分享了”等）
    2) 截取前半句：遇到第一个中文逗号、句号，取其前面
    3) 若没有上述断句符，截取前 10~15 个字符（尽量不腰斩英文单词）
    """

    text = strip_markdown_to_plain(paragraph or "")

    # 去 URL / 压缩空白
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 去 bullet / 编号前缀
    text = re.sub(r"^[\-*•\s]+", "", text).strip()
    text = re.sub(r"^\d+[\.)]\s*", "", text).strip()

    # 去掉口语化前缀
    text = _strip_spoken_prefix(text)

    if not text:
        return ""

    # 清理“引子：- 列表项”这类结构
    # 例："两个很实用的视角： - 推荐 ..." -> "两个很实用的视角"
    if "：" in text:
        left, right = text.split("：", 1)
        if left and re.match(r"^\s*[-—•*]\s*", right):
            text = left.strip()

    # 截取“前半句”：第一个中文逗号/句号优先；若太靠后则回退到 10~15 字截断
    core = ""
    punct_candidates = []
    for p in ["，", "。"]:
        idx = text.find(p)
        if idx > 0:
            punct_candidates.append(idx)
    punct_idx = min(punct_candidates) if punct_candidates else -1
    if punct_idx > 0 and punct_idx <= 25:
        core = text[:punct_idx].strip()

    if not core:
        # 没有可用断句符：截取一定长度，但避免在英文单词/数字中间切断
        limit = max(10, min(slice_len, 15))
        if len(text) <= limit:
            core = text
        else:
            core = text[:limit]
            if _is_ascii_alnum(core[-1]) and _is_ascii_alnum(text[limit]):
                last_space = core.rfind(" ")
                if last_space > limit // 2:
                    core = text[:last_space]
                else:
                    for i in range(limit, min(len(text), limit + 10)):
                        if not _is_ascii_alnum(text[i]):
                            core = text[:i]
                            break

    # 进一步清理：遇到“从…降到/从…提升到”这类度量句，优先保留“动作 + 对象”
    # 例："通过并行化把 CI 从 8 分钟降到 2 分钟" -> "通过并行化把 CI"
    if "从" in core:
        cut = core.find("从")
        if cut >= 6 and re.search(r"从\s*[\d一二三四五六七八九十]", text):
            maybe = core[:cut].rstrip()
            maybe = maybe.rstrip(" ，,。．.；;、:：")
            if len(maybe) >= 6:
                core = maybe

    # 去掉残留的括号/列表标记
    core = re.sub(r"\s*[-—•*]\s*", " ", core).strip()
    core = core.lstrip("/／")
    core = core.strip("（）()[]【】")
    if "（" in core:
        core = core.split("（", 1)[0].rstrip()
    if "(" in core:
        core = core.split("(", 1)[0].rstrip()

    # 避免截断时留下半截引号内容
    for q in ["“", "\"", "'", "‘"]:
        if q in core:
            left = core.split(q, 1)[0].rstrip()
            if len(left) >= 6:
                core = left
                break
    core = core.strip("\"'“”‘’ ")

    # 清理尾部“挂尾巴”的连接词/语气词（不要过度删除，避免破坏短语）
    core = core.rstrip("的了呢吧呀啊着在让与和及并")
    core = core.strip(" ，,。．.；;、:：")

    # 最终防御：短句必须是“有意义的中文要点”
    if not _is_meaningful_cn_phrase(core):
        return ""

    return core


def _join_phrases_with_limit(phrases: List[str], *, max_chars: int) -> str:
    """用“、”拼接短句，并保证总长度不超过 max_chars。"""

    out: List[str] = []
    current = ""

    for p in phrases:
        p = (p or "").strip(" 、，,。．.；;:：")
        if not p:
            continue

        candidate = p if not current else f"{current}、{p}"
        if len(candidate) <= max_chars:
            current = candidate
            out.append(p)
            continue

        # 放不下就直接停止（避免最后截断破坏“要点感”）
        break

    return (current or "").strip(" 、")


def _extract_text_lines_under_each_h3(md_text: str) -> List[List[str]]:
    """提取每个 ### 标题下的正文行（含 bullet），用于摘要候选。"""

    sections: List[List[str]] = []
    current: Optional[List[str]] = None

    for raw in (md_text or "").splitlines():
        stripped = (raw or "").strip()

        if re.match(r"^\s*###\s+", stripped):
            if current is not None:
                sections.append(current)
            current = []
            continue

        if current is None:
            continue

        # 遇到更高层级标题：结束当前小节
        if re.match(r"^\s*##\s+", stripped):
            sections.append(current)
            current = None
            continue

        if not stripped:
            continue

        # 去掉引用符号
        stripped = re.sub(r"^>+\s*", "", stripped).strip()

        if _is_digest_meta_line(stripped):
            continue

        current.append(stripped)

    if current is not None:
        sections.append(current)

    return sections


def _score_digest_candidate(raw_line: str, core: str) -> int:
    """给候选短句打分，尽量挑出更“像要点”的那句。"""

    line = (raw_line or "").strip()
    c = (core or "").strip()

    score = 0

    # 太像“引子”的句子一般以冒号结尾（例如“连续分享了...更新：”）
    if line.endswith(("：", ":")):
        score -= 3

    # 明确的“总结句”优先（通常比长段落更适合作为摘要要点）
    if re.search(r"(一句话点题|The Takeaway|要点：|要点:)", line, flags=re.I):
        score += 6

    if "数字分身" in line:
        score += 3

    if any(k in line for k in ["DESIGN.md", "研发规范", "工具链", "设计文档"]):
        score += 2

    if re.search(r"OpenClaw|Hermes|GBrain|Minions|Claude", line, flags=re.I):
        score += 1

    # 包含关键工程点：CI/并行/架构/Agent
    if "CI" in line or "CI" in c:
        score += 4
    if re.search(r"\bagent\b", line, flags=re.I) or re.search(r"\bagent\b", c, flags=re.I):
        score += 3
    if re.search(r"并行|并行化|pipeline|工作流", line, flags=re.I):
        score += 2
    if re.search(r"架构|架构更新|系统|工程|落地", line):
        score += 2

    # 有数字通常更具体
    if re.search(r"\d", line):
        score += 1

    # 过短不利于表达要点
    if len(c) < 6:
        score -= 1

    return score


def guess_digest_from_markdown(md_text: str, max_chars: int = 90) -> str:
    """中文摘要启发式：

    目标：从每个 ### 小节的正文中，抓出“中文内容要点”，拼成公众号摘要。

    - 不再提取 ### 标题作为摘要（避免标题是纯英文人名导致摘要“全是英文名”）
    - 提取每个 ### 标题下的正文要点（不取标题本身）
    - 去掉口语化前缀后，截取前半句（中文逗号/句号）或前 10~15 字
    - 用“、”拼接，总长限制 max_chars
    """

    try:
        phrases: List[str] = []

        # 1) 主路径：每个 ### 小节取“第一段正文”，再提炼核心短句
        for para in _extract_first_paragraph_under_each_h3(md_text):
            core = _extract_core_phrase_from_paragraph(para, slice_len=14)
            if core:
                phrases.append(core)

        # 2) 兜底：若第一段没有抓到（比如全是英文名/链接），则扫描该小节内的其他正文行
        if not phrases:
            for lines in _extract_text_lines_under_each_h3(md_text):
                picked = ""
                for line in lines:
                    core = _extract_core_phrase_from_paragraph(line, slice_len=14)
                    if core:
                        picked = core
                        break
                if picked:
                    phrases.append(picked)

        phrases = _dedupe_preserve_order(phrases)

        if not phrases:
            # 最终兜底：从全文里找第一句包含中文的内容
            plain = strip_markdown_to_plain(md_text)
            plain = re.sub(r"https?://\S+", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            plain = _strip_spoken_prefix(plain)
            if _contains_cjk(plain):
                phrases = [_extract_core_phrase_from_paragraph(plain, slice_len=14) or plain[:12]]

        digest = _join_phrases_with_limit(phrases, max_chars=max_chars)

        # 再兜底一次：返回非空字符串（公众号摘要字段不喜欢空）
        if not digest:
            digest = "AI 要点更新"

        return digest

    except Exception:
        # 极限兜底：避免摘要逻辑异常阻断发稿
        try:
            plain = strip_markdown_to_plain(md_text or "")
            plain = re.sub(r"https?://\S+", " ", plain)
            plain = re.sub(r"\s+", " ", plain).strip()
            plain = _strip_spoken_prefix(plain)
            if _contains_cjk(plain):
                core = _extract_core_phrase_from_paragraph(plain, slice_len=12) or plain[:12]
                return truncate_chars((core or "").strip(), max_chars)
        except Exception:
            pass

        return "AI 要点更新"


def extract_wechat_digest(md_text: str, max_chars: int = 90) -> str:
    """兼容旧函数名：内部直接复用 guess_digest_from_markdown。"""

    return guess_digest_from_markdown(md_text, max_chars=max_chars)


def guess_title_from_markdown(md_text: str) -> Optional[str]:
    """Prefer first H1 line like '# xxx'."""
    for line in md_text.splitlines():
        m = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return None


# ----------------------------
# Markdown -> WeChat HTML
# ----------------------------


def _normalize_title_for_compare(s: str) -> str:
    s = (s or "").strip().lower()
    # unify separators
    s = s.replace("—", "-").replace("–", "-").replace("|", "-")
    s = re.sub(r"\s+", " ", s)
    # keep only common chars
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff\- ]+", "", s)
    return s.strip()


def _is_title_equivalent(a: str, b: str) -> bool:
    na = _normalize_title_for_compare(a)
    nb = _normalize_title_for_compare(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    # allow "contains" match for small formatting diffs
    return (na in nb) or (nb in na)


_URL_RE = re.compile(r"(https?://[^\s)）]+)")


def _extract_first_url(text: str) -> Optional[str]:
    m = _URL_RE.search(text or "")
    return m.group(1) if m else None


def _guess_button_text(url: str) -> str:
    u = (url or "").lower()
    if "x.com/" in u or "twitter.com/" in u:
        return "查看推文"
    if "youtube.com/" in u or "youtu.be/" in u:
        return "查看视频"
    return "查看原文"


def _merge_style(tag: Any, style: str) -> None:
    old = "" if tag is None else tag.get("style", "")
    if old and not old.endswith(";"):
        old += ";"
    tag["style"] = (old + style).strip(";") + ";"


def markdown_to_wechat_html(md_text: str, *, article_title: Optional[str] = None) -> str:
    """Convert markdown to WeChat-friendly inline-styled HTML.

    Goals (公众号风格):
    - 自动去重标题（正文第一段等价于草稿 title 时移除）
    - 分类标题居中/分割线风格
    - 每个人物条目卡片化 + item 之间用 hr 分割
    - 原文链接渲染为按钮（避免裸 URL 占据版面）
    """

    raw_html = md_to_html(
        md_text,
        extensions=[
            "extra",
            "sane_lists",
            "tables",
            "fenced_code",
        ],
        output_format="html5",
    )

    soup = BeautifulSoup(raw_html, "lxml")

    container = soup.new_tag("div")
    container["id"] = "js_content"
    container["style"] = (
        "font-size:16px;"
        "line-height:1.95;"
        "color:#111827;"
        "font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,"
        "'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;"
        "letter-spacing:0.2px;"
        "word-break:break-word;"
    )

    # Move body nodes into container
    for node in list(soup.body.contents) if soup.body else list(soup.contents):
        if getattr(node, "name", None) is None and str(node).strip() == "":
            continue
        container.append(node.extract())

    # 1) Remove duplicate H1 title (WeChat draft already has title field)
    top_nodes = [n for n in list(container.contents) if not (getattr(n, "name", None) is None and str(n).strip() == "")]
    if top_nodes and getattr(top_nodes[0], "name", None) == "h1" and article_title:
        h1_text = top_nodes[0].get_text(strip=True)
        if _is_title_equivalent(h1_text, article_title):
            top_nodes[0].extract()

    # Styles (inline, WeChat-safe)
    SECTION_STYLE = (
        "border:1px solid #dbeafe;"
        "border-radius:14px;"
        "padding:14px 14px 10px;"
        "margin:18px 0;"
        "background:#ffffff;"
        "box-shadow:0 6px 18px rgba(15,23,42,0.06);"
    )
    SECTION_HEADER_STYLE = (
        "text-align:center;"
        "font-size:15px;"
        "font-weight:800;"
        "color:#1d4ed8;"
        "background:#eef6ff;"
        "padding:9px 12px;"
        "border-radius:999px;"
        "margin:0 0 14px 0;"
    )
    ITEM_DIVIDER_STYLE = "border:none;border-top:1px solid #e5e7eb;margin:16px 0 14px;"
    ITEM_TITLE_STYLE = "font-size:18px;line-height:1.35;margin:0 0 10px;font-weight:800;color:#0f172a;"
    P_STYLE = "margin:10px 0;line-height:1.95;font-size:16px;color:#111827;"
    LI_STYLE = "margin:6px 0;line-height:1.85;"
    UL_STYLE = "margin:10px 0 10px 20px;padding:0;"
    OL_STYLE = "margin:10px 0 10px 20px;padding:0;"
    BLOCKQUOTE_STYLE = (
        "margin:12px 0;"
        "padding:10px 12px;"
        "border-left:4px solid #93c5fd;"
        "background:#eff6ff;"
        "border-radius:10px;"
    )
    HR_STYLE = "border:none;border-top:1px solid #e5e7eb;margin:18px 0;"

    META_CALLOUT_STYLE = (
        "margin:12px 0;"
        "padding:10px 12px;"
        "background:#f8fafc;"
        "border:1px dashed #c7d2fe;"
        "border-radius:12px;"
        "color:#111827;"
    )
    FOOTER_STYLE = (
        "margin-top:12px;"
        "padding-top:10px;"
        "border-top:1px dashed #e5e7eb;"
    )
    TAG_STYLE = (
        "display:inline-block;"
        "padding:4px 10px;"
        "border-radius:999px;"
        "border:1px solid #e2e8f0;"
        "background:#f1f5f9;"
        "color:#334155;"
        "font-size:12px;"
        "margin:6px 8px 0 0;"
    )

    # 2) Wrap H2 blocks into section cards
    elems = [n for n in list(container.contents) if not (getattr(n, "name", None) is None and str(n).strip() == "")]
    container.clear()

    current_section = None
    for el in elems:
        el.extract()
        if getattr(el, "name", None) == "h2":
            # Start new section
            current_section = soup.new_tag("div")
            current_section["style"] = SECTION_STYLE

            h2_text = el.get_text(" ", strip=True)
            h2_text = re.sub(r"^\s*\d+\)\s*", "", h2_text)
            if "x / twitter" in h2_text.lower():
                h2_text = f"—— {h2_text} 精选 ——"
            else:
                h2_text = f"—— {h2_text} ——"

            header = soup.new_tag("div")
            header["style"] = SECTION_HEADER_STYLE
            header.string = h2_text
            current_section.append(header)

            container.append(current_section)
            continue

        if current_section is not None:
            current_section.append(el)
        else:
            container.append(el)

    # 3) Inside each section: wrap H3 blocks into items, add hr between items
    for section in container.find_all("div", recursive=False):
        # Only handle our sections
        if "border:1px solid" not in (section.get("style", "")):
            continue

        children = [n for n in list(section.contents) if not (getattr(n, "name", None) is None and str(n).strip() == "")]
        if not children:
            continue

        header = children[0]
        rest = children[1:]

        # Rebuild section content
        for n in rest:
            n.extract()

        current_item = None
        item_count = 0

        def flush_item(it: Any) -> None:
            if it is None:
                return

            # Extract link + keywords lines into a footer area
            links: List[Tuple[str, str]] = []
            keywords: List[str] = []

            # We only treat very "metadata-like" list items as link/keyword.
            for li in list(it.find_all("li")):
                li_text = li.get_text(" ", strip=True)

                # keywords
                m_kw = re.match(r"^(英文关键词|关键词)\s*[:：]\s*(.+)\s*$", li_text)
                if m_kw:
                    raw_kw = m_kw.group(2)
                    parts = [p.strip() for p in re.split(r"[,，;；]", raw_kw) if p.strip()]
                    keywords.extend(parts)
                    li.extract()
                    continue

                # links: "原文链接：https://..." / "视频链接：https://..." / "xxx：https://..."
                url = _extract_first_url(li_text)
                if url:
                    # Heuristic: treat lines that look like "<label>: <url>" as link metadata.
                    left = li_text.replace(url, "").strip()
                    left = re.sub(r"^[\-•\s]+", "", left)
                    left_clean = re.sub(r"\s+", " ", left).strip()

                    looks_like_label_line = left_clean.endswith(":") or left_clean.endswith("：")
                    # If it's a long sentence, it's likely NOT a pure link line.
                    if looks_like_label_line and len(left_clean) <= 80:
                        label = left_clean.rstrip(":：").strip()
                        btn_text = _guess_button_text(url)
                        # If the label is short and meaningful, use it as button text.
                        if 1 <= len(label) <= 18 and label not in ("原文链接", "视频链接"):
                            btn_text = label

                        links.append((btn_text, url))
                        li.extract()
                        continue

            # Clean up empty lists
            for ul in list(it.find_all(["ul", "ol"])):
                if not ul.find_all("li", recursive=False):
                    ul.extract()

            # Callout styling for takeaway / 一句话点题
            for p in it.find_all("p"):
                p_text = p.get_text(" ", strip=True)
                if p_text.startswith("一句话点题：") or p_text.startswith("The Takeaway") or p_text.startswith("要点："):
                    _merge_style(p, META_CALLOUT_STYLE)

            if links or keywords:
                footer = soup.new_tag("div")
                footer["style"] = FOOTER_STYLE

                for btn_text, url in links:
                    label = soup.new_tag("div")
                    label["style"] = URL_LABEL_STYLE
                    label.string = f"🔗 {btn_text} (请复制后在浏览器打开):"
                    footer.append(label)

                    url_box = soup.new_tag("div")
                    url_box["style"] = URL_BOX_STYLE
                    url_box.string = url
                    footer.append(url_box)

                if keywords:
                    # keywords label
                    kw_label = soup.new_tag("div")
                    kw_label["style"] = "margin-top:10px;font-size:13px;color:#64748b;font-weight:700;"
                    kw_label.string = "关键词"
                    footer.append(kw_label)

                    for kw in keywords[:20]:
                        tag = soup.new_tag("span")
                        tag["style"] = TAG_STYLE
                        tag.string = kw
                        footer.append(tag)

                it.append(footer)

        # Iterate section content
        for el in rest:
            if getattr(el, "name", None) == "h3":
                if current_item is not None:
                    flush_item(current_item)
                    section.append(current_item)

                if item_count > 0:
                    hr = soup.new_tag("hr")
                    hr["style"] = ITEM_DIVIDER_STYLE
                    section.append(hr)

                current_item = soup.new_tag("div")
                current_item["style"] = "margin:0;"

                _merge_style(el, ITEM_TITLE_STYLE)
                current_item.append(el)
                item_count += 1
                continue

            if current_item is not None:
                current_item.append(el)
            else:
                section.append(el)

        if current_item is not None:
            flush_item(current_item)
            section.append(current_item)

    # 4) Apply baseline typography styles
    for p in container.find_all("p"):
        _merge_style(p, P_STYLE)

    for ul in container.find_all("ul"):
        _merge_style(ul, UL_STYLE)

    for ol in container.find_all("ol"):
        _merge_style(ol, OL_STYLE)

    for li in container.find_all("li"):
        _merge_style(li, LI_STYLE)

    for bq in container.find_all("blockquote"):
        _merge_style(bq, BLOCKQUOTE_STYLE)

    for hr in container.find_all("hr"):
        _merge_style(hr, HR_STYLE)

    # Default anchor style
    for a in container.find_all("a"):
        _merge_style(a, "color:#2563eb;text-decoration:none;font-weight:700;")

    # inline code
    for code in container.find_all("code"):
        if code.find_parent("pre") is None:
            _merge_style(code, "background:#f1f5f9;border:1px solid #e2e8f0;border-radius:6px;padding:0 5px;")

    for pre in container.find_all("pre"):
        _merge_style(pre, "background:#0b1020;color:#e6edf3;padding:12px 14px;border-radius:10px;overflow:auto;")

    for img in container.find_all("img"):
        _merge_style(img, "max-width:100%;height:auto;display:block;margin:12px auto;border-radius:12px;")

    # Final pass: turn any trailing "Generated through ...: url" paragraph into a small footer with button
    for p in list(container.find_all("p")):
        txt = p.get_text(" ", strip=True)
        if txt.lower().startswith("generated through"):
            url = _extract_first_url(txt)
            if url:
                # keep a short label line + copyable URL
                p.clear()
                p.name = "div"
                _merge_style(p, "margin:18px 0 0;font-size:13px;color:#64748b;line-height:1.6;")
                p.append("Generated through the Follow Builders skill")

                label = soup.new_tag("div")
                label["style"] = URL_LABEL_STYLE
                label.string = "🔗 项目地址 (请复制后在浏览器打开):"
                p.append(label)

                url_box = soup.new_tag("div")
                url_box["style"] = URL_BOX_STYLE
                url_box.string = url
                p.append(url_box)

    return str(container)


def _looks_like_html_input(text: str) -> bool:
    """Heuristic: if the file already contains HTML (e.g. patched/styled content),
    we should treat it as ready-to-upload HTML instead of re-rendering from Markdown.
    """
    s = (text or "").lstrip()
    if not s.startswith("<"):
        return False
    # common wrappers we use
    if "<section" in s[:2000] or "<div" in s[:2000] or "<p" in s[:2000]:
        return True
    return False


def _cn_weekday(dt: datetime) -> str:
    # Python: Monday=0
    mapping = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    return mapping[dt.weekday()]


def _try_parse_date_from_text(text: str) -> Optional[datetime]:
    """Try to parse a date from common patterns in title/markdown/filename."""
    if not text:
        return None

    # 2026-04-23 / 2026/4/23 / 2026.4.23
    m = re.search(r"(20\d{2})[\-/.](\d{1,2})[\-/.](\d{1,2})", text)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except Exception:
            pass

    # 2026年4月23日
    m2 = re.search(r"(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", text)
    if m2:
        try:
            return datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
        except Exception:
            pass

    return None


def _format_cn_date(dt: datetime) -> str:
    return f"{dt.year}年{dt.month}月{dt.day}日（{_cn_weekday(dt)}）"


def markdown_to_wechat_html_digest_card(
    md_text: str,
    *,
    article_title: Optional[str] = None,
    date_hint: Optional[str] = None,
) -> str:
    """Render a digest-like Markdown into a WeChat-friendly "card" HTML.

    This style matches the patched output you used before:
    - Outer <section> card
    - A top header bar (title + date)
    - H2 as centered divider
    - H3 as item title
    - Link meta lines -> a single button area
    - Keyword meta lines removed
    """

    raw_html = md_to_html(
        md_text,
        extensions=[
            "extra",
            "sane_lists",
            "tables",
            "fenced_code",
        ],
        output_format="html5",
    )
    soup = BeautifulSoup(raw_html, "lxml")

    # Extract H1 title (if any)
    h1 = soup.find("h1")
    h1_text = h1.get_text(" ", strip=True) if h1 else ""
    if h1 is not None:
        h1.extract()

    display_title = (article_title or h1_text or "").strip() or "AI Digest"

    # Build date
    dt = (
        _try_parse_date_from_text(date_hint or "")
        or _try_parse_date_from_text(display_title)
        or _try_parse_date_from_text(h1_text)
        or datetime.now()
    )
    date_cn = _format_cn_date(dt)

    # Try to derive a short product name from title
    base_name = display_title
    # common separators: "—" "-" "|"
    for sep in ["—", "-", "|"]:
        if sep in base_name:
            base_name = base_name.split(sep, 1)[0].strip()
            break
    if not base_name:
        base_name = "AI Digest"

    # Outer structure
    section = soup.new_tag("section")
    section["style"] = (
        "border: 1px solid #e5e6eb;"
        "border-radius: 8px;"
        "overflow: hidden;"
        "margin-bottom: 24px;"
        "box-shadow: 0 4px 10px rgba(0,0,0,0.03);"
    )

    header = soup.new_tag("div")
    header["style"] = (
        "background-color: #eaf2ff;"
        "padding: 16px 20px;"
        "font-weight: bold;"
        "font-size: 18px;"
        "color: #1f5add;"
        "border-bottom: 1px solid #e5e6eb;"
    )
    header.string = f"🔨 {base_name} | {date_cn}"
    section.append(header)

    content = soup.new_tag("div")
    content["style"] = (
        "padding: 20px 20px 10px 20px;"
        "color: #333333;"
        "line-height: 1.8;"
        "font-size: 15px;"
    )
    section.append(content)

    # Take body nodes
    body_nodes = list(soup.body.contents) if soup.body else list(soup.contents)
    nodes: List[Any] = []
    for n in body_nodes:
        if getattr(n, "name", None) is None and str(n).strip() == "":
            continue
        nodes.append(n)

    def clean_h_text(t: str) -> str:
        t = (t or "").strip()
        t = re.sub(r"^\s*\d+\)\s*", "", t)
        t = re.sub(r"^\s*\d+\.\s*", "", t)
        return t

    def render_h2_title(t: str) -> str:
        low = t.lower()
        t = clean_h_text(t)
        if "x / twitter" in low or "twitter" in low or t.lower() in ("x", "x/twitter"):
            return "—— X / Twitter 精选 ——"
        if "podcast" in low or "播客" in t:
            return "—— 播客精选 ——"
        return f"—— {t} ——"

    def normalize_h3(t: str) -> str:
        t = (t or "").strip()
        # Convert Chinese parentheses to dot separator
        if "（" in t and t.endswith("）"):
            left, inside = t.split("（", 1)
            inside = inside[:-1]
            t = f"{left.strip()} · {inside.strip()}"
        return t

    current_h2_title: Optional[str] = None
    current_items: List[Dict[str, Any]] = []
    current_item: Optional[Dict[str, Any]] = None

    def flush_item() -> None:
        nonlocal current_item, current_items
        if current_item is None:
            return
        current_items.append(current_item)
        current_item = None

    def flush_section() -> None:
        nonlocal current_h2_title, current_items
        if not current_h2_title:
            return

        # Section divider
        divider = soup.new_tag("div")
        divider["style"] = (
            "text-align: center;"
            "color: #666;"
            "margin: 20px 0 30px;"
            "font-weight: bold;"
            "letter-spacing: 2px;"
        )
        divider.string = current_h2_title
        content.append(divider)

        # Items
        for idx, it in enumerate(current_items):
            title_div = soup.new_tag("div")
            title_div["style"] = "font-size: 17px; font-weight: bold; color: #111; margin-bottom: 12px;"
            title_div.string = it["title"]
            content.append(title_div)

            for el in it["body"]:
                content.append(el)

            # links -> copyable URL area
            links: List[Tuple[str, str]] = it.get("links") or []
            if links:
                btn_wrap = soup.new_tag("div")
                btn_wrap["style"] = "margin-bottom: 30px;"
                for btn_text, url in links[:3]:
                    label = soup.new_tag("div")
                    label["style"] = URL_LABEL_STYLE
                    label.string = f"🔗 {btn_text} (请复制后在浏览器打开):"
                    btn_wrap.append(label)

                    url_box = soup.new_tag("div")
                    url_box["style"] = URL_BOX_STYLE
                    url_box.string = url
                    btn_wrap.append(url_box)
                content.append(btn_wrap)

            if idx < len(current_items) - 1:
                hr = soup.new_tag("hr")
                hr["style"] = "border: none; border-top: 1px solid #eee; margin: 30px 0;"
                content.append(hr)

        # reset
        current_h2_title = None
        current_items = []

    # Build sections/items based on headings
    for n in nodes:
        if getattr(n, "name", None) == "h2":
            flush_item()
            flush_section()
            current_h2_title = render_h2_title(n.get_text(" ", strip=True))
            continue

        if getattr(n, "name", None) == "h3":
            flush_item()
            current_item = {
                "title": normalize_h3(n.get_text(" ", strip=True)),
                "body": [],
                "links": [],
            }
            continue

        # content nodes
        if current_item is None:
            # ignore leading content outside sections
            continue

        # style paragraphs
        if getattr(n, "name", None) == "p":
            txt = n.get_text(" ", strip=True)
            if txt.startswith("一句话点题："):
                n["style"] = "margin: 0 0 20px; font-weight: bold;"
            elif "The Takeaway" in txt or "Takeaway" in txt:
                n["style"] = (
                    "margin: 0 0 16px;"
                    "color: #555;"
                    "background-color: #f7f9fa;"
                    "padding: 12px 16px;"
                    "border-left: 4px solid #1f5add;"
                    "border-radius: 4px;"
                )
            elif txt.lower().startswith("generated through"):
                url = _extract_first_url(txt)
                # render footer
                footer = soup.new_tag("div")
                footer["style"] = (
                    "text-align: center;"
                    "font-size: 12px;"
                    "color: #999;"
                    "margin-top: 40px;"
                    "padding-top: 20px;"
                    "border-top: 1px dashed #eee;"
                )
                footer.string = "Generated through the Follow Builders skill"
                current_item["body"].append(footer)

                if url:
                    label = soup.new_tag("div")
                    label["style"] = URL_LABEL_STYLE + "text-align: center;"
                    label.string = "🔗 项目地址 (请复制后在浏览器打开):"
                    current_item["body"].append(label)

                    url_box = soup.new_tag("div")
                    url_box["style"] = URL_BOX_STYLE
                    url_box.string = url
                    current_item["body"].append(url_box)
                continue
            else:
                # default paragraph spacing
                n["style"] = n.get("style", "") + "margin: 0 0 16px;"

        # style lists + extract metadata items
        if getattr(n, "name", None) in ("ul", "ol"):
            n["style"] = "margin: 0 0 16px; padding-left: 20px; color: #444;"

            for li in list(n.find_all("li", recursive=False)):
                li_txt = li.get_text(" ", strip=True)

                # remove keywords lines
                if re.match(r"^(英文关键词|关键词)\s*[:：]", li_txt):
                    li.extract()
                    continue

                url = _extract_first_url(li_txt)
                if url:
                    # Heuristic: treat "xxx：https://" or "原文链接：https://" as metadata links
                    left = li_txt.replace(url, "").strip()
                    left = re.sub(r"^[\-•\s]+", "", left)
                    left = re.sub(r"\s+", " ", left).strip().rstrip(":：")
                    btn_text = "查看原文"
                    if "youtube" in url.lower() or "youtu.be" in url.lower():
                        btn_text = "查看原文 (YouTube)"
                    elif "视频" in left:
                        btn_text = "查看原文 (视频)"
                    elif left and len(left) <= 18 and left not in ("原文链接", "视频链接"):
                        btn_text = left

                    current_item["links"].append((btn_text, url))
                    li.extract()
                    continue

                li["style"] = "margin-bottom: 8px;"

            # drop empty list after extraction
            if not n.find_all("li", recursive=False):
                continue

        current_item["body"].append(n)

    flush_item()
    flush_section()

    return str(section)


def _is_http_url(href: str) -> bool:
    h = (href or "").strip().lower()
    return h.startswith("http://") or h.startswith("https://")


def _html_fragment_from_soup(soup: BeautifulSoup) -> str:
    """Return HTML without auto-added <html><body> wrappers."""
    root = soup.body if soup.body else soup
    return "".join(str(x) for x in list(root.contents))


def _patch_html_links_to_copyable_boxes(html_text: str) -> str:
    """WeChat often strips or disables external clickable links.

    If the content contains <a href="...">查看原文</a> only, users will only see
    the text (e.g. "查看原文") and cannot access / copy the real URL.

    This patch converts HTML anchors into a copyable URL box:
    - Keeps anchor text as plain text (so the sentence remains readable)
    - Adds a visible URL block (monospace box) for copying

    Note: This is intentionally conservative and only handles http(s) links.
    """

    if not html_text or "<a" not in html_text:
        return html_text

    soup = BeautifulSoup(html_text, "lxml")

    # Avoid inserting duplicate URL boxes for the same href under the same parent.
    inserted: set[tuple[int, str]] = set()

    for a in list(soup.find_all("a")):
        href = (a.get("href") or "").strip()
        if not _is_http_url(href):
            continue

        raw_text = a.get_text(" ", strip=True)
        display_text = raw_text or _guess_button_text(href)

        parent = a.parent
        a.replace_with(display_text)

        if parent is not None:
            key = (id(parent), href)
            if key in inserted:
                continue
            inserted.add(key)

        wrap = soup.new_tag("div")
        wrap["style"] = "margin: 10px 0 16px;"

        label = soup.new_tag("div")
        label["style"] = URL_LABEL_STYLE
        label.string = f"🔗 {display_text} (请复制后在浏览器打开):"
        wrap.append(label)

        url_box = soup.new_tag("div")
        url_box["style"] = URL_BOX_STYLE
        url_box.string = href
        wrap.append(url_box)

        # Try to insert the URL box in a location that doesn't break HTML structure.
        if parent is not None and getattr(parent, "name", None) == "div":
            # Typical styled HTML uses: <div><a href>查看原文</a></div>
            # After replacement, the div becomes a lonely text node "查看原文".
            # Replace the whole wrapper div to avoid leaving an useless "查看原文" line.
            non_empty_children = [c for c in parent.contents if str(c).strip() != ""]
            if len(non_empty_children) == 1 and parent.get_text(" ", strip=True) == display_text:
                parent.replace_with(wrap)
                continue

        if parent is not None and getattr(parent, "name", None) == "li":
            parent.append(wrap)
        elif parent is not None and getattr(parent, "name", None) == "p":
            parent.insert_after(wrap)
        elif parent is not None and getattr(parent, "name", None) in ("blockquote", "section"):
            parent.insert_after(wrap)
        else:
            # fallback
            (soup.body or soup).append(wrap)

    return _html_fragment_from_soup(soup)


def render_wechat_html(
    source_text: str,
    *,
    article_title: str,
    markdown_path: Path,
    render_style: str,
    input_format: str = "auto",
) -> str:
    """Render input file content into final HTML for WeChat draft.

    Parameters
    - input_format:
      - auto (default): if content looks like HTML, treat it as HTML; otherwise Markdown
      - markdown: force Markdown rendering even if the content starts with '<'
      - html: treat the content as HTML directly

    Regardless of the input format, we will *always* patch <a href> into visible
    copyable URL boxes, so the final draft shows real URLs instead of only
    "查看原文".
    """

    fmt = (input_format or "auto").strip().lower()
    if fmt not in ("auto", "markdown", "md", "html"):
        raise ValueError(f"未知 input_format：{input_format}（可选：auto / markdown / html）")

    def _render_from_markdown(md_text: str) -> str:
        style = (render_style or "").strip().lower()
        if style in ("classic", "default", "legacy"):
            return markdown_to_wechat_html(md_text, article_title=article_title)
        if style in ("digest-card", "digest", "card"):
            return markdown_to_wechat_html_digest_card(
                md_text,
                article_title=article_title,
                date_hint=str(markdown_path),
            )
        raise ValueError(f"未知 render_style：{render_style}（可选：digest-card / classic）")

    looks_html = _looks_like_html_input(source_text)

    if fmt == "html":
        html = source_text
    elif fmt in ("markdown", "md"):
        html = _render_from_markdown(source_text)
    else:
        # auto
        html = source_text if looks_html else _render_from_markdown(source_text)

    return _patch_html_links_to_copyable_boxes(html)


# ----------------------------
# Local cover generation (PIL)
# ----------------------------


def _pick_palette(seed_text: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Pick two RGB colors deterministically from seed text."""
    h = hashlib.md5(seed_text.encode("utf-8")).digest()
    # Avoid too-bright / too-dark extremes
    c1 = (30 + h[0] % 120, 30 + h[1] % 120, 60 + h[2] % 120)
    c2 = (60 + h[3] % 150, 40 + h[4] % 150, 30 + h[5] % 150)
    return c1, c2


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try several common fonts for Chinese; fallback to default."""
    candidates = [
        # Common on many Linux images
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans.ttf",
    ]
    for p in candidates:
        try:
            if Path(p).exists() or p == "DejaVuSans.ttf":
                return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def generate_dynamic_cover(
    *,
    title: str,
    topic: Optional[str],
    out_path: Path,
    size: Tuple[int, int] = DEFAULT_COVER_SIZE,
    date: Optional[str] = None,
) -> Path:
    """Generate a simple but non-static cover image based on title/topic (pure local)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    w, h = size
    seed = f"{title}|{topic or ''}|{date or ''}"
    c1, c2 = _pick_palette(seed)

    # Background gradient
    base = Image.new("RGB", (w, h), c1)
    grad = Image.new("RGB", (w, h), c2)
    mask = Image.new("L", (w, h))
    mask_px = mask.load()
    for y in range(h):
        v = int(255 * (y / max(1, h - 1)))
        for x in range(w):
            # slight diagonal feel
            vv = min(255, max(0, int(v * 0.85 + (x / max(1, w - 1)) * 40)))
            mask_px[x, y] = vv
    img = Image.composite(grad, base, mask)

    # Add subtle noise pattern
    noise = Image.effect_noise((w, h), 18).convert("L")
    noise = noise.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.composite(img, Image.new("RGB", (w, h), (10, 10, 10)), noise.point(lambda p: p * 0.12))

    draw = ImageDraw.Draw(img)

    # Title wrapping
    title_clean = title.strip()
    main_font = _load_font(46)
    sub_font = _load_font(26)
    meta_font = _load_font(20)

    # WeChat cover is small height; keep text compact
    max_chars_per_line = 14
    wrapped = textwrap.wrap(title_clean, width=max_chars_per_line)
    wrapped = wrapped[:2] if wrapped else [title_clean]

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Decorative left bar
    bar_w = 10
    draw.rectangle([0, 0, bar_w, h], fill=(255, 255, 255))

    x0 = 48
    y0 = 66

    # Shadow for readability
    def shadow_text(x: int, y: int, text: str, font: ImageFont.ImageFont, fill: Tuple[int, int, int]):
        shadow = (0, 0, 0)
        for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 2), (2, 0)]:
            draw.text((x + dx, y + dy), text, font=font, fill=shadow)
        draw.text((x, y), text, font=font, fill=fill)

    line_gap = 10
    for i, line in enumerate(wrapped):
        shadow_text(x0, y0 + i * (46 + line_gap), line, main_font, (255, 255, 255))

    # Topic label (optional)
    if topic:
        topic_text = truncate_utf8_bytes(topic.strip(), 32)
        shadow_text(x0, h - 92, f"主题：{topic_text}", sub_font, (230, 238, 255))

    # Footer
    shadow_text(x0, h - 46, f"{date} · 自动生成封面", meta_font, (210, 220, 235))

    img.save(out_path, format="PNG")
    return out_path


# ----------------------------
# WeChat API client
# ----------------------------


class WeChatAPIError(RuntimeError):
    pass


@dataclass
class WeChatCreds:
    appid: str
    appsecret: str


class WeChatClient:
    def __init__(self, *, appid: str, appsecret: str, timeout: int = 30):
        self.creds = WeChatCreds(appid=appid, appsecret=appsecret)
        self.timeout = timeout
        self._session = requests.Session()

    def _get(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.get(url, params=params, timeout=self.timeout)
        data = resp.json()
        self._raise_if_err(data)
        return data

    def _post_json(self, url: str, params: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        resp = self._session.post(url, params=params, json=payload, timeout=self.timeout)
        data = resp.json()
        self._raise_if_err(data)
        return data

    def _post_raw(self, url: str, params: Dict[str, Any], data: bytes) -> Dict[str, Any]:
        resp = self._session.post(url, params=params, data=data, timeout=self.timeout)
        d = resp.json()
        self._raise_if_err(d)
        return d

    @staticmethod
    def _raise_if_err(data: Dict[str, Any]) -> None:
        # WeChat: success usually has no errcode or errcode=0
        errcode = data.get("errcode")
        if errcode not in (None, 0):
            raise WeChatAPIError(f"WeChat API error: errcode={errcode}, errmsg={data.get('errmsg')}, raw={data}")

    def get_access_token(self) -> str:
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.creds.appid,
            "secret": self.creds.appsecret,
        }
        data = self._get(url, params)
        token = data.get("access_token")
        if not token:
            raise WeChatAPIError(f"获取 access_token 失败：{data}")
        return token

    def getcallbackip(self, access_token: str) -> List[str]:
        url = "https://api.weixin.qq.com/cgi-bin/getcallbackip"
        data = self._get(url, {"access_token": access_token})
        return data.get("ip_list") or []

    def upload_image_as_material(self, *, access_token: str, image_path: Path) -> Tuple[str, Optional[str]]:
        url = "https://api.weixin.qq.com/cgi-bin/material/add_material"
        params = {"access_token": access_token, "type": "image"}
        with image_path.open("rb") as f:
            resp = self._session.post(url, params=params, files={"media": f}, timeout=max(self.timeout, 60))
        data = resp.json()
        self._raise_if_err(data)
        media_id = data.get("media_id")
        if not media_id:
            raise WeChatAPIError(f"上传图片失败：{data}")
        return media_id, data.get("url")

    def draft_add(
        self,
        *,
        access_token: str,
        title: str,
        author: str,
        digest: str,
        content_html: str,
        thumb_media_id: str,
        content_source_url: str = "",
        need_open_comment: int = 0,
        only_fans_can_comment: int = 0,
    ) -> str:
        url = "https://api.weixin.qq.com/cgi-bin/draft/add"
        payload = {
            "articles": [
                {
                    "title": title,
                    "author": author,
                    "digest": digest,
                    "content": content_html,
                    "content_source_url": content_source_url,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": need_open_comment,
                    "only_fans_can_comment": only_fans_can_comment,
                }
            ]
        }
        data_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        data = self._post_raw(url, {"access_token": access_token}, data_bytes)
        media_id = data.get("media_id")
        if not media_id:
            raise WeChatAPIError(f"创建草稿失败：{data}")
        return media_id

    def draft_get_url(self, *, access_token: str, media_id: str) -> Optional[str]:
        url = "https://api.weixin.qq.com/cgi-bin/draft/get"
        data = self._post_json(url, {"access_token": access_token}, {"media_id": media_id})
        news_item = data.get("news_item")
        if isinstance(news_item, list) and news_item:
            return news_item[0].get("url")
        return None

    def draft_delete(self, *, access_token: str, media_id: str) -> None:
        """Delete a draft by media_id.

        API: https://api.weixin.qq.com/cgi-bin/draft/delete
        """
        url = "https://api.weixin.qq.com/cgi-bin/draft/delete"
        self._post_json(url, {"access_token": access_token}, {"media_id": media_id})

    def mass_preview_mpnews(self, *, access_token: str, media_id: str, touser: str) -> Dict[str, Any]:
        url = "https://api.weixin.qq.com/cgi-bin/message/mass/preview"
        payload = {
            "touser": touser,
            "mpnews": {"media_id": media_id},
            "msgtype": "mpnews",
        }
        return self._post_json(url, {"access_token": access_token}, payload)

    def freepublish_submit(self, *, access_token: str, media_id: str) -> str:
        url = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"
        data = self._post_json(url, {"access_token": access_token}, {"media_id": media_id})
        publish_id = data.get("publish_id")
        if not publish_id:
            raise WeChatAPIError(f"提交发布失败：{data}")
        return publish_id

    def freepublish_get(self, *, access_token: str, publish_id: str) -> Dict[str, Any]:
        url = "https://api.weixin.qq.com/cgi-bin/freepublish/get"
        return self._post_json(url, {"access_token": access_token}, {"publish_id": publish_id})


# ----------------------------
# State
# ----------------------------


@dataclass
class PublisherState:
    last_title: Optional[str] = None
    last_markdown: Optional[str] = None
    last_generated_at: Optional[str] = None

    last_thumb_media_id: Optional[str] = None
    last_draft_media_id: Optional[str] = None
    last_draft_url: Optional[str] = None

    last_publish_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "last_title": self.last_title,
            "last_markdown": self.last_markdown,
            "last_generated_at": self.last_generated_at,
            "last_thumb_media_id": self.last_thumb_media_id,
            "last_draft_media_id": self.last_draft_media_id,
            "last_draft_url": self.last_draft_url,
            "last_publish_id": self.last_publish_id,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "PublisherState":
        return PublisherState(
            last_title=d.get("last_title"),
            last_markdown=d.get("last_markdown"),
            last_generated_at=d.get("last_generated_at"),
            last_thumb_media_id=d.get("last_thumb_media_id"),
            last_draft_media_id=d.get("last_draft_media_id"),
            last_draft_url=d.get("last_draft_url"),
            last_publish_id=d.get("last_publish_id"),
        )


# ----------------------------
# Env (.env) loading
# ----------------------------


def load_env_file_if_needed(env_file: Optional[Path]) -> None:
    if not env_file:
        return
    if not env_file.exists():
        raise RuntimeError(f"env 文件不存在：{env_file}")

    # Prefer python-dotenv if installed; fallback to minimal parser
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(dotenv_path=str(env_file), override=False)
        return
    except Exception:
        pass

    # Minimal .env parser: KEY=VALUE lines
    for line in read_text(env_file).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


def require_creds() -> WeChatCreds:
    appid = os.getenv("WECHAT_APPID")
    appsecret = os.getenv("WECHAT_APPSECRET")
    if not appid or not appsecret:
        raise RuntimeError(
            "缺少公众号凭证。请通过环境变量或 .env 提供：WECHAT_APPID, WECHAT_APPSECRET"
        )
    return WeChatCreds(appid=appid, appsecret=appsecret)


# ----------------------------
# Typer CLI
# ----------------------------


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="微信公众号自动发布 CLI（草稿/预览/发布）",
)


@app.command("doctor")
def doctor(
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="可选：.env 文件路径"),
    timeout: int = typer.Option(30, "--timeout", help="网络超时时间（秒）"),
) -> None:
    """快速验证：凭证是否正确、access_token 是否可用、是否有基础接口权限。"""
    load_env_file_if_needed(env_file)
    creds = require_creds()

    client = WeChatClient(appid=creds.appid, appsecret=creds.appsecret, timeout=timeout)
    token = client.get_access_token()
    ips = client.getcallbackip(token)

    typer.secho("[OK] access_token 获取成功", fg=typer.colors.GREEN)
    typer.echo(f"- getcallbackip: {len(ips)} 个 IP")
    typer.echo("\n下一步：建议运行 generate-draft 测试 draft/add & material/add_material 权限。")


@app.command("generate-draft")
def generate_draft(
    markdown_path: Path = typer.Option(..., "--markdown", exists=True, file_okay=True, dir_okay=False, help="Markdown 文件路径"),
    title: Optional[str] = typer.Option(None, "--title", help="文章标题（不传则尝试从 Markdown H1 推断）"),
    digest: Optional[str] = typer.Option(None, "--digest", help="文章摘要（不传则通过 auto-digest 逻辑从正文推断）"),
    topic: Optional[str] = typer.Option(None, "--topic", help="用于封面展示的主题（可选）"),
    author: str = typer.Option("", "--author", help="作者（可留空）"),
    source_url: str = typer.Option("", "--source-url", help="阅读原文链接（可留空）"),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, "--output-dir", help="输出目录"),
    state_path: Path = typer.Option(DEFAULT_STATE_PATH, "--state", help="state.json 路径（用于缓存 media_id 流转）"),
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="可选：.env 文件路径"),
    cover_path: Optional[Path] = typer.Option(None, "--cover", help="可选：直接使用本地封面图片（跳过动态生成）"),
    cover_size: str = typer.Option("900x383", "--cover-size", help="动态封面尺寸，例如 900x383"),
    render_style: str = typer.Option(
        "digest-card",
        "--render-style",
        help=(
            "渲染风格：digest-card（卡片样式） / classic（旧样式）。"
            "（建议传原始 Markdown 源文件；若输入内容已是 HTML，也会做链接补丁处理）"
        ),
    ),
    input_format: str = typer.Option(
        "auto",
        "--input-format",
        help=(
            "输入格式：auto（默认自动判断）/ markdown（强制按 Markdown 渲染）/ html（强制按 HTML 处理）。"
            "强烈建议传原始 Markdown 源文件（不要传 *_styled.md）。"
        ),
    ),
    delete_old_draft: bool = typer.Option(
        False,
        "--delete-old-draft",
        help="创建新草稿前，先删除 state.json 中记录的上一条草稿（last_draft_media_id）。",
    ),
    timeout: int = typer.Option(30, "--timeout", help="网络超时时间（秒）"),
) -> None:
    """生成动态封面 -> 上传封面 -> Markdown 转 HTML -> 创建草稿，并写入 state.json。"""
    load_env_file_if_needed(env_file)

    md_text = read_text(markdown_path)

    # Common pitfall: passing *_styled.md (which is actually HTML) will bypass the Markdown renderer.
    # We still support it, but we strongly recommend using the original Markdown source.
    looks_html = _looks_like_html_input(md_text)
    if markdown_path.name.endswith("_styled.md") or (looks_html and (input_format or "auto").strip().lower() == "auto"):
        typer.secho(
            "[WARN] 检测到输入文件疑似为已渲染的 HTML（例如 *_styled.md）。建议改用原始 Markdown 源文件生成，避免绕过 markdown->wechat 渲染逻辑。",
            fg=typer.colors.YELLOW,
        )
        typer.echo("- 推荐用法：python3 wechat_publisher/publish_wechat_draft.py generate-draft --markdown <原始.md>")
        typer.echo("- 若你确实要直接上传 HTML：请加 --input-format html（脚本仍会把 <a href> 补成可复制链接框）")

    final_title = (title or guess_title_from_markdown(md_text) or markdown_path.stem).strip()

    # Always render local preview first (even if API creds are missing)
    html = render_wechat_html(
        md_text,
        article_title=final_title,
        markdown_path=markdown_path,
        render_style=render_style,
        input_format=input_format,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save local preview html
    html_path = output_dir / "wechat_ready.html"
    write_text(html_path, html)

    # WeChat API creds are only required from here
    try:
        creds = require_creds()
    except Exception as e:
        safe_json_dump(
            output_dir / "result.json",
            {
                "ok": False,
                "title": final_title,
                "error": str(e),
                "html_path": str(html_path),
                "state_path": str(state_path),
            },
        )
        typer.secho("[WARN] 已生成本地预览 HTML，但缺少公众号凭证，无法创建草稿", fg=typer.colors.YELLOW)
        typer.echo(f"- html preview: {html_path}")
        typer.echo("请通过环境变量或 --env-file 提供：WECHAT_APPID, WECHAT_APPSECRET")
        raise typer.Exit(code=2)

    if digest:
        final_digest = truncate_chars_with_dots(digest, 90)
    else:
        # Auto-digest: 中文摘要启发式（<= 90 chars，且以 "..." 结尾）
        final_digest = guess_digest_from_markdown(md_text, max_chars=90)

    # Prepare cover image
    if cover_path is not None:
        if not cover_path.exists():
            raise RuntimeError(f"指定的封面图片不存在：{cover_path}")
        cover_file = cover_path
    else:
        # Parse size
        try:
            w_s, h_s = cover_size.lower().split("x", 1)
            size = (int(w_s), int(h_s))
        except Exception:
            raise RuntimeError("--cover-size 格式错误，应类似 900x383")

        # include date in cover
        date_str = datetime.now().strftime("%Y-%m-%d")
        cover_file = output_dir / f"cover_{sha1_short(final_title)}.png"
        generate_dynamic_cover(title=final_title, topic=topic, out_path=cover_file, size=size, date=date_str)

    # WeChat API
    old_state = PublisherState.from_dict(load_json_if_exists(state_path))

    client = WeChatClient(appid=creds.appid, appsecret=creds.appsecret, timeout=timeout)
    token = client.get_access_token()

    deleted_draft_media_id: Optional[str] = None
    if delete_old_draft and old_state.last_draft_media_id:
        deleted_draft_media_id = old_state.last_draft_media_id
        try:
            client.draft_delete(access_token=token, media_id=deleted_draft_media_id)
            typer.secho(f"[OK] 已删除旧草稿：{deleted_draft_media_id}", fg=typer.colors.GREEN)
        except Exception as e:
            # We don't hard fail here: sometimes the draft is already deleted manually.
            typer.secho(
                f"[WARN] 删除旧草稿失败（将继续创建新草稿）：{deleted_draft_media_id}, err={e}",
                fg=typer.colors.YELLOW,
            )

    thumb_media_id, thumb_url = client.upload_image_as_material(access_token=token, image_path=cover_file)
    draft_media_id = client.draft_add(
        access_token=token,
        title=final_title,
        author=author,
        digest=final_digest,
        content_html=html,
        thumb_media_id=thumb_media_id,
        content_source_url=source_url,
    )
    draft_url = client.draft_get_url(access_token=token, media_id=draft_media_id)

    # Update state (never store touser / wechatid)
    old_state = PublisherState.from_dict(load_json_if_exists(state_path))
    new_state = PublisherState(
        last_title=final_title,
        last_markdown=str(markdown_path),
        last_generated_at=datetime.now().isoformat(timespec="seconds"),
        last_thumb_media_id=thumb_media_id,
        last_draft_media_id=draft_media_id,
        last_draft_url=draft_url,
        last_publish_id=old_state.last_publish_id,
    )
    safe_json_dump(state_path, new_state.to_dict())

    # Also write a small result json in output dir for quick inspection
    safe_json_dump(
        output_dir / "result.json",
        {
            "ok": True,
            "title": final_title,
            "thumb_media_id": thumb_media_id,
            "thumb_url": thumb_url,
            "draft_media_id": draft_media_id,
            "draft_url": draft_url,
            "html_path": str(html_path),
            "cover_path": str(cover_file),
            "state_path": str(state_path),
        },
    )

    typer.secho("[OK] 草稿已创建", fg=typer.colors.GREEN)
    typer.echo(f"- title: {final_title}")
    typer.echo(f"- draft_media_id: {draft_media_id}")
    typer.echo(f"- draft_url: {draft_url or '(未返回，可在公众号后台草稿箱查看)'}")
    typer.echo(f"- cover: {cover_file}")
    typer.echo(f"- html preview: {html_path}")
    typer.echo(f"- state: {state_path}")


@app.command("preview")
def preview(
    touser: Optional[str] = typer.Option(None, "--to-user", help="预览接收人的微信号（不会写入 state.json）"),
    media_id: Optional[str] = typer.Option(None, "--media-id", help="要预览的图文 media_id（不传则使用 state.json 的 last_draft_media_id）"),
    state_path: Path = typer.Option(DEFAULT_STATE_PATH, "--state", help="state.json 路径"),
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="可选：.env 文件路径"),
    timeout: int = typer.Option(30, "--timeout", help="网络超时时间（秒）"),
) -> None:
    """调用 message/mass/preview，把刚生成的草稿发到指定微信号预览。"""
    load_env_file_if_needed(env_file)
    creds = require_creds()

    st = PublisherState.from_dict(load_json_if_exists(state_path))
    final_media_id = (media_id or st.last_draft_media_id)
    if not final_media_id:
        raise RuntimeError("缺少 media_id：请先运行 generate-draft，或在 preview 里传 --media-id")

    final_touser = touser or os.getenv("WECHAT_PREVIEW_TOUSER")
    if not final_touser:
        # interactive prompt (won't be persisted)
        final_touser = typer.prompt("请输入预览接收人的微信号 touser（不会写入任何文件）")

    client = WeChatClient(appid=creds.appid, appsecret=creds.appsecret, timeout=timeout)
    token = client.get_access_token()

    data = client.mass_preview_mpnews(access_token=token, media_id=final_media_id, touser=final_touser)

    typer.secho("[OK] 已发起预览发送", fg=typer.colors.GREEN)
    typer.echo(f"- media_id: {final_media_id}")
    typer.echo(f"- to_user: (已隐藏)")
    typer.echo(f"- raw: {json.dumps(data, ensure_ascii=False)}")


@app.command("publish")
def publish(
    media_id: Optional[str] = typer.Option(None, "--media-id", help="要发布的草稿 media_id（不传则使用 state.json 的 last_draft_media_id）"),
    state_path: Path = typer.Option(DEFAULT_STATE_PATH, "--state", help="state.json 路径"),
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="可选：.env 文件路径"),
    yes: bool = typer.Option(False, "--yes", help="跳过确认，直接发布"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="是否等待发布完成并打印状态"),
    poll_interval: int = typer.Option(2, "--poll", help="等待发布时的轮询间隔（秒）"),
    timeout: int = typer.Option(30, "--timeout", help="网络超时时间（秒）"),
) -> None:
    """正式发布：freepublish/submit（Route B）。"""
    load_env_file_if_needed(env_file)
    creds = require_creds()

    st = PublisherState.from_dict(load_json_if_exists(state_path))
    final_media_id = (media_id or st.last_draft_media_id)
    if not final_media_id:
        raise RuntimeError("缺少 media_id：请先运行 generate-draft，或在 publish 里传 --media-id")

    if not yes:
        typer.echo("\n即将发布草稿到公众号（freepublish/submit）：")
        typer.echo(f"- media_id: {final_media_id}")
        typer.echo(f"- title: {st.last_title or '(unknown)'}")
        typer.echo("\n注意：发布后会出现在公众号历史消息/群发。")
        ok = typer.confirm("确认发布？", default=False)
        if not ok:
            typer.secho("已取消发布", fg=typer.colors.YELLOW)
            return

    client = WeChatClient(appid=creds.appid, appsecret=creds.appsecret, timeout=timeout)
    token = client.get_access_token()

    publish_id = client.freepublish_submit(access_token=token, media_id=final_media_id)

    # persist publish_id
    st.last_publish_id = publish_id
    safe_json_dump(state_path, st.to_dict())

    typer.secho("[OK] 已提交发布", fg=typer.colors.GREEN)
    typer.echo(f"- publish_id: {publish_id}")

    if not wait:
        typer.echo("如需查询发布结果，可后续运行 publish-status（暂未单独提供命令），或重新执行 publish --wait")
        return

    typer.echo("\n等待发布完成（轮询 freepublish/get）...")
    # Status:
    # - 0: 成功
    # - 1: 发布中
    # - 2: 原创失败
    # - 3: 常规失败
    # - 4: 运营审核中
    # - 5: 运营审核失败
    for _ in range(120):  # up to ~4min with 2s poll
        data = client.freepublish_get(access_token=token, publish_id=publish_id)
        publish_status = data.get("publish_status")
        if publish_status == 0:
            typer.secho("[OK] 发布成功", fg=typer.colors.GREEN)
            article_id = data.get("article_id")
            if article_id:
                typer.echo(f"- article_id: {article_id}")
            safe_json_dump(DEFAULT_OUTPUT_DIR / "publish_result.json", data)
            return
        if publish_status in (2, 3, 5):
            typer.secho("[FAILED] 发布失败", fg=typer.colors.RED)
            safe_json_dump(DEFAULT_OUTPUT_DIR / "publish_result.json", data)
            typer.echo(json.dumps(data, ensure_ascii=False, indent=2))
            raise typer.Exit(code=2)

        time.sleep(max(1, poll_interval))

    typer.secho("[WARN] 等待超时：发布可能仍在进行中，请稍后到后台或再次查询", fg=typer.colors.YELLOW)


@app.command("run")
def run_all(
    markdown_path: Path = typer.Option(..., "--markdown", exists=True, file_okay=True, dir_okay=False, help="Markdown 文件路径"),
    title: Optional[str] = typer.Option(None, "--title", help="文章标题（可选）"),
    digest: Optional[str] = typer.Option(None, "--digest", help="文章摘要（可选）"),
    topic: Optional[str] = typer.Option(None, "--topic", help="主题（用于封面，可选）"),
    author: str = typer.Option("", "--author", help="作者（可留空）"),
    source_url: str = typer.Option("", "--source-url", help="阅读原文链接（可留空）"),
    preview_flag: bool = typer.Option(True, "--preview/--no-preview", help="是否先发送预览"),
    touser: Optional[str] = typer.Option(None, "--to-user", help="预览接收人的微信号（不会写入 state.json）"),
    publish_yes: bool = typer.Option(False, "--yes", help="直接发布（不二次确认）"),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, "--output-dir", help="输出目录"),
    state_path: Path = typer.Option(DEFAULT_STATE_PATH, "--state", help="state.json 路径"),
    env_file: Optional[Path] = typer.Option(None, "--env-file", help="可选：.env 文件路径"),
) -> None:
    """一键流程：generate-draft -> (preview) -> publish（默认阻塞确认）。"""
    # Reuse subcommands by calling underlying functions would be cleaner, but Typer calls are fine.
    generate_draft(
        markdown_path=markdown_path,
        title=title,
        digest=digest,
        topic=topic,
        author=author,
        source_url=source_url,
        output_dir=output_dir,
        state_path=state_path,
        env_file=env_file,
        cover_path=None,
        cover_size="900x383",
        timeout=30,
    )

    if preview_flag:
        preview_cmd_touser = touser or os.getenv("WECHAT_PREVIEW_TOUSER")
        preview(
            touser=preview_cmd_touser,
            media_id=None,
            state_path=state_path,
            env_file=env_file,
            timeout=30,
        )

    publish(
        media_id=None,
        state_path=state_path,
        env_file=env_file,
        yes=publish_yes,
        wait=True,
        poll_interval=2,
        timeout=30,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
