---
name: improve-retro
description: 问题记录与定期总结提炼。Use when 同一问题反复出现、Milestone 结束、或需要把踩过的坑提炼成可复用规则/新 Skill 时。也适用于定期复盘、更新验收标准或拆分策略、沉淀方法论的场景，以及现有 Skill 解决不了某个问题、要找现成外部技能的场景。
---

# Improve-Retro：持续改进

## 概述

把执行中反复出现的问题自动记录下来，定期总结，提炼成可复用规则、新 Skill 或方法论更新，形成闭环。

**核心原则：** 同样的坑不踩第二次。改进必须沉淀为「下次会自动生效」的东西（规则/Skill/标准），而非一次性口头总结。

## 何时使用

- 同一问题反复出现 ≥ 2 次
- CI/测试失败且非显而易见原因
- Review 被退回 ≥ 2 次
- Milestone 结束 / 每完成 10 个 Issue / 每周固定时间 → 定期总结
- 问题不在现有 8 个 Skill 的职责里，又反复出现或卡住任务 → 先查有没有现成的外部技能（见下方）

## 问题自动记录

满足触发条件时追加到 `docs/issues-log.md`，格式：

```markdown
### [日期]: 问题标题
- **出现位置**: #3, #5
- **事实(fact)**: 可从日志/测试/页面/用户明确消息复核的原始事实（报错原文、命令输出、文件:行号）
- **推断(inference)**: 对成因的判断——标明这是推断，不是事实
- **决定(decision)**: 项目负责人/需求方明确选择的范围或策略（谁定的、定了什么）
- **外部待办(external_blocker)**: 需供应商/律师/部署人员/用户继续提供的证据
- **建议(suggestion)**: 打算怎么改
- **限制(limit)**: 环境/权限/信息不足导致无法验证的部分
- **下一步(next_owner / due_at)**: 谁在什么时间前做下一动作
```

**为什么要分这五类：** 复盘里的信息来自四个不同来源——你观察到的（fact）、你推测的（inference）、别人拍板的（decision）、还没拿到的外部证据（external_blocker）。混在一起，一次页面观察会被当成产品事实，一个外部 pending 会被当成已完成。

**硬规则（防状态污染）：`inference` 和 `external_blocker` 绝不能被写进任何 `verified` / `complete` / `done` 字段。** 一个结论只要它的依据还停在推断或外部待办，它的终态就只能是 `unverified` / `pending_external`，不能靠改措辞降级成通过。

## 定期总结提炼流程

1. 读取本期所有问题记录
2. 分类：重复出现的 vs 一次性的
3. 提炼：哪些固化为 Skill？哪些更新验收标准？哪些调整拆分策略？
4. 输出改进清单，逐条更新到对应文档/Skill，并记入 `docs/improvements/CHANGELOG.md`

## 进 playbook 的门槛

改动 playbook（通用规则）比改项目文档影响面大得多，所以要卡一道：

- **只有事实支撑的规则才进 playbook。** 纯推断先留在项目 `docs/issues-log.md`，等第二次遇到再提。
- **至少满足其一**：同一问题在不同场景复现过一次（回放），或者有第二条独立证据。
- **栈特定的坑不进 playbook。** 「某框架某版本的 API 变了」属于项目经验；「重构要按关注点逐个剥离」才是通用规则。
- 拿不准就问自己：换一个技术栈、换一个项目，这条还成立吗？不成立就别往上提。

## 现有 Skill 解决不了时

出发点仍是现有 8 个 Skill。需求不清、任务太大、没有测试、审查不过，先回到对应的 Skill。两条都满足才往外找：问题不在这 8 个的职责里；已经出现两次以上，或卡住了当前任务。

写新 Skill 之前，先按 `reference/external-skills-guide.md` 查有没有现成的外部技能。

- Agent 只提一个候选，写清它解决什么、会改哪些文件、哪些没验证过。热度只作参考。
- 用户明确说出在哪个项目装哪一个，才安装。只装进碰到问题的项目，不替换现有 Skill，不整套安装。
- 试用结果记进项目的 `docs/issues-log.md`。试用改变了实现或测试，才按上面的门槛考虑写回 playbook；一次试用不够。

## 产出

- `docs/issues-log.md` 问题记录
- 改进清单 + `docs/improvements/CHANGELOG.md` 条目
- 新增/更新的 Skill 或验收标准

## 提炼为新 Skill 时

参考 `reference/SKILL-writing-guide.md` 的写作规范与 `reference/vendored-skills/superpowers/skills/writing-skills`。

## 常见错误

- **总结停在口头** → 下次照样犯。必须落成规则/Skill/标准更新。
- **重复与一次性不分** → 把偶发问题也固化成规则，增加负担。先分类再提炼。
- **把推断写成事实** → 据此改规则，方向可能整个是错的。没有证据的成因判断标进「推断」栏。
- **栈特定经验塞进 playbook** → 通用规则被某框架某版本的细节污染，换项目就失效。栈特定留在项目侧。

## 参考

- 记录文件：`docs/issues-log.md`、`docs/improvements/CHANGELOG.md`
- 上一步：`skills/observe-session/SKILL.md`
- 写 Skill 规范：`reference/SKILL-writing-guide.md`
- 外部技能查找与试用：`reference/external-skills-guide.md`
