# Skills 6.X Optimization Plan（执行版）

**目标**：基于 Superpowers v6.X 的改进点，对 `vibe-coding-playbook` 核心 skill 做定向增量优化，提升审查流程、子代理协同与验证一致性，同时保持跨工具兼容。

## 参考版本与直接对比

- 当前参考基线：`reference/vendored-skills/superpowers/`（v6.0.x，约 2026-06-19 clone）
- 直接对比版本：`reference/vendored-skills/superpowers@6.1.1/`（v6.1.1，2026-07-06 临时 clone）
- 对比结论（关键文件）：
  - `subagent-driven-development/SKILL.md`：任务台账路径更稳定（`.superpowers/sdd/progress.md`）+ 清理/恢复说明
  - `using-superpowers/SKILL.md`：提示词大幅压缩（更少 token，更聚焦规则）
  - `writing-skills/SKILL.md`：删减平台路径细节，保留核心写作原则
  - `requesting-code-review`、`receiving-code-review`、`verification-before-completion`：无实质变化

## 已落地变更（字段级）

### 1) verify-review（审查流程）
- 输出格式升级为 **Review Packet**：结论 / P0 / P1 / 必须修改 / 建议 / **证据引用**
- 流程补充 **单审查员双裁决**：规则裁决 + 工程裁决
- 常见错误新增：`无证据下结论 → 退回重审`

### 2) execute-implement（子代理协同）
- 新增小节：**子代理 dispatch 契约**
  - 必须声明 model
  - 必须说明审查边界（P0/P1 拦截、P2/P3 建议）
  - 禁止指示审查员忽略问题（只能补充证据）
- 任务台账路径建议对齐 v6.1.1：`.superpowers/sdd/progress.md`
- 常见错误新增：`dispatch 未写边界 → 审查漂移`

### 3) verify-test（验证一致性）
- P0 E2E 硬规则细化：真实端到端验证必须跑通；跑不了则 blocked
- blocked 判定必须写明：缺什么 / 替代验证 / 解除条件
- 常见错误新增：`把 L1 冒烟当功能验证 → 假绿灯`

### 4) SKILL-writing-guide（写作规范）
- 在「让形式匹配失败类型」后补 **可执行样例（最小句式）**
- 头部新增参考基线说明：基于 v6.0.x，已对照 v6.1.1 做增量优化

## 一致性与同步

- 已执行 `python scripts/sync-skills.py`
- 已校验：`.cursor/skills/`、`.claude/skills/` 与 `skills/` 真源 diff 为 0（仅 CRLF 警告）

## 验收结论

- P0：verify-review 输出含「证据引用」字段
- P0：execute-implement 含「子代理 dispatch 契约」
- P1：受影响 skill 常见错误新增至少 1 条 v6.X 相关条目
- P1：同步后跨工具副本一致

## 后续建议（可选）

- 将 `superpowers@6.1.1/` 仅作对比存档（不提交），避免仓库体积膨胀
- 若后续 superpowers 再升级，优先复查 `subagent-driven-development` 与 `using-superpowers`
