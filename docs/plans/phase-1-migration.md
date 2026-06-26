# Phase 1: 方法论落地到仓库（已完成，归档）

**目标：** 把飞书文档 v1.2 转化为可执行的本地 playbook。

> **状态：已全部完成并归档。** 这是 playbook 自举计划，7 个 Issue 均 done。
> 后续里程碑（M0 收集参考 → M1 定稿 → M2 Skill 真源 → M3 跨工具 → M4 试点验证 → M5 收口）
> 的进展记录在 `docs/improvements/CHANGELOG.md`。本文件仅作历史留存。

## 活跃 Issue

| # | 任务 | 依赖 | P0 | 状态 |
|---|---|---|---|---|
| 1 | 搭建仓库骨架 | 无 | 目录结构完整 | done |
| 2 | 迁入飞书完整文档 | #1 | 原文在 `docs/` 下 | done |
| 3 | 拆分为五层 methodology 文档 | #2 | 01-06 六个文件 | done |
| 4 | 对齐 5 个 Agent 角色模板 | #2 | 与原文 2.1 一致 | done |
| 5 | 编写 Cursor Rules（三条铁律） | #4 | `.cursor/rules/` 生效 | done |
| 6 | 把方法论五层做成 Skills + AGENTS.md | #5 | `skills/` 7 个 Skill + `AGENTS.md` 可用 | done |
| 7 | 端到端 example walkthrough | #5-#6 | `examples/` 有完整演示 | done |

## 技术决策（不可回调）

- 文档格式：Markdown（UTF-8）
- 原文保留：`docs/AI 编程方法论 v1.2 — 可操作版.md`
- ~~分层副本：`docs/methodology/01-06.md`~~（M2/M3 已删除，与真源重复；改由 `skills/` + `AGENTS.md` 承载可执行版本）
- 信息索引：`CONTEXT_INDEX.md` 作为 Agent 入口
