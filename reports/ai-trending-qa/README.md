# Daily AI Trending QA Report

这个目录用于保存每天自动生成的「GitHub AI Trending 测开分析报告」。

- 生成逻辑：`scripts/github_ai_qa_analyzer.py`
- 自动化工作流：`.github/workflows/daily-ai-trending-qa-report.yml`
- 产物路径：
  - `reports/ai-trending-qa/YYYY-MM-DD/report.md`
  - `reports/ai-trending-qa/YYYY-MM-DD/repos.json`

说明：
- 工作流默认按 **Asia/Shanghai** 的日期生成（每天 08:10 自动跑，cron 使用 UTC）。
- `repos.json` 是原始数据快照，`report.md` 是面向 QA/测开视角的结构化分析报告。
