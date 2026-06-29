---
title: "每日 AI 学习笔记｜Day 75：语音 Agent 实时延迟预算与卡顿定位测试"
date: 2026-06-29
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, latency, streaming, e2e-testing]
---

# 每日 AI 学习笔记｜Day 75：语音 Agent 实时延迟预算与卡顿定位测试

## 核心总结

昨天把语音 Agent 的打断与轮次状态机拆成了可验证事件，今天继续向线上体验最敏感的维度收敛：**实时延迟预算与卡顿定位**。语音产品是否“聪明”，用户往往要等交互结束才会感知；但是否“顺滑”，用户在 300ms 到 2s 内就会直接做出判断。测试开发不能只看总耗时，而要把一次语音轮次拆成 `vad_start → asr_final → llm_first_token → tts_first_chunk → audio_first_play` 的阶段预算，定位究竟卡在采集、识别、推理、合成还是前端播放。

本文给出一套面向 Golang Ginkgo、Python Playwright、K8s 与 API Testing 的端到端实践：从“用户发起语音问天气，要求 2 秒内听到首段回复”的真实场景出发，把单点性能验证下沉到业务链路中的阶段断言、超时告警与 trace 归因，最终用用户可感知的首包时延、尾延迟和卡顿率共同判定质量。

{/* truncate */}

## 1. 为什么语音 Agent 的延迟测试不能只看总耗时

文本 Agent 常见指标是接口 RT、首 token 时间、完成时间；语音 Agent 则多了音频采集、VAD、ASR、流式推理、TTS 分块合成和客户端播放队列。用户听到“第一句话”之前，任何一个阶段卡住，体验都会直接断层。

一个典型线上事故是：服务端日志显示整轮请求只用了 2.8 秒，看起来还不错；但用户实际 4 秒后才听到第一句回复。复盘后才发现，ASR final 很快返回，LLM 首 token 也正常，但 TTS 首 chunk 被前端播放器缓冲策略额外拖了 1.2 秒。只盯总耗时，会把真正的问题埋掉。

对测试开发来说，更有价值的不是“这轮 2.8 秒”，而是下面这组分段预算：

1. **输入感知延迟：** 用户开口后，多快进入有效识别。
2. **理解规划延迟：** ASR final 到 LLM first token 是否稳定。
3. **出声准备延迟：** LLM first token 到 TTS first chunk 是否可控。
4. **用户可听见延迟：** TTS first chunk 到 audio first play 是否足够短。
5. **尾部完成延迟：** 整段回复播放完成后，是否留下长尾卡顿。

## 2. 建立延迟预算：把体验目标翻译成阶段 SLO

延迟预算要先从用户体验目标出发，再映射到系统事件。下面是一份适合语音问答场景的基础口径：

<table header-row="true" col-widths="180,220,220,260">
  <tr>
    <td>阶段</td>
    <td>起止事件</td>
    <td>建议预算</td>
    <td>测试关注点</td>
  </tr>
  <tr>
    <td>感知延迟</td>
    <td>`vad_speech_started` → `asr_first_partial`</td>
    <td>P95 ≤ 200ms</td>
    <td>麦克风采样、VAD 门限、噪声环境</td>
  </tr>
  <tr>
    <td>识别收敛延迟</td>
    <td>`asr_first_partial` → `asr_final`</td>
    <td>P95 ≤ 800ms</td>
    <td>音频长度、口音、停顿、ASR 服务波动</td>
  </tr>
  <tr>
    <td>推理首包延迟</td>
    <td>`asr_final` → `llm_first_token`</td>
    <td>P95 ≤ 700ms</td>
    <td>Prompt 长度、检索、工具规划</td>
  </tr>
  <tr>
    <td>合成首包延迟</td>
    <td>`llm_first_token` → `tts_first_chunk`</td>
    <td>P95 ≤ 400ms</td>
    <td>TTS 模型、分块策略、网络抖动</td>
  </tr>
  <tr>
    <td>首播延迟</td>
    <td>`tts_first_chunk` → `audio_first_play`</td>
    <td>P95 ≤ 250ms</td>
    <td>前端缓冲、播放器队列、解码策略</td>
  </tr>
  <tr>
    <td>用户首响时间</td>
    <td>`vad_speech_started` → `audio_first_play`</td>
    <td>P95 ≤ 2.0s</td>
    <td>用户真实感知，是否“开口就能接话”</td>
  </tr>
</table>

这张表的价值在于：一旦首响超时，你能立刻落到某个阶段，而不是在十几个服务日志里盲查。预算也不应该一刀切。问答、导航、下单、语音陪练的容忍区间都不同，但阶段拆分方法是一致的。

## 3. E2E 场景设计：用户语音问天气，要求 2 秒内听到首句回复

测试用例要覆盖完整用户旅程，而不是单独压测某个 ASR 或 TTS 接口。下面是一个可以直接落地的端到端场景。

### 场景：通勤路上语音问天气

**用户目标：** 用户在移动端点击语音按钮，说出“今天北京会下雨吗？需要带伞吗？”，期望 2 秒内听到 Agent 的首句回答，并在 6 秒内听完完整建议。

**输入资产：**

- `fixtures/audio/weather_beijing_need_umbrella.wav`：包含用户完整提问。
- `fixtures/api/weather_mock_beijing.json`：天气服务测试桩，固定返回降雨概率与温度。
- `fixtures/expected/latency_budget.json`：阶段预算阈值定义。

**执行步骤与预期中间状态：**

1. 用户打开语音入口并说出天气问题。
   - 预期：产生 `session_id` 与 `turn_id=turn-1`，出现 `vad_speech_started` 与 `asr_first_partial`。
2. ASR 完成识别，系统开始规划回答。
   - 预期：`asr_final` 文本包含“北京”“带伞”，且 `asr_final - vad_speech_started` 在预算内。
3. Agent 查询天气服务并启动流式推理。
   - 预期：出现 `tool_started(service=weather)`、`tool_result` 与 `llm_first_token`，中途无超过 500ms 的空窗。
4. TTS 开始分块合成，客户端准备播放。
   - 预期：出现 `tts_first_chunk`，播放器收到首个可播放 chunk。
5. 用户听到首句答复，例如“北京今天有降雨概率，建议带伞”。
   - ✅ 最终验证点：`audio_first_play - vad_speech_started <= 2000ms`；完整播放完成前无卡死、无明显停顿；trace 能归因每个阶段耗时；用户最终看到与听到的天气建议一致。

这个场景把体验指标直接绑到用户动作上。单点性能指标依然存在，但它们被放进一条完整链路里，只有对用户真实可感知结果负责，指标才有意义。

## 4. 工程实践：Ginkgo 断言阶段预算而不是单一 RT

下面的 Go 示例演示如何把事件时间戳拉平后做阶段预算断言。重点不是压出一个平均值，而是验证一次真实请求在预算内完成，并能明确指出卡住的阶段。

```go
package voicelatency_test

import (
    "encoding/json"
    "net/http"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type Event struct {
    Type      string `json:"type"`
    Timestamp int64  `json:"timestamp_ms"`
    Payload   map[string]string `json:"payload"`
}

func fetchEvents(baseURL, sessionID string) []Event {
    resp, err := http.Get(baseURL + "/v1/voice/sessions/" + sessionID + "/events")
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var events []Event
    Expect(json.NewDecoder(resp.Body).Decode(&events)).To(Succeed())
    return events
}

func ts(events []Event, eventType string) int64 {
    for _, e := range events {
        if e.Type == eventType {
            return e.Timestamp
        }
    }
    Fail("missing event: " + eventType)
    return 0
}

var _ = Describe("Voice Agent latency budget E2E", func() {
    It("keeps first-audio latency within 2 seconds for weather query", func() {
        baseURL := "http://voice-agent-e2e.default.svc.cluster.local"
        sessionID := startVoiceReplay(baseURL, "fixtures/audio/weather_beijing_need_umbrella.wav")

        Eventually(func() []Event {
            return fetchEvents(baseURL, sessionID)
        }, 15*time.Second, 200*time.Millisecond).ShouldNot(BeEmpty())

        events := fetchEvents(baseURL, sessionID)

        vadStart := ts(events, "vad_speech_started")
        asrFinal := ts(events, "asr_final")
        llmFirst := ts(events, "llm_first_token")
        ttsFirst := ts(events, "tts_first_chunk")
        audioFirst := ts(events, "audio_first_play")
        audioDone := ts(events, "audio_play_completed")

        Expect(asrFinal - vadStart).To(BeNumerically("<=", 1000))
        Expect(llmFirst - asrFinal).To(BeNumerically("<=", 700))
        Expect(ttsFirst - llmFirst).To(BeNumerically("<=", 400))
        Expect(audioFirst - ttsFirst).To(BeNumerically("<=", 250))
        Expect(audioFirst - vadStart).To(BeNumerically("<=", 2000))
        Expect(audioDone - audioFirst).To(BeNumerically("<=", 4000))
    })
})
```

这段代码的重点有两个：第一，预算按阶段拆开后，失败时能直接报出瓶颈位置；第二，`audio_first_play` 必须来自客户端或播放网关的真实事件，不能拿服务端 `tts_started` 代替，否则只是在验证“系统以为自己开始说话了”。

## 5. Playwright：从用户听感验证首响与卡顿

服务端时间线正常，不代表用户真的听到了。浏览器或移动端 WebView 还需要验证播放器是否及时开播、字幕是否同步、播放中是否出现冻结。

```python
from pathlib import Path
from playwright.sync_api import expect


def test_voice_agent_first_audio_latency(page):
    page.goto("/voice-agent")
    page.get_by_role("button", name="开始语音").click()
    page.set_input_files("input[type=file]", Path("fixtures/audio/weather_beijing_need_umbrella.wav"))

    expect(page.locator('[data-testid="agent-state"]')).to_have_text("正在识别")
    expect(page.locator('[data-testid="agent-state"]')).to_have_text("正在回答")

    expect(page.locator('[data-testid="audio-player"]')).to_have_attribute("data-first-play-within-slo", "true")
    expect(page.locator('[data-testid="caption"]')).to_contain_text("建议带伞")
    expect(page.locator('[data-testid="audio-player"]')).to_have_attribute("data-stutter-count", "0")
    expect(page.locator('[data-testid="final-answer"]')).to_contain_text("北京")
```

前端侧不要用“我觉得这次听起来还可以”代替验证。更稳妥的做法是把首播时间、缓冲次数、最长停顿、字幕首显时间做成测试埋点，直接暴露给自动化脚本读取。

## 6. K8s 与 API Testing：用 trace 把卡顿定位到具体服务

线上排查最难的地方不是看到慢，而是知道慢在哪里。K8s 环境里建议把一次会话需要的关键标签统一注入到所有服务日志与 trace span 中：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voice-e2e-latency-budget
  namespace: voice-agent-e2e
data:
  required_labels: "session_id,turn_id,stage,scenario"
  first_audio_slo_ms: "2000"
  max_stutter_count: "0"
  trace_required_spans: "vad,asr,llm,tts,player"
```

API 层可以补一条分段耗时检查，把每个阶段时间显式拉出来：

```bash
curl -s "$BASE_URL/v1/voice/sessions/$SESSION_ID/latency-breakdown" | jq '{
  first_audio_ms,
  vad_to_asr_final_ms,
  asr_final_to_llm_first_token_ms,
  llm_first_token_to_tts_first_chunk_ms,
  tts_first_chunk_to_audio_first_play_ms,
  stutter_count
}'
```

如果 `first_audio_ms` 超标，不要直接把锅甩给模型。真实线上常见原因包括：ASR final 等待过长、检索工具超时、TTS chunk 太大、播放器为避免爆音而额外预缓冲，以及 CDN 回源抖动。测试环境必须能把这些跨度归因出来。

## 7. 常见缺陷与排查线索

<table header-row="true" col-widths="180,240,240,240">
  <tr>
    <td>缺陷</td>
    <td>用户表现</td>
    <td>trace 线索</td>
    <td>修复方向</td>
  </tr>
  <tr>
    <td>ASR final 迟迟不出</td>
    <td>用户说完后长时间静默</td>
    <td>`asr_first_partial` 正常，但 `asr_final` 晚</td>
    <td>优化终止判定、缩短静音收敛时间</td>
  </tr>
  <tr>
    <td>LLM 首 token 慢</td>
    <td>字幕迟迟不出现</td>
    <td>`tool_result` 后到 `llm_first_token` 空窗过大</td>
    <td>缩短 prompt、缓存检索结果、减少同步工具</td>
  </tr>
  <tr>
    <td>TTS 首 chunk 大</td>
    <td>服务端已回答，用户仍没听到</td>
    <td>`llm_first_token` 很快，但 `tts_first_chunk` 晚</td>
    <td>缩小 chunk、开启流式合成</td>
  </tr>
  <tr>
    <td>前端预缓冲过度</td>
    <td>字幕先出，声音后到</td>
    <td>`tts_first_chunk` 到 `audio_first_play` 明显拉长</td>
    <td>调整播放器队列与解码策略</td>
  </tr>
  <tr>
    <td>播放中途卡顿</td>
    <td>回答断断续续</td>
    <td>`audio_buffering_started` 重复出现</td>
    <td>检查 chunk 生成节奏、网络抖动与 CDN</td>
  </tr>
</table>

这些缺陷最容易在“平均耗时看起来还不错”的时候漏掉。语音质量真正危险的是尾部波动：平均值过关，但 P95、P99 让真实用户频繁感知到停顿。

## 8. 课后思考题

1. 如果同一轮请求的首响时间满足 2 秒，但完整播放时间经常超过 8 秒，这应该算通过还是失败？你会如何设置双层门槛？
2. 在需要先调用天气、地图、知识库三个工具的语音 Agent 中，阶段预算应该如何拆到单工具与聚合链路？
3. 如果服务端 trace 显示 `tts_first_chunk` 很早，但客户端 `audio_first_play` 依然超时，前端还需要补哪些埋点才能继续定位？
4. 当网络较差时，应该优先保证“尽快开口但可能音质一般”，还是“更平滑但更晚出声”？你的产品线会怎么取舍？
5. 如何构造一组可回放音频夹具，同时覆盖安静环境、地铁噪声、蓝牙耳机抖动和弱网场景？

## 今日小结

Day 75 的重点不是再做一次泛化性能测试，而是把语音 Agent 的“顺滑感”拆成可验证、可归因、可设门禁的阶段预算。真正对线上最有价值的，不是知道这轮请求慢了，而是知道它慢在识别、推理、合成还是播放。

对资深测试开发来说，语音性能测试的交付物不该只是一张平均 RT 报表，而应是一套用户体验口径明确的 E2E 质量基线：首响有预算、卡顿有计数、尾延迟有上限、trace 能定位瓶颈。只有这样，语音 Agent 才能从“偶尔能用”走到“用户愿意持续使用”。