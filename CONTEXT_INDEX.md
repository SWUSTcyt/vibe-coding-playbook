# CONTEXT_INDEX

> Agent 信息索引：需要什么读什么，不要一次性灌入全部上下文。
> 跨工具入口：`AGENTS.md`（三铁律 + 五层 + skill 调用指引，Cursor/Claude Code/Codex 均识别）。

## 方法论

> 唯一真源（Single Source of Truth）：`docs/AI 编程方法论 v1.2 — 可操作版.md`（人读完整版）。
> 给 Agent 用的可执行版本已落为 `skills/` 与 `AGENTS.md`，不再维护分层副本。

| 需要什么 | 读这个 |
|---|---|
| 完整方法论（唯一真源，人读） | `docs/AI 编程方法论 v1.2 — 可操作版.md` |
| 总览 & 铁律 & 速览表 | `README.md` |
| 跨工具入口（铁律+五层+skill 指引） | `AGENTS.md` |
| SKILL.md 写作规范 | `reference/SKILL-writing-guide.md` |
| 参考用第三方 skill | `reference/vendored-skills/`（vendored，仅借鉴） |

## 模板

| 场景 | 模板 |
|---|---|
| 需求规格评审 | `templates/spec-template.md` |
| 轻量计划（<500 tokens） | `templates/plan-document-template.md` |
| 拆任务 Issue | `templates/issue-template.md` |
| Milestone 定义 | `templates/milestone-template.md` |
| PR 验收摘要 | `templates/pr-summary-template.md` |
| Session 摘要 | `templates/session-summary-template.md` |

## 流程 Skill（真源，按阶段调用）

| 阶段 | Skill |
|---|---|
| Plan：需求评审 | `skills/plan-spec/SKILL.md` |
| Plan：拆分 + 验收前置 | `skills/plan-breakdown/SKILL.md` |
| Execute：开发 | `skills/execute-implement/SKILL.md` |
| Verify：测试 | `skills/verify-test/SKILL.md` |
| Verify：审查验收 | `skills/verify-review/SKILL.md` |
| Observe：可观测/降质检测 | `skills/observe-session/SKILL.md` |
| Improve：提炼改进 | `skills/improve-retro/SKILL.md` |

## Agent 角色（Claude Code subagents）

| 角色 | 定义文件 |
|---|---|
| explore（调研） | `.claude/agents/explore.md` |
| plan（规划） | `.claude/agents/plan.md` |
| implement（开发） | `.claude/agents/implement.md` |
| review（审查） | `.claude/agents/review.md` |
| CI watcher（CI 监控） | `.claude/agents/ci-watcher.md` |

> Cursor 加载 `.cursor/skills/`，Claude Code 加载 `.claude/skills/` 与 `.claude/agents/`；
> 二者均由 `skills/` 真源经 `scripts/sync-skills.py` 生成。

## 运行时文档

| 用途 | 路径 |
|---|---|
| playbook 自举计划（已完成归档） | `docs/plans/phase-1-migration.md` |
| 问题自动记录 | `docs/issues-log.md` |
| Session 摘要 | `docs/session-summaries/` |
| 改进记录 | `docs/improvements/CHANGELOG.md` |
| E2E 验证指南 | `docs/e2e-verify-guide.md` |
| 流程 Skill 真源 | `skills/` |
