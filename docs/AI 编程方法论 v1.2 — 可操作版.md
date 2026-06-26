# AI 编程方法论 v1\.2 — 可操作版

> 每一步都具体到：做什么、怎么做、产出什么。

━━━━━━━━━━━━━━━━━━━━━━

## 概述

**一句话：用约束对抗熵增。** 让模型在持续运行中不降低自己的标准，稳定地把高质量代码合进去。

**三条铁律：**

1. **标准前置，不可回调** — 验收标准定义在写代码之前，中途绝不降低

2. **信息触手可及，而非全部塞入** — Agent 需要什么能自己找到，不需要一次性灌入

3. **任务足够小，流程足够固化** — 大任务必拆分，重复流程必自动化

**五层闭环：**

```Plain Text
Plan（规划）→ Execute（执行）→ Verify（验证）→ Observe（观测）→ Improve（改进）
   ↑                                                              │
   └──────────────────────────────────────────────────────────────┘
```

**速览表：**

\| 层 \| 核心动作 \| 关键产出 \|

\| **Plan** \| Spec Review → Epic → Milestone → Issue \| Spec 文档、Plan Document（\< 500 tokens）、P0\-P3 验收标准 \|

\| **Execute** \| 角色化 Agent 协作 \+ 并行 Issue 开发 \| 代码、测试、Skill 模块 \|

\| **Verify** \| 三层测试 \+ CI/CD \+ 分层验收 \| 测试报告、PR Summary \|

\| **Observe** \| Issue 看板 \+ Session 摘要 \+ 降质检测 \| 状态看板、Session 日志 \|

\| **Improve** \| 问题自动记录 → 定期总结 → 规则提炼 \| 改进清单、新 Skill、更新后的方法论 \|

**快速启动：**

```Plain Text
□ 1. Spec Review → 输出 Spec 文档
□ 2. 拆 Epic → Milestone → Issue（带 P0-P3 验收标准）
□ 3. 创建 Plan Document（< 500 tokens）+ CONTEXT_INDEX.md
□ 4. 设计 DB Schema / 接口契约
□ 5. 配置 5 个 Agent 角色模板
□ 6. 并行启动无依赖 Issue 开发
□ 7. PR 自动触发 CI + Review
□ 8. Milestone 结束时总结提炼规则
```

━━━━━━━━━━━━━━━━━━━━━━

# 一、Plan 层：从想法到可执行计划

## 1\.1 Spec Review（需求规格评审）

**做什么：** 和 AI 一起过需求，确保双方理解一致，产出 Spec 文档。

**怎么做：**

4. 用自然语言描述项目目标（你想做什么、给谁用、核心功能有哪些）

5. 让 AI 追问澄清问题（边界条件、异常场景、非功能性需求）

6. 让 AI 输出结构化 Spec，包含：

- 功能描述（一句话总结 \+ 核心功能列表）

- 边界条件（什么不在范围内）

- 非功能性需求（性能、安全、可维护性）

- 技术约束（语言、框架、部署环境）

**产出：** Spec 文档（Markdown，约 200\-500 字）

**提示词示例：**

> "我想做一个【XXX】。请你像产品经理一样向我提问，帮我澄清需求边界。问完后，输出一份结构化 Spec 文档，包括功能描述、边界条件、非功能性需求、技术约束。"

━━━━━━━━━━━━━━━━━━━━━━

## 1\.2 归约拆分：Epic → Milestone → Issue

**做什么：** 把 Spec 从大到小逐层拆解，直到每个任务单元都可以被一个 Agent 独立完成。

**怎么做：**

- **拆 Epic：** 每个 Epic = 一个独立功能模块，先拆项目需要的 2\-3 个即可

- **拆 Milestone：** 每个 Milestone 须包含：起始条件、交付物、验收标准。只拆前 1\-2 个的细节

- **拆 Issue：** 粒度黄金法则 — 如果需要 3 轮以上 review 才能合入，就是太大了。每个 Issue 包含：任务描述、输入/输出定义、P0\-P3 验收标准、依赖条件

**提示词示例：**

> "基于这份 Spec，帮我做任务拆分：先拆出 Epic，再选第一个 Epic 拆出 Milestone，最后选第一个 Milestone 拆到 Issue 级别。每个 Issue 要包含任务描述、输入/输出、验收标准（分 P0/P1/P2/P3 四级）、依赖关系。"

━━━━━━━━━━━━━━━━━━━━━━

## 1\.3 计划文档（Plan Document）

**做什么：** 创建一份极简的项目状态文档，作为项目"唯一真实来源"。

**怎么做：**

- 严格控制在 **\~500 tokens** 以内（约 300 个中文字）

- 只记录：当前 Milestone、Issue 状态、关键决策、共享定义（DB Schema / 接口契约摘要）

- 状态更新靠 GitHub Issues，不靠这个文档记细节

- 文档存为 `PLAN.md`，Agent 每次启动时自动读取

**为什么：** Session 会断，上下文会丢，但文档不会。Agent 每次醒来都能快速对齐状态。

**模板：**

```Plain Text
# 项目: XXX | 状态: M1 开发中

## 当前 Milestone: M1 - 注册登录 MVP [40%]

## Issue 状态
- [x] #1 数据库 Schema 设计 → done
- [ ] #2 用户注册 API → in-progress (agent-3)
- [ ] #3 登录认证 API → todo
- [ ] #4 前端登录页 → todo

## 关键决策
- 认证方案: JWT + refresh token
- 数据库: PostgreSQL

## 共享定义
- User Schema: id, email, password_hash, created_at
- API Base: /api/v1
```

━━━━━━━━━━━━━━━━━━━━━━

## 1\.4 验收标准前置

**做什么：** 在每个 Issue 创建时就把验收标准写清楚。

**怎么做：**

每个 Issue 用 P0\-P3 分级：

\| 等级 \| 含义 \| 处理方式 \|

\| **P0** \| 阻塞性，不修复不能合入 \| 必须修复 \|

\| **P1** \| 重要缺陷，本次合入前修复 \| 必须修复 \|

\| **P2** \| 建议修复，可后续 PR \| 记录为 follow\-up issue \|

\| **P3** \| 锦上添花，可忽略 \| 记录不追踪 \|

- 让 AI 根据 Issue 描述自动生成验收标准列表，你只需确认/调整

- **原则：中途不允许降级。** 做不完就拆 Issue，不降标准

**提示词示例：**

> "针对这个 Issue，帮我生成一份验收标准清单，按 P0/P1/P2/P3 分级。P0 是阻塞性缺陷，P1 是本次必须修复的，P2 可后续 PR，P3 是锦上添花。"

━━━━━━━━━━━━━━━━━━━━━━

# 二、Execute 层：Agent 执行与协作

## 2\.1 角色化 Agent

**做什么：** 不同性质的工作交给不同"角色"的 Agent，各自有专属系统指令。

五个标准角色：

\| 角色 \| 职责 \| 触发条件 \| 提示词要点 \|

\| **explore** \| 搜索理解代码/文档、调研方案 \| 不确定技术选型、需了解代码结构 \| "不要写代码，只做调研，给出推荐方案及理由" \|

\| **plan** \| 制定计划、拆分任务、调整 Milestone \| 项目启动、新 Milestone、计划变更 \| "基于 Spec 和进展，做任务拆分和优先级排序，产出 Plan Document 更新" \|

\| **implement** \| 写代码、写测试、修 Bug \| 每个 Issue 被分配时 \| "对照 Issue 和验收标准写代码。必须包含：单元测试 \+ 功能测试 \+ 使用示例。提交 PR 前先自查" \|

\| **review** \| 代码审查、验收标准核验 \| 每次 PR 提交后 \| "对照 Issue 验收标准逐项检查，给出 P0\-P3 问题列表。不负责合并" \|

\| **CI watcher** \| 监控 CI 状态、分析失败原因 \| PR 提交后 / CI 失败时 \| "监控 CI，失败时分析日志、定位原因、给出修复建议" \|

━━━━━━━━━━━━━━━━━━━━━━

## 2\.2 子 Agent 委托机制

**做什么：** 主 Agent 遇到特定问题时，动态创建隔离子 Agent 处理，完成后销毁。

委托场景速查：

\| 场景 \| 委托给谁 \| 触发条件 \|

\| 需要了解现有代码 \| explore 子 Agent \| 不确定代码在哪 \|

\| 某段代码始终写不对 \| explore → 查文档/查类似实现 \| 同一问题反复失败 2 次 \|

\| CI 失败不明原因 \| CI watcher 子 Agent \| CI 报错 \|

\| 怀疑进度偏离计划 \| plan 子 Agent（检查） \| 每完成 3 个 Issue \|

\| 代码写完要自查 \| review 子 Agent \| PR 提交前 \|

\| 需查找外部文档/API \| explore 子 Agent \| 需第三方信息 \|

**关键原则：** 子 Agent 临时的、隔离的；只返回结果不替你做决策；可同时起多个并行查询。

━━━━━━━━━━━━━━━━━━━━━━

## 2\.3 并行 Issue 处理

**做什么：** 无依赖关系的 Issue 同时推进，类似多人多分支并行开发。

**怎么做：**

7. 每个 Milestone 开始时画 Issue 依赖图，标记可并行的

8. 同时启动多个 implement Agent，各自处理独立 Issue

9. 并行 Agent 共享：DB Schema、API 接口契约、代码风格规范

**注意：** 并行 Issue 必须操作不同文件/模块，否则串行。AI 解决 Git 冲突能力较强，但尽量从源头避免。

━━━━━━━━━━━━━━━━━━━━━━

## 2\.4 Skill 模块化

**做什么：** 把反复用到的能力封装成可复用 Skill。

满足以下任一条件就值得封装：

- 在 3 个以上 Issue 中重复出现

- 有固定的输入/输出模式

- 需要特定工具链或领域知识

常见 Skill：`db-migration`、`api-crud`、`auth-flow`、`test-gen`、`error-handling`

封装格式示例：

```Plain Text
# Skill: api-crud
## 输入：数据模型定义 + API 规范
## 输出：完整 CRUD 代码 + 单元测试 + API 文档片段
## 使用："使用 api-crud skill，基于以下 User 模型生成 CRUD API..."
```

━━━━━━━━━━━━━━━━━━━━━━

## 2\.5 防滑坡 \& 计划变更

### 开发中回顾标准

- 每完成 3 个 Issue → 自动重读 Plan Document 和验收标准

- 每个 Issue 提交前 → review 子 Agent 对照标准做自审查

- 连续 2 个 Issue 有 P1 问题 → 暂停，排查是 Issue 太大还是标准不清晰

### 计划变更处理

\| Agent 状态 \| 操作 \|

\| 还没读 Plan Document \| 直接改文档 \|

\| 已读取尚未执行 \| 改文档 \+ 对话中告知 \|

\| 正在执行中 \| Chat 沟通，给时间调整 \|

\| 变更很大 \| 停下当前 Agent，重新规划 \|

**原则：尽量避免对正在执行的 Agent 做重大变更。**

━━━━━━━━━━━━━━━━━━━━━━

## 2\.6 Token 成本控制

**最大浪费源不是上下文共享，而是任务失败重试。**

对策：

10. **Issue 足够小** — 一次做对，不反复

11. **信息按需获取** — Agent 通过 MCP 工具自己找，不一次全灌进去

12. **建立文档索引** — 项目根目录放 `CONTEXT_INDEX.md`，Agent 启动只读索引表（几十 tokens），需要时按路径读取具体文档

```Plain Text
# 上下文索引
- 数据库 Schema → docs/schema.md
- API 规范 → docs/api-spec.md
- 代码风格 → docs/style-guide.md
- 已封装的 Skill → docs/skills/
- 历史问题记录 → docs/issues-log.md
```

━━━━━━━━━━━━━━━━━━━━━━

# 三、Verify 层：测试与验收

## 3\.1 测试三层体系

\| 层级 \| 覆盖范围 \| 谁来写 \| 要求 \|

\| **单元测试** \| 函数/方法正常路径 \+ 边界 \+ 异常 \| implement Agent \| 覆盖率 ≥ 80% \|

\| **功能测试** \| API 完整请求\-响应链路 \| implement Agent \| 至少 1 正常 \+ 1 异常 \|

\| **Examples** \| API/模块典型用法 \| implement Agent \| 2\-3 个实际使用场景 \|

提示词："为以下函数编写单元测试，覆盖正常输入、边界值、异常输入三种情况。"

**硬规则（功能不回退）：** 凡声称"功能不回退 / 可用"，必须至少跑通一次关键路径的**真实端到端冒烟**（真实模型 / 外部服务 / 工具链），而非仅"构建通过""服务能起来"。后者只是 L1 烟雾，证明不了业务链路。若因缺密钥 / 环境跑不了，该验收项只能标 **blocked / 待人工，不得标 done**。（来源：M4 试点踩坑，详见 `docs/improvements/CHANGELOG.md`）

━━━━━━━━━━━━━━━━━━━━━━

## 3\.2 验收标准分层执行

不是所有验收标准都要人检查，按层级分配：

\| 层级 \| 谁检查 \| 检查什么 \|

\| L1 自动 \| CI / Linter / 测试框架 \| 编译、Lint、测试全绿、覆盖率 \|

\| L2 Agent \| review Agent \| 对照 Issue 验收标准 P0/P1 逐项核验 \|

\| L3 人 \| 你 \| 只看 P0 项 \+ 整体设计方向（5\-10 分钟） \|

**流程：** PR 提交 → CI 自动跑 L1 → 不通过则 CI watcher 分析 → 修复 → 通过后 review Agent 做 L2 → 通过后通知你做 L3 → 确认合入

━━━━━━━━━━━━━━━━━━━━━━

## 3\.3 测试用例前置

- Issue 创建时验收标准里就包含"需要哪些测试"

- implement Agent 编码前先输出测试计划（场景 \+ 预期结果）

- 人确认 → Agent 开始编码

━━━━━━━━━━━━━━━━━━━━━━

# 四、Observe 层：可观测性

## 4\.1 Issue 状态看板

为项目 Issue 定义标准标签：

- `todo` → `in-progress`（标注 Agent 名）→ `in-review` → `blocked`（标注原因）→ `done`

Agent 自动更新标签，用 GitHub Projects 做看板（TODO → In Progress → Review → Done）。

━━━━━━━━━━━━━━━━━━━━━━

## 4\.2 PR Summary 自动生成

每个 PR 末尾附带 Summary：

```Plain Text
## PR Summary
- **Issue**: #3 用户注册 API
- **做了什么**: 实现 POST /api/v1/auth/register
- **涉及文件**: src/auth/register.ts, tests/auth/register.test.ts
- **使用的 Skill**: api-crud, auth-flow
- **子 Agent 调用**: explore x1（查 JWT 最佳实践）
- **Review 轮次**: 2 轮
```

━━━━━━━━━━━━━━━━━━━━━━

## 4\.3 Agent Session 摘要

每次会话结束后记录：

- 处理的 Issue 列表、使用的 Skill

- 遇到的错误及解决方案

- Token 消耗、是否"摸鱼"（长时间无实质产出）

存入 `docs/session-summaries/`。用于复盘 Token 花费和发现模型降质。

━━━━━━━━━━━━━━━━━━━━━━

## 4\.4 模型降质检测

\| 指标 \| 正常值 \| 告警阈值 \| 处理方式 \|

\| Review 轮次 \| 1\-2 轮 \| ≥ 4 轮 \| 检查 Issue 是否太大，或换模型 \|

\| 同一问题反复 \| 0 次 \| ≥ 2 次 \| 检查验收标准是否清晰 \|

\| 标准滑坡 \| 无 \| P0 被标为 P2 \| 强制重读标准文档 \|

\| Issue 完成率 \| \> 80% \| \< 50% \| 拆分 Issue，或换模型 \|

**识别信号：** 连续 3 个 Issue review \> 4 轮 → 换模型；review 开始说"差不多了合吧" → 检查滑坡；同一 Bug 修 2 次没好 → 模型在摸鱼。

━━━━━━━━━━━━━━━━━━━━━━

# 五、Improve 层：持续改进

## 5\.1 问题自动记录

Agent 遇到以下情况时自动记录到 `docs/issues-log.md`：

- 同一问题反复出现 ≥ 2 次

- CI 失败且非显而易见原因

- Review 被退回 ≥ 2 次

记录格式：

```Plain Text
### 2026-06-07: JWT Token 过期处理不统一
- **出现位置**: #3 用户注册 API, #5 登录 API
- **问题**: 不同 API 对 Token 过期的处理方式不一致
- **最终解法**: 提取 auth-flow Skill，统一处理逻辑
- **可复用规则**: 涉及认证的 Issue 必须先加载 auth-flow Skill
```

━━━━━━━━━━━━━━━━━━━━━━

## 5\.2 定期总结提炼

触发时机：每个 Milestone 结束 / 每完成 10 个 Issue / 每周固定时间

流程：

13. 读取本期所有问题记录

14. 分类：重复出现的 vs 一次性的

15. 提炼：哪些固化为 Skill？哪些更新验收标准？哪些调整拆分策略？

16. 输出改进清单，逐条更新到对应文档/Skill

━━━━━━━━━━━━━━━━━━━━━━

# 六、工具落地层：方法论 → Cursor / Claude Code / Codex

> 前五层是「做什么、为什么」，本层解决「在具体工具里用什么机制实现」。
> 三家工具都识别 `SKILL.md` 与 `AGENTS.md`，因此本方法论采用「单一真源 + 各工具薄适配」。

## 6.1 概念映射表

| 方法论概念 | Cursor | Claude Code | Codex CLI |
|---|---|---|---|
| 三铁律常驻 | `.cursor/rules/*.mdc`（always-on） | `CLAUDE.md` / `AGENTS.md` | `AGENTS.md` |
| 角色化 Agent（5 角色） | 子代理（Task）+ 角色规则 | subagents（`.claude/agents/*.md`） | `AGENTS.md` 角色说明 + 提示词 |
| 子 Agent 委托 | Task 工具派生隔离子代理 / 后台 Agent | subagents / Task | 串行新会话 |
| 并行 Issue | 多个后台 Agent / 多 git worktree | 多 subagent 并行 / git worktree | 多终端会话 |
| Skill 模块 | `.cursor/skills/<name>/SKILL.md` | `.claude/skills/<name>/SKILL.md` | `~/.agents/skills/`（跨运行时别名）+ `AGENTS.md` |
| CONTEXT_INDEX 按需读取 | `@文件` 引用 / 索引表 | 同左（按路径读取） | 同左 |
| Plan Document 唯一真源 | `PLAN.md` + 规则提醒 | `PLAN.md` | `PLAN.md` |
| 自动化触发（降质检测 / 问题记录） | hooks | hooks | 脚本 / CI |

**单一真源约定：** skill 真源统一放仓库 `skills/<name>/SKILL.md`；各工具目录（`.cursor/skills/`、`.claude/skills/`）做同步或软链，避免多份维护。

## 6.2 Skill 触发约定

- **流程类 skill**（plan / verify 等）：允许从上下文自动触发（description 写清触发条件）。
- **强约束 / 重操作 skill**（如 db-migration）：建议显式点名调用（Cursor 可设 `disable-model-invocation: true`）。
- description 只写「何时用」，不要把多步流程写进去（否则 Agent 会照 description 跳过正文）。

━━━━━━━━━━━━━━━━━━━━━━

# 七、本地 / 单人轻量退化版

> 前文默认 GitHub Issues + Projects + CI/CD 的重度协作流。
> 单人 / 本地（如仅用 Cursor）时，按下表退化，保留「闭环」本质，去掉协作开销。

| 重度流程 | 轻量退化（本地 / 单人） |
|---|---|
| GitHub Issues | `PLAN.md` 内的 Issue 状态表（`- [ ] #2 ...` ） |
| GitHub Projects 看板 | `PLAN.md` 表格 或 编辑器 TODO 列表 |
| PR + 人工合并 | 本地特性分支 + 自查后直接合入主干 |
| CI（L1 自动验收） | 本地测试 / lint 脚本（如 `pytest`、`ruff`），提交前必跑 |
| CI watcher 角色 | 跑本地测试命令的 Agent，失败时分析日志 |
| review 角色（L2） | review 子 Agent 对照验收标准自审，仍保留 |
| 人工验收（L3） | 你本人只看 P0 + 整体方向（5-10 分钟），不变 |
| PR Summary | commit message 规范 + `docs/improvements/CHANGELOG.md` |
| Session 摘要 | `docs/session-summaries/` 仍保留（复盘 token 与降质） |

**保留不可退化的核心：** 标准前置不可回调、P0-P3 分级、三层测试、闭环改进。退化的只是「承载工具」，不是「质量标准」。

━━━━━━━━━━━━━━━━━━━━━━

# 附录：关键词速查

\| 关键词 \| 含义 \| 所在层 \|

\| Spec \| 项目级需求规格 \| Plan \|

\| Epic \| 独立功能模块 \| Plan \|

\| Milestone \| 阶段性交付节点 \| Plan \|

\| Issue \| 最小可执行任务 \| Plan \|

\| Plan Document \| ≤500 tokens 的项目唯一真实来源 \| Plan \|

\| P0\-P3 \| 验收标准分级 \| Plan \|

\| explore \| 调研子 Agent \| Execute \|

\| plan \| 规划子 Agent \| Execute \|

\| implement \| 开发子 Agent \| Execute \|

\| review \| 审查子 Agent \| Execute \|

\| CI watcher \| CI 监控子 Agent \| Execute \|

\| Skill \| 可复用能力模块 \| Execute \|

\| CONTEXT\_INDEX \| 文档索引表 \| Execute \|

\| Unit / Integration / Examples \| 测试三层 \| Verify \|

\| L1/L2/L3 \| 验收分层检查 \| Verify \|

\| Issue Label \| 状态标签看板 \| Observe \|

\| PR Summary \| PR 可观测性摘要 \| Observe \|

\| Session Summary \| Agent 会话记录 \| Observe \|

\| 降质检测 \| 模型能力退化预警 \| Observe \|

\| 问题记录 \| 自动错误日志 \| Improve \|

\| 总结提炼 \| 定期规则萃取 \| Improve \|

━━━━━━━━━━━━━━━━━━━━━━

> **版本**: v1\.3 \| **日期**: 2026\-06\-19 \| **状态**: 待继续迭代

> **变更**: 

> \- v1\.3 — 统一 P0-P3 四级分级；新增「六、工具落地层」（方法论概念→Cursor/Claude Code/Codex 机制映射）与「七、本地/单人轻量退化版」；确立本文档为唯一真源

> \- v1\.2 — 重构层次结构：合并重复内容，统一五层架构，Token管理归入Execute层，降质检测归入Observe层，关键词速查归入附录

> \- v1\.1 — 补全每一步的具体操作、提示词示例、模板和判定标准

> \- v1\.0 — 初始版本

