# GitHub Release 草稿（可直接粘贴到 Releases）

**标题建议**：基于 Superpowers v6.1.1 的增量优化（审查/协同/验证）  
**标签建议**：`v0.2.0`（你当前若无版本号，可按里程碑命名）

## 摘要
本次发布基于对 **Superpowers v6.1.1** 的直接对比，针对 playbook 核心 skill 做了定向增量优化，聚焦三点：  
1) 审查流程更硬（证据化）  
2) 子代理协同更清晰（dispatch 契约）  
3) 验证标准更一致（P0 E2E 与 blocked 判定）

## 主要变更
### 1) verify-review：审查更可复核
- 输出升级为 **Review Packet**（结论 / P0 / P1 / 必须修改 / 建议 / 证据引用）
- 增加 **单审查员双裁决**：规则裁决 + 工程裁决
- 常见错误新增：无证据下结论 → 退回重审

### 2) execute-implement：子代理协同更明确
- 新增 **子代理 dispatch 契约**：必须声明 model / 必须写审查边界 / 禁止指示忽略问题
- 任务台账路径建议对齐 v6.1.1（`.superpowers/sdd/progress.md`）
- 常见错误新增：dispatch 未写边界 → 审查漂移

### 3) verify-test：验证标准更一致
- 细化 **P0 E2E 硬规则**：关键路径必须真实端到端验证
- blocked 判定必须写：缺什么 / 替代验证 / 解除条件
- 常见错误新增：把 L1 冒烟当功能验证 → 假绿灯

### 4) 写作规范与文档
- `reference/SKILL-writing-guide.md`：补「形式匹配失败类型」可执行样例，并明确参考基线（v6.0.x → v6.1.1）
- 新增执行版计划：`docs/plans/skills-6x-optimization-plan.md`
- 改进记录已更新：`docs/improvements/CHANGELOG.md`

## 验证与一致性
- 直接对比：临时 clone `reference/vendored-skills/superpowers@6.1.1/`，与旧版 `superpowers/` 做关键文件 diff
- 同步：执行 `python scripts/sync-skills.py`
- 一致性校验：`.cursor/skills/`、`.claude/skills/` 与 `skills/` diff=0

## 本次提交信息
- **Commit**: `75759fe86989e8b28f03b55671b65927866903f5`
- **Date**: 2026-07-07 00:26:33 +0800
- **Message**: `refactor(skills): 基于 Superpowers v6.1.1 直接对比，增量优化审查/协同/验证规范`

## 变更文件（关键）
- `skills/verify-review/SKILL.md`
- `skills/execute-implement/SKILL.md`
- `skills/verify-test/SKILL.md`
- `.cursor/skills/` 与 `.claude/skills/` 同步副本
- `reference/SKILL-writing-guide.md`
- `docs/improvements/CHANGELOG.md`
- `docs/plans/skills-6x-optimization-plan.md`
- `docs/superpowers-v6-analysis.md`

## 兼容性
- 不改变五层闭环（Plan/Execute/Verify/Observe/Improve）
- 不改变跨工具入口 `AGENTS.md` 的结构（仅增量字段）

## 升级建议
- 如果你在项目中使用本 playbook 的 skill，建议重新同步：
  - `python scripts/sync-skills.py --project /path/to/your-project`
  - 并复制/更新项目根目录 `AGENTS.md`（如已改动）
