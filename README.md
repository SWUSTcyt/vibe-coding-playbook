# vibe-coding-playbook

**AI 编程方法论 v1.2 — 可操作版** 的本地落地仓库。

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
| Plan | Spec Review → Epic → Milestone → Issue | Spec、Plan Document（<500 tokens）、P0-P3 验收标准 |
| Execute | 角色化 Agent 协作 + 并行 Issue 开发 | 代码、测试、Skill 模块 |
| Verify | 三层测试 + CI/CD + 分层验收 | 测试报告、PR Summary |
| Observe | Issue 看板 + Session 摘要 + 降质检测 | 状态看板、Session 日志 |
| Improve | 问题自动记录 → 定期总结 → 规则提炼 | 改进清单、新 Skill、更新后的方法论 |

## 仓库结构

```
AGENTS.md                            # 跨工具通用入口（Cursor/Claude Code/Codex）
docs/
  AI 编程方法论 v1.2 — 可操作版.md   # 方法论唯一真源（人读完整版）
skills/                              # 七个流程 Skill 真源（唯一可编辑处）
templates/                           # Spec / Plan / Issue / PR 等模板
scripts/sync-skills.py               # 把 skills/ 同步到各工具目录
.cursor/  rules/ + skills/           # Cursor 加载位（rules 常驻 + skills 副本）
.claude/  agents/ + skills/          # Claude Code 加载位（9 subagent + skills 副本）
reference/                           # SKILL 写作规范 + vendored 参考 skill（gitignore）
examples/                            # 端到端示例（待建）
CONTEXT_INDEX.md                     # Agent 信息入口
```

## 快速启动

### 从 GitHub 克隆

```bash
git clone https://github.com/<your-username>/vibe-coding-playbook.git
```

### 安装 Skill 到你的项目

把 playbook 的七个核心 Skill 安装到任意项目（以 Cursor + Claude Code 为例）：

```bash
cd vibe-coding-playbook

# 方式一：使用同步脚本（推荐）
python scripts/sync-skills.py --project /path/to/your-project

# 方式二：手动复制（Cursor）
cp -r skills/* /path/to/your-project/.cursor/skills/

# 方式二：手动复制（Claude Code）
cp -r skills/* /path/to/your-project/.claude/skills/
```

同时将 `AGENTS.md` 复制到项目根目录：

```bash
cp AGENTS.md /path/to/your-project/AGENTS.md
```

> 复制 `AGENTS.md` 时，按项目实际情况修改「Skill 调用指引」表格，
> 如有项目级 Skill（如 `understand`、`feature`），补充到表中。

### 在项目中使用

1. 阅读 `AGENTS.md` / `CONTEXT_INDEX.md` 定位所需信息
2. 调用 `plan-spec` skill 做 Spec Review（模板 `templates/spec-template.md`）
3. 调用 `plan-breakdown` 拆 Epic → Milestone → Issue（带 P0-P3 验收标准）
4. 写 Plan Document（<500 tokens）到 `docs/plans/`
5. 按阶段调用 `skills/`（execute-implement / verify-test / verify-review / observe-session / improve-retro）

### 保持 Skill 同步

```bash
# playbook 自身更新后，同步到 .cursor/skills/ 和 .claude/skills/
python scripts/sync-skills.py

# 同步到某个项目的 Skill
python scripts/sync-skills.py --project /path/to/your-project

# 仅检查差异（不写入）
python scripts/sync-skills.py --check
python scripts/sync-skills.py --check --project /path/to/your-project
```

## 来源

飞书原文：[AI 编程方法论 v1.2](https://my.feishu.cn/docx/QiJRdY898o0hs4xZXlwcs34ynFf)
