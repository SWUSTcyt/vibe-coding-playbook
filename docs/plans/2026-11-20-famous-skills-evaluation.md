# Issue：外部技能查找入口（现有 Skill 解决不了时）

> 本文件只在 playbook 仓库里，不随安装分发。分发给项目的是 `reference/external-skills-guide.md`。
> 这里记：用户原话与确认、要改和不改、验收、对各来源仓库的判断、试用汇总。

## 用户原话

> 我现在想了解下其他出名的skills,比如mattpocock/skills affaan-m/ECC awesom-llm-apps graphify caveman claude-mem agent-skills这些据说都是很出名的skills,帮我了解下呢，我想用于提升当前工作流，或者有些确实很好的，我想用于后续的开发

> 总之这个可以持续更新，而且帮我做一个评估哪些可能能用的到，因为我们不能老是闭门造车，开发过程中可能遇到的问题，如果有现成的skills能解决那当然很好了

> 以及你是否有获取热度比较高的skills的方法或者渠道，这样后续你就可以帮我找合适的skills,不一定是必须优化我们当前的项目，也可以是作用到其他地方，像你说的遇到不同情况选择不同的skills

> 是的，热度不能直接用，肯定要核实或者试用才行

> 你说把找skills分析skills的能力加入到当前skills可以吗，如果遇到我们项目skills解决不了的问题，可以考虑找新的skills去解决问题，核心出发点还是我们当前的skills

## 用户确认（2026-11-20）

方案说明之后，用户回复：

> 可以的帮我落地

确认的方案是五条：查找步骤和候选表放进 `reference/`；由 `improve-retro` 引用；`AGENTS.md` 加一句作补充；试用记录不放进分发的文件；安装要用户明确说出在哪个项目装哪一个。

用户知情的两点：到确认时没有装过或试过任何外部技能，这条规则没达到 `improve-retro`「有回放或第二条独立证据」的门槛，按用户决定先加；外部技能是 Agent 会照着执行的指令，安装前要读完正文和附带脚本。

## 要改 / 不改

- 要改：新增 `reference/external-skills-guide.md`；`skills/improve-retro/SKILL.md` 加触发条件和一节；`AGENTS.md` 关键约定加一条；`CONTEXT_INDEX.md`、`README.md`、`docs/improvements/CHANGELOG.md` 同步；写本任务文件和一份会话摘要。
- 不改：其余 7 个 Skill、全部模板、安装脚本。不新增第 9 个 Skill。不在 `execute-implement` 里加「开工先搜」。不安装任何外部技能。

## 验收（改动前写下）

| ID | 级别 | 验收标准 | 验证路径 |
|---|---|---|---|
| EXT-01 | P0 | 装到项目后指南随之分发，安装检查通过 | 临时目录 `--install`，确认 `reference/external-skills-guide.md` 存在，再 `--check` 返回 0 |
| EXT-02 | P0 | 触发条件、只提候选、明确说出项目和技能才安装，这三点在指南、`improve-retro`、`AGENTS.md` 里说法一致 | 逐处读文字核对 |
| EXT-03 | P1 | 现有闭环不变 | 改动里 Skill 只有 `improve-retro`；`execute-implement` 没有搜索步骤 |
| EXT-04 | P1 | 分发的指南里没有项目专属的试用记录、本机路径；写明试用记录记在哪 | 读指南；扫描本机路径 |
| EXT-05 | P1 | 副本同步，格式干净，Skill 正文不超过 500 行 | `sync-skills.py` 与 `--check`、`git diff --check`、行数 |

这些是文字核对和分发检查，不是真实项目试用。

### 验收结果（2026-11-20，实现者自查，只在本地运行）

| ID | 结论 | 依据 |
|---|---|---|
| EXT-01 | 通过 | 临时目录安装分发 7 个参考文档，`reference/external-skills-guide.md` 在其中；Skill 进 `.cursor/skills/` 与 `.claude/skills/`；随后 `--check` 返回 0 |
| EXT-02 | 文字核对通过 | 指南「何时去找」「提出候选」「安装」三节、`skills/improve-retro/SKILL.md`「现有 Skill 解决不了时」一节、`AGENTS.md` 关键约定「外部技能」一条，三处都是：两条都满足才找、只提候选、用户明确说出在哪个项目装哪一个才安装 |
| EXT-03 | 通过 | Skill 的改动只有 `improve-retro` 及其两套副本 |
| EXT-04 | 通过 | 指南里没有试用记录表和本机路径；「试用之后」一节写明记在项目的 `docs/issues-log.md` |
| EXT-05 | 通过 | `sync-skills.py --check` 一致，`git diff --check` 干净，`improve-retro` 正文 90 行 |

实现和自查是同一个模型（Claude Fable 5.2，高级档）、同一段对话，没有换模型做合入前审查。

## 合入前审查（2026-11-20）

审查模型 Claude Fable 5.2（高级档），和编写者是同一个模型、同一段对话，没有换模型。只读审查，检查只在本地运行，仓库没有 CI。结论：P0、P1 无，可合入。用户选择先改 2 条 P2，推送后再确认合并。

- P2（已改）：安装步骤没写怎么装。指南「安装」补了带全参数的命令示例，以及命令跑不通时只复制那一个技能目录；「怎么找」补了 `npx skills` 是第三方工具、会上报匿名使用统计、怎么关。参数对照了公开文档，没有实际运行。
- P2（已改）：推荐前核对缺许可证。核对清单加一条，候选说明里加上许可证。
- 用户在审查后追加：「以及真的需要安装技能要安装什么技能要先通知我哦」。指南「安装」第一条写明：安装之前先告诉用户装哪一个、来源、装进哪个项目、要运行的命令、会新增或修改哪些文件。
- P3（没改，用户选择只改 P2）：「用户直接要求找某一类技能时不受这两条限制」只写在指南里；本文件名和内容对不上；本文件没有单独记发布授权，依据是用户确认的方案里写了「改完走分支和 PR，合并仍等你确认」，以及之后的「那你可以再推一次，等你推上去我再review」。
- 无法从 diff 验证：验收表和实现在同一笔提交里，证明不了验收写在改动之前。
- 安装检查对项目自有技能报「多余」：用户决定先不改，等真装了外部技能、确实碍事再说。

## 实施中发现、没有在这次改的

项目的 `.cursor/skills/` 或 `.claude/skills/` 里多出一个技能时，`sync-skills.py --install <项目> --check` 会报「多余」并返回非 0（2026-11-20 在临时目录实测；重新安装不会删掉它）。README 本来就允许项目补充自己的 Skill，所以这是脚本检查和说明之间已有的不一致，外部技能装进项目后会碰到。改脚本不在用户确认的范围内，这次只在指南里照实写明，是否修改另行确认。

## 对各来源仓库的判断（2026-11-20，只查阅公开页面）

- [mattpocock/skills](https://github.com/mattpocock/skills)：约 56 个小技能，作者写明不是接管流程的框架。主路径（追问、写 Spec、拆票、TDD、审查）与现有闭环重叠。每个仓库用之前要配置 Issue 放哪、标签和文档位置。多出来的是 `grill-with-docs`，追问时维护词表和 ADR。
- [affaan-m/ECC](https://github.com/affaan-m/ECC)：公开页面写约 72 个 Agent、327 个 Skill，另有钩子、记忆和安全扫描。它自己的循环是 plan、test、implement、review、verify、remember、improve。官方说明 Cursor 是能力受限的适配，并警告不要叠两种安装。不整套安装。
- [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)：100 多个可运行的 Agent 和 RAG 示例，另有少量按问题安装的小技能。示例在做产品 Agent 时当例子翻。
- [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)：把代码库做成可查询的知识图。代码用本地语法分析，不上传；文档和图片才走模型。它是工具，不是要写进 Skill 的规则。
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)：缩短回答和工具输出的本地代理。公开的节省数字样本量小。
- [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)：跨会话记忆。钩子记下工具调用和文件修改。Cursor 不能在提交前改写提示，记忆要靠搜索取回。默认走托管服务，匿名统计默认开着。
- [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)：26 个技能。主路径重叠，多出来的是性能、无障碍、代码简化、调试、接口设计等按问题用的技能。
- `anthropics/skills`：官方示例技能，本仓库的 `reference/vendored-skills/` 里有一份本地参考（不进版本管理）。

`agent-skills` 这个名字对上 addyosmani 和 anthropics 两个仓库。

查找渠道：[skills.sh](https://www.skills.sh/) 按 `npx skills` 的匿名安装次数排名。总榜上有多个同名副本，例如好几个名叫 superpowers 的仓库，原来的只有 obra/superpowers。命令行搜索的用法抄自公开文档，没有在本机运行过。

## 试用汇总

项目里的试用先记在该项目的 `docs/issues-log.md`。复盘时汇总到这里，并更新指南里的候选表。

| 日期 | 问题 | 用了什么 | 项目 | 结果 |
|---|---|---|---|---|
| 2026-11-20 | 建立查找入口 | 无 | 无 | 只查阅公开页面，未安装，未试用 |
