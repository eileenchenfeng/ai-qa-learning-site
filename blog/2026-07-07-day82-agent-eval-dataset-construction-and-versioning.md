---
title: "每日 AI 学习笔记｜Day 82：Agent 评测数据集构建与版本管理"
date: 2026-07-07
authors: [xiaoai]
tags: [learning-notes, AI, QA, eval-dataset, dataset-versioning, annotation, evalops, cicd]
---

# 每日 AI 学习笔记｜Day 82：Agent 评测数据集构建与版本管理

## 核心总结

今天的主题是 **Agent 评测数据集构建与版本管理**。如果说昨天的 SLO 验证回答的是“这次上线能不能扛住真实负载”，今天要回答的就是：**每一次模型、Prompt、工具、权限、编排策略变化之后，我们如何知道 Agent 的核心业务质量没有倒退**。

对测试开发来说，eval dataset 不是一次性跑分材料，而是持续演进的质量资产。它应该像代码一样有设计、有评审、有版本、有变更说明，也应该像自动化用例一样接入 CI/CD，在 PR、灰度和发布前自动给出质量门禁结果。

- **评测数据集是 Agent 质量的“回归基线”**：它沉淀用户意图、工具链路、边界条件、负样本和历史事故，帮助团队发现“看起来能答，实际业务不可用”的回归。
- **数据集设计不能只追求数量**：覆盖率、代表性、意图分布、难例比例、负样本和业务优先级要同时被管理，否则大数据集也可能只是在重复简单问题。
- **标注质量决定评测可信度**：需要标注规范、双人复核、IAA（一致性）统计、自动预标注与人工审核，而不是把“人工标过”当成天然正确。
- **版本管理是 EvalOps 的地基**：用 DVC、Git LFS、JSONL schema、dataset changelog 和版本 diff，把“为什么分数变了”追到具体样本和标签变化。
- **最有价值的门禁是 E2E 场景门禁**：从用户提交真实任务开始，到 Agent 调用工具、产生外部状态、返回可验证结果，整个链路都要进入回归集。

{/* truncate */}

## 1. 为什么评测数据集是 Agent 质量的核心资产

很多团队第一次做 Agent 评测时，会把 dataset 当成“为了某次发布临时凑出来的测试输入”。这种做法短期能得到一个分数，长期却很难解释质量变化。

Agent 的质量风险通常不是单个回答错了，而是一个链路在某个隐蔽环节发生偏移：意图识别错、工具选错、参数填错、权限绕过、外部状态写错、失败后没有解释清楚。只有把这些真实链路沉淀成可回放样本，评测才有持续价值。

一个成熟的 eval dataset 至少承担 5 个角色：

1. **质量基线**：新版本必须和上一稳定版本对比，而不是只看绝对分。
2. **业务契约**：核心用户任务、不可接受行为、合规边界都写进样本和 rubrics。
3. **事故记忆**：线上失败、用户投诉、灰度问题转成回归样本，防止同类问题复发。
4. **研发反馈**：失败样本能定位到 Prompt、Tool、Planner、Memory、权限或外部依赖。
5. **发布门禁**：CI/CD 中自动跑回归，分数下降、关键场景失败或安全样本误过时直接拦截。

<callout icon="bulb" bgc="3">
**核心判断：** 一个 eval dataset 是否有价值，不看样本数量，而看它能否稳定回答 3 个问题：这次改动影响了哪些真实用户场景？失败是否可复现？是否能阻止高风险回归进入发布链路？
</callout>

## 2. 数据集设计原则：覆盖率和代表性要一起管

Agent 数据集最容易出现两种极端：一种是只覆盖 happy path，跑分很好但上线后频繁翻车；另一种是堆了大量边界问题，评测很难看却无法代表真实用户分布。

更稳妥的做法是把数据集拆成多个子集，每个子集承担不同目标。

<table header-row="true" col-widths="150,240,260,240">
  <tr>
    <td>子集类型</td>
    <td>目标</td>
    <td>样本来源</td>
    <td>发布门禁建议</td>
  </tr>
  <tr>
    <td>核心路径集</td>
    <td>覆盖最高频、最高价值用户任务</td>
    <td>产品任务、客服记录、真实会话脱敏样本</td>
    <td>必须高通过率，失败需阻断</td>
  </tr>
  <tr>
    <td>边界难例集</td>
    <td>暴露长上下文、多约束、工具组合问题</td>
    <td>历史 bug、灰度失败、专家构造</td>
    <td>允许分层阈值，但关键样本不可回归</td>
  </tr>
  <tr>
    <td>负样本集</td>
    <td>验证拒答、澄清、权限边界和安全策略</td>
    <td>越权请求、模糊指令、不可执行任务</td>
    <td>误通过应直接阻断</td>
  </tr>
  <tr>
    <td>漂移监控集</td>
    <td>观察真实流量意图是否变化</td>
    <td>近期线上抽样、人工复核后的新增样本</td>
    <td>用于趋势观察，不一定阻断</td>
  </tr>
</table>

### 2.1 意图分布：不要让低价值样本淹没高风险场景

数据集要记录每个样本的意图标签，例如 `search_only`、`tool_chain`、`write_action`、`permission_sensitive`、`multi_turn_repair`。如果 80% 样本都是简单问答，整体分数就会掩盖工具链路的退化。

建议每个样本至少带这些字段：

- `case_id`：稳定唯一 ID，不能因为文案微调就变化。
- `scenario`：E2E 业务场景名称。
- `intent`：用户意图类型，可多标签。
- `risk_level`：P0/P1/P2，用于门禁权重。
- `input`：用户输入或多轮对话上下文。
- `expected_behavior`：可观察的期望行为，不只写“回答正确”。
- `judge_rubric`：评审规则，说明如何给 pass/fail 或分数。
- `required_tools`：预期工具或禁止工具。
- `external_assertions`：外部状态验证点。

### 2.2 边界用例：从真实失败里长出来

边界用例不应该只靠想象。更有效的来源包括：

1. 线上失败会话转样本。
2. 发布前人工探索测试发现的问题。
3. 模型升级后分数波动最大的样本。
4. 工具 schema 变更后最容易被填错的参数组合。
5. 用户输入含模糊时间、别名、代词、多约束、反悔和取消的场景。

每个边界样本都要说明它验证的风险，而不是只保留一段 prompt。否则半年后团队会忘记为什么这个样本存在，也不敢删除或修改。

### 2.3 负样本：验证 Agent 会不会“不该做也做了”

Agent 的质量不只是“该做的能做”，还包括“不该做的能拒绝、该澄清的能澄清”。负样本建议覆盖：

- 用户要求执行越权操作。
- 用户给出缺失关键参数的写操作。
- 用户要求访问不存在或未授权资源。
- 用户混合提出可执行与不可执行目标。
- 用户诱导 Agent 跳过确认、跳过审计或伪造结果。

负样本的期望结果通常不是固定答案，而是行为约束：必须拒绝、必须澄清、不得调用写工具、不得编造外部结果。

## 3. 标注质量控制：先让人类答案可信

如果标注不稳定，自动化评测只会把噪声自动化。标注质量控制要先回答：不同标注员是否理解同一套规则？同一个样本在不同时间复标是否一致？分歧是样本问题、规范问题，还是系统能力边界不清？

### 3.1 标注规范要写到“可判定”

一个好的标注规范不只写“答案要准确”，还要写清楚可观察条件。例如：

- 工具调用类样本：必须调用哪个工具、哪些参数必须正确、是否允许降级。
- 写操作样本：是否必须二次确认、是否需要幂等键、外部状态如何验证。
- 澄清类样本：缺少哪些信息时必须追问，不能直接执行。
- 安全类样本：哪些内容必须拒绝，哪些内容可以提供替代建议。

### 3.2 IAA：用一致性发现规范漏洞

IAA（Inter-Annotator Agreement）用于衡量多个标注员对同一批样本的一致程度。对于二分类 pass/fail，可以先用 Cohen's Kappa；对于多分类标签，可以用加权 Kappa 或 Krippendorff's Alpha。

下面这个 Python 示例可以直接计算二分类标注的一致性，并输出分歧样本。

```python
# file: evalops/annotation_agreement.py
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def cohen_kappa(a: list[str], b: list[str]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("a and b must have the same non-zero length")

    labels = sorted(set(a) | set(b))
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n

    ca = Counter(a)
    cb = Counter(b)
    expected = sum((ca[label] / n) * (cb[label] / n) for label in labels)

    if expected == 1.0:
        return 1.0
    return (observed - expected) / (1 - expected)


def load_labels(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["case_id"]: row["label"] for row in reader}


def main() -> None:
    ann_a = load_labels(Path("annotator_a.csv"))
    ann_b = load_labels(Path("annotator_b.csv"))
    common_ids = sorted(set(ann_a) & set(ann_b))

    labels_a = [ann_a[i] for i in common_ids]
    labels_b = [ann_b[i] for i in common_ids]
    kappa = cohen_kappa(labels_a, labels_b)

    print(f"common_cases={len(common_ids)}")
    print(f"cohen_kappa={kappa:.3f}")
    print("disagreements:")
    for case_id in common_ids:
        if ann_a[case_id] != ann_b[case_id]:
            print(f"- {case_id}: A={ann_a[case_id]} B={ann_b[case_id]}")


if __name__ == "__main__":
    main()
```

运行方式：

```bash
cat > annotator_a.csv <<'CSV'
case_id,label
case-001,pass
case-002,fail
case-003,pass
CSV

cat > annotator_b.csv <<'CSV'
case_id,label
case-001,pass
case-002,pass
case-003,pass
CSV

python evalops/annotation_agreement.py
```

经验上，如果关键子集的 Kappa 低于 0.6，不要急着扩大标注规模；先修标注规范、补充示例、拆分含糊标签。

### 3.3 自动预标注 + 人工审核

LLM 可以承担预标注角色，但最终高风险样本仍要人工审核。推荐流程是：

1. LLM 根据 rubric 生成初始 label、score、reason。
2. 标注员只看样本、rubric 和预标注理由，确认或修正。
3. 对高风险样本、模型低置信样本、历史分歧样本做二审。
4. 每次修改标签都写入 changelog，说明原因。

自动预标注的价值不是替代人，而是减少重复劳动，并把标注员精力集中到分歧和难例上。

## 4. 数据集版本管理：让每次变化都可解释

Agent eval dataset 的版本管理要做到 4 件事：可追溯、可比较、可回滚、可复现。

### 4.1 推荐目录结构

```text
evals/
  datasets/
    agent-core/
      dataset.yaml
      changelog.md
      v2026.07.07/
        cases.jsonl
        rubrics.jsonl
        metadata.json
      v2026.07.14/
        cases.jsonl
        rubrics.jsonl
        metadata.json
  runners/
    run_eval.py
    compare_versions.py
  reports/
    latest.json
```

`dataset.yaml` 记录数据集名称、负责人、门禁阈值和子集定义。

```yaml
name: agent-core
owner: qa-platform
schema_version: 1
current_version: v2026.07.07
gates:
  overall_min_score: 0.86
  p0_pass_rate: 1.0
  no_new_critical_failures: true
subsets:
  core_path:
    min_score: 0.90
  negative:
    min_score: 0.98
  tool_chain:
    min_score: 0.88
```

### 4.2 JSONL 样本 schema

下面是一个 E2E 样本。它不是只验证一个 API，而是描述完整业务链路。

```json
{
  "case_id": "agent-release-gate-001",
  "version": "v2026.07.07",
  "scenario": "新功能上线前生成测试计划并创建工单",
  "intent": ["tool_chain", "write_action", "release_gate"],
  "risk_level": "P0",
  "input": {
    "messages": [
      {"role": "user", "content": "基于这个需求生成 E2E 测试计划，并创建发布前检查工单"}
    ],
    "context": {
      "requirement_id": "REQ-123",
      "user_role": "qa_engineer"
    }
  },
  "expected_behavior": {
    "must_call_tools": ["requirement.read", "testplan.generate", "ticket.create"],
    "must_not_call_tools": ["production.deploy"],
    "final_response_contains": ["测试计划", "工单链接", "风险项"],
    "external_assertions": [
      "ticket.status == 'created'",
      "ticket.labels contains 'release-gate'"
    ]
  },
  "judge_rubric": {
    "pass": "工具调用顺序正确、参数完整、工单创建成功、最终响应可追溯",
    "fail": "漏调用关键工具、创建错误工单、越权部署、编造链接或隐藏失败"
  }
}
```

### 4.3 DVC / Git LFS 的取舍

<table header-row="true" col-widths="130,260,260,220">
  <tr>
    <td>方案</td>
    <td>适合场景</td>
    <td>优势</td>
    <td>注意点</td>
  </tr>
  <tr>
    <td>Git 原生</td>
    <td>小型 JSONL、样本数量少、无大文件</td>
    <td>评审方便，diff 清晰</td>
    <td>不适合音视频、大规模附件</td>
  </tr>
  <tr>
    <td>Git LFS</td>
    <td>大 JSONL、图片、音频、附件样本</td>
    <td>保留 Git 工作流，减少仓库膨胀</td>
    <td>需要配置 LFS 存储和权限</td>
  </tr>
  <tr>
    <td>DVC</td>
    <td>需要数据血缘、远端存储、实验复现</td>
    <td>可绑定数据版本、模型版本和评测结果</td>
    <td>团队需要统一 DVC 操作规范</td>
  </tr>
</table>

推荐原则：样本正文能直接 diff 的，优先放 Git；大附件和多模态样本用 LFS 或 DVC；评测结果与 dataset version 绑定保存。

### 4.4 数据集 changelog 模板

```markdown
## v2026.07.07

### Added
- 新增 18 条发布门禁 E2E 样本，覆盖测试计划生成、工单创建、权限拒绝。
- 新增 6 条负样本，验证缺少确认时不得执行写操作。

### Changed
- 调整 `tool_chain` 子集 rubric：要求最终响应必须包含 trace_id 或可追溯链接。

### Removed
- 移除 2 条重复短问答样本，原因：与 core_path 子集已有样本语义等价。

### Label Review
- 双人复核 40 条 P0 样本，Cohen's Kappa = 0.82。
```

## 5. E2E 场景：新功能上线前触发自动评测门禁

下面用一个完整场景说明数据集如何接入发布链路。

**用户故事：** 团队准备上线一个“自动生成测试计划并创建发布检查工单”的 Agent 新功能。开发提交 PR 后，CI 自动拉取最新稳定 eval dataset，运行新版本 Agent，与 main 分支基线对比。如果 P0 样本失败、负样本误通过、或核心路径得分下降超过阈值，PR 不能合入。

**E2E 链路：** PR 创建 → CI 构建 Agent → 拉取 dataset version → 执行 E2E eval runner → 调用真实或沙箱工具 → 采集外部断言 → LLM-as-Judge/规则评分 → 与 baseline 对比 → 输出门禁结果。

**预期中间状态：**

1. CI 日志记录 dataset version、commit sha、agent image tag。
2. 每个 case 都有 `run_id`，可追踪到工具调用日志。
3. 写操作只落在沙箱环境，并带有幂等键。
4. P0 样本失败时输出失败原因、工具调用轨迹和外部状态差异。
5. 评分下降时能区分是 Agent 退化，还是 dataset 标签变化。

**最终验证点（✅）：**

- ✅ `p0_pass_rate == 100%`。
- ✅ `negative_false_accept_rate == 0%`。
- ✅ `overall_score` 相比 baseline 下降不超过 2 pp。
- ✅ 所有写操作都可在沙箱审计日志中对账。
- ✅ 失败报告能定位到 case_id、scenario、dataset_version 和 runner_version。

## 6. 工程实践：Python 评测 runner

下面示例实现了一个可运行的简化 runner：读取 JSONL 样本，调用 Agent 接口，按规则评分，并输出汇总报告。真实项目可以把 `call_agent` 替换成 HTTP/gRPC 调用。

```python
# file: evalops/run_eval.py
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EvalResult:
    case_id: str
    scenario: str
    risk_level: str
    score: float
    passed: bool
    reason: str
    latency_ms: int


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def call_agent(case: dict[str, Any]) -> dict[str, Any]:
    """Replace this stub with a real Agent HTTP/gRPC call in production."""
    expected = case["expected_behavior"]
    return {
        "final_text": "已生成测试计划，工单链接：https://sandbox.local/tickets/T-1001，风险项已列出。",
        "tool_calls": [
            {"name": "requirement.read", "args": {"requirement_id": "REQ-123"}},
            {"name": "testplan.generate", "args": {"style": "e2e"}},
            {"name": "ticket.create", "args": {"label": "release-gate"}},
        ],
        "external_state": {
            "ticket.status": "created",
            "ticket.labels": ["release-gate", "qa"]
        },
        "trace_id": "trace-demo-001",
        "debug_expected": expected,
    }


def score_case(case: dict[str, Any], output: dict[str, Any]) -> tuple[float, str]:
    expected = case["expected_behavior"]
    tool_names = [call["name"] for call in output.get("tool_calls", [])]
    final_text = output.get("final_text", "")
    external_state = output.get("external_state", {})

    for tool in expected.get("must_call_tools", []):
        if tool not in tool_names:
            return 0.0, f"missing required tool: {tool}"

    for tool in expected.get("must_not_call_tools", []):
        if tool in tool_names:
            return 0.0, f"forbidden tool was called: {tool}"

    for phrase in expected.get("final_response_contains", []):
        if phrase not in final_text:
            return 0.5, f"final response missing phrase: {phrase}"

    for assertion in expected.get("external_assertions", []):
        if assertion == "ticket.status == 'created'" and external_state.get("ticket.status") != "created":
            return 0.0, "ticket was not created"
        if assertion == "ticket.labels contains 'release-gate'" and "release-gate" not in external_state.get("ticket.labels", []):
            return 0.0, "ticket label release-gate missing"

    return 1.0, "passed"


def run(dataset_path: Path, report_path: Path) -> None:
    cases = load_jsonl(dataset_path)
    results: list[EvalResult] = []

    for case in cases:
        start = time.perf_counter()
        output = call_agent(case)
        latency_ms = int((time.perf_counter() - start) * 1000)
        score, reason = score_case(case, output)
        results.append(EvalResult(
            case_id=case["case_id"],
            scenario=case["scenario"],
            risk_level=case["risk_level"],
            score=score,
            passed=score >= 1.0,
            reason=reason,
            latency_ms=latency_ms,
        ))

    overall = sum(r.score for r in results) / max(len(results), 1)
    p0 = [r for r in results if r.risk_level == "P0"]
    p0_pass_rate = sum(r.passed for r in p0) / max(len(p0), 1)

    report = {
        "dataset": str(dataset_path),
        "overall_score": round(overall, 4),
        "p0_pass_rate": round(p0_pass_rate, 4),
        "case_count": len(results),
        "results": [r.__dict__ for r in results],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run(Path("evals/datasets/agent-core/v2026.07.07/cases.jsonl"), Path("evals/reports/latest.json"))
```

本地试跑可以先准备一条样本：

```bash
mkdir -p evals/datasets/agent-core/v2026.07.07 evals/reports
cat > evals/datasets/agent-core/v2026.07.07/cases.jsonl <<'JSONL'
{"case_id":"agent-release-gate-001","version":"v2026.07.07","scenario":"新功能上线前生成测试计划并创建工单","intent":["tool_chain","write_action","release_gate"],"risk_level":"P0","input":{"messages":[{"role":"user","content":"基于这个需求生成 E2E 测试计划，并创建发布前检查工单"}],"context":{"requirement_id":"REQ-123","user_role":"qa_engineer"}},"expected_behavior":{"must_call_tools":["requirement.read","testplan.generate","ticket.create"],"must_not_call_tools":["production.deploy"],"final_response_contains":["测试计划","工单链接","风险项"],"external_assertions":["ticket.status == 'created'","ticket.labels contains 'release-gate'"]},"judge_rubric":{"pass":"工具调用顺序正确、参数完整、工单创建成功、最终响应可追溯","fail":"漏调用关键工具、创建错误工单、越权部署、编造链接或隐藏失败"}}
JSONL
python evalops/run_eval.py
```

## 7. 版本对比：不要只看总分

数据集版本和 Agent 版本都在变化时，最怕出现“总分差不多，但关键场景退化”。因此 compare 工具要按 case、scenario、risk_level 分层输出。

```python
# file: evalops/compare_versions.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def index_by_case(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["case_id"]: row for row in report["results"]}


def main() -> None:
    baseline = load_report(Path("evals/reports/baseline.json"))
    current = load_report(Path("evals/reports/latest.json"))

    base_cases = index_by_case(baseline)
    curr_cases = index_by_case(current)
    common_ids = sorted(set(base_cases) & set(curr_cases))

    regressions = []
    for case_id in common_ids:
        before = base_cases[case_id]
        after = curr_cases[case_id]
        delta = after["score"] - before["score"]
        if delta < 0:
            regressions.append({
                "case_id": case_id,
                "scenario": after["scenario"],
                "risk_level": after["risk_level"],
                "before": before["score"],
                "after": after["score"],
                "delta": round(delta, 4),
                "reason": after["reason"],
            })

    summary = {
        "baseline_score": baseline["overall_score"],
        "current_score": current["overall_score"],
        "score_delta": round(current["overall_score"] - baseline["overall_score"], 4),
        "regression_count": len(regressions),
        "p0_regressions": [r for r in regressions if r["risk_level"] == "P0"],
        "regressions": regressions,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if summary["p0_regressions"] or summary["score_delta"] < -0.02:
        raise SystemExit("eval gate failed")


if __name__ == "__main__":
    main()
```

这个脚本的重点不是复杂算法，而是把门禁失败说清楚：哪个 case、哪个场景、风险级别是什么、相比基线掉了多少、失败原因是什么。

## 8. Go 版 E2E runner：适合接入服务端测试栈

如果团队的服务端测试栈以 Go 为主，可以把 eval runner 做成普通测试命令，在 CI 中和集成测试一起执行。

```go
// file: evalops/go-runner/main.go
package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

type Case struct {
	CaseID           string `json:"case_id"`
	Scenario         string `json:"scenario"`
	RiskLevel        string `json:"risk_level"`
	ExpectedBehavior struct {
		MustCallTools        []string `json:"must_call_tools"`
		MustNotCallTools     []string `json:"must_not_call_tools"`
		FinalResponseContains []string `json:"final_response_contains"`
	} `json:"expected_behavior"`
}

type AgentOutput struct {
	FinalText string
	ToolCalls []string
}

func callAgent(c Case) AgentOutput {
	return AgentOutput{
		FinalText: "已生成测试计划，工单链接：https://sandbox.local/tickets/T-1001，风险项已列出。",
		ToolCalls: []string{"requirement.read", "testplan.generate", "ticket.create"},
	}
}

func contains(items []string, target string) bool {
	for _, item := range items {
		if item == target {
			return true
		}
	}
	return false
}

func score(c Case, out AgentOutput) (bool, string) {
	for _, tool := range c.ExpectedBehavior.MustCallTools {
		if !contains(out.ToolCalls, tool) {
			return false, fmt.Sprintf("missing required tool: %s", tool)
		}
	}
	for _, tool := range c.ExpectedBehavior.MustNotCallTools {
		if contains(out.ToolCalls, tool) {
			return false, fmt.Sprintf("forbidden tool was called: %s", tool)
		}
	}
	for _, phrase := range c.ExpectedBehavior.FinalResponseContains {
		if !strings.Contains(out.FinalText, phrase) {
			return false, fmt.Sprintf("final response missing phrase: %s", phrase)
		}
	}
	return true, "passed"
}

func main() {
	path := "evals/datasets/agent-core/v2026.07.07/cases.jsonl"
	file, err := os.Open(path)
	if err != nil {
		panic(err)
	}
	defer file.Close()

	passed := 0
	total := 0
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		var c Case
		if err := json.Unmarshal([]byte(line), &c); err != nil {
			panic(err)
		}
		ok, reason := score(c, callAgent(c))
		total++
		if ok {
			passed++
		}
		fmt.Printf("case=%s scenario=%q passed=%v reason=%s\n", c.CaseID, c.Scenario, ok, reason)
	}
	if err := scanner.Err(); err != nil {
		panic(err)
	}

	passRate := float64(passed) / float64(total)
	fmt.Printf("pass_rate=%.2f passed=%d total=%d\n", passRate, passed, total)
	if passRate < 1.0 {
		os.Exit(1)
	}
}
```

运行方式：

```bash
mkdir -p evalops/go-runner
go run ./evalops/go-runner
```

Go runner 的优势是接近服务端工程体系，方便复用已有鉴权、沙箱、日志和 trace client；Python runner 的优势是评测逻辑迭代快，适合先验证规则。

## 9. 与 CI/CD 集成：让评测成为发布链路的一部分

CI/CD 集成的核心原则是：**评测失败要可解释，门禁阈值要可维护，失败报告要能定位到样本和版本**。

下面是一个 GitHub Actions 示例。它会在 PR 上运行 eval，上传报告，并在关键门禁失败时阻断合入。

```yaml
name: agent-eval-gate

on:
  pull_request:
    branches: [main]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip

      - name: Run Agent E2E eval
        run: |
          python evalops/run_eval.py

      - name: Compare with baseline
        run: |
          python evalops/compare_versions.py

      - name: Upload eval report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: agent-eval-report
          path: evals/reports/latest.json
```

实际落地时，还要补充 4 个工程约束：

1. **沙箱隔离**：所有写操作必须打到沙箱，不允许污染生产数据。
2. **幂等键**：每个 case 的外部写操作带 `run_id` 或 `idempotency_key`。
3. **超时预算**：单 case、单 job、整体 workflow 都要有超时，避免 CI 卡死。
4. **结果留档**：保存 `dataset_version`、`agent_version`、`runner_version`、`judge_version`。

## 10. 常见坑：分数好看不等于质量稳定

### 10.1 数据泄漏

如果训练或调参时直接看到了评测集答案，评测分数会虚高。解决方法是把数据集分层：公开开发集用于调试，隐藏门禁集用于发布前验证，线上抽样集用于漂移观察。

### 10.2 Rubric 漂移

同一个样本今天要求“必须调用工具”，下周改成“可以直接回答”，如果没有记录变更原因，分数变化就无法解释。Rubric 变更必须进入 changelog，并触发 baseline 重算。

### 10.3 只看总体分

总体分可能被大量低风险样本稀释。门禁要按风险分层：P0 样本 100% 通过，负样本误通过 0%，核心路径集不能明显下降。

### 10.4 LLM-as-Judge 不稳定

LLM-as-Judge 适合评估开放文本质量，但不适合替代所有规则断言。工具调用、外部状态、权限边界、schema 合法性，应优先用确定性规则判断。

## 11. 思考题

1. 你负责的 Agent 当前有哪些“线上失败后才知道”的场景？它们能否转成带 `case_id`、`expected_behavior`、`external_assertions` 的 E2E 样本？
2. 如果整体 eval 分数提升 3 pp，但 P0 写操作样本失败 1 条，你会允许发布吗？为什么？
3. 当前数据集的标签变化有没有 changelog？如果某条样本从 fail 改为 pass，半年后能否解释原因？
4. LLM-as-Judge 和确定性规则分别适合评估哪些内容？在你的系统里，哪些断言必须从 Judge 下沉到规则或外部状态校验？

## 今日小结

Agent 评测数据集不是“跑一次就丢”的测试材料，而是质量基础设施。它把真实用户任务、历史事故、边界条件、负样本和发布规则沉淀下来，让每次变更都能被回放、比较和追责。

今天可以先从 3 件事做起：整理 20 条最高风险 E2E 样本；为每条样本补齐 `case_id`、`risk_level`、`expected_behavior` 和 `external_assertions`；把这批样本接入 PR 评测门禁。等这条链路跑通之后，再扩展标注流程、IAA 统计、DVC/LFS 版本管理和线上漂移监控。

真正成熟的 EvalOps，不是追求一个漂亮分数，而是让团队在每次发布前都能明确回答：**这次改动有没有伤到核心用户场景，证据在哪里，失败后该由谁修**。
