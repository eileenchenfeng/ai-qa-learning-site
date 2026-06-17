---
title: "每日 AI 学习笔记｜Day 64：AI Agent 状态机不变量与收敛性测试"
date: 2026-06-18
authors: [xiaoai]
tags: [learning-notes, AI, QA, Agent, state-machine, invariants, convergence-testing, reliability, Ginkgo, Playwright, Kubernetes, API-Testing]
---

# 每日 AI 学习笔记｜Day 64：AI Agent 状态机不变量与收敛性测试

<callout icon="star" bgc="4">
**核心总结：** 生产级 AI Agent 最容易出现的高危问题，往往不是“某一步失败了”，而是**状态被错误推进、旧事件把新状态回滚、补偿执行后系统没有真正收敛、用户界面与后端状态各说各话**。因此，测试开发不能只验证某个接口是否返回 200，而要围绕 **状态机不变量（Invariant）** 设计完整的 E2E 场景：从用户发起任务，到 Agent 规划、工具调用、审批回调、补偿恢复、最终通知，整条链路必须始终满足“终态唯一、非法回退被拒绝、重复事件不产生额外副作用、用户可见状态与后端真实状态一致”。今天的重点，是把 **状态机建模、收敛性验证、不变量断言** 变成可落地的工程实践：用 **Ginkgo** 验证执行链路和状态推进规则，用 **Python API Testing** 校验状态查询、版本号与非法跃迁拦截，用 **Playwright** 验证页面可见流程与终态说明，用 **Kubernetes** 演练乱序消息、重试风暴、worker 重启和补偿重放，确保 Agent 在复杂分布式场景里依然能稳定收敛到唯一正确结果。
</callout>

前两天我们分别讨论了异步回调、Webhook 一致性，以及事件溯源、审计与可重放测试。继续沿着这条主线往前走，下一步就要回答一个更底层的问题：**系统为什么能保证自己最终停在正确状态，而不是停在“看起来差不多”的错误状态？**

对于资深测试开发来说，真正需要守住的不是某个按钮、某个接口，而是整条业务链路中的状态演化规则。今天这篇笔记，我们就聚焦 **AI Agent 状态机不变量与收敛性测试**。

{/* truncate */}

## 0. 今日核心要点

1. **状态机不是文档图，而是线上系统的约束边界。**
2. **不变量比单次断言更重要，它决定系统在异常下能否守住底线。**
3. **收敛性测试要验证“最终只会停在一个合法终态”，而不是“最终有个结果就行”。**
4. **E2E 场景必须覆盖重复事件、乱序事件、补偿执行和人工介入。**
5. **用户可见状态、后端任务状态、审计事件必须相互一致。**
6. **状态版本号、sequence、幂等键和补偿标记是自动化验证的关键观测点。**

---

## 1. 核心理论：为什么 AI Agent 必须围绕状态机来测

### 1.1 Agent 不是单接口系统，而是长链路状态系统

传统接口测试常常默认“请求进来，响应出去”，但生产中的 AI Agent 远不止这一层。一次典型任务通常包含：

- 用户提交目标；
- Agent 生成计划；
- 调用多个工具；
- 等待审批或外部回调；
- 出现异常后触发补偿；
- 最终生成结果并通知用户。

这意味着系统真正的正确性，不只由某个步骤决定，而是由**状态是否沿着合法路径演进**决定。如果状态机没设计清楚，系统就会出现很多“表面成功、实际错误”的事故：

- 任务已经完成，却被迟到的失败事件打回 `failed`；
- 补偿已经执行，却仍然向用户展示“处理中”；
- 人工驳回后，旧的自动成功回调又把任务改回 `completed`；
- 前端显示“已完成”，但后端实际还停在 `awaiting_approval`。

<callout icon="bulb" bgc="3">
**测试视角：** 对 Agent 来说，最危险的不是单点失败，而是**系统已经进入错误状态，却没有任何机制把它拦住**。
</callout>

### 1.2 什么是不变量（Invariant）

不变量，就是无论系统经历成功、失败、重试、补偿、乱序还是人工介入，都必须始终成立的规则。对于 AI Agent，常见不变量至少包括以下几类：

<table header-row="true" col-widths="180,260,300,180">
  <tr>
    <td>不变量类型</td>
    <td>规则示例</td>
    <td>为什么重要</td>
    <td>测试优先级</td>
  </tr>
  <tr>
    <td>终态唯一</td>
    <td>任务一旦进入 completed / failed / cancelled，不允许再进入其他终态</td>
    <td>防止结果被后续过期事件污染</td>
    <td>P0</td>
  </tr>
  <tr>
    <td>状态不可逆</td>
    <td>已审批通过后，旧的 pending/failed 事件不能回滚状态</td>
    <td>避免乱序事件造成假失败</td>
    <td>P0</td>
  </tr>
  <tr>
    <td>副作用幂等</td>
    <td>重复回调不能重复发消息、重复创建单据、重复扣费</td>
    <td>避免“重复成功”事故</td>
    <td>P0</td>
  </tr>
  <tr>
    <td>视图一致</td>
    <td>用户界面、状态查询接口、审计时间线展示同一事实</td>
    <td>避免前后端理解不一致</td>
    <td>P0</td>
  </tr>
  <tr>
    <td>租户隔离</td>
    <td>tenant-a 的事件绝不能推进 tenant-b 的任务</td>
    <td>防止串租户事故</td>
    <td>P0</td>
  </tr>
</table>

### 1.3 收敛性到底在测什么

很多团队会说“最终一致性”，但如果没有可验证的定义，这句话几乎没有意义。测试里真正要验证的收敛性，通常是以下三件事：

1. **有限时间内收敛**：任务会在合理时间进入某个合法终态；
2. **收敛结果唯一**：无论中间有多少重试、补偿和乱序，最终终态唯一；
3. **收敛后不再漂移**：进入终态后，系统不会被后续旧事件再次改写。

因此，收敛性测试不只是“Eventually 变成 completed”，而是：

- Eventually 进入合法终态；
- Consistently 保持该终态不再变化；
- 副作用计数、页面展示、审计事件都同步稳定。

---

## 2. 工程实践：先建模状态机，再设计 E2E 测试

### 2.1 推荐的 Agent 状态机骨架

下面是一份适合任务型 Agent 的简化状态机：

```text
queued
  ↓
planning
  ↓
running
  ├── awaiting_approval
  ├── waiting_callback
  ├── compensating
  ↓
completed / failed / cancelled / manual_intervention_required
```

这几个状态不一定要照搬，但测试时一定要明确：

- 哪些是**中间态**；
- 哪些是**终态**；
- 哪些状态**允许被谁推进**；
- 哪些事件**必须被拒绝**。

### 2.2 状态推进规则要显式化

<table header-row="true" col-widths="180,230,250,220">
  <tr>
    <td>当前状态</td>
    <td>允许事件</td>
    <td>目标状态</td>
    <td>关键验证点</td>
  </tr>
  <tr>
    <td>queued</td>
    <td>task.accepted</td>
    <td>planning</td>
    <td>只允许初始化事件推进</td>
  </tr>
  <tr>
    <td>planning</td>
    <td>plan.generated / validation.failed</td>
    <td>running / failed</td>
    <td>计划失败需直接进入终态</td>
  </tr>
  <tr>
    <td>running</td>
    <td>tool.completed / approval.required / callback.waiting / task.failed</td>
    <td>running / awaiting_approval / waiting_callback / failed</td>
    <td>中间执行可分叉，但必须合法</td>
  </tr>
  <tr>
    <td>awaiting_approval</td>
    <td>approval.granted / approval.denied</td>
    <td>running / cancelled</td>
    <td>审批未完成前不能直接 completed</td>
  </tr>
  <tr>
    <td>waiting_callback</td>
    <td>callback.received / timeout.expired</td>
    <td>running / compensating</td>
    <td>超时后必须有明确处理策略</td>
  </tr>
  <tr>
    <td>compensating</td>
    <td>compensation.succeeded / compensation.failed</td>
    <td>failed / manual_intervention_required</td>
    <td>补偿本身也必须收敛</td>
  </tr>
  <tr>
    <td>completed / failed / cancelled</td>
    <td>任何旧事件</td>
    <td>保持原状态</td>
    <td>终态不可回退</td>
  </tr>
</table>

### 2.3 E2E 用例设计应该围绕真实业务链路展开

结合当前默认的测试设计风格，建议每条用例都覆盖完整链路，而不是只写“验证某个状态字段”。例如：

1. **用户发起“生成周报并发送群通知”任务**；
2. Agent 进入 `planning`，生成执行计划；
3. 调用知识库检索和摘要工具；
4. 因为要发送外部通知，进入 `awaiting_approval`；
5. 审批通过后进入 `running`；
6. 外部系统回调迟到一次、重放一次；
7. 任务最终进入 `completed`；
8. 页面展示为“已完成”；
9. 审计链路显示一次合法推进；
10. 通知只发出一次。

<callout icon="star" bgc="5">
**高价值测试原则：** 每条 E2E 用例都应该同时覆盖三类断言：**状态断言、证据断言、副作用断言**。只有这样，才能真正发现“状态错了但接口没报错”的问题。
</callout>

---

## 3. Ginkgo 实战：把状态机不变量变成自动化断言

### 3.1 定义统一的观测模型

```go
//go:build statemachinee2e

package statemachinee2e_test

type TaskView struct {
    TaskID             string   `json:"task_id"`
    TenantID           string   `json:"tenant_id"`
    State              string   `json:"state"`
    LastSequence       int64    `json:"last_sequence"`
    SideEffectCount    int      `json:"side_effect_count"`
    UserVisibleState   string   `json:"user_visible_state"`
    TimelineEventTypes []string `json:"timeline_event_types"`
}

type InvariantSnapshot struct {
    Terminal           bool     `json:"terminal"`
    AllowedTransitions []string `json:"allowed_transitions"`
    Violations         []string `json:"violations"`
}
```

这个模型有两个作用：

- `TaskView` 用来描述用户和接口能看到的真实状态；
- `InvariantSnapshot` 用来描述当前是否已经违反状态机规则。

### 3.2 E2E：完整任务链路必须收敛到唯一终态

```go
package statemachinee2e_test

import (
    . "github.com/onsi/ginkgo/v2"
    . "github.com/onsi/gomega"
)

var _ = Describe("Agent state convergence", Label("P0", "e2e", "state-machine"), func() {
    It("should converge to one terminal state after approval and callback", func() {
        taskID := SubmitAgentTask(SubmitTaskRequest{
            TenantID: "tenant-a",
            Prompt:   "汇总本周线上质量风险并发送管理摘要",
        })

        Eventually(func(g Gomega) {
            detail := GetTaskView(taskID)
            g.Expect(detail.State).To(BeElementOf("awaiting_approval", "running", "waiting_callback", "completed"))
            g.Expect(detail.LastSequence).To(BeNumerically(">", 0))
        }).Should(Succeed())

        ApproveTask(taskID)
        InjectCallback(taskID, "callback.received", 21)

        Eventually(func(g Gomega) {
            detail := GetTaskView(taskID)
            g.Expect(detail.State).To(Equal("completed"))
            g.Expect(detail.UserVisibleState).To(Equal("任务已完成"))
            g.Expect(detail.SideEffectCount).To(Equal(1))
        }).Should(Succeed())

        Consistently(func(g Gomega) {
            detail := GetTaskView(taskID)
            g.Expect(detail.State).To(Equal("completed"))
            g.Expect(detail.SideEffectCount).To(Equal(1))
        }, "15s", "1s").Should(Succeed())
    })
})
```

这里最关键的不是 `Eventually == completed`，而是后面的 `Consistently`：它确保系统已经真正稳定停在终态，而不是“短暂成功”。

### 3.3 E2E：过期失败事件不能回滚成功终态

```go
var _ = Describe("Terminal state protection", Label("P0", "e2e", "rollback-guard"), func() {
    It("should ignore stale failed event after task already completed", func() {
        taskID := CreateCompletedTaskForTest("tenant-a")
        before := GetTaskView(taskID)
        Expect(before.State).To(Equal("completed"))

        InjectCallback(taskID, "task.failed", 9)

        Consistently(func(g Gomega) {
            current := GetTaskView(taskID)
            g.Expect(current.State).To(Equal("completed"))
            g.Expect(current.LastSequence).To(BeNumerically(">", 9))
        }, "10s", "1s").Should(Succeed())
    })
})
```

这一类场景在生产里特别常见：成功事件先到，失败事件后到。如果没有 sequence / version 防护，系统就会被旧事件拖回去。

### 3.4 E2E：重复事件不允许产生重复副作用

```go
var _ = Describe("Idempotent side effects", Label("P0", "e2e", "idempotency"), func() {
    It("should send notification only once when duplicate callback is replayed", func() {
        taskID := CreateApprovedTaskWaitingCallback("tenant-a")

        InjectCallback(taskID, "callback.received", 18)
        InjectCallback(taskID, "callback.received", 18)

        Eventually(func(g Gomega) {
            detail := GetTaskView(taskID)
            g.Expect(detail.State).To(Equal("completed"))
            g.Expect(detail.SideEffectCount).To(Equal(1))
        }).Should(Succeed())
    })
})
```

对 Agent 平台来说，“重复成功”常常比显式失败更难排查，因为从监控看一切都像成功，但消息却发了两次、任务单建了两份、账单也扣了两次。

### 3.5 E2E：补偿失败后必须进入明确可处理终态

```go
var _ = Describe("Compensation convergence", Label("P0", "e2e", "compensation"), func() {
    It("should move to manual_intervention_required when compensation cannot finish", func() {
        taskID := SubmitAgentTask(SubmitTaskRequest{
            TenantID: "tenant-a",
            Prompt:   "创建发布计划并同步外部系统",
        })

        InjectFault(taskID, "external-system-timeout")
        TriggerCompensation(taskID)
        InjectFault(taskID, "compensation-failed")

        Eventually(func(g Gomega) {
            detail := GetTaskView(taskID)
            g.Expect(detail.State).To(Equal("manual_intervention_required"))
            g.Expect(detail.UserVisibleState).To(ContainSubstring("需要人工介入"))
        }).Should(Succeed())
    })
})
```

重点不是“补偿调用过了”，而是**补偿失败后系统有没有进入一个清晰、可处理、不可继续漂移的状态**。

---

## 4. Python API Testing：校验非法跃迁、版本保护与状态查询一致性

### 4.1 API：拒绝非法状态跃迁

```python
import requests

BASE_URL = "https://agent.example.test"


def test_state_transition_should_reject_direct_complete_from_queued(auth_headers):
    task_id = create_task(initial_state="queued", tenant_id="tenant-a")

    resp = requests.post(
        f"{BASE_URL}/api/tasks/{task_id}/transitions",
        json={"event_type": "callback.received", "sequence": 3},
        headers=auth_headers("tenant-a"),
        timeout=10,
    )

    assert resp.status_code == 409
    body = resp.json()
    assert body["error_code"] == "INVALID_TRANSITION"
    assert body["from_state"] == "queued"
    assert body["to_state"] == "completed"
```

如果系统连非法跃迁都能接受，后面的审计、页面和补偿基本都会一起失真。

### 4.2 API：sequence 过期事件必须被拦截

```python
def test_stale_sequence_should_not_overwrite_terminal_state(auth_headers):
    task_id = create_completed_task(tenant_id="tenant-a", last_sequence=20)

    resp = requests.post(
        f"{BASE_URL}/api/tasks/{task_id}/transitions",
        json={"event_type": "task.failed", "sequence": 18},
        headers=auth_headers("tenant-a"),
        timeout=10,
    )

    assert resp.status_code == 202
    body = resp.json()
    assert body["accepted"] is False
    assert body["ignored_reason"] == "stale_sequence"
```

### 4.3 API：状态查询、时间线和审计视图必须一致

```python
def test_task_state_should_match_timeline_and_audit(auth_headers):
    task_id = create_completed_task(tenant_id="tenant-a", last_sequence=12)

    detail = requests.get(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=auth_headers("tenant-a"),
        timeout=10,
    ).json()

    timeline = requests.get(
        f"{BASE_URL}/api/tasks/{task_id}/timeline",
        headers=auth_headers("tenant-a"),
        timeout=10,
    ).json()

    audit = requests.get(
        f"{BASE_URL}/api/tasks/{task_id}/audit",
        headers=auth_headers("tenant-a"),
        timeout=10,
    ).json()

    assert detail["state"] == "completed"
    assert timeline["current_state"] == detail["state"]
    assert audit["final_state"] == detail["state"]
    assert audit["last_sequence"] == detail["last_sequence"]
```

### 4.4 API：跨租户事件绝不能推进当前任务

```python
def test_cross_tenant_transition_should_be_forbidden(auth_headers):
    task_id = create_task(initial_state="running", tenant_id="tenant-a")

    resp = requests.post(
        f"{BASE_URL}/api/tasks/{task_id}/transitions",
        json={"event_type": "callback.received", "tenant_id": "tenant-b", "sequence": 8},
        headers=auth_headers("tenant-b"),
        timeout=10,
    )

    assert resp.status_code in (403, 404)
```

---

## 5. Playwright 实战：验证用户看到的状态流是否真实、稳定、可解释

### 5.1 E2E：审批 + 回调完成后，页面必须稳定停在“已完成”

```python
from playwright.sync_api import expect


def test_agent_task_should_converge_to_completed_ui(page, base_url):
    page.goto(f"{base_url}/agent/tasks")
    page.get_by_placeholder("输入任务目标").fill("汇总本周质量问题并发送总结")
    page.get_by_role("button", name="开始执行").click()

    expect(page.get_by_text("等待审批")).to_be_visible(timeout=15_000)
    page.get_by_role("button", name="批准执行").click()

    expect(page.get_by_text("等待外部回调")).to_be_visible(timeout=15_000)
    expect(page.get_by_text("任务已完成")).to_be_visible(timeout=120_000)
    expect(page.get_by_role("button", name="查看结果")).to_be_visible()
```

### 5.2 E2E：终态建立后，旧失败事件不能让 UI 回退

```python
from playwright.sync_api import expect


def test_completed_ui_should_not_rollback_after_stale_failed_event(page, base_url):
    page.goto(f"{base_url}/agent/tasks/demo-rollback-guard")

    expect(page.get_by_text("任务已完成")).to_be_visible(timeout=30_000)
    expect(page.get_by_text("执行失败")).not_to_be_visible()
    expect(page.get_by_role("button", name="查看结果")).to_be_visible()
```

### 5.3 E2E：补偿失败时，页面必须明确暴露“需要人工介入”

```python
from playwright.sync_api import expect


def test_compensation_failure_should_surface_manual_intervention(page, base_url):
    page.goto(f"{base_url}/agent/tasks/demo-compensation-failed")

    expect(page.get_by_text("系统正在执行补偿处理")).to_be_visible(timeout=15_000)
    expect(page.get_by_text("需要人工介入处理")).to_be_visible(timeout=60_000)
    expect(page.get_by_role("button", name="查看处理建议")).to_be_visible()
```

用户看到的页面文案其实就是状态机对外的“翻译层”。如果这个翻译层和后端真实状态不一致，再完整的后端校验都很难挽回用户信任。

---

## 6. Kubernetes 演练：把分布式扰动引入收敛性验证

### 6.1 场景一：worker 重启后任务必须继续收敛，不得重新开始

```bash
kubectl -n agent-platform rollout restart deployment/agent-runner
kubectl -n agent-platform rollout status deployment/agent-runner --timeout=180s
```

演练时持续提交 E2E 任务，验证：

1. 已在运行中的任务不会回退到 `queued`；
2. 重启后新 worker 能继续消费未完成任务；
3. 最终任务仍然进入唯一合法终态；
4. 不会因此重复触发通知、重复创建工单或重复写审计事件。

### 6.2 场景二：消息延迟与乱序投递下，状态版本保护仍然有效

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: agent-callback-delay
  namespace: chaos-testing
spec:
  action: delay
  mode: one
  selector:
    namespaces:
      - agent-platform
    labelSelectors:
      app: callback-consumer
  delay:
    latency: "1800ms"
    correlation: "70"
    jitter: "400ms"
  duration: "6m"
```

这时重点观测：

- `last_sequence` 是否只增不减；
- `completed` 终态是否被迟到事件回滚；
- 审计时间线是否记录“事件被忽略”的原因；
- 页面是否保持与真实状态一致。

### 6.3 场景三：补偿链路本身也要做收敛性验证

很多团队只测“主流程”，但生产事故经常出在补偿链路。建议演练：

- 外部系统超时；
- 触发补偿；
- 补偿成功后任务进入 `failed` 并给出明确原因；
- 补偿失败后进入 `manual_intervention_required`；
- 整个过程中页面、API、审计链路始终一致。

<callout icon="bulb" bgc="2">
**平台侧提醒：** 如果补偿链路没有自己的状态机与终态规则，它就会变成另一个“永远处理中”的黑洞。
</callout>

---

## 7. 课后思考题

1. 你当前负责的系统里，是否已经明确区分了**中间态**和**终态**？有没有“看起来完成了，但还可能被改写”的状态？
2. 你们的异步回调或 MQ 消费链路里，是否有显式的 `sequence`、版本号或事件时间保护？如果没有，最先会出什么事故？
3. 现在的自动化测试里，有多少是验证“能成功”，有多少是真正在验证“不会错误回退、不会重复副作用、最终稳定收敛”？
4. 补偿失败后，系统是进入明确的人审状态，还是继续停留在模糊的处理中？
5. 如果要为现有 Agent 平台补一套状态机质量闸门，你会优先落哪 3 条 P0 不变量？

---

## 8. 今日小结

今天我们把焦点从“事件是否来了”进一步推进到“系统是否稳定收敛”。对于 AI Agent 这类长链路、多组件、强异步的系统来说，**状态机不变量就是质量底线，收敛性就是生产可信度**。

真正成熟的测开体系，不能只验证某个请求成功、某条日志存在，而要能回答下面这些更关键的问题：

- 任务最终会不会只停在一个合法终态？
- 旧事件会不会把新状态打坏？
- 重试和补偿会不会带来重复副作用？
- 用户看到的结果，是否真的和系统事实一致？

如果你把这些问题都纳入 E2E 自动化，那么你的测试就不再只是“验功能”，而是在帮系统守住**分布式状态正确性**这条最重要的生产红线。
