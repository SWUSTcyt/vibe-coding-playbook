# vibe-coding-playbook

用约束对抗熵增的 AI 编程 playbook。执行在 `skills/`，人读总览是 skills 的导出物。

> 一句话：用约束对抗熵增。让模型在持续运行中不降低自己的标准，稳定地把高质量代码合进去。

## 三条铁律

1. **标准前置，不可回调** — 验收标准定义在写代码之前，中途绝不降低
2. **信息触手可及，而非全部塞入** — Agent 需要什么能自己找到，不需要一次性灌入
3. **任务足够小，流程足够固化** — 大任务必拆分，重复流程必自动化

## 五层闭环

```
Plan（规划）→ Execute（执行）→ Verify（验证）→ Observe（观测）→ Improve（改进）
     ↑                                                              │
     └──────────────────────────────────────────────────────────────┘
```

| 层 | 核心动作 | 关键产出 |
|---|---|---|
| Plan | Spec Review（含用户使用路径）→ Epic → Milestone → Issue | Spec、Plan Document（<500 tokens）、P0-P3 验收标准 |
| Execute | 角色化 Agent 协作 + 并行 Issue 开发 | 代码、测试、Skill 模块 |
| Verify | 三层测试 + 分层验收 + 发布/合并安全 | 测试报告、PR Summary、发布回执 |
| Observe | Issue 看板 + Session 摘要 + 降质检测 | 状态看板、Session 日志 |
| Improve | 问题自动记录 → 定期总结 → 规则提炼 | 改进清单、新 Skill、更新后的方法论 |

## 仓库结构

```
AGENTS.md                            # 跨工具通用入口（Cursor/Claude Code/Codex）
docs/
  AI 编程方法论 — 人读版.md           # 人读导出（发版后可选更新；Agent 勿读）
  archive/                           # 冻结的飞书迁入稿 v1.2
  e2e-verify-guide.md                # E2E 验证指南（含可消费性验收）
  improvements/CHANGELOG.md          # 改进记录（五层闭环的 Improve 产出）
  plans/ / release-notes/            # 计划文档 / 发布说明归档
skills/                              # 八个流程 Skill 真源（唯一可编辑处）
templates/                           # Spec / Plan / Issue / 证据合同 / 发布清单等模板
scripts/sync-skills.py               # 把 skills/ 同步到各工具目录（支持 --install / --check）
.cursor/  rules/ + skills/           # Cursor 加载位（rules 常驻 + skills 副本）
.claude/  agents/ + skills/          # Claude Code 加载位（subagents + skills 副本）
reference/
  SKILL-writing-guide.md             # SKILL.md 写作规范
  service-refactor-guide.md          # 服务化重构参考（契约/分层/关注点剥离）
  model-and-connector-guide.md       # 模型/外部服务/连接器（失败关闭、隔离，按需读取）
  vendored-skills/                   # 第三方参考 skill（gitignore，仅本地借鉴）
examples/                            # 端到端示例
CONTEXT_INDEX.md                     # Agent 信息入口
```

## 快速启动

### 从 GitHub 克隆

```bash
git clone https://github.com/<your-username>/vibe-coding-playbook.git
```

### 安装 Skill 到你的项目

```bash
cd vibe-coding-playbook
python scripts/sync-skills.py --install /path/to/your-project
```

一条命令装齐四样东西（缺一会断链）：

| 装什么 | 装到哪 | 说明 |
|---|---|---|
| 八个核心 Skill | `<项目>/.cursor/skills/`、`<项目>/.claude/skills/` | Cursor 与 Claude Code 各一份 |
| Skill 引用的模板 | `<项目>/templates/` | Skill 正文按 `templates/xxx.md` 引用，不装会断链 |
| Skill 引用的参考文档 | `<项目>/reference/` | 如 `model-and-connector-guide.md`；`vendored-skills/` 不分发 |
| `AGENTS.md` | `<项目>/AGENTS.md` | 已存在则跳过；要覆盖加 `--force-agents` |

装完校验一次：

```bash
python scripts/sync-skills.py --install /path/to/your-project --check
```

该命令按内容哈希比对 Skill，并扫描 Skill 引用的模板与 `reference/*.md` 是否齐全，有问题返回非 0。

> 装好后按项目实际情况修改 `AGENTS.md` 的「Skill 调用指引」表格，
> 如有项目级 Skill（如 `understand`、`feature`），补充到表中。

### 在项目中使用

1. 阅读 `AGENTS.md` / `CONTEXT_INDEX.md` 定位所需信息
2. 调用 `plan-spec` skill 做 Spec Review（模板 `templates/spec-template.md`；有 UI 的产品先定用户使用路径与主/次布局）
3. 调用 `plan-breakdown` 拆 Epic → Milestone → Issue（带 P0-P3 验收标准）
4. 写 Plan Document（<500 tokens）到 `docs/plans/`
5. 按阶段调用 `skills/`（execute-implement / verify-test / verify-review / verify-release / observe-session / improve-retro）

### 保持 Skill 同步

```bash
# playbook 自身：skills/ 真源 -> 本仓库 .cursor/skills/ 和 .claude/skills/
python scripts/sync-skills.py
python scripts/sync-skills.py --check

# playbook 升级后，重新装到项目（幂等，会修复漂移与缺失）
python scripts/sync-skills.py --install /path/to/your-project

# 项目内同步：把项目自己的 .claude/skills/ 同步到 .cursor/skills/
# 注意这不是安装，不会从本仓库取 Skill，也不分发模板
python scripts/sync-skills.py --project /path/to/your-project
```

| 模式 | 源 | 用途 |
|---|---|---|
| 默认 | 本仓库 `skills/` | 维护 playbook 自身的工具副本 |
| `--install` | 本仓库 `skills/` + 被引用的 `templates/` 与 `reference/*.md` | **安装到你的项目**（推荐） |
| `--project` | 项目自己的 `.claude/skills/` | 项目内两个工具目录互相对齐 |

## 版本历史

| 版本 | 主要内容 |
|---|---|
| [v0.5.0](https://github.com/SWUSTcyt/vibe-coding-playbook/releases/tag/v0.5.0) | 证据合同与 `verify-release`；skills 瘦身与任务三档；有 UI 的使用路径；人读方法论与执行分离（v1.2 归档） |
| [v0.4.0](https://github.com/SWUSTcyt/vibe-coding-playbook/releases/tag/v0.4.0) | 安装闭环修复（`--install` + 内容哈希校验）+ Spec 治理瘦身（四态生命周期、前置 Spec 地图、可选 AC 追踪、外部写操作授权） |
| [v0.3.0](https://github.com/SWUSTcyt/vibe-coding-playbook/releases/tag/v0.3.0) | 融入服务化封装与工程骨架管理原则（接口契约前置、关注点剥离重构、密钥/分层/封装边界纪律、可消费性验收，框架无关） |
| [v0.2.0](https://github.com/SWUSTcyt/vibe-coding-playbook/releases/tag/v0.2.0) | 基于 Superpowers v6.1.1 直接对比的增量优化（Review Packet + 证据引用、子代理 dispatch 契约、P0 E2E 硬规则与 blocked 判定） |

完整改进记录见 `docs/improvements/CHANGELOG.md`。

## 来源

人读总览：`docs/AI 编程方法论 — 人读版.md`（由 skills 导出；Agent 启动不读）。

飞书原文（历史）：[AI 编程方法论 v1.2](https://my.feishu.cn/docx/QiJRdY898o0hs4xZXlwcs34ynFf)。迁入稿已冻结在 `docs/archive/`。
