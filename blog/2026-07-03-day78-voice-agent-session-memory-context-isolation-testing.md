---
title: "每日 AI 学习笔记｜Day 78：语音 Agent 会话记忆与上下文隔离测试"
date: 2026-07-03
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, memory, context-isolation, session, ginkgo, playwright, k8s, e2e-testing]
---

# 每日 AI 学习笔记｜Day 78：语音 Agent 会话记忆与上下文隔离测试

## 核心总结

昨天我们把语音 Agent 的工具调用链路拆到“权限、幂等、失败恢复”这一层，今天继续往前走一步：**很多线上问题不是工具本身坏了，而是 Agent 把上一轮、上一个用户、甚至上一个会话的上下文带进了当前决策**。语音场景里，这类问题尤其容易发生，因为用户说话天然省略主语、代词多、会临时改口，还会跨轮补充条件。只要会话记忆边界不清，系统就可能把“帮我查杭州天气”误接成“按上一轮默认帮我订杭州机票”，或者把 A 用户的偏好残留给 B 用户。

所以，记忆测试不能只看“模型能不能记住上下文”，更要看**它什么时候该记住、什么时候必须忘掉、什么时候只能在当前会话可见**。面向资深测试开发，更可靠的做法是把记忆问题设计成完整 E2E 场景：从语音输入、多轮澄清、记忆写入、工具调用、跨会话切换、重新登录，到最终用户可观测结果与审计日志收敛，验证**会话内连续性、会话间隔离性、敏感信息最小保留**三件事是否同时成立。

{/* truncate */}

## 1. 为什么语音 Agent 比文本 Bot 更容易发生上下文污染

文本 Bot 常见的是“一问一答”；语音 Agent 更像一条连续流。用户会说“帮我看看明天去上海的高铁”“不对，是后天”“优先上午”“等等先别订”，系统需要在连续 turn 里理解哪些是补充、哪些是覆写、哪些只是口头自我修正。如果记忆粒度设计得太粗，就会把临时槽位误当长期偏好；如果清理不及时，又会把上一轮会话的残留条件带到下一轮。

真正高风险的污染通常有三类：

1. **会话内错继承**：同一 session 中，旧槽位覆盖了用户后续澄清。
2. **会话间残留**：新 session 继承了上一 session 的临时上下文。
3. **跨用户串扰**：共享缓存、错误 key 或错误 trace 关联导致 A 用户记忆泄露给 B 用户。

<table header-row="true" col-widths="180,220,250,250">
  <tr>
    <td>风险层</td>
    <td>典型线上现象</td>
    <td>常见根因</td>
    <td>E2E 验证点</td>
  </tr>
  <tr>
    <td>会话内错继承</td>
    <td>用户改口后，Agent 仍按旧时间或旧地点执行</td>
    <td>slot merge 策略错误，后写未覆盖先写</td>
    <td>trace 中可见字段演进；最终执行参数与最后一次确认一致</td>
  </tr>
  <tr>
    <td>会话间残留</td>
    <td>新会话默认沿用上一轮的城市、联系人、审批人</td>
    <td>session reset 不完整，本地缓存或 memory store 未清空</td>
    <td>新会话只带长期画像，不带上轮临时变量</td>
  </tr>
  <tr>
    <td>跨用户串扰</td>
    <td>A 的偏好、历史任务、敏感摘要出现在 B 的对话里</td>
    <td>cache key 未带 user_id / tenant_id，检索过滤缺失</td>
    <td>跨用户查询结果完全隔离；审计日志可回溯到正确主体</td>
  </tr>
</table>

## 2. 测试目标不是“记得更多”，而是“边界刚刚好”

做语音 Agent 记忆测试时，一个常见误区是把“记住更多信息”当成更智能。事实上，质量更高的系统通常是**该记的记住，不该记的立即丢弃**。例如“我喜欢靠窗座位”可以沉淀成长期偏好；“明天下午四点去上海”通常只该留在当前任务上下文；“身份证号后四位”在任务完成后应尽快脱敏或清理。

<callout icon="bulb" bgc="3">
**一个实用判断标准：** 任何记忆条目在进入持久层前，都应该先回答 3 个问题：它属于长期偏好还是临时任务变量？它的可见范围是当前 turn、当前 session，还是当前用户的长期画像？任务完成后它是否还值得保留？
</callout>

## 3. E2E 场景：连续改口后，最终只保留最后一次明确意图

### 场景：用户通过语音预订差旅，期间连续两次修正行程

**用户目标：** 用户先说“帮我订明天下午去上海的高铁”，随后改成“不是明天，是后天上午”，又补充“先别下单，只查最早两班”。系统应在同一 session 内正确覆写旧槽位，并且最终只执行只读查询，不发生任何下单动作。

**执行步骤与预期中间状态：**

1. 用户发起首轮语音请求。
   - 预期：创建 `session_id`、`turn_id=1`，抽取 `destination=上海`、`date=明天`、`time_window=下午`、`intent=query_or_book_ticket`。
2. 用户第二轮改口“不是明天，是后天上午”。
   - 预期：`date` 与 `time_window` 被覆写为 `后天/上午`；旧槽位仍可在 trace 中看到历史版本，但不再参与最终执行。
3. 用户第三轮补充“先别下单，只查最早两班”。
   - 预期：意图从可能写操作收敛为只读查询；`write_enabled=false`；查询条件保留为 `后天上午 -> 最早两班`。
4. Agent 调用余票查询工具并返回结果卡片。
   - 预期：只出现 `train.search`，不出现 `train.book`；结果卡片展示后天上午最早两班。
5. 用户结束会话并重新开启新会话。
   - ✅ 最终验证点：新会话中不再默认携带“上海、后天上午、最早两班”这些临时任务变量；若用户仅说“帮我查高铁”，系统必须重新追问目的地和时间，而不是沿用上轮残留上下文。

这个场景的价值在于，它同时验证了**同会话内覆写正确**和**跨会话后清理彻底**。如果只做单步接口验证，很难把这两个风险放到同一条真实链路里看清楚。

## 4. 工程实践：Ginkgo 校验会话隔离、用户隔离与敏感字段清理

下面的 Go 示例把“多轮覆写正确 + 新会话不残留 + 跨用户不串扰”放进一个 E2E 用例。示例假设系统提供会话 trace 与 memory dump 查询接口。

```go
package voice_memory_e2e_test

import (
    "encoding/json"
    "fmt"
    "net/http"
    "net/url"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type MemoryEntry struct {
    Scope      string `json:"scope"`
    Key        string `json:"key"`
    Value      string `json:"value"`
    SessionID  string `json:"session_id"`
    UserID     string `json:"user_id"`
    PersistTTL int    `json:"persist_ttl"`
}

type MemoryDump struct {
    UserID  string        `json:"user_id"`
    Entries []MemoryEntry `json:"entries"`
}

func getMemoryDump(baseURL, userID, sessionID string) MemoryDump {
    api := fmt.Sprintf(
        "%s/v1/debug/memory?user_id=%s&session_id=%s",
        baseURL,
        url.QueryEscape(userID),
        url.QueryEscape(sessionID),
    )

    resp, err := http.Get(api)
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var dump MemoryDump
    Expect(json.NewDecoder(resp.Body).Decode(&dump)).To(Succeed())
    return dump
}

var _ = Describe("Voice Agent memory isolation E2E", Ordered, func() {
    It("overrides temporary slots inside one session and clears them across sessions", func() {
        baseURL := "http://voice-agent-e2e.default.svc.cluster.local"
        userA := "user_eileen"
        userB := "user_alex"

        firstSession := startVoiceScenario(baseURL, userA, []string{
            "帮我订明天下午去上海的高铁",
            "不是明天，是后天上午",
            "先别下单，只查最早两班",
        })

        Eventually(func(g Gomega) {
            dump := getMemoryDump(baseURL, userA, firstSession)
            g.Expect(dump.Entries).NotTo(BeEmpty())

            latest := map[string]string{}
            for _, entry := range dump.Entries {
                latest[entry.Key] = entry.Value
                g.Expect(entry.UserID).To(Equal(userA))
                g.Expect(entry.SessionID).To(Equal(firstSession))
            }

            g.Expect(latest).To(HaveKeyWithValue("destination", "上海"))
            g.Expect(latest).To(HaveKeyWithValue("date", "后天"))
            g.Expect(latest).To(HaveKeyWithValue("time_window", "上午"))
            g.Expect(latest).To(HaveKeyWithValue("mode", "query_only"))
        }, 10*time.Second, 300*time.Millisecond).Should(Succeed())

        secondSession := startVoiceScenario(baseURL, userA, []string{
            "帮我查高铁",
        })
        secondDump := getMemoryDump(baseURL, userA, secondSession)
        for _, entry := range secondDump.Entries {
            Expect(entry.SessionID).To(Equal(secondSession))
            Expect(entry.Key).NotTo(Equal("destination"), "新会话不应默认带入上轮目的地")
            Expect(entry.Key).NotTo(Equal("time_window"), "新会话不应默认带入上轮时间窗")
        }

        otherUserDump := getMemoryDump(baseURL, userB, firstSession)
        Expect(otherUserDump.Entries).To(BeEmpty(), "跨用户不得读取到他人的 session memory")
    })
})
```

这个用例里，最关键的不是断言某个字段值，而是要求你把 `scope`、`session_id`、`user_id`、`persist_ttl` 这些元数据一起暴露出来。没有这些可观测字段，线上出现上下文污染时，只能从用户投诉倒推，很难精确定位是覆写错了、清理漏了，还是 cache key 打错了。

## 5. 工程实践：Playwright 验证多轮语音澄清与新会话重置

前端端到端测试应该盯住两类用户可感知结果：第一，系统是否明确告诉用户“我理解成什么了”；第二，会话重新开始时，界面和后端状态是否一起重置，而不是只清空输入框。

```python
from playwright.sync_api import Page, expect


def test_voice_context_isolation_across_sessions(page: Page):
    page.goto("/voice-agent")

    page.get_by_role("button", name="开始语音").click()
    page.get_by_test_id("mock-utterance-input").fill("帮我订明天下午去上海的高铁")
    page.get_by_role("button", name="发送语音").click()
    expect(page.get_by_test_id("slot-destination")).to_have_text("上海")
    expect(page.get_by_test_id("slot-time")).to_have_text("明天下午")

    page.get_by_test_id("mock-utterance-input").fill("不是明天，是后天上午")
    page.get_by_role("button", name="发送语音").click()
    expect(page.get_by_test_id("slot-time")).to_have_text("后天上午")
    expect(page.get_by_test_id("slot-time-history")).to_contain_text("已覆盖：明天下午")

    page.get_by_test_id("mock-utterance-input").fill("先别下单，只查最早两班")
    page.get_by_role("button", name="发送语音").click()
    expect(page.get_by_test_id("intent-mode")).to_have_text("只查询")
    expect(page.get_by_test_id("write-warning")).to_have_text("当前不会执行下单")
    expect(page.get_by_test_id("result-card")).to_contain_text("最早两班")

    page.get_by_role("button", name="新建会话").click()
    expect(page.get_by_test_id("session-banner")).to_have_text("新会话已开始")
    expect(page.get_by_test_id("slot-destination")).to_have_text("未设置")
    expect(page.get_by_test_id("slot-time")).to_have_text("未设置")

    page.get_by_test_id("mock-utterance-input").fill("帮我查高铁")
    page.get_by_role("button", name="发送语音").click()
    expect(page.get_by_test_id("clarify-question")).to_have_text("你想查哪座城市、哪一天的车次？")
```

这个例子强调了一点：**“新会话”不是 UI 上多一个空白气泡，而是一次真正的上下文边界切换**。如果页面显示像新会话，但后台 memory store 还挂着上一轮槽位，那只是把污染藏起来了，不是解决了。

## 6. API 与 K8s：把记忆边界做成质量门禁

和幂等、权限一样，记忆边界也应该变成发布前的硬指标，而不是靠经验兜底。下面给出一个可直接落地的 ConfigMap 样例：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voice-agent-memory-quality-gate
  namespace: voice-agent-e2e
data:
  require_user_scope_in_memory_key: "true"
  require_session_scope_for_temporary_slots: "true"
  max_cross_session_temporary_leak_count: "0"
  max_cross_user_memory_leak_count: "0"
  require_sensitive_slot_redaction_after_completion: "true"
  required_memory_trace_fields: "user_id,tenant_id,session_id,turn_id,scope,key,persist_ttl,redacted"
  allowed_persistent_keys: "seat_preference,language_preference,notification_preference"
```

同时建议在 API 层暴露一组聚合指标，方便每次构建后自动判断是否可以放行：

```bash
curl -s "$BASE_URL/v1/quality/memory/summary?build=$BUILD_ID" | jq '{
  build_id,
  cross_session_temporary_leak_count,
  cross_user_memory_leak_count,
  sensitive_slot_redaction_fail_count,
  clarification_after_reset_rate,
  by_scope
}'
```

如果发布门禁只看“多轮问答成功率”，会话污染问题很容易被掩盖，因为很多错误不会直接报 500，而是以“回答看起来合理、但拿错上下文”的方式悄悄溜进线上。更有效的门禁方式是同时盯住：

- 会话内：槽位覆写正确率、改口后最终参数一致率。
- 会话间：临时变量残留数、新会话追问触发率。
- 用户间：跨用户命中数、错误主体访问数、敏感字段泄露数。

## 7. 常见缺陷与排查线索

<table header-row="true" col-widths="180,220,260,260">
  <tr>
    <td>缺陷</td>
    <td>用户表现</td>
    <td>trace / memory 线索</td>
    <td>修复方向</td>
  </tr>
  <tr>
    <td>临时槽位被错误持久化</td>
    <td>新会话默认带出上一轮城市或日期</td>
    <td>`scope=persistent` 中出现 `destination/date` 等任务变量</td>
    <td>区分 profile memory 与 task memory，按 key 白名单写入持久层</td>
  </tr>
  <tr>
    <td>session reset 只清前端不清后端</td>
    <td>页面像新会话，但回答仍沿用旧上下文</td>
    <td>新 `session_id` 下仍能查到旧 `session_id` 的 memory entry</td>
    <td>把 reset 做成服务端原子操作，并校验 cache / store / trace 同步清理</td>
  </tr>
  <tr>
    <td>跨用户缓存 key 冲突</td>
    <td>B 用户看到 A 的摘要或偏好</td>
    <td>memory key 不含 `user_id` / `tenant_id`，或过滤条件缺失</td>
    <td>统一改为 `tenant + user + scope + key` 组合键，检索时强制主体过滤</td>
  </tr>
  <tr>
    <td>敏感字段任务结束后未脱敏</td>
    <td>后续对话还能复述手机号、证件号</td>
    <td>`redacted=false` 的敏感字段在 completed task 后仍可见</td>
    <td>任务完成触发敏感槽位擦除，保留必要审计但不保留明文</td>
  </tr>
  <tr>
    <td>覆写顺序错误</td>
    <td>用户已改口，系统仍按旧参数查询或执行</td>
    <td>turn 序号更新了，但最终执行参数仍引用旧版本 slot</td>
    <td>按 turn version 做 last-write-wins，并在确认前只读取最新快照</td>
  </tr>
</table>

## 8. 课后思考题

1. 哪些信息应该被定义成长期偏好，哪些只能停留在当前任务上下文？如果你来设计白名单，会如何划分？
2. 如果用户在会话 A 中说了“以后都优先英文回复”，在会话 B 中是否应该自动继承？这个需求和“明天上午去上海”为什么不一样？
3. 当系统支持“恢复上次未完成任务”时，如何避免把原本应该销毁的临时上下文重新带回来？
4. 如果同一台共享设备被不同账号轮流登录，你会在哪几层做上下文隔离：浏览器、本地缓存、服务端 memory store，还是工具权限层？

## 9. 今日小结

Day 78 的重点，不是让 Agent 记得更多，而是让它**只在正确的边界内记住正确的内容**。语音 Agent 一旦进入多轮澄清、连续改口、跨会话恢复这类真实场景，真正决定事故率的往往不是模型理解能力，而是上下文管理能力。

今天可以沉淀成 3 条实践规则：第一，所有记忆测试都优先按完整 E2E 业务链路设计，而不是拆成孤立接口检查；第二，所有 memory entry 都必须能回答“属于谁、属于哪一轮、保留多久、为什么能保留”；第三，所有新会话都要验证服务端与前端一起重置，不能只做表面清空。下一篇可以继续往**语音 Agent 的中断恢复与可撤销操作测试**推进，重点验证用户打断、取消、恢复执行时的状态一致性。