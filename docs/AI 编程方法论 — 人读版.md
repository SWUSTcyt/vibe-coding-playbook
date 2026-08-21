# AI 编程方法论 — 人读版

> 本文由仓库里的 `skills/` 整理，给人读。落后以 skills 为准。
> **Agent 不要打开本文。** 执行只读 `AGENTS.md`、`PLAN.md` 与对应 skill。
> 发版后对照 `docs/improvements/CHANGELOG.md` 更新本文，绝不反向改 skills。

对应仓库主线（未打 tag 时以 master 为准）。飞书迁入的冻结稿在 `docs/archive/AI 编程方法论 v1.2 — 可操作版.md`。

---

## 概述

**一句话：用约束对抗熵增。** 让模型在持续运行中不降低自己的标准，稳定地把高质量代码合进去。

### 三条铁律

1. **标准前置，不可回调** — 验收标准写在代码之前，中途不降低。做不完就拆任务，不降标准。
2. **信息触手可及，而非全部塞入** — 按索引按需读取，不一次性灌入全部上下文。
3. **任务足够小，流程足够固化** — 大任务必拆分；重复流程做成 Skill。

### 五层闭环

```
Plan（规划）→ Execute（执行）→ Verify（验证）→ Observe（观测）→ Improve（改进）
     ↑                                                              │
     └──────────────────────────────────────────────────────────────┘
```

| 层 | 核心动作 | 关键产出 |
|---|---|---|
| Plan | Spec（含使用路径）→ Epic → Milestone → Issue | Spec、PLAN.md、P0–P3、证据合同 |
| Execute | 一次一个 Issue；测试前置 | 代码、测试、示例 |
| Verify | 三层测试 + 审查 + 发布门禁 | 测试报告、Review Packet、发布回执 |
| Observe | Session / PR / 降质指标 | 摘要（事实与推断分开） |
| Improve | 问题记录 → 提炼规则或新 Skill | CHANGELOG、新 Skill |

### 文档分工（不要混）

| 角色 | 读什么 |
|---|---|
| Agent 执行 | `skills/`（入口 `AGENTS.md`） |
| 当前项目进度 | `PLAN.md`（≤500 tokens） |
| 人读总览 | 本文（skills 的导出物） |
| 人读历史 | `docs/archive/` 下的 v1.2 迁入稿 |

---

## 一、Plan：从想法到可执行计划

对应 skill：`plan-spec`、`plan-breakdown`。

### 1.1 先按任务规模分档

不是所有需求都走完整 Spec。先分三档，**每一档都停下等你确认边界再动手**：

| 档 | 什么时候 | 走多重 |
|---|---|---|
| spike | 改文案、修单个 bug、试探 | 跳过 Spec，一句话标注意图 |
| bounded | 单个有界功能 | 轻量 Spec：一句话 + 边界 + P0 总纲 |
| architectural | 多能力 / 架构级 / 边界模糊 | 完整流程；多能力先出 Spec 地图 |

拿不准就往上取一档。已有清晰 Spec → 直接拆任务。

### 1.2 Spec 怎么写

- 先问：有几个「用户能独立感知、且能独立上线」的能力？多个就先出 **Spec 地图**，只细化最近 1–2 个。
- 按能力拆，不按代码模块拆。
- 四态：`Draft` → `Frozen`（才能拆 Issue）→ `Verified`（P0/P1 都有证据）→ `Superseded`（语义变更新建版本，不原地改）。
- 对外交付的接口先定契约：输入 / 输出与错误 / 怎么调用；契约用行业标准，要变就加版本。
- **能力矩阵**：每类能力四选一 `verified | planned | unsupported | pending_external`。范围确认 ≠ 已经验收。

模板：`templates/spec-template.md`。

### 1.3 有界面的产品：先定「用户怎么用」

纯后端 / 库 / CLI 跳过。有终端 UI 的产品，冻结前必须写清：

- 核心任务主线（主界面为它让出焦点）
- 关键路径步骤（入口 → … → 完成）
- 主内容 vs 次要内容（历史、设置、日志进侧栏或二级页）
- 对应的端到端 P0 场景

反例：核心问答和对话记录挤在一屏。布局主次是产品决策，要等人确认。

### 1.4 拆分与验收前置

- 有 Spec 地图则 **一份子 Spec = 一个 Epic**，不要另划边界。
- 只细化最近 1–2 个 Milestone / Issue。Issue 若需要 3 轮以上 review 才能合，就太大了。
- P0 阻塞必修 / P1 本次必修 / P2 后续 PR / P3 可忽略。**中途不降级。**
- 有 UI 的 Milestone 要写「用户使用路径增量」，映射回 Spec 的路径步骤。
- `PLAN.md` 只写当前 Milestone 与活跃项，不当 Spec 目录。

### 1.5 证据合同与外部依赖

验收标准回答「要做到什么」；证据合同回答「凭什么算做到了、做不到停在哪」。

P0/P1 Issue 至少挂一份证据合同：`source_of_truth`、`required_fields`、`fail_closed_state`。**「模型说已核验」不能当真源。** 缺这三项不得标完成。

代码写完 ≠ Issue 完成。外部条件（条款、盲测、部署）要在开始时登记依赖；缺则拆成「本地实现完成」+ `pending_external`，总进度不得显示完成。

---

## 二、Execute：一次做对一个 Issue

对应 skill：`execute-implement`。

- 一次只做一个 Issue。编码前先出测试计划（见下一章）。
- 信息按 `CONTEXT_INDEX.md` 按需读，不灌全库。
- **外部写操作分权**：允许写代码 ≠ 允许改远端。`commit` / `push` / 开 PR / `merge` / 打 tag / 发 Release 各自授权，互不推导。
- 密钥不进仓库；配置分环境，不把生产默认值写进代码。
- 接 **模型 / 外部服务 / 连接器** 时，再读 `reference/model-and-connector-guide.md`：先宿主门禁再外部请求，证据不足就失败关闭，不调用模型。纯前端 / CRUD 不必读。
- 子代理必须声明模型和审查边界；禁止叫审查员忽略问题。

---

## 三、Verify：测试、审查、发布

对应 skill：`verify-test`、`verify-review`、`verify-release`。

### 3.1 三层测试

| 层 | 要求 |
|---|---|
| 单元 | 正常 + 边界 + 异常，覆盖率 ≥ 80% |
| 功能 | ≥ 1 正常 + 1 异常 |
| Examples | 2–3 个真实用法 |

声称「功能不回退」必须跑通过关键路径的**真实端到端**。缺密钥只能标 `blocked`，不能标 done。「构建通过」不等于功能测试。

测试要可证伪：预期独立于被测实现；不要用「字符串出现过就算过」。模型类项目还要有失败关闭负例、连接器默认断网、质量数据四层隔离（细节在 guide，不在这篇展开）。

### 3.2 审查

对照 Issue 的 P0/P1 逐项给证据（文件:行号 / 回执 / 数据库终态）。审查不负责合并。标准不滑坡，不说「差不多了合吧」。

分层：L1 自动测试 → L2 Agent 对照验收 → L3 人看 P0 和方向。未获授权的远端写操作是 P0。

### 3.3 发布与合并

实现完成 ≠ 已经安全进主干。走 `verify-release`：allowlist 逐路径（禁止无审查的 `git add .`）、查可见性、feature 分支、secret 扫描、一个 PR、检查过了再合、合后写回执。

单人仓获授权后可自合；协作仓不自合、不对共享分支 force-push。合并 ≠ 上线。

人读方法论是否随发版更新：**仅人、可选**，不是发布完成条件；Agent 不要打开、不要改本文。

---

## 四、Observe：看得见才管得住

对应 skill：`observe-session`。

Session 摘要把四类信息分开：事实 / 决定 / 推断 / 外部待办。推断和外部待办不能写成 `verified` / `done`。

有 UI 的 PR 必须有「用户视角：本次让用户能做什么」。Milestone 完成时写「现在能走通哪条使用路径」，并映射回 Spec，不要只报技术功能清单。

降质信号：同一问题反复、review 轮次暴涨、开始说「差不多了合吧」——命中就干预（拆 Issue 或换模型），不要等结果烂了。

---

## 五、Improve：同样的坑不踩第二次

对应 skill：`improve-retro`。

问题记录同样要分事实 / 推断 / 决定 / 外部待办。改进必须落成下次会自动生效的东西：规则、Skill、模板，而不是口头总结。

**人读版是导出，不是上级。** 闭环里「更新方法论」是指更新 skills（以及可选地对照 CHANGELOG 刷新本文），不是让长文指导 Agent。

---

## 六、工具怎么落地

| 阶段 | Skill | 何时用 |
|---|---|---|
| Plan | `plan-spec` | 需求模糊，先对齐边界 |
| Plan | `plan-breakdown` | 拆 Epic / Milestone / Issue |
| Execute | `execute-implement` | 一个 Issue 开工 |
| Verify | `verify-test` | 测试计划与三层测试 |
| Verify | `verify-review` | 对照验收审查 |
| Verify | `verify-release` | commit / push / PR / merge |
| Observe | `observe-session` | 会话结束、降质 |
| Improve | `improve-retro` | 复盘、提炼规则 |

真源在 `skills/`，用 `scripts/sync-skills.py` 同步到 Cursor / Claude Code；装到项目用 `--install`（会带上被引用的模板和 `reference/*.md`）。

Claude 子 Agent（plan / implement / review / explore / ci-watcher）只指向对应 skill，不读本文。

---

## 七、本地 / 单人怎么退化

没有 GitHub Issues / 必过 CI 时，质量标准不变，载体变轻：

- 看板 → `PLAN.md` 表格
- CI → 本地测试 / lint
- 协作审查 → 自审 + 你看 P0

单人也不在默认分支直接提交，仍走 feature 分支。

---

## 相对冻结稿（v1.2）多了什么

下面这些只存在于现行 skills，旧迁入稿里没有。需要细节时打开对应 skill，不要回写 archive。

- 任务三档（spike / bounded / architectural）
- Spec 四态、地图、能力矩阵
- 证据合同、外部依赖图、失败关闭
- 有 UI 的使用路径与主次布局；阶段反馈的用户视角
- `verify-release`（发布 / 合并安全与协作感知）
- 模型与连接器按需 guide（非常驻）
- 事实 / 推断 / 决定 / 外部待办分离
