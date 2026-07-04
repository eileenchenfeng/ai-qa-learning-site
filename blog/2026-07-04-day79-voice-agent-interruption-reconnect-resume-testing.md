---
title: "每日 AI 学习笔记｜Day 79：语音 Agent 中断、重连与会话续跑测试"
date: 2026-07-04
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, interruption-recovery, reconnect, websocket, ginkgo, playwright, kubernetes, e2e-testing]
---

# 每日 AI 学习笔记｜Day 79：语音 Agent 中断、重连与会话续跑测试

## 核心总结

前两天我们把语音 Agent 的**工具调用安全**和**会话记忆边界**拆开看，今天继续补上另一块最容易在真实线上出事故的能力：**用户说到一半被打断、前端断网、WebSocket 重连、下游任务仍在执行时，系统能不能把状态收拢到“可继续、可取消、不可重复提交”的正确位置**。这类问题难，不是因为某个接口会不会报错，而是因为语音链路天然是流式的：ASR 在流、NLU 在流、工具调用在流、UI 也在流，任何一个环节中断，都会让“当前这次意图到底算没算完成”变得模糊。

对资深测试开发来说，真正该验收的不是“断线后能不能重连”，而是**断线前后的状态机有没有保持单一事实源**：同一个会话是否还能被正确识别，同一个待执行任务是否只会提交一次，用户恢复连接后看到的是“继续这次任务”还是“重新来一遍”，以及后台 trace、审计日志、补偿记录是否与用户最终看到的结果一致。

{/* truncate */}

## 1. 为什么“中断恢复”比“失败重试”更难测

很多团队会把语音 Agent 的异常处理理解成普通接口重试，但线上真实问题往往复杂得多。一次中断可能同时影响四层状态：浏览器里的语音采集状态、服务端的会话状态、异步工具执行状态，以及最终写入外部系统的结果。如果这四层状态没有收敛到同一个真相，用户就会看到最危险的一类问题：页面显示“请重新开始”，后台却已经提交成功；或者页面显示“已恢复”，实际上服务端已经丢了这次任务。

中断恢复常见的事故面主要有三类：

1. **前端假恢复**：UI 显示“已重连”，但会话上下文已丢失，后续回答脱离原任务。
2. **后台双提交**：重连后重新发送确认，导致同一写操作被执行两次。
3. **状态悬空**：工具已在后台执行，但前端不知道该继续等待、允许取消，还是提示用户重新发起。

<table header-row="true" col-widths="170,220,260,260">
  <tr>
    <td>风险层</td>
    <td>典型线上现象</td>
    <td>常见根因</td>
    <td>E2E 验证点</td>
  </tr>
  <tr>
    <td>前端假恢复</td>
    <td>页面提示“连接已恢复”，但上下文槽位、转写草稿、任务状态被清空</td>
    <td>重连仅恢复 socket，不恢复 session snapshot</td>
    <td>重连后继续显示原会话状态，且后续追问基于原任务继续</td>
  </tr>
  <tr>
    <td>后台双提交</td>
    <td>用户重复确认一次，外部系统生成两条工单、两次会议或两笔订单</td>
    <td>resume 请求未复用原 `intent_id` / `idempotency_key`</td>
    <td>同一业务意图只有一次最终写入，审计日志唯一</td>
  </tr>
  <tr>
    <td>状态悬空</td>
    <td>工具任务仍在跑，但前端既不能继续，也不能取消</td>
    <td>状态机缺少 `resumable` / `cancellable` 中间态</td>
    <td>重连后明确展示“继续等待 / 取消任务 / 重试查询”三类可执行动作</td>
  </tr>
</table>

## 2. 验收面怎么定：不是“恢复连接”，而是“恢复业务语义”

用户在语音场景里不会关心 WebSocket 是否重建成功，用户只关心一句话：**“我刚才那件事现在到底进行到哪一步了？”** 所以，中断恢复测试必须围绕业务链路来验收，而不是围绕传输层来验收。

更实用的拆法是把验收面分成三层：

- **会话连续性**：断线前后的 `session_id`、槽位快照、待确认动作是否连续。
- **执行唯一性**：任何会改变外部世界的动作，恢复前后都必须共享同一 `intent_id` 与 `idempotency_key`。
- **用户可解释性**：重连后用户是否能看到当前状态、下一步可执行动作、以及失败时的补救路径。

<callout icon="bulb" bgc="3">
**一个实用判断标准：** 只要任务已经跨过“可能写外部系统”的边界，中断恢复测试就不能止步于“连接恢复成功”；必须继续验证同一任务是否唯一、状态是否可解释、以及恢复后的下一步操作是否与后台真实状态一致。
</callout>

## 3. E2E 场景：语音创建发布会议，中途断网后恢复续跑

### 场景：用户确认创建会议后，浏览器网络闪断 8 秒

**用户目标：** 用户说“帮我约今天下午 5 点和 Alex、Mina 开发布复盘会”，Agent 查询忙闲后展示确认卡片。用户点击确认后的几秒内，浏览器网络闪断，WebSocket 断开；服务端仍在等待下游日程系统响应。用户恢复网络后重新进入页面，系统应继续显示这次任务的真实状态，而不是重新触发一次创建。

**测试环境：**

- 前端通过 WebSocket 接收实时转写、Agent 状态与任务进度。
- 服务端将 `session_id`、`intent_id`、`task_id`、`idempotency_key` 写入 trace store。
- 日程服务被注入一次 5 秒延迟，模拟“后台仍在处理，但前端先断线”。

**执行步骤与预期中间状态：**

1. 用户发起语音请求并完成参数澄清。
   - 预期：生成稳定的 `session_id`、`intent_id=create_meeting`；前端显示待确认卡片，后台尚未写入外部系统。
2. 用户点击“确认创建”。
   - 预期：系统生成 `task_id` 与 `idempotency_key`，会话进入 `committing`；trace 可看到一次 `calendar.create_event` 提交。
3. 浏览器网络闪断，WebSocket 断开 8 秒。
   - 预期：前端状态切为 `reconnecting`；服务端任务不因前端断连自动重复提交，也不直接丢弃。
4. 下游日程系统在断连期间完成创建。
   - 预期：后台状态从 `committing` 收敛到 `succeeded`；审计日志只有一次成功写入。
5. 用户恢复网络并重新连回原页面。
   - 预期：前端基于 `session_id + task_id` 拉取快照，看到“会议已创建”，而不是再次出现确认按钮。
6. 用户刷新页面后再次查看日历。
   - ✅ 最终验证点：结果页只展示一条会议记录；前端恢复页、后端 trace、审计日志、日历最终状态四者一致，并且不存在第二次 `calendar.create_event`。

这个场景的价值，在于它同时覆盖了**前端断连、后台续跑、恢复后只读对账、写操作不重放**四个关键点。只测某个重连接口是否返回 200，根本无法验证这条链路有没有真正收敛。

## 4. 工程实践：Ginkgo 校验断连续跑与最终唯一写入

下面的 Go 示例假设系统暴露会话快照接口与审计查询接口。核心思路是：断连不等于失败，测试要验证后台任务在断连窗口内继续推进，并且恢复后仍能拿到同一条任务结果。

```go
package voice_resume_e2e_test

import (
    "encoding/json"
    "fmt"
    "net/http"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type SessionSnapshot struct {
    SessionID      string `json:"session_id"`
    IntentID       string `json:"intent_id"`
    TaskID         string `json:"task_id"`
    Status         string `json:"status"`
    IdempotencyKey string `json:"idempotency_key"`
    ResultTitle    string `json:"result_title"`
}

func mustGetSnapshot(baseURL, sessionID string) SessionSnapshot {
    resp, err := http.Get(fmt.Sprintf("%s/v1/voice/sessions/%s/snapshot", baseURL, sessionID))
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var snapshot SessionSnapshot
    Expect(json.NewDecoder(resp.Body).Decode(&snapshot)).To(Succeed())
    return snapshot
}

func mustGetAuditCount(baseURL, taskID string) int {
    resp, err := http.Get(fmt.Sprintf("%s/v1/audit/calendar/events?task_id=%s", baseURL, taskID))
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var result struct {
        Count int `json:"count"`
    }
    Expect(json.NewDecoder(resp.Body).Decode(&result)).To(Succeed())
    return result.Count
}

var _ = Describe("Voice Agent interruption recovery E2E", Ordered, func() {
    It("resumes a committing task after reconnect without duplicating writes", func() {
        baseURL := "http://voice-agent-e2e.default.svc.cluster.local"
        sessionID := startVoiceScenario(baseURL, []string{
            "帮我约今天下午五点和 Alex、Mina 开发布复盘会",
            "确认创建",
        })

        disconnectWebsocketClient(sessionID, 8*time.Second)

        Eventually(func(g Gomega) {
            snapshot := mustGetSnapshot(baseURL, sessionID)
            g.Expect(snapshot.IntentID).To(Equal("create_meeting"))
            g.Expect(snapshot.TaskID).NotTo(BeEmpty())
            g.Expect(snapshot.IdempotencyKey).NotTo(BeEmpty())
            g.Expect(snapshot.Status).To(Or(Equal("committing"), Equal("succeeded")))
        }, 10*time.Second, 300*time.Millisecond).Should(Succeed())

        Eventually(func(g Gomega) {
            snapshot := mustGetSnapshot(baseURL, sessionID)
            g.Expect(snapshot.Status).To(Equal("succeeded"))
            g.Expect(snapshot.ResultTitle).To(Equal("发布复盘会"))
            g.Expect(mustGetAuditCount(baseURL, snapshot.TaskID)).To(Equal(1))
        }, 20*time.Second, 500*time.Millisecond).Should(Succeed())
    })
})
```

这个用例里最重要的不是 `Status == succeeded` 本身，而是你必须同时把 `session_id`、`task_id`、`idempotency_key` 和最终审计条数暴露出来。没有这些字段，就没法判断“恢复成功”到底是续跑成功，还是静默重提了一次。

## 5. 工程实践：Playwright 验证前端断线提示、重连恢复与去重

前端 E2E 用例要盯住两个用户可见结果：第一，断线时页面是否明确进入“正在恢复”状态；第二，恢复后页面展示的是同一任务的最终状态，而不是重新要求用户再点一次确认。

```python
from playwright.sync_api import Page, expect


def test_voice_reconnect_resumes_existing_commit(page: Page):
    page.goto("/voice-agent")
    page.get_by_role("button", name="开始语音").click()
    page.get_by_test_id("mock-utterance-input").fill("帮我约今天下午五点和 Alex、Mina 开发布复盘会")
    page.get_by_role("button", name="发送语音").click()

    confirm_card = page.get_by_test_id("confirmation-card")
    expect(confirm_card).to_contain_text("Alex")
    expect(confirm_card).to_contain_text("Mina")
    expect(confirm_card).to_contain_text("今天下午 5:00")

    page.get_by_role("button", name="确认创建").click()
    expect(page.get_by_test_id("task-status")).to_have_text("正在提交")

    page.context.set_offline(True)
    expect(page.get_by_test_id("connection-banner")).to_have_text("连接中断，正在恢复会话")

    page.context.set_offline(False)
    page.get_by_role("button", name="重新连接").click()

    expect(page.get_by_test_id("resume-banner")).to_have_text("已恢复到刚才的任务进度")
    expect(page.get_by_test_id("task-status")).to_have_text("会议已创建")
    expect(page.get_by_test_id("confirmation-card")).to_be_hidden()
    expect(page.get_by_test_id("result-card")).to_contain_text("发布复盘会")
    expect(page.get_by_test_id("audit-count")).to_have_text("1")
```

这个例子强调的是：**重连后的 UI 必须恢复到“业务状态”，不是只恢复到“页面在线”**。如果系统只是把 socket 连上，但又把确认卡片重新露出来，用户很可能会再点一次，直接把重复提交问题引出来。

## 6. API 与 K8s：把“可续跑、可取消、不可重放”做成质量门禁

这类能力不能只靠人工回归。更稳妥的做法，是把中断恢复约束直接写进发布前的质量门禁。下面给出一个可以直接落到集群里的 ConfigMap 样例：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voice-agent-resume-quality-gate
  namespace: voice-agent-e2e
data:
  require_resume_snapshot: "true"
  require_single_task_id_across_reconnect: "true"
  max_duplicate_commit_count: "0"
  max_orphan_pending_task_count: "0"
  require_resume_state_visibility: "true"
  allowed_recoverable_states: "listening,thinking,committing,succeeded,failed,cancellable,resumable"
  required_resume_trace_fields: "session_id,intent_id,task_id,idempotency_key,connection_id,status,resume_from"
```

同时建议在 API 层暴露一组聚合指标，供每次构建后自动判断是否可放行：

```bash
curl -s "$BASE_URL/v1/quality/recovery/summary?build=$BUILD_ID" | jq '{
  build_id,
  reconnect_success_rate,
  resume_snapshot_restore_rate,
  duplicate_commit_count,
  orphan_pending_task_count,
  median_resume_latency_ms,
  by_state
}'
```

如果门禁只看“WebSocket 重连成功率”，问题很容易被掩盖。真正更有用的指标应该同时盯住：

- 会话层：重连后快照恢复率、会话连续性正确率。
- 任务层：重复提交数、悬空任务数、恢复后取消成功率。
- 用户层：恢复提示可见率、恢复后无需二次确认的成功率。

## 7. 常见缺陷与排查线索

线上真出问题时，排查顺序很重要。建议优先按下面这张表来收敛：

<table header-row="true" col-widths="180,260,280">
  <tr>
    <td>缺陷现象</td>
    <td>优先检查</td>
    <td>典型修复方向</td>
  </tr>
  <tr>
    <td>重连后又看到确认按钮</td>
    <td>前端是否按 `task_id` 拉取快照，而不是重新走一遍确认流程</td>
    <td>恢复页优先读快照；确认卡片仅在 `pending_confirmation` 态显示</td>
  </tr>
  <tr>
    <td>同一任务生成两条外部记录</td>
    <td>恢复请求是否复用了原 `intent_id` 与 `idempotency_key`</td>
    <td>把去重主键前移到确认前生成，并贯穿恢复链路</td>
  </tr>
  <tr>
    <td>页面提示失败，但后台其实成功</td>
    <td>前端失败态是否只看 socket 结果，没做快照对账</td>
    <td>断连恢复后先拉取最终快照，再决定展示成功还是失败</td>
  </tr>
  <tr>
    <td>后台一直卡在 pending</td>
    <td>是否缺少任务超时收敛、补偿或人工接管机制</td>
    <td>增加 orphan task 扫描、超时终态和人工接管入口</td>
  </tr>
</table>

一个经验是：**只要前端文案、后端 trace、审计系统三者里有两者对不上，就不要相信“这个恢复已经做好了”**。恢复问题最怕的是“看起来好了”，因为这种假象最容易带着重复写入一路溜到线上。

## 8. 课后思考题

1. 如果语音 Agent 在 `pending_confirmation` 阶段断线，恢复后是否应该自动回到确认卡片，还是重新让用户说一遍？你的判断依据是什么？
2. 如果后台任务已经成功，但前端在恢复前先点击了“取消”，系统应以哪个状态为准？你会怎样设计冲突收敛规则？
3. 对“只读查询”和“会写外部系统”的语音任务，中断恢复策略为什么不能完全一样？哪些指标应该分开监控？
4. 如果你负责设计这套系统的可观测性，会强制要求每个恢复相关 trace 至少包含哪些字段？为什么？

## 9. 今日小结

今天这篇笔记想强调一件事：**语音 Agent 的中断恢复，本质上是在考验系统有没有把“连接状态”和“业务状态”分开建模**。连接可以断，任务不能乱；页面可以刷新，意图不能重放；用户可以回来继续，系统不能假装什么都没发生。

对测试开发来说，最有效的办法不是再补几条“断网重连成功”的检查，而是把场景拉成完整 E2E 链路：用户发起任务、确认提交、连接中断、后台续跑、页面恢复、结果对账、审计唯一。只有当这些环节在同一条链路里同时成立，你才能比较放心地说：这套语音 Agent 真的具备线上可恢复性。
