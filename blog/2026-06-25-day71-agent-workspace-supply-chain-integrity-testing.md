---
title: "每日 AI 学习笔记｜Day 71：Agent 工作区供应链与依赖完整性测试"
date: 2026-06-25
authors: [xiaoai]
tags: [learning-notes, AI, QA, Agent, Security, Supply-Chain, SBOM, SLSA, Kubernetes]
---

今天进入一个更贴近生产事故的主题：**Agent 工作区供应链与依赖完整性测试**。很多 Agent 任务不是只在模型里完成，而是会拉取仓库、安装依赖、执行脚本、构建镜像、调用外部 CLI。只要工作区里的依赖、脚本、镜像或缓存被污染，Agent 就可能在“看似正常完成任务”的过程中执行恶意代码，泄露凭证，或者把不可信产物推向生产链路。

{/* truncate */}

<callout icon="bulb" bgc="5">
**核心总结**：今天的重点是把 AI Agent 的测试边界从“输入输出是否正确”扩展到“工作区是否可信、依赖是否可追溯、产物是否可验证”。对资深测开来说，供应链测试不能只检查 `package-lock.json` 或镜像扫描结果，而要设计端到端业务链路：用户触发 Agent 处理仓库 → Agent 拉取代码并安装依赖 → 执行测试/构建/发布动作 → 生成可交付结果。沿链路验证依赖来源、版本锁定、脚本执行权限、缓存隔离、SBOM 生成、签名校验和审计日志，才能发现真实生产中最容易被忽略的投毒风险。
</callout>

## 1. 为什么 Day 71 要关注 Agent 工作区供应链

传统自动化测试通常运行在相对固定的 CI 环境中，依赖和镜像由团队维护。但 Agent 场景更动态：它可能临时克隆仓库、根据 README 安装工具、读取用户上传文件、生成脚本并执行，甚至根据报错自动搜索解决方案。

这带来三个变化：

1. **执行路径更开放**：Agent 会根据上下文自主选择命令，恶意脚本更容易混入正常流程。
2. **依赖来源更多样**：代码仓库、包管理器、容器镜像、二进制工具、MCP 工具和用户附件都可能成为入口。
3. **结果更容易被信任**：一旦 Agent 输出“测试通过”“构建成功”，后续系统可能直接采纳。

因此，今天的目标不是做一次漏洞扫描，而是建立一套面向 Agent 工作区的供应链完整性验证方法。

## 2. 核心理论：Agent 供应链风险的五个层次

### 2.1 代码来源层

代码来源层回答的问题是：**Agent 正在处理的代码是否来自预期位置？** 测试时要确认仓库 URL、分支、commit、tag、submodule 是否可信，是否存在同名仓库、分支漂移、浅克隆丢失历史、fork 替换等风险。

### 2.2 依赖解析层

依赖解析层关注 `go.mod`、`requirements.txt`、`package-lock.json`、`uv.lock`、`Cargo.lock` 等文件。核心风险是依赖混淆、版本漂移、锁文件缺失、安装脚本副作用，以及私有源与公网源优先级不一致。

### 2.3 脚本执行层

Agent 很容易执行 `make test`、`npm install`、`pip install -e .`、`go generate`、`preinstall`、`postinstall` 等命令。测试重点不是命令能否运行，而是命令是否会读取敏感文件、访问外网、修改 Git 配置、写入系统路径或启动后台进程。

### 2.4 构建产物层

构建产物层关注镜像、二进制、测试报告、覆盖率文件、发布包是否可追溯。理想状态下，每个产物都能回答：由哪个 commit、哪些依赖、哪个构建环境、哪个 Agent 身份生成。

### 2.5 工作区隔离层

Agent 的工作区通常包含源码、缓存、日志、临时文件和凭证上下文。测试时必须验证不同任务、不同用户、不同仓库之间是否存在缓存复用、文件残留、环境变量泄露或权限继承。

## 3. E2E 测试场景设计：从用户请求到产物审计

下面用端到端方式组织测试，而不是孤立验证某个包管理器命令。

<table header-row="true" header-col="false" col-widths="160,260,300,300">
  <tr>
    <td>场景</td>
    <td>用户真实触发</td>
    <td>关键步骤</td>
    <td>最终验证点</td>
  </tr>
  <tr>
    <td>依赖投毒拦截</td>
    <td>用户要求 Agent 修复仓库测试失败</td>
    <td>Agent 克隆仓库，安装依赖，执行测试并生成修复建议</td>
    <td>✅ 未安装未锁定依赖；✅ 发现异常安装脚本；✅ 报告中标出风险依赖</td>
  </tr>
  <tr>
    <td>工作区残留防护</td>
    <td>连续处理两个不同用户的仓库任务</td>
    <td>任务 A 生成缓存和日志，任务 B 在新工作区运行</td>
    <td>✅ B 无法读取 A 的文件；✅ 缓存按任务隔离；✅ 日志不包含跨用户信息</td>
  </tr>
  <tr>
    <td>镜像完整性验证</td>
    <td>用户要求 Agent 构建并部署测试镜像</td>
    <td>Agent 构建镜像，生成 SBOM，执行镜像扫描和签名校验</td>
    <td>✅ 镜像 digest 固定；✅ SBOM 可追溯；✅ 未签名镜像禁止进入发布步骤</td>
  </tr>
  <tr>
    <td>脚本副作用检测</td>
    <td>用户要求 Agent 运行项目自带测试脚本</td>
    <td>Agent 执行 make 或 npm 脚本，并采集文件、网络、进程行为</td>
    <td>✅ 异常外连被拦截；✅ 敏感路径读取被记录；✅ 后台进程被清理</td>
  </tr>
</table>

## 4. 工程实践一：用 Python 做依赖锁定与异常脚本检查

下面示例用于在 Agent 执行安装命令前做轻量检查。它不是替代安全扫描，而是作为 E2E 链路中的前置质量门禁。

```python
#!/usr/bin/env python3
"""
workspace_guard.py
在 Agent 工作区中检查依赖锁文件、危险安装脚本和可疑源配置。
"""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass, asdict

ROOT = pathlib.Path.cwd()

LOCK_FILES = {
    "python": ["requirements.txt", "uv.lock", "poetry.lock", "Pipfile.lock"],
    "node": ["package-lock.json", "pnpm-lock.yaml", "yarn.lock"],
    "go": ["go.mod", "go.sum"],
}

DANGEROUS_SCRIPT_PATTERNS = [
    r"curl\s+[^|]+\|\s*(bash|sh)",
    r"wget\s+[^|]+\|\s*(bash|sh)",
    r"rm\s+-rf\s+(/|\$HOME|~)",
    r"chmod\s+777",
    r"export\s+.*TOKEN",
    r"/etc/passwd",
    r"\.ssh/",
]

@dataclass
class Finding:
    severity: str
    category: str
    file: str
    message: str


def exists_any(names: list[str]) -> bool:
    return any((ROOT / name).exists() for name in names)


def scan_text_file(path: pathlib.Path) -> list[Finding]:
    findings: list[Finding] = []
    if path.stat().st_size > 2 * 1024 * 1024:
        return findings
    text = path.read_text(errors="ignore")
    for pattern in DANGEROUS_SCRIPT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(Finding(
                severity="high",
                category="dangerous-script",
                file=str(path.relative_to(ROOT)),
                message=f"匹配到高风险脚本模式：{pattern}",
            ))
    return findings


def scan_package_json() -> list[Finding]:
    path = ROOT / "package.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    findings: list[Finding] = []
    scripts = data.get("scripts", {})
    for name in ["preinstall", "install", "postinstall", "prepare"]:
        if name in scripts:
            findings.append(Finding(
                severity="medium",
                category="npm-lifecycle-script",
                file="package.json",
                message=f"发现 npm 生命周期脚本 {name}: {scripts[name]}",
            ))
    return findings


def main() -> int:
    findings: list[Finding] = []

    if (ROOT / "package.json").exists() and not exists_any(LOCK_FILES["node"]):
        findings.append(Finding("high", "missing-lock", "package.json", "Node 项目缺少锁文件"))
    if (ROOT / "pyproject.toml").exists() and not exists_any(LOCK_FILES["python"]):
        findings.append(Finding("medium", "missing-lock", "pyproject.toml", "Python 项目缺少锁文件"))
    if (ROOT / "go.mod").exists() and not (ROOT / "go.sum").exists():
        findings.append(Finding("high", "missing-lock", "go.mod", "Go 项目缺少 go.sum"))

    for name in ["Makefile", "package.json", "scripts/install.sh", "scripts/test.sh"]:
        path = ROOT / name
        if path.exists() and path.is_file():
            findings.extend(scan_text_file(path))

    findings.extend(scan_package_json())

    print(json.dumps([asdict(item) for item in findings], ensure_ascii=False, indent=2))
    return 1 if any(item.severity == "high" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
```

在 CI 或 Agent 执行器中，可以把它放在安装依赖之前：

```bash
python3 workspace_guard.py
pip install -r requirements.txt
pytest -q
```

## 5. 工程实践二：Go 侧记录工具执行审计链路

Agent 执行命令时，建议把每一次工具调用都记录成可审计事件。下面是一个简化版 Go 示例，用于包装命令执行并输出结构化日志。

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"time"
)

type ExecAudit struct {
	TaskID      string   `json:"task_id"`
	UserID      string   `json:"user_id"`
	WorkspaceID string   `json:"workspace_id"`
	Command     []string `json:"command"`
	StartedAt   string   `json:"started_at"`
	DurationMS  int64    `json:"duration_ms"`
	ExitCode    int      `json:"exit_code"`
}

func runWithAudit(ctx context.Context, taskID, userID, workspaceID string, args []string) error {
	start := time.Now()
	cmd := exec.CommandContext(ctx, args[0], args[1:]...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	exitCode := 0
	if err != nil {
		exitCode = 1
		if exitErr, ok := err.(*exec.ExitError); ok {
			exitCode = exitErr.ExitCode()
		}
	}

	audit := ExecAudit{
		TaskID:      taskID,
		UserID:      userID,
		WorkspaceID: workspaceID,
		Command:     args,
		StartedAt:   start.Format(time.RFC3339),
		DurationMS:  time.Since(start).Milliseconds(),
		ExitCode:    exitCode,
	}
	_ = json.NewEncoder(os.Stdout).Encode(audit)
	return err
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	if err := runWithAudit(ctx, "task-71", "user-demo", "ws-immutable-001", []string{"go", "test", "./..."}); err != nil {
		fmt.Fprintf(os.Stderr, "command failed: %v\n", err)
		os.Exit(1)
	}
}
```

这个审计链路在排查供应链问题时很关键：当某个测试报告异常通过或构建产物被污染时，我们需要回放 Agent 到底执行了哪些命令、在哪个工作区执行、以什么身份执行。

## 6. 工程实践三：K8s 中的工作区隔离策略

对于运行在 Kubernetes 中的 Agent，建议把每个任务放进短生命周期 Pod，并默认开启只读根文件系统、最小权限 ServiceAccount 和网络出口控制。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: agent-task-day71
  labels:
    app: agent-runner
    task-id: day71-demo
spec:
  restartPolicy: Never
  serviceAccountName: agent-runner-low-privilege
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: runner
      image: ghcr.io/example/agent-runner@sha256:replace-with-real-digest
      command: ["/bin/sh", "-lc"]
      args:
        - |
          python3 workspace_guard.py
          go test ./...
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
      env:
        - name: TASK_ID
          value: day71-demo
      volumeMounts:
        - name: workspace
          mountPath: /workspace
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: workspace
      emptyDir: {}
    - name: tmp
      emptyDir: {}
```

关键点是：镜像使用 digest，而不是浮动 tag；工作区用 `emptyDir` 跟随 Pod 生命周期销毁；默认不挂载宿主机路径；敏感 Secret 只在确实需要的步骤注入。

## 7. 质量门禁：供应链完整性的最低通过线

一个可落地的 Agent 供应链质量门禁可以从以下规则开始：

1. **来源固定**：仓库必须固定到 commit SHA；容器镜像必须固定到 digest。
2. **依赖锁定**：存在锁文件，并在安装前检查锁文件是否与 manifest 一致。
3. **脚本可见**：安装和测试脚本必须被记录；高风险模式触发人工确认。
4. **产物可追溯**：构建产物附带 commit、依赖摘要、构建时间、执行身份和工作区 ID。
5. **SBOM 必备**：镜像或二进制发布前必须生成 SBOM，并纳入归档。
6. **签名校验**：关键镜像和发布包必须做签名或摘要校验。
7. **工作区清理**：任务结束后清理临时文件、后台进程、缓存和日志中的敏感字段。

## 8. Playwright 场景：验证 Agent UI 是否暴露供应链风险

如果 Agent 有 Web 控制台，可以用 Playwright 做一条端到端验证：用户提交仓库任务后，页面必须展示风险依赖、命令审计和产物摘要。

```python
from playwright.sync_api import expect, sync_playwright


def test_agent_workspace_supply_chain_report():
    with sync_playwright() as p:
        page = p.chromium.launch(headless=True).new_page()
        page.goto("http://localhost:3000/agent/tasks/new")

        page.get_by_label("Repository URL").fill("https://github.com/example/vulnerable-demo")
        page.get_by_label("Task").fill("Run tests and summarize supply chain risks")
        page.get_by_role("button", name="Start").click()

        expect(page.get_by_text("Workspace guard completed")).to_be_visible(timeout=60_000)
        expect(page.get_by_text("Dependency lock check")).to_be_visible()
        expect(page.get_by_text("Command audit trail")).to_be_visible()
        expect(page.get_by_text("SBOM status")).to_be_visible()
        expect(page.get_by_text("High risk lifecycle script")).to_be_visible()
```

这个用例覆盖的是完整业务链路，而不是单点检查 UI 文案：它从用户提交任务开始，到 Agent 执行检查，再到页面展示最终可观测结果。

## 9. 课后思考题

1. 如果 Agent 需要自动运行用户仓库里的 `make test`，哪些命令必须被禁止或要求人工确认？
2. 依赖锁文件存在是否等于供应链安全？还需要验证哪些信息？
3. 在多租户 Agent 平台中，缓存复用可以提升效率，但它会引入哪些隔离风险？
4. SBOM 生成后如果没有被消费，它的质量价值在哪里会断掉？
5. 你会如何设计一条 E2E 用例，证明“未签名镜像不能进入部署步骤”？

## 10. 今日小结

今天我们把 Agent 测试推进到工作区供应链层面。核心思想是：**Agent 不是只生成文本，它会执行真实命令；只要命令执行链路不可信，最终结果就不能被信任。**

对测开团队而言，落地优先级建议是：先固定来源和依赖，再记录命令审计，随后加入 SBOM、签名校验和工作区隔离。等这些基础能力稳定后，再把供应链风险纳入自动化质量门禁，让 Agent 每一次处理仓库任务时都能留下可追溯、可复现、可审计的证据链。
