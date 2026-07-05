---
title: "每日 AI 学习笔记｜Day 80：语音 Agent 打断、取消与补偿收敛测试"
date: 2026-07-05
authors: [xiaoai]
tags: [learning-notes, AI, QA, voice-agent, barge-in, cancellation, compensation, ginkgo, playwright, kubernetes, api-testing, e2e-testing]
---

# 每日 AI 学习笔记｜Day 80：语音 Agent 打断、取消与补偿收敛测试

## 核心总结

昨天我们解决的是“断了以后能不能接着跑”，今天要继续往更难的一步走：**当用户在语音 Agent 执行过程中主动打断、临时改主意、要求取消，甚至在外部系统已经部分落库后又反悔时，系统能不能把“停止、回滚、保留什么结果”说清楚、做干净、且不留下半成功脏状态**。这类问题本质上已经不是单纯的 ASR 或对话体验问题，而是一个**带状态机、带补偿、带幂等、带用户可解释性**的完整工程质量问题。

对测试开发来说，最容易误判的地方在于：很多系统看上去已经支持“取消”，其实只是前端把 loading 动画关掉了，后台任务还在继续跑；或者系统确实发出了 cancel 请求，但下游写操作已经越过不可逆边界，最终只能靠补偿任务收尾。真正应该验收的是：**打断是否及时生效、取消是否有明确生效边界、补偿是否唯一执行、用户最终看到的状态是否与 trace / audit / 外部系统一致**。

{/* truncate */}

## 1. 为什么“打断与取消”比“失败恢复”更容易埋雷

失败恢复更多是在系统视角处理“出错之后怎么办”；打断与取消则是用户主动改变系统执行路径。两者最大的区别在于，取消往往发生在任务还没有自然结束的时候，这意味着系统需要同时处理三件事：**停止正在进行的流式响应、判断下游动作是否已经跨过不可逆边界、把最终状态解释给用户**。

线上最危险的不是“取消失败”四个字，而是那种表面取消、实际未停的半吊子状态。例如用户说“先别发了”，页面也提示“已取消”，但邮件还是发出去了；或者页面显示“已停止”，实际上数据库里已经插入了一半记录，后面又没有补偿，把脏数据直接留在线上。

常见风险面通常落在下面四类：

1. **前端假取消**：UI 已退出执行态，但服务端任务仍在继续。
2. **不可逆边界判断错误**：系统把已经落外部系统的动作当成“可直接撤销”。
3. **补偿重复执行**：同一取消请求触发多次回滚，导致状态二次污染。
4. **用户语义误判**：把“等等”“先暂停”“别发给全部人”这类自然语言错误归类成彻底取消。

<table header-row="true" col-widths="170,230,250,250">
  <tr>
    <td>风险层</td>
    <td>典型线上现象</td>
    <td>常见根因</td>
    <td>E2E 验证点</td>
  </tr>
  <tr>
    <td>前端假取消</td>
    <td>页面提示“已取消”，但下游任务仍继续执行并最终写入</td>
    <td>只取消前端流，不取消服务端 worker / queue</td>
    <td>取消后任务状态进入 `cancelled` 或 `compensating`，且不再出现新的执行副作用</td>
  </tr>
  <tr>
    <td>不可逆边界误判</td>
    <td>已经发出的消息或已创建的日程被当成“未提交”处理</td>
    <td>状态机没有显式区分 `pre_commit` / `post_commit`</td>
    <td>取消结果明确区分“已终止”与“已提交，转补偿”两类终态</td>
  </tr>
  <tr>
    <td>补偿重复执行</td>
    <td>一次取消触发两次删除、两次撤回、两次回滚</td>
    <td>缺少 `cancel_request_id` / `compensation_id` 幂等约束</td>
    <td>审计日志中同一业务对象只有一次有效补偿</td>
  </tr>
  <tr>
    <td>用户语义误判</td>
    <td>“先暂停一下”被直接理解成彻底取消，任务丢失</td>
    <td>中断意图分类过粗，缺少 pause / clarify / cancel 分层</td>
    <td>关键口令与状态转移一致，必要时先追问再取消</td>
  </tr>
</table>

## 2. 取消能力的验收面：不是“停下来”，而是“收得干净”

真正成熟的语音 Agent，取消能力至少要覆盖四层约束：

- **交互层**：用户说出“停止”“取消发送”“先别提交”后，系统是否立即停止继续播报和继续生成。
- **执行层**：任务是否真的收到 cancel signal，异步 worker 是否停止领取后续步骤。
- **事务层**：如果已经跨过外部写入边界，是进入 `cancelled`，还是进入 `compensating`。
- **审计层**：最终 trace、审计日志、外部系统状态、前端结果页是否能对账。

<callout icon="bulb" bgc="3">
**一个实用判断标准：** 取消测试不该只断言“接口返回了 success”，而应该继续追到最终外部状态。只要任务会改动外部世界，就必须回答清楚 3 个问题：取消发生在边界前还是边界后？最终有没有留下半成功脏状态？用户看到的提示是否和真实结果一致？
</callout>

## 3. E2E 场景：语音批量发周报，发送前被打断取消，发送后触发补偿

**场景：** 用户说“帮我把本周测试周报发给项目组和老板”，Agent 生成预览卡片并开始执行“发群消息 + 发邮件”两个动作。用户在第一步消息准备完成、第二步邮件即将发送前说“等等，先取消，我还要改一下内容”。如果消息和邮件都还没真正发出，系统应直接取消；如果项目群消息已经发出，但邮件尚未发出，系统应进入补偿分支，只撤回已发消息并终止邮件发送。

**执行步骤与预期中间状态：**

1. 用户发起语音请求并确认发送对象。
   - 预期：生成 `session_id`、`intent_id=send_weekly_report`，前端展示发送预览，任务状态为 `pending_confirmation`。
2. 用户点击“确认发送”。
   - 预期：系统生成 `task_id`、`cancel_token`、`idempotency_key`；执行计划中包含 `send_group_message`、`send_email` 两步。
3. 第一阶段执行进入“准备发群消息”。
   - 预期：状态为 `running`，trace 中可见当前 step 为 `send_group_message.prepare`，外部系统尚无落库副作用。
4. 用户说“等等，先取消，我还要改一下”。
   - 预期：ASR 中断当前播报，NLU 将意图归类为 `cancel_execution`；服务端记录 `cancel_request_id`，任务进入 `cancelling`。
5. 系统判断取消边界。
   - 预期 A（边界前）：若群消息尚未提交，则任务直接收敛到 `cancelled`，所有下游步骤不再执行。
   - 预期 B（边界后）：若群消息已发出，则任务进入 `compensating`，撤回群消息，禁止继续发送邮件。
6. 用户查看最终结果页。
   - ✅ 最终验证点：前端明确展示“已取消”或“已取消并完成补偿”；审计日志中取消请求只生效一次；外部系统不存在“消息保留但邮件没发、页面却说全取消成功”这种不一致状态。

这个场景的价值，在于它把**用户自然语言打断、流式中止、异步取消、边界判断、补偿回滚、最终可解释性**放进了同一条业务链路，而不是把“取消按钮可点”单独拆成一条表面用例。

## 4. 工程实践：Ginkgo 校验取消信号、补偿唯一性与最终状态收敛

下面的 Go 示例假设系统提供任务快照接口、补偿审计接口与外部消息查询接口。重点不是“调用了 cancel API”，而是验证取消前后状态是否按预期收敛。

```go
package voice_cancel_e2e_test

import (
    "encoding/json"
    "fmt"
    "net/http"
    "net/url"
    "time"

    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

type TaskSnapshot struct {
    TaskID          string `json:"task_id"`
    Status          string `json:"status"`
    CurrentStep     string `json:"current_step"`
    CancelRequestID string `json:"cancel_request_id"`
    CompensationID  string `json:"compensation_id"`
    GroupMessageID  string `json:"group_message_id"`
    EmailSent       bool   `json:"email_sent"`
}

func getTaskSnapshot(baseURL, taskID string) TaskSnapshot {
    resp, err := http.Get(fmt.Sprintf("%s/v1/tasks/%s/snapshot", baseURL, taskID))
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var snapshot TaskSnapshot
    Expect(json.NewDecoder(resp.Body).Decode(&snapshot)).To(Succeed())
    return snapshot
}

func getCompensationCount(baseURL, taskID string) int {
    resp, err := http.Get(fmt.Sprintf("%s/v1/audit/compensations?task_id=%s", baseURL, url.QueryEscape(taskID)))
    Expect(err).NotTo(HaveOccurred())
    defer resp.Body.Close()
    Expect(resp.StatusCode).To(Equal(http.StatusOK))

    var result struct {
        Count int `json:"count"`
    }
    Expect(json.NewDecoder(resp.Body).Decode(&result)).To(Succeed())
    return result.Count
}

var _ = Describe("Voice Agent cancellation E2E", Ordered, func() {
    It("cancels before irreversible boundary or compensates exactly once after commit", func() {
        baseURL := "http://voice-agent-e2e.default.svc.cluster.local"

        taskID := startVoiceScenarioAndConfirm(baseURL, []string{
            "帮我把本周测试周报发给项目组和老板",
            "确认发送",
        })

        waitUntilStep(baseURL, taskID, "send_group_message.prepare")
        triggerVoiceInterrupt(baseURL, taskID, "等等，先取消，我还要改一下")

        Eventually(func(g Gomega) {
            snapshot := getTaskSnapshot(baseURL, taskID)
            g.Expect(snapshot.CancelRequestID).NotTo(BeEmpty())
            g.Expect(snapshot.Status).To(Or(Equal("cancelling"), Equal("cancelled"), Equal("compensating"), Equal("compensated")))
        }, 8*time.Second, 300*time.Millisecond).Should(Succeed())

        Eventually(func(g Gomega) {
            snapshot := getTaskSnapshot(baseURL, taskID)
            g.Expect(snapshot.EmailSent).To(BeFalse())

            switch snapshot.Status {
            case "cancelled":
                g.Expect(snapshot.GroupMessageID).To(BeEmpty())
                g.Expect(getCompensationCount(baseURL, taskID)).To(Equal(0))
            case "compensated":
                g.Expect(snapshot.GroupMessageID).NotTo(BeEmpty())
                g.Expect(snapshot.CompensationID).NotTo(BeEmpty())
                g.Expect(getCompensationCount(baseURL, taskID)).To(Equal(1))
            default:
                g.Fail(fmt.Sprintf("unexpected terminal status: %s", snapshot.Status))
            }
        }, 20*time.Second, 500*time.Millisecond).Should(Succeed())
    })
})
```

这个用例最关键的地方，是把 `cancel_request_id`、`compensation_id`、`group_message_id` 和 `email_sent` 一起拉出来校验。否则你只看到“取消成功”四个字，根本不知道系统到底是没发、发了一半、还是发了以后又悄悄补偿了一次。

## 5. 工程实践：Playwright 验证语音打断、取消提示与补偿结果页

前端 E2E 的重点，是验证用户能否看懂系统当前到底做到了哪一步。取消类问题最怕“后端状态对了，页面说错了”，因为这会直接诱发二次操作。

```python
from playwright.sync_api import Page, expect


def test_voice_cancel_and_compensation_result(page: Page):
    page.goto("/voice-agent")
    page.get_by_role("button", name="开始语音").click()
    page.get_by_test_id("mock-utterance-input").fill("帮我把本周测试周报发给项目组和老板")
    page.get_by_role("button", name="发送语音").click()

    expect(page.get_by_test_id("preview-card")).to_contain_text("项目组")
    expect(page.get_by_test_id("preview-card")).to_contain_text("老板")
    page.get_by_role("button", name="确认发送").click()

    expect(page.get_by_test_id("task-status")).to_have_text("正在执行发送计划")
    expect(page.get_by_test_id("current-step")).to_have_text("准备发送群消息")

    page.get_by_test_id("mock-utterance-input").fill("等等，先取消，我还要改一下")
    page.get_by_role("button", name="发送语音").click()

    expect(page.get_by_test_id("interrupt-banner")).to_have_text("已收到取消请求，正在停止当前任务")
    expect(page.get_by_test_id("task-status")).to_have_text("正在取消")

    result_card = page.get_by_test_id("result-card")
    expect(result_card).to_be_visible()
    expect(result_card).to_contain_text("本次任务已停止")
    expect(result_card).to_contain_text("邮件未发送")
    expect(result_card).not_to_contain_text("请重新确认发送")

    audit_panel = page.get_by_test_id("audit-panel")
    expect(audit_panel).to_contain_text("取消请求次数：1")
    expect(audit_panel).to_contain_text("补偿执行次数：0|1")
```

这个例子想强调的是：**结果页必须把“直接取消成功”和“已执行部分补偿”区分展示**。如果两种情况都只写成“任务结束”，用户根本不知道外部世界有没有已经发生的副作用，也就不知道自己下一步该改内容重试，还是先去确认撤回是否完成。

## 6. API 设计：让取消与补偿成为一等公民

如果后端 API 只暴露一个 `POST /cancel`，而不暴露任务当前边界和最终收敛结果，测试会非常被动。更适合上线质量治理的做法，是把取消链路设计成可观测、可对账的状态机。

建议至少具备下面几类接口与字段：

```bash
# 触发取消
curl -X POST "$BASE_URL/v1/tasks/$TASK_ID/cancel" \
  -H 'Content-Type: application/json' \
  -d '{
    "reason": "user_voice_interrupt",
    "utterance": "等等，先取消，我还要改一下",
    "request_id": "cancel-20260705-001"
  }'

# 查看最终状态
curl -s "$BASE_URL/v1/tasks/$TASK_ID/snapshot" | jq '{
  task_id,
  status,
  current_step,
  cancel_request_id,
  irreversible_boundary,
  compensation_id,
  external_effects,
  user_visible_message
}'
```

这里最重要的不是接口路径，而是字段语义：

- `irreversible_boundary`：明确告诉调用方当前是否已经跨过不可逆写入边界。
- `external_effects`：列出已经发生的外部副作用，例如“群消息已发出 1 条”。
- `user_visible_message`：让前端直接拿到可解释结果，避免前后端各自猜状态。
- `request_id` / `cancel_request_id`：保证同一次取消请求不会重复生效。

## 7. K8s 与发布门禁：把“可取消、可补偿、不可二次回滚”写成质量阈值

对线上系统来说，取消能力不能只靠人工经验验证。更稳的做法，是把关键约束固化为发布门禁。下面给出一个可直接落地的 ConfigMap 示例：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: voice-agent-cancel-quality-gate
  namespace: voice-agent-e2e
data:
  require_cancel_token: "true"
  require_irreversible_boundary_flag: "true"
  max_false_cancel_count: "0"
  max_duplicate_compensation_count: "0"
  max_post_cancel_external_effect_count: "0"
  require_user_visible_cancel_result: "true"
  allowed_terminal_states: "cancelled,compensated,failed"
  required_trace_fields: "session_id,task_id,current_step,cancel_request_id,compensation_id,irreversible_boundary,status"
```

同时建议在 API 层暴露聚合指标，每次构建后自动拉取：

```bash
curl -s "$BASE_URL/v1/quality/cancellation/summary?build=$BUILD_ID" | jq '{
  build_id,
  cancel_success_rate,
  false_cancel_count,
  duplicate_compensation_count,
  post_cancel_external_effect_count,
  median_cancel_convergence_ms,
  by_terminal_state
}'
```

如果门禁只看“取消接口 2xx 成功率”，几乎一定会漏掉真正的线上事故。更实用的指标应该同时关注：

- **交互层**：取消意图识别正确率、打断后停止播报耗时。
- **任务层**：取消收敛耗时、取消后仍继续执行的任务数。
- **补偿层**：重复补偿数、补偿失败数、补偿后残留外部副作用数。
- **用户层**：结果页可解释率、取消后无需人工介入的成功率。

## 8. 常见缺陷与排查线索

<table header-row="true" col-widths="180,240,260,260">
  <tr>
    <td>缺陷现象</td>
    <td>优先检查</td>
    <td>trace / audit 线索</td>
    <td>典型修复方向</td>
  </tr>
  <tr>
    <td>用户说取消，系统却继续播报</td>
    <td>前端音频播放与模型流输出是否支持即时 interrupt</td>
    <td>存在 cancel event，但流式 token 仍持续输出</td>
    <td>把播报层、生成层、执行层都接入统一 cancel token</td>
  </tr>
  <tr>
    <td>页面显示已取消，群消息仍发出</td>
    <td>worker 是否真正消费到 cancel signal</td>
    <td>cancel_time 早于 send_time，但任务仍进入 `sent`</td>
    <td>在每个可中断 step 前增加 cancel checkpoint</td>
  </tr>
  <tr>
    <td>补偿执行两次</td>
    <td>补偿任务是否以业务对象幂等键去重</td>
    <td>同一 message_id 存在两条 compensation success</td>
    <td>引入 `compensation_id` 和唯一索引，补偿前先查终态</td>
  </tr>
  <tr>
    <td>用户说“先暂停”却被彻底取消</td>
    <td>中断意图分类模型是否只分 stop / continue 两类</td>
    <td>语义分类结果缺少 `pause` / `clarify` 标签</td>
    <td>把 pause、cancel、modify 拆成独立状态迁移</td>
  </tr>
  <tr>
    <td>补偿成功了，但页面仍显示失败</td>
    <td>前端是否只读首次失败事件，没等终态快照</td>
    <td>trace 终态为 `compensated`，UI 却保留 `failed`</td>
    <td>结果页统一以终态快照渲染，而不是消费中间事件拼状态</td>
  </tr>
</table>

一个经验是：**取消问题一定要从“最终外部世界是什么样”往回倒推**。只看应用内状态很容易被误导，因为真正影响用户信任的，往往不是系统内部以为自己做了什么，而是邮件到底发没发、消息到底撤没撤、审批到底提没提交。

## 9. 课后思考题

1. 如果语音 Agent 在说“我来帮你发送周报”时被用户打断说“先别发给老板”，你会把它判成取消、修改目标范围，还是重新澄清？为什么？
2. 对“发消息、发邮件、提审批、创建日历”这四类动作，你会怎样定义各自的不可逆边界？哪些可以直接取消，哪些必须走补偿？
3. 如果补偿动作本身也失败了，结果页应该怎样向用户解释，才能既不掩盖风险，也不制造二次误操作？
4. 如果你来定义取消质量门禁，最不能妥协的 3 个指标会是什么？这些指标为什么能比“取消接口成功率”更接近真实风险？

## 10. 今日小结

Day 80 想沉淀的核心经验只有一句话：**语音 Agent 的取消能力，验收的不是“能不能停”，而是“停下以后有没有把现场收干净”**。只要系统会改动外部世界，取消就一定要和状态机、幂等、补偿、审计一起设计；否则所谓“支持打断”很容易只是交互层的一层幻觉。

从测试方法上看，最有效的做法依然是完整 E2E 业务链路：用户发起任务、确认执行、语音打断、服务端取消、边界判定、必要补偿、结果页解释、外部状态对账。只有这条链路能闭环，你才能比较有把握地说，这个语音 Agent 真正具备线上可控的中止能力。