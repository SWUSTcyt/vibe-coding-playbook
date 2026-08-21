# Plan Document: 人读导出与口径分离

> 约束：< 500 tokens。这是**当前运行状态**的唯一真源，只写当前 Milestone 与活跃项。
> 执行以 `skills/` 为准。改进历史见 `docs/improvements/CHANGELOG.md`。

## 目标

无活跃开发 Issue。人读方法论已从 skills 导出；v1.2 迁入稿已冻结归档。

## 活跃 Spec

（无）

## 活跃 Issue

| Issue | P0 摘要 | 依赖 |
|---|---|---|
| — | 无 | — |

## 已确定的技术决策

- 执行真源只有 `skills/`；工具目录是副本
- `--install` 同时分发模板和被引用的 `reference/*.md`
- 人读导出：`docs/AI 编程方法论 — 人读版.md`（Agent 勿读，不反向约束 skills）

## 不做的事

- 不做 REQ→AC→Issue→Test 全链路机器门禁、不引入 `traceability.yaml`
- 不做 token/返工率自动统计
- 不把人读长文写入 Agent 启动路径

## 验收分级

P0：阻塞必修 / P1：本次必修 / P2：后续 PR / P3：可忽略

> **P0 验收硬规则**：每个 P0 验收项必须包含至少一条**真实端到端验证路径**。
> 跑不了只能标 **blocked**，不能标 done。详见 `docs/e2e-verify-guide.md`。
