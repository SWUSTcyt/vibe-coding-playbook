# Plan Document: v0.4 安装闭环与治理瘦身

> 约束：< 500 tokens。这是**当前运行状态**的唯一真源，只写当前 Milestone 与活跃项。
> 方法论全文见 `docs/AI 编程方法论 v1.2 — 可操作版.md`；改进历史见 `docs/improvements/CHANGELOG.md`。

## 目标

修复 playbook 安装/同步断链，并以最小增量补上 Spec 生命周期、轻量 AC 关联与外部写操作授权约束。

## 活跃 Issue

| Issue | P0 摘要 | 状态 |
|---|---|---|
| 0 安装闭环 | `--install` 装齐 skill+模板；`--check` 查内容漂移与模板缺失 | done |
| 0.5 语义修复 | P0-P3 语义一致；PLAN 定位为当前运行状态真源 | done |
| 1' Spec 生命周期 | Draft/Frozen/Verified/Superseded + parent 字段 | done |
| 2' 轻量 AC 关联 | Spec 可编号 AC，Issue 可声明 implements/accepts | done |
| 3' 授权与 retro 分型 | 外部写操作分权；retro 分事实/推断/建议/限制 | done |

## 已确定的技术决策

- Skill 真源只有 `skills/`，工具目录为副本，靠 `scripts/sync-skills.py` 生成
- 安装到项目必须同时分发 `templates/`，否则 skill 引用断链

## 不做的事

- 不做 REQ→AC→Issue→Test 全链路机器门禁、不引入 `traceability.yaml`
- 不做 token/返工率自动统计

> 注：原「不新增 release-publish skill」已随复盘 P0-5 调整——新增 `verify-release`（发布/合并安全 + 协作感知），见 `docs/improvements/CHANGELOG.md`。

## 验收分级

P0：阻塞必修 / P1：本次必修 / P2：后续 PR / P3：可忽略

> **P0 验收硬规则**：每个 P0 验收项必须包含至少一条**真实端到端验证路径**。
> 跑不了只能标 **blocked**，不能标 done。详见 `docs/e2e-verify-guide.md`。
