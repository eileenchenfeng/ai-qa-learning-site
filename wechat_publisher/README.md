# wechat_publisher

把 Markdown 摘要转换成适合微信公众号的 **内联样式 HTML**，并通过微信公众号 API 完成：

- 动态封面生成（纯本地 PIL）→ 上传获取 `thumb_media_id`
- 上传草稿到草稿箱（`draft/add`）
- 发送预览（`message/mass/preview`）
- 正式发表（Route B：`freepublish/submit`）

> 安全说明：
> - 本工具 **不再从 `MEMORY.md` 读取 AppID/AppSecret**。
> - 不会在 `state.json` 等可持久化文件里写入微信号 `touser`。

---

## 1. 安装

```bash
pip3 install -r wechat_publisher/requirements.txt
```

---

## 2. 配置（推荐 .env）

在仓库根目录或任意位置创建一个 `.env` 文件（不要提交到 git）：

```bash
WECHAT_APPID=你的公众号AppID
WECHAT_APPSECRET=你的公众号AppSecret
# 可选：预览接收人的微信号（也可以每次用 --to-user 传入）
# WECHAT_PREVIEW_TOUSER=你的微信号
```

运行命令时通过 `--env-file` 指定：

```bash
python3 wechat_publisher/publish_wechat_draft.py doctor --env-file .env
```

也可以直接用环境变量：

```bash
export WECHAT_APPID=xxx
export WECHAT_APPSECRET=yyy
```

---

## 3. 快速验证权限（doctor）

```bash
python3 wechat_publisher/publish_wechat_draft.py doctor --env-file .env
```

如果 doctor 通过但后续上传失败，通常是接口权限没开：
- `material/add_material`（上传封面）
- `draft/add`（创建草稿）
- `message/mass/preview`（预览）
- `freepublish/submit`（发布）

建议做法：
1) 先跑 `generate-draft`，确认草稿箱可写；
2) 再跑 `preview`；
3) 最后跑 `publish`。

---

## 4. 生成并上传草稿（generate-draft）

```bash
python3 wechat_publisher/publish_wechat_draft.py generate-draft \
  --env-file .env \
  --markdown AI_Builders_Digest_ZH_2026-04-21.md \
  --title "AI Builders Digest | 2026-04-21" \
  --author "陈凤" \
  --topic "每日精选" \
  --source-url ""
```

输出：
- `wechat_publisher/output/wechat_ready.html`：可本地打开预览
- `wechat_publisher/output/result.json`：本次草稿生成结果（不含 access_token）
- `wechat_publisher/state.json`：缓存草稿 `media_id` 等信息（不含微信号）

---

## 5. 发送预览（preview）

### 方式 A：通过参数传入（不会落盘）

```bash
python3 wechat_publisher/publish_wechat_draft.py preview \
  --env-file .env \
  --to-user "你的微信号"
```

### 方式 B：使用环境变量（同样不会落盘）

```bash
export WECHAT_PREVIEW_TOUSER="你的微信号"
python3 wechat_publisher/publish_wechat_draft.py preview --env-file .env
```

默认会使用 `state.json` 中记录的最新 `last_draft_media_id`。

---

## 6. 正式发表（publish）

```bash
python3 wechat_publisher/publish_wechat_draft.py publish --env-file .env
```

- 默认会阻塞询问确认
- 默认会轮询 `freepublish/get` 等待发布结果

如需跳过确认：

```bash
python3 wechat_publisher/publish_wechat_draft.py publish --env-file .env --yes
```

---

## 7. 一键流程（run）

```bash
python3 wechat_publisher/publish_wechat_draft.py run \
  --env-file .env \
  --markdown AI_Builders_Digest_ZH_2026-04-21.md \
  --title "AI Builders Digest | 2026-04-21" \
  --author "陈凤" \
  --preview \
  --to-user "你的微信号"
```

> 注意：`--to-user` 仅在内存中使用，不会写入任何文件。
