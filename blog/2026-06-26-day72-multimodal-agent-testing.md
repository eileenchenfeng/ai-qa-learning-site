---
title: "每日 AI 学习笔记｜Day 72：多模态 Agent 测试与跨模态一致性验证"
date: 2026-06-26
authors: [xiaoai]
tags: [learning-notes, AI, QA, Agent, Multimodal, OCR, Playwright, Kubernetes, E2E]
---

<callout icon="bulb" bgc="5">
**核心总结**：Day 72 的重点是把 Agent 质量评估从文本对话扩展到图片、截图、PDF、表格截图和 UI 状态等多模态输入。资深测开需要关注的不是“模型能不能识别一张图”，而是完整业务链路：用户上传材料 → Agent 解析视觉信息 → 调用工具或页面执行动作 → 生成结构化结果 → 留下可审计证据。测试设计应覆盖 OCR 准确性、视觉定位、跨模态一致性、幻觉抑制、敏感信息遮蔽、失败降级和可观测性，最终用 E2E 场景证明 Agent 在真实工作流中可靠。
</callout>

今天进入 **多模态 Agent 测试与跨模态一致性验证**。很多 AI 测开场景已经不再只处理文本：Agent 可能读取截图定位按钮，解析工单附件里的表格，识别合同 PDF 中的关键字段，或者根据监控大盘截图判断故障范围。视觉输入一旦被误读，后续 API 调用、页面操作和结论报告都会被放大影响。

{/* truncate */}

## 1. 为什么 Day 72 要关注多模态 Agent 测试

文本 Agent 的主要风险通常集中在意图理解、工具调用和结果生成。多模态 Agent 多了一层“感知风险”：它先把图片、截图、扫描件、图表转换成内部语义，再基于这些语义行动。测试时不能只看最终回答是否流畅，而要追踪视觉证据是否真的支撑了行动。

对测开来说，多模态测试有三个变化：

1. **输入更接近真实世界**：截图、照片、PDF 扫描件、表格图片会带来噪声、遮挡、压缩和分辨率差异。
2. **错误更难定位**：最终结论错误可能来自 OCR、视觉定位、上下文推理、工具调用或输出格式任一环节。
3. **验证必须证据化**：测试报告需要记录图片区域、识别文本、坐标、置信度、工具调用参数和最终结果。

## 2. 核心理论：多模态 Agent 的质量分层

### 2.1 感知层：看见了什么

感知层关注 OCR、图像分类、目标检测、图表理解和 UI 元素定位。常见问题包括漏字、错字、坐标偏移、把装饰元素当作可点击控件，以及把图表趋势读反。

### 2.2 对齐层：图像与文本是否一致

用户经常同时给出文字指令和图片证据。例如“把截图里失败的用例整理成表格”。测试要验证 Agent 是否优先使用图片里的事实，而不是凭文字指令猜测；当文字和图片冲突时，要能标记冲突并停止自动行动。

### 2.3 行动层：基于视觉结果做了什么

多模态 Agent 往往会继续调用 Playwright、API、数据库或工单系统。行动层验证重点是：视觉识别结果如何转成操作参数，参数是否可追溯，误识别时是否会触发安全降级。

### 2.4 证据层：结果是否可审计

可审计不是简单保存原图，而是保存“原图区域 → 识别文本/对象 → 推理结论 → 工具调用 → 最终结果”的链路。没有证据链的多模态自动化，很难在失败后做根因分析。

## 3. E2E 测试场景设计：从附件上传到业务结果

下面的用例按真实用户链路组织，单点能力验证下沉到步骤中的中间状态和最终验证点。

<table header-row="true" header-col="false" col-widths="170,260,320,330">
  <tr>
    <td>场景</td>
    <td>用户真实触发</td>
    <td>关键链路</td>
    <td>最终验证点</td>
  </tr>
  <tr>
    <td>截图定位并修复 UI 问题</td>
    <td>用户上传失败页面截图，要求 Agent 定位原因并提交修复建议</td>
    <td>Agent 识别错误提示和按钮位置，打开页面复现，采集 DOM 与网络请求，生成修复方案</td>
    <td>✅ 识别的错误文案与截图一致；✅ Playwright 复现路径可运行；✅ 报告引用截图区域与日志证据</td>
  </tr>
  <tr>
    <td>工单附件表格抽取</td>
    <td>用户上传一张表格截图，要求汇总失败用例和责任模块</td>
    <td>Agent OCR 表格，结构化为 JSON，调用工单 API 补充模块信息，生成统计结论</td>
    <td>✅ 行列未错位；✅ 低置信字段被标注待确认；✅ API 查询参数来自可追溯单元格</td>
  </tr>
  <tr>
    <td>监控大盘截图诊断</td>
    <td>用户上传告警大盘截图，要求判断是否需要升级事故</td>
    <td>Agent 识别指标名称、时间窗口和异常点，查询真实监控 API 对齐截图，输出升级建议</td>
    <td>✅ 截图读数与 API 数据差异在阈值内；✅ 时间窗口不漂移；✅ 缺失指标时不会编造结论</td>
  </tr>
  <tr>
    <td>敏感信息图片处理</td>
    <td>用户上传包含邮箱、token 或手机号的截图，要求生成对外报告</td>
    <td>Agent 识别敏感区域，先脱敏再生成摘要，保留内部审计证据</td>
    <td>✅ 对外文本不包含敏感值；✅ 原图只在受控路径保留；✅ 审计日志记录脱敏规则</td>
  </tr>
</table>

## 4. 工程实践一：用 Python 构建 OCR 结果质量门禁

下面示例模拟一个轻量门禁：输入 OCR 引擎输出的 JSON，检查字段完整性、置信度、坐标合法性和跨字段一致性。真实项目中可以把它接到 Agent 执行链路中，在调用业务 API 前阻断低质量视觉结果。

```python
#!/usr/bin/env python3
"""
multimodal_ocr_gate.py
校验多模态 Agent 的 OCR 结构化结果，适合作为 E2E 链路中的前置质量门禁。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = ["case_id", "status", "module", "owner"]
MIN_CONFIDENCE = 0.82
VALID_STATUS = {"PASS", "FAIL", "SKIP", "BLOCKED"}


@dataclass
class GateIssue:
    level: str
    field: str
    message: str


def inside_image(box: list[int], width: int, height: int) -> bool:
    if len(box) != 4:
        return False
    x1, y1, x2, y2 = box
    return 0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height


def validate_row(row: dict[str, Any], width: int, height: int) -> list[GateIssue]:
    issues: list[GateIssue] = []
    for field in REQUIRED_FIELDS:
        cell = row.get(field)
        if not cell or not str(cell.get("text", "")).strip():
            issues.append(GateIssue("error", field, "字段缺失或为空"))
            continue
        if float(cell.get("confidence", 0)) < MIN_CONFIDENCE:
            issues.append(GateIssue("warning", field, "OCR 置信度低，需要人工确认"))
        if not inside_image(cell.get("box", []), width, height):
            issues.append(GateIssue("error", field, "坐标超出图片范围"))

    status = row.get("status", {}).get("text")
    if status and status.upper() not in VALID_STATUS:
        issues.append(GateIssue("error", "status", f"非法状态值: {status}"))

    case_id = row.get("case_id", {}).get("text", "")
    if case_id and not case_id.startswith("TC-"):
        issues.append(GateIssue("warning", "case_id", "用例编号不符合 TC- 前缀规范"))
    return issues


def main() -> None:
    payload = json.loads(Path("ocr_result.json").read_text(encoding="utf-8"))
    width = int(payload["image"]["width"])
    height = int(payload["image"]["height"])
    all_issues: list[dict[str, str]] = []

    for idx, row in enumerate(payload.get("rows", []), start=1):
        for issue in validate_row(row, width, height):
            item = asdict(issue)
            item["row"] = str(idx)
            all_issues.append(item)

    result = {
        "passed": not any(i["level"] == "error" for i in all_issues),
        "issues": all_issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

示例输入 `ocr_result.json`：

```json
{
  "image": {"width": 1440, "height": 900},
  "rows": [
    {
      "case_id": {"text": "TC-1024", "confidence": 0.96, "box": [20, 120, 160, 148]},
      "status": {"text": "FAIL", "confidence": 0.93, "box": [180, 120, 250, 148]},
      "module": {"text": "checkout", "confidence": 0.89, "box": [270, 120, 390, 148]},
      "owner": {"text": "qa-platform", "confidence": 0.86, "box": [410, 120, 560, 148]}
    }
  ]
}
```

运行方式：

```bash
python3 multimodal_ocr_gate.py
```

在 CI 中可以约定：`error` 直接阻断 Agent 后续工具调用，`warning` 允许生成结果但必须在报告中标记待确认字段。

## 5. 工程实践二：用 Playwright 验证截图定位到页面行为

多模态 Agent 经常根据截图选择页面元素。下面示例把“视觉定位结果”转成 Playwright 的可验证动作，并在点击前做 DOM 语义校验。

```python
import json
from pathlib import Path
from playwright.sync_api import Page, expect


def click_visual_target(page: Page, target_file: str) -> None:
    target = json.loads(Path(target_file).read_text(encoding="utf-8"))
    text = target["text"]
    role = target.get("role", "button")
    confidence = float(target.get("confidence", 0))

    if confidence < 0.85:
        raise AssertionError(f"视觉定位置信度过低: {confidence}")

    locator = page.get_by_role(role, name=text)
    expect(locator).to_be_visible(timeout=5000)
    expect(locator).to_be_enabled()
    locator.click()


def test_agent_visual_click_checkout(page: Page):
    page.goto("https://example.test/cart")
    click_visual_target(page, "visual_target.json")
    expect(page).to_have_url(lambda url: "/checkout" in url)
```

`visual_target.json` 示例：

```json
{
  "text": "去结算",
  "role": "button",
  "confidence": 0.91,
  "source_box": [1120, 740, 1258, 792]
}
```

这个测试的关键不是“能不能点中按钮”，而是把视觉证据和 DOM 语义绑定起来：截图里看到的是“去结算”，页面上也必须存在同名可点击按钮，点击后业务状态要发生预期变化。

## 6. 工程实践三：在 K8s 中隔离多模态处理任务

图片和 PDF 处理通常会引入 OCR 模型、临时文件和原始附件。下面给出一个 Job 模板，用于把多模态解析任务放到受控工作区中运行。

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: multimodal-agent-parse-job
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: parser
          image: registry.example.com/agent/multimodal-parser:2026-06-26
          command: ["python3", "parse_attachment.py"]
          env:
            - name: OUTPUT_DIR
              value: /workspace/output
            - name: REDACT_MODE
              value: strict
          volumeMounts:
            - name: workspace
              mountPath: /workspace
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
      volumes:
        - name: workspace
          emptyDir:
            sizeLimit: 2Gi
```

E2E 验证点包括：任务结束后 `emptyDir` 被释放，输出目录不包含未脱敏原图，容器没有写根文件系统，日志中没有打印 OCR 原始敏感字段。

## 7. 质量指标：不要只看 OCR Accuracy

多模态 Agent 的指标要覆盖感知、行动和结果三个层次。

<table header-row="true" header-col="false" col-widths="180,300,300,260">
  <tr>
    <td>指标</td>
    <td>定义</td>
    <td>采集方式</td>
    <td>建议门槛</td>
  </tr>
  <tr>
    <td>字段级准确率</td>
    <td>关键字段 OCR 文本与人工标注一致的比例</td>
    <td>对比标注集与结构化 JSON</td>
    <td>核心字段 ≥ 98%</td>
  </tr>
  <tr>
    <td>坐标 IoU</td>
    <td>识别框与标注框的重叠程度</td>
    <td>视觉检测结果与标注框计算 IoU</td>
    <td>交互元素 ≥ 0.75</td>
  </tr>
  <tr>
    <td>行动正确率</td>
    <td>基于视觉结果触发的工具调用是否符合业务预期</td>
    <td>回放 Agent trace 与业务断言</td>
    <td>高风险动作 100%</td>
  </tr>
  <tr>
    <td>证据覆盖率</td>
    <td>最终结论中可追溯到图片区域和工具调用的比例</td>
    <td>检查报告中的 source_box、trace_id、api_request_id</td>
    <td>关键结论 100%</td>
  </tr>
</table>

## 8. 常见陷阱与防护策略

### 8.1 把截图当成事实源，却没有二次校验

监控大盘截图可能过期，页面截图可能来自旧版本。高风险场景中，Agent 应该用截图做线索，再查询真实系统数据确认。

### 8.2 只评估最终答案，不评估中间视觉证据

如果只看 Agent 最终输出，很容易漏掉“结论碰巧正确，但识别过程错误”的问题。建议在 trace 中记录每个视觉字段的 `source_box`、`confidence` 和后续使用位置。

### 8.3 忽略隐私与合规

截图往往包含邮箱、手机号、订单号、token、客户名称。多模态链路要先脱敏再生成外发内容，对原始附件设置保存期限和访问控制。

## 9. 课后思考题

1. 如果 Agent 从截图中识别出一个金额，并据此调用退款 API，你会设计哪些 E2E 断言来防止误操作？
2. 当用户文字描述和图片内容冲突时，Agent 应该继续执行、询问用户，还是生成风险报告？请给出你的判断规则。
3. 多模态测试标注集应该如何覆盖低分辨率、暗色模式、遮挡、水印、旋转和压缩噪声？
4. 在你的团队里，哪些现有自动化用例可以升级为“截图/附件输入 → Agent 行动 → 业务结果”的 E2E 场景？

## 10. 今日小结

Day 72 的核心是：多模态 Agent 的质量不止取决于视觉模型能力，更取决于感知结果能否安全地进入业务行动链路。测试设计要从真实用户触发出发，把图片解析、跨模态对齐、工具调用、数据脱敏和审计证据串成完整 E2E 场景。下一步可以继续扩展到 Agent 评测基准设计，把文本、工具、视觉和业务结果统一纳入可回放的 EvalOps 流程。
