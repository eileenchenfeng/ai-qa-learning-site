#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Feishu CardKit helpers (Card v2 / schema 2.0)

说明
- 这里只负责“生成卡片 DSL / CardKit 包装结构”，不负责发送。
- 发送请使用 inner_skills/feishu-im-send/scripts/im_send.py：
  - create_card（生成 card_id）
  - send（用 card_id 发送 interactive）

注意
- 卡片 DSL 必须是 schema 2.0。
- 不使用 note / action 容器；button 直接放在 elements 里。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def wrap_cardkit(*, name: str, dsl: Dict[str, Any]) -> Dict[str, Any]:
    return {"name": name, "dsl": dsl}


def md(content: str) -> Dict[str, Any]:
    return {"tag": "markdown", "content": content}


def hr() -> Dict[str, Any]:
    return {"tag": "hr"}


def caption(text: str) -> Dict[str, Any]:
    # 卡片 Schema 2.0 禁用 note，使用 div + caption 代替
    return {
        "tag": "div",
        "text": {
            "tag": "plain_text",
            "content": text,
            # 兼容字段：部分环境支持 text_size / text_color；不支持时会忽略
            "text_size": "caption",
            "text_color": "grey",
        },
    }


def button(*, text: str, url: str, style: str = "default") -> Dict[str, Any]:
    # style: primary | default | danger
    if style not in {"primary", "default", "danger"}:
        style = "default"

    return {
        "tag": "button",
        "text": {"tag": "plain_text", "content": text},
        "type": style,
        "behaviors": [{"type": "open_url", "default_url": url}],
    }


def column_set(columns: List[Dict[str, Any]], background_style: str = "default") -> Dict[str, Any]:
    # background_style: default | grey
    return {
        "tag": "column_set",
        "flex_mode": "none",
        "background_style": background_style,
        "columns": columns,
    }


def column(*, elements: List[Dict[str, Any]], weight: int = 1) -> Dict[str, Any]:
    return {
        "tag": "column",
        "width": "weighted",
        "weight": weight,
        "elements": elements,
    }


def build_card(
    *,
    title: str,
    template: str,
    elements: List[Dict[str, Any]],
    card_name: str = "AimeCard",
) -> Dict[str, Any]:
    """Build CardKit dsl (schema 2.0).

    template 常用值：blue / green / red / orange / purple / grey
    """

    dsl = {
        "schema": "2.0",
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": template,
        },
        "body": {"elements": elements},
    }

    return wrap_cardkit(name=card_name, dsl=dsl)
