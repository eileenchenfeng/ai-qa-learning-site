---
title: "每日 AI 学习笔记｜Day 73：语音 Agent 与实时音频链路质量验证"
date: 2026-06-27
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, audio-testing, e2e-testing, observability]
---

# 每日 AI 学习笔记｜Day 73：语音 Agent 与实时音频链路质量验证

## 核心总结

今天把多模态测试继续推进到**语音 Agent** 场景：质量验证不能只看 ASR、LLM 或 TTS 的单点准确率，而要按用户真实通话链路做端到端评估。一个可上线的语音 Agent 至少要同时满足四类约束：听得准、答得对、说得自然、异常时能安全降级。测试开发要把音频采集、实时转写、工具调用、回复生成、语音合成、打断处理、链路追踪和回放复现串成一条可观测流水线。

本文给出一套面向 Golang Ginkgo、Python Playwright、K8s 与 API Testing 的实践框架：用 E2E 场景承载单点验证，把中间状态沉淀为 trace、事件流和质量指标，避免只在接口层证明“服务返回了 200”。

{/* truncate */}

## 1. 为什么语音 Agent 测试更容易漏问题

文本 Agent 的输入输出天然可记录，失败时可以直接对 prompt、tool call、response 做 diff。语音 Agent 多了音频采样、编码、VAD、ASR、流式生成、TTS、播放端延迟等环节，同一句话在不同麦克风、噪声、口音和网络抖动下会产生不同事件序列。

对测试开发来说，真正的风险不是某个模型指标少了 1%，而是用户听到的体验断裂：Agent 抢话、漏听、误触发工具、把失败原因读给用户、或者在高延迟下连续重复同一句回复。

语音 Agent 的端到端链路可以拆成下面这些可观测节点：

1. **采集与传输：** 浏览器、App 或设备端采集音频，编码为 PCM、Opus 或 WebRTC track。
2. **端点检测：** VAD 判断用户是否开始或结束说话，影响打断、超时和轮次边界。
3. **语音识别：** ASR 输出 partial transcript 与 final transcript。
4. **意图理解：** LLM 将 transcript 转成任务意图，并决定是否调用工具。
5. **工具执行：** API、数据库、工单或搜索服务返回结构化结果。
6. **回复生成：** LLM 生成面向用户的自然语言回复。
7. **语音合成：** TTS 输出音频流，控制音色、语速、停顿和情绪。
8. **播放与交互：** 客户端播放音频，并支持用户中途打断。

测试用例不应写成“验证 ASR 接口可用”“验证 TTS 接口可用”，而应写成“用户在嘈杂环境下查询订单并中途纠正信息，Agent 能正确更新上下文并给出可听懂的结果”。单点验证下沉到每个步骤的中间预期里。

## 2. 质量模型：从离线准确率到在线体验 SLO

语音 Agent 的质量指标要同时覆盖内容正确性和实时体验。下面这组指标适合作为第一版质量看板：

| 质量维度 | 指标 | 推荐观测方式 | 失败信号 |
|---|---|---|---|
| 听得准 | WER、关键词召回、final transcript 稳定性 | 离线音频集回放 + 在线抽样复核 | 关键槽位识别错，如订单号、金额、日期 |
| 答得对 | 任务成功率、工具调用正确率、事实一致性 | E2E 场景断言 + LLM judge 辅助复核 | 调错工具、漏掉权限判断、编造结果 |
| 说得顺 | 首包音频延迟、完整回复时长、重复率 | trace span + 客户端播放事件 | 用户等待过久、TTS 重复、语音截断 |
| 可交互 | barge-in 成功率、轮次恢复率 | 注入打断音频 + 检查状态机 | 用户打断后 Agent 仍继续说话 |
| 可恢复 | ASR/TTS/API 故障降级率 | Chaos 注入 + 端到端断言 | 把内部错误读给用户，或会话卡死 |

其中最容易被忽略的是**轮次边界**。用户一句话还没说完时，ASR partial 可能已经触发了 LLM；用户又补充一句“不是北京，是上海”时，Agent 必须能撤销或修正前一轮意图。测试时需要把 partial、final、turn_id、tool_call_id 全部写入 trace，否则事故复盘只会看到一段最终回复，无法判断错在听、想、查还是说。

## 3. E2E 场景设计：把真实通话变成可回放资产

一个高价值语音测试场景应该包含完整业务链路、环境扰动和可验证结果。下面是可直接落地的场景模板。

### 场景：用户在地铁噪声中修改酒店预订

**用户目标：** 用户通过语音 Agent 查询酒店订单，并把入住日期从 7 月 1 日改到 7 月 3 日。

**输入资产：**
- `fixtures/audio/hotel_change_noisy.wav`：包含地铁背景噪声、停顿和纠正表达。
- `fixtures/orders/order_10086.json`：测试订单，允许改期。
- `fixtures/expected/hotel_change_trace.json`：期望事件骨架，不要求逐字匹配自然语言。

**执行步骤与预期中间状态：**

1. 用户打开语音入口并开始说话。
   - 预期：客户端产生 `session_started`，服务端创建 `trace_id` 与 `turn_id=1`。
2. 播放带噪声音频：“帮我查一下订单 10086，想把入住日期从 7 月 1 改到 7 月 3。”
   - 预期：ASR final transcript 保留订单号、原日期、新日期三个关键槽位。
3. Agent 调用订单查询 API。
   - 预期：tool name 为 `get_order`，参数 `order_id=10086`，不得调用改期接口。
4. Agent 确认订单可修改后调用改期 API。
   - 预期：tool name 为 `update_booking_date`，参数包含 `check_in_date=2026-07-03`。
5. TTS 播放结果。
   - ✅ 最终验证点：用户听到“已改到 7 月 3 日”含义一致的回复；订单状态更新成功；trace 中无未处理异常；首包音频延迟低于 1500 ms。

这类用例的重点不是文本逐字一致，而是关键事实、工具调用和用户可感知结果一致。对 TTS 文案可以使用语义匹配，对订单状态使用强断言。

## 4. 工程实践：Ginkgo 端到端 API 回放

下面的示例用 Go + Ginkgo 调用语音 Agent 的测试服务。测试把音频文件上传到 `/v1/voice/sessions`，轮询事件流，最后断言 ASR、工具调用、订单状态和延迟指标。

```go
package voicee2e_test

import (
    "bytes"
    "encoding/json"
    "io"
    "mime/multipart"
    "net/http"
    "os"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type VoiceEvent struct {
    Type      string                 `json:"type"`
    TraceID   string                 `json:"trace_id"`
    TurnID    string                 `json:"turn_id"`
    Payload   map[string]interface{} `json:"payload"`
    Timestamp int64                  `json:"timestamp_ms"`
}

func uploadAudio(baseURL, path string) string {
    body := &bytes.Buffer{}
    writer := multipart.NewWriter(body)

    file, err := os.Open(path)
    Expect(err).NotTo(HaveOccurred())
    defer file.Close()

    part, err := writer.CreateFormFile("audio", "hotel_change_noisy.wav")
    Expect(err).NotTo(HaveOccurred())
    _, err = io.Copy(part, file)
    Expect(err).NotTo(HaveOccurred())

    _ = writer.WriteField("scenario", "hotel_change_noisy")
    Expect(writer.Close()).To(Succeed())

    req, err := http.NewRequest("POST", baseURL+"/v1/voice/sessions", body)
    Expect(err).NotTo(HaveOccurred())
    req.Header.Set("Content-Type", writer.FormDataContentType())

    resp, err := http.DefaultClient.Do(req)
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusAccepted))

    var out struct { SessionID string `json:"session_id"` }
    Expect(json.NewDecoder(resp.Body).Decode(&out)).To(Succeed())
    return out.SessionID
}

func fetchEvents(baseURL, sessionID string) []VoiceEvent {
    Eventually(func(g Gomega) []VoiceEvent {
        resp, err := http.Get(baseURL + "/v1/voice/sessions/" + sessionID + "/events")
        g.Expect(err).NotTo(HaveOccurred())
        defer resp.Body.Close()
        g.Expect(resp.StatusCode).To(Equal(http.StatusOK))

        var events []VoiceEvent
        g.Expect(json.NewDecoder(resp.Body).Decode(&events)).To(Succeed())
        return events
    }, 20*time.Second, 500*time.Millisecond).Should(ContainElement(
        WithTransform(func(e VoiceEvent) string { return e.Type }, Equal("tts.completed")),
    ))

    resp, err := http.Get(baseURL + "/v1/voice/sessions/" + sessionID + "/events")
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()

    var events []VoiceEvent
    Expect(json.NewDecoder(resp.Body).Decode(&events)).To(Succeed())
    return events
}

var _ = Describe("Voice Agent E2E", Ordered, func() {
    const baseURL = "http://localhost:8080"

    It("用户在噪声环境中修改酒店预订，Agent 能完成识别、查单、改期和语音确认", func() {
        sessionID := uploadAudio(baseURL, "fixtures/audio/hotel_change_noisy.wav")
        events := fetchEvents(baseURL, sessionID)

        By("验证 ASR final transcript 保留关键槽位")
        Expect(events).To(ContainElement(SatisfyAll(
            WithTransform(func(e VoiceEvent) string { return e.Type }, Equal("asr.final")),
            WithTransform(func(e VoiceEvent) map[string]interface{} { return e.Payload }, SatisfyAll(
                HaveKeyWithValue("order_id", "10086"),
                HaveKeyWithValue("new_check_in_date", "2026-07-03"),
            )),
        )))

        By("验证工具调用顺序：先查单，再改期")
        var tools []string
        for _, e := range events {
            if e.Type == "tool.called" {
                tools = append(tools, e.Payload["name"].(string))
            }
        }
        Expect(tools).To(Equal([]string{"get_order", "update_booking_date"}))

        By("验证 TTS 首包延迟")
        var firstAudioLatency float64
        for _, e := range events {
            if e.Type == "tts.first_audio" {
                firstAudioLatency = e.Payload["latency_ms"].(float64)
                break
            }
        }
        Expect(firstAudioLatency).To(BeNumerically("<", 1500))
    })
})
```

这段代码的关键点是：它没有把 ASR、工具调用和 TTS 拆成三个孤立用例，而是在一个真实业务场景里验证每个中间状态。这样失败时可以直接从 trace 定位链路断点。

## 5. 工程实践：Playwright 验证浏览器语音入口

浏览器端测试需要关注权限、录音状态、播放状态和用户打断。Playwright 可以通过 mock `getUserMedia` 和 WebSocket 事件模拟音频输入。下面示例验证“用户中途打断 Agent 回复后，服务端取消上一轮 TTS 并进入新一轮识别”。

```python
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, expect

AUDIO_FIXTURE = Path("fixtures/audio/user_barge_in.wav")

async def test_voice_barge_in_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            permissions=["microphone"],
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        await page.add_init_script("""
        window.__voiceTestEvents = [];
        const originalWebSocket = window.WebSocket;
        window.WebSocket = function(url) {
          const ws = new originalWebSocket(url);
          ws.addEventListener('message', event => {
            try { window.__voiceTestEvents.push(JSON.parse(event.data)); } catch(e) {}
          });
          return ws;
        };
        """)

        await page.goto("http://localhost:3000/voice-agent")
        await page.get_by_role("button", name="开始语音").click()
        await expect(page.get_by_text("正在聆听")).to_be_visible()

        # 测试环境通常由前端测试开关读取该 fixture，再推送到 mock audio worklet。
        await page.evaluate("""
        async ({ audioPath }) => {
          await window.voiceTestKit.playFixture(audioPath);
        }
        """, {"audioPath": str(AUDIO_FIXTURE)})

        await expect(page.get_by_text("正在回复")).to_be_visible(timeout=10000)
        await page.get_by_role("button", name="打断").click()
        await expect(page.get_by_text("正在聆听")).to_be_visible(timeout=5000)

        events = await page.evaluate("window.__voiceTestEvents")
        event_types = [e["type"] for e in events]

        assert "tts.cancelled" in event_types
        assert "turn.started" in event_types
        assert event_types.index("tts.cancelled") < event_types[-1:].index("turn.started") if event_types[-1:] == ["turn.started"] else True

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_voice_barge_in_flow())
```

实际项目里建议把 `voiceTestKit` 做成前端测试专用注入层，支持播放本地 fixture、模拟麦克风权限拒绝、插入网络抖动、记录播放器状态。这样 UI 自动化不需要依赖真实麦克风，也不会因为机器环境不同导致录音不稳定。

## 6. K8s 与可观测性：让每个语音轮次可复盘

语音 Agent 的 K8s 部署通常至少包含 ASR gateway、LLM orchestrator、tool service、TTS service 和 session store。测试环境要打开统一 trace，并把同一个 `trace_id` 贯穿 WebSocket、HTTP API、消息队列和工具调用。

建议在每个轮次记录这些 span：

```yaml
trace_schema:
  trace_id: required
  session_id: required
  turn_id: required
  spans:
    - name: client.audio.capture
      attrs: [codec, sample_rate, duration_ms]
    - name: asr.streaming
      attrs: [partial_count, final_transcript, keyword_slots, latency_ms]
    - name: llm.intent.plan
      attrs: [model, prompt_version, tool_plan, token_usage]
    - name: tool.invoke
      attrs: [tool_name, status_code, retry_count, latency_ms]
    - name: tts.synthesis
      attrs: [voice, first_audio_latency_ms, total_audio_ms]
    - name: client.playback
      attrs: [started_at, interrupted, underrun_count]
```

K8s 层可以为语音链路设计几类故障注入：

- ASR pod 增加 300 ms 延迟，验证首包回复是否超过 SLO。
- TTS 返回 5xx，验证 Agent 是否切到文本兜底或提示稍后重试。
- tool service 超时，验证不会把内部错误栈读给用户。
- WebSocket 中断重连，验证 session 是否能恢复到正确 turn。

这类演练要落在端到端场景里。例如“用户查询订单时 TTS 故障”，最终验证点应该是用户看到可理解的文本兜底、订单查询没有重复执行、trace 标记 `tts.failed` 与 `fallback.text_shown`，而不是单独证明 TTS mock 返回了 500。

## 7. API Testing：事件契约比最终文案更稳定

语音 Agent 的最终回复存在自然语言波动，直接断言整句文案会让测试脆弱。更稳定的方式是断言事件契约。

推荐的事件流契约如下：

```json
{
  "session_id": "s_123",
  "trace_id": "t_456",
  "events": [
    {"type": "session.started", "turn_id": "1"},
    {"type": "asr.partial", "turn_id": "1"},
    {"type": "asr.final", "turn_id": "1", "payload": {"slots": {"order_id": "10086"}}},
    {"type": "tool.called", "turn_id": "1", "payload": {"name": "get_order"}},
    {"type": "tool.completed", "turn_id": "1", "payload": {"status": "success"}},
    {"type": "tts.first_audio", "turn_id": "1", "payload": {"latency_ms": 1280}},
    {"type": "tts.completed", "turn_id": "1"}
  ]
}
```

断言策略可以分三层：

1. **强断言：** 关键槽位、工具名称、权限结果、数据库最终状态。
2. **范围断言：** 首包延迟、总耗时、重试次数、音频时长。
3. **语义断言：** 用户可见回复是否表达正确事实，不要求逐字一致。

这能让测试既稳定又贴近用户体验。

## 8. 课后思考题

1. 如果 ASR final transcript 正确，但 Agent 调用了错误工具，你会从 trace 中优先检查哪些字段？
2. barge-in 测试中，如何证明上一轮 TTS 已被真正取消，而不是客户端静音但服务端仍在生成？
3. 对同一段音频，ASR partial 每次略有不同。哪些断言应该放宽，哪些断言必须保持强约束？
4. 如果用户说“下周三”，测试环境应如何固定时间基准，避免日期槽位不稳定？
5. 当 TTS 故障时，语音 Agent 应该如何降级，才能既不欺骗用户，也不泄露内部错误？

## 9. 今日小结

Day 73 的重点是把语音 Agent 的质量验证从“模型接口可用”升级为“用户通话链路可信”。端到端场景需要覆盖音频输入、ASR、LLM、工具调用、TTS、播放和打断，单点指标则沉淀在每个步骤的中间状态与 trace 中。

对资深测试开发而言，下一步可以把语音 fixture、事件契约、trace schema 和 K8s 故障注入统一进 CI。这样每次模型、prompt、工具或基础设施变更，都能用同一批真实场景回放，判断用户是否仍然听得准、问得通、改得成。