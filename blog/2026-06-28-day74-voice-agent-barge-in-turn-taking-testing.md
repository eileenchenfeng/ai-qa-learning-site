---
title: "每日 AI 学习笔记｜Day 74：语音 Agent 打断与轮次状态机测试"
date: 2026-06-28
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, barge-in, state-machine, e2e-testing]
---

# 每日 AI 学习笔记｜Day 74：语音 Agent 打断与轮次状态机测试

## 核心总结

昨天验证了语音 Agent 的实时音频链路，今天继续收窄到更容易出线上事故的**打断与轮次状态机**。语音交互不是“用户说完一句，Agent 回一句”的理想队列，而是用户会中途纠正、插话、沉默、重复、突然切换意图；系统也会同时存在 ASR partial、LLM streaming、tool call、TTS playback 和客户端播放事件。测试开发要把这些并发事件统一到 `session_id / turn_id / utterance_id / response_id` 上，验证状态迁移是否可解释、可回放、可恢复。

本文给出一套面向 Golang Ginkgo、Python Playwright、K8s 与 API Testing 的端到端实践：从真实用户打断场景出发，把单点能力验证下沉到每一步的中间状态，最终以用户可感知结果、业务状态和 trace 事件共同判定通过。

{/* truncate */}

## 1. 为什么打断测试比普通语音识别更难

普通语音识别测试关注“这段音频最终转成了什么文本”。打断测试关注的是“当用户在 Agent 说话时又开口，系统是否立刻停止播放、取消过期推理、保留必要上下文，并把新意图接到正确轮次”。这里的问题不只在 ASR，也不只在 TTS，而在多条异步流水线的状态一致性。

一个典型失败链路是：用户说“帮我订明天去上海的票”，Agent 开始确认；用户马上打断“不是上海，是杭州”。如果系统只把第二句话当成新任务，可能会生成两个订单；如果只停止 TTS 但没有取消旧 tool call，后台仍可能提交上海订单；如果取消了工具但没有记录原因，事故复盘时只能看到“用户取消”，无法知道是主动取消还是系统误杀。

端到端质量目标可以压缩成四句话：

1. **听见打断：** 客户端和服务端都能识别用户重新开口。
2. **停住旧输出：** TTS 与播放端停止过期回复，不再继续播报旧答案。
3. **收敛新轮次：** LLM、工具调用和业务状态绑定到新的 `turn_id`。
4. **留下证据：** trace 能解释每次取消、覆盖、恢复和最终提交。

## 2. 状态机建模：把“正在说话”变成可断言事件

打断问题适合用状态机描述，因为它天然包含并发、取消和恢复。测试时不建议只断言最终文案，而要断言关键状态迁移。

推荐的最小状态集合如下：

| 状态 | 含义 | 进入条件 | 必须观测到的事件 |
|---|---|---|---|
| `LISTENING` | 等待用户输入 | 会话开始或上一轮结束 | `mic_opened`、`vad_ready` |
| `USER_SPEAKING` | 用户正在说话 | VAD 检测到语音 | `speech_started`、ASR partial |
| `THINKING` | Agent 正在理解和规划 | ASR final 生成 | `turn_finalized`、`llm_started` |
| `CALLING_TOOL` | 正在访问外部工具 | LLM 产生 tool call | `tool_started`、`tool_result` |
| `AGENT_SPEAKING` | TTS 或客户端正在播放 | 回复开始合成或播放 | `tts_started`、`audio_playing` |
| `INTERRUPTED` | 旧回复被用户打断 | Agent 播放期间检测到用户语音 | `barge_in_detected`、`tts_cancelled` |
| `RECOVERING` | 系统把新语音接入新轮次 | 打断后产生新 ASR final | 新 `turn_id`、旧 `response_id` 终止 |
| `COMPLETED` | 当前任务稳定完成 | 用户确认或业务提交成功 | `business_committed`、`session_idle` |

这张表的价值不在于状态名字，而在于每个状态都能落到事件日志。没有事件，就无法写稳定的 E2E 断言；没有 `turn_id`，就无法区分旧回复和新意图。

## 3. E2E 场景设计：用户中途纠正目的地

测试用例必须覆盖完整业务链路，而不是孤立验证“打断接口返回成功”。下面是一个可以直接落地的场景。

### 场景：用户预订行程时中途纠正目的地

**用户目标：** 用户通过语音 Agent 查询并预订明天上午的出行方案，先说目的地为上海，在 Agent 复述时打断并改成杭州。

**输入资产：**

- `fixtures/audio/book_trip_shanghai_then_hangzhou.wav`：包含用户第一句话、Agent 播放窗口内的打断语音、短暂停顿。
- `fixtures/api/trip_inventory.json`：测试库存数据，上海和杭州均有可用方案。
- `fixtures/expected/barge_in_trace.json`：期望事件骨架，只固定关键字段，不要求自然语言逐字一致。

**执行步骤与预期中间状态：**

1. 用户打开语音入口并开始说“帮我订明天上午去上海的票”。
   - 预期：服务端创建 `session_id`，第一轮 `turn_id=turn-1`，ASR final 包含“上海”。
2. Agent 查询上海方案并开始播报“找到明天上午去上海的方案……”。
   - 预期：出现 `tool_started(destination=上海)`、`tool_result`、`response_id=resp-1`、`audio_playing`。
3. 用户在播报期间打断：“不是上海，是杭州”。
   - 预期：出现 `barge_in_detected`，`resp-1` 被标记为 `cancelled_by_user_speech`，客户端停止播放旧音频。
4. 系统进入新轮次并解析“杭州”。
   - 预期：生成 `turn_id=turn-2`，ASR final 包含“杭州”，旧的上海提交链路不得继续执行。
5. Agent 查询杭州方案并等待用户确认。
   - 预期：`tool_started(destination=杭州)`，没有 `business_committed(destination=上海)`。
6. 用户确认后完成预订。
   - ✅ 最终验证点：业务状态只存在杭州订单；用户听到的最终回复语义包含“杭州”；trace 中旧响应已取消、新轮次已完成、无悬挂 tool call。

这个用例把 VAD、ASR、LLM、工具调用、TTS、播放器和业务提交都放进同一条链路。单点能力仍然被验证，但它们不再单独成案，而是成为用户旅程里的中间断言。

## 4. 工程实践：Ginkgo 断言打断状态机

下面的 Go 示例把事件流作为一等公民。测试不会只检查 HTTP 200，而是等待关键事件出现，并验证旧响应被取消、新轮次完成。

```go
package voicebargein_test

import (
    "encoding/json"
    "net/http"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type Event struct {
    Type       string            `json:"type"`
    SessionID  string            `json:"session_id"`
    TurnID     string            `json:"turn_id"`
    ResponseID string            `json:"response_id"`
    Payload    map[string]string `json:"payload"`
}

func getEvents(baseURL, sessionID string) []Event {
    resp, err := http.Get(baseURL + "/v1/voice/sessions/" + sessionID + "/events")
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var events []Event
    Expect(json.NewDecoder(resp.Body).Decode(&events)).To(Succeed())
    return events
}

func eventuallyHas(events func() []Event, match func(Event) bool) {
    Eventually(func() bool {
        for _, e := range events() {
            if match(e) {
                return true
            }
        }
        return false
    }, 10*time.Second, 200*time.Millisecond).Should(BeTrue())
}

var _ = Describe("Voice Agent barge-in E2E", func() {
    It("cancels the stale Shanghai response and completes the Hangzhou booking", func() {
        baseURL := "http://voice-agent-e2e.default.svc.cluster.local"
        sessionID := startVoiceReplay(baseURL, "fixtures/audio/book_trip_shanghai_then_hangzhou.wav")
        events := func() []Event { return getEvents(baseURL, sessionID) }

        eventuallyHas(events, func(e Event) bool {
            return e.Type == "tool_started" && e.TurnID == "turn-1" && e.Payload["destination"] == "上海"
        })

        eventuallyHas(events, func(e Event) bool {
            return e.Type == "barge_in_detected" && e.Payload["interrupted_response_id"] == "resp-1"
        })

        eventuallyHas(events, func(e Event) bool {
            return e.Type == "response_cancelled" && e.ResponseID == "resp-1" && e.Payload["reason"] == "user_speech"
        })

        eventuallyHas(events, func(e Event) bool {
            return e.Type == "tool_started" && e.TurnID == "turn-2" && e.Payload["destination"] == "杭州"
        })

        Consistently(func() bool {
            for _, e := range events() {
                if e.Type == "business_committed" && e.Payload["destination"] == "上海" {
                    return false
                }
            }
            return true
        }, 3*time.Second, 200*time.Millisecond).Should(BeTrue())

        eventuallyHas(events, func(e Event) bool {
            return e.Type == "business_committed" && e.Payload["destination"] == "杭州"
        })
    })
})
```

这里的重点是 `Consistently`。很多打断缺陷不是立刻失败，而是旧 tool call 在几百毫秒后继续提交。E2E 用例要给旧链路一个暴露窗口，否则会误判为通过。

## 5. Playwright：验证浏览器播放端真的停住

服务端取消旧响应不代表用户耳机里已经停住。Web 端还需要断言播放器状态、字幕状态和可见提示。Playwright 可以通过页面事件和测试埋点验证这一层。

```python
from pathlib import Path
from playwright.sync_api import expect


def test_barge_in_stops_stale_audio(page):
    page.goto("/voice-agent")
    page.get_by_role("button", name="开始语音").click()

    page.set_input_files("input[type=file]", Path("fixtures/audio/book_trip_shanghai_then_hangzhou.wav"))

    expect(page.locator('[data-testid="agent-state"]')).to_have_text("正在播报")
    expect(page.locator('[data-testid="caption"]')).to_contain_text("上海")

    expect(page.locator('[data-testid="barge-in-banner"]')).to_have_text("已检测到打断")
    expect(page.locator('[data-testid="audio-player"]')).to_have_attribute("data-playing", "false")

    expect(page.locator('[data-testid="agent-state"]')).to_have_text("正在处理新问题")
    expect(page.locator('[data-testid="caption"]')).to_contain_text("杭州")

    page.get_by_role("button", name="确认预订").click()
    expect(page.locator('[data-testid="booking-result"]')).to_contain_text("杭州")
```

前端断言不要依赖音频波形逐帧比对，优先使用业务可观测状态：播放器是否停止、旧字幕是否撤销、新轮次字幕是否出现、最终结果是否只展示新目的地。

## 6. K8s 与 API Testing：让取消信号跨服务传播

在线系统里，打断事件通常要跨多个服务传播：网关收到客户端语音，实时 ASR 生成 partial，编排服务取消 LLM streaming，TTS 服务停止合成，业务服务取消或忽略旧 tool call。测试环境要把这些服务放在同一套可观测命名空间里。

一个实用的 K8s 验证方式是为每次 E2E 会话注入统一标签：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voice-e2e-observability
  namespace: voice-agent-e2e
data:
  required_labels: "session_id,turn_id,response_id,scenario"
  stale_response_policy: "cancel_or_ignore"
  max_barge_in_stop_latency_ms: "300"
```

API 层可以补一个取消传播检查：

```bash
curl -s "$BASE_URL/v1/voice/sessions/$SESSION_ID/events" \
  | jq '[.[] | select(.type == "response_cancelled" or .type == "tool_cancelled" or .type == "business_committed") ]'
```

最终断言不应只看 `response_cancelled`，还要看旧业务动作是否没有提交。对已经发出的外部请求，可以用幂等键和 `turn_id` 做防重：旧轮次请求即使返回，也只能写入 `ignored_stale_result`，不能进入提交路径。

## 7. 常见缺陷与排查线索

| 缺陷 | 用户表现 | trace 线索 | 修复方向 |
|---|---|---|---|
| 只停播放，不停推理 | 用户改口后仍执行旧动作 | `tts_cancelled` 后仍有旧 `tool_result` 提交 | 取消信号传给编排层和工具层 |
| 新旧轮次混写 | 最终回复混入两个目的地 | 同一 `response_id` 绑定多个 `turn_id` | 强制 response 与 turn 一对一 |
| ASR partial 过早触发 | 用户没说完就开始下单 | `llm_started` 早于 `turn_finalized` | 对高风险动作等待 final transcript |
| 客户端未停旧音频 | 页面显示新字幕但耳机仍播旧话 | 服务端有取消，前端无 `audio_stopped` | 播放器监听取消事件并清空队列 |
| 复盘缺证据 | 线上只知道用户取消 | 缺少 cancel reason 和 stale result | 统一事件 schema 与必填字段 |

这些问题的共同点是：最终结果可能偶尔正确，但链路证据不完整。测开同学要把“偶尔对”改成“为什么对、哪里保证对”。

## 8. 课后思考题

1. 如果用户打断后又沉默 5 秒，系统应该恢复旧回复、询问确认，还是保持等待？你会用哪些事件区分这三种策略？
2. 对支付、下单、删除数据这类高风险动作，ASR partial 是否允许触发工具调用？如果允许，必须加哪些防护？
3. 当 TTS 已经合成完但客户端还没播完时，取消信号应该以服务端状态为准，还是以前端播放状态为准？
4. 如何设计一批音频夹具，覆盖不同口音、噪声、停顿和打断时机，同时保持用例可维护？
5. 如果旧 tool call 无法真正取消，只能忽略返回结果，trace 里应该如何表达这个事实？

## 今日小结

Day 74 的重点是把语音 Agent 的打断体验拆成可测试的状态机。上线质量不能只证明 ASR 听懂了、TTS 能播了，而要证明旧轮次能被及时取消，新轮次能稳定接管，业务提交只发生在用户最终确认的意图上。

对资深测试开发来说，最有价值的资产不是一条“验证打断成功”的用例，而是一套可复用的事件契约：每个 `turn_id` 有边界，每个 `response_id` 有生命周期，每次取消有原因，每个旧结果有归宿。这样的 E2E 体系才能支撑语音 Agent 在真实用户环境中持续迭代。
