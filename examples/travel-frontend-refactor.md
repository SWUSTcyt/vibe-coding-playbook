# 端到端示例：旅游助手前端现代化

> 用本 playbook 的 skills 驱动一个真实重构走完五层闭环。
> 试点项目：`langchain1.0 + qwen + agent 旅游助手`（LangChain 1.0 + Qwen + MCP高德 + Gradio）。
> 目标：后端技术栈不变（langchain + python），把现有 Gradio 前端重构得现代、好看。
>
> 注：下文的 Spec / Issue / 代码片段为「演示样例」，真实执行时由对应 skill 生成。本示例重在展示流程与 skill 衔接。

---

## 层 0：启动对齐

Agent 启动先读 `AGENTS.md`（三铁律 + 五层）与 `PLAN.md`（项目状态）。
本地/单人场景：用 `PLAN.md` 代替 GitHub Issues，用本地测试脚本代替 CI（见方法论第七章）。

---

## 层 1 · Plan

### 1a. 需求评审 → skill: `plan-spec`

调用 `plan-spec`，产品经理式追问后产出 Spec：

```markdown
# Spec: 旅游助手前端现代化

## 一句话描述
把现有 Gradio 旅游助手界面重构为现代、美观、响应式的对话界面，给 C 端用户使用。

## 核心功能
- [ ] 现代化对话界面（气泡、头像、流式输出动画）
- [ ] 「AI 思考过程」可折叠面板（保留现有 reasoning 展示能力）
- [ ] 开发者模式（工具调用日志 / 原始事件 JSON）
- [ ] 响应式布局（桌面 + 移动）

## 边界条件（不在范围内）
- 不改后端 Agent 逻辑（agent.py / tools.py / middleware.py 不动）
- 不改 MCP/Qwen 接入方式
- 不做用户登录 / 多会话持久化

## 非功能性需求
| 维度 | 要求 |
|---|---|
| 性能 | 首屏 < 2s；流式输出无明显卡顿 |
| 安全 | 坐标脱敏保留；不在前端暴露 API Key |
| 可维护性 | 前端样式与逻辑分离，主题可配置 |

## 技术约束
| 项 | 选择 |
|---|---|
| 语言 | Python（后端不变） |
| 框架 | 待定：A) Gradio 自定义主题/CSS  B) FastAPI + 现代 SPA |
| 部署环境 | 本地 `python main.py` |

## 验收总纲（P0）
1. 现有对话与 reasoning 展示功能不回退
2. 新界面在桌面与移动端均可正常使用
3. 后端文件零改动
```

**决策点（前端方案）：** 在 plan-spec 阶段就和用户敲定 A 或 B。
- A（Gradio 主题/CSS 重构）：最省事、纯 Python、改动小，适合 demo 升级。
- B（FastAPI + SPA）：更现代、上限高，但引入 JS 栈、工作量大。
> 本示例假设选 A。

### 1b. 拆分 + 验收前置 → skill: `plan-breakdown`

调用 `plan-breakdown`，产出 Epic/Milestone/Issue + P0-P3，并写入 `PLAN.md`：

```markdown
# 项目: 旅游助手前端现代化 | 状态: M1 开发中

## 当前 Milestone: M1 - Gradio 现代化主题 MVP [0%]

## Issue 状态
- [ ] #1 抽离前端样式层（主题 + 自定义 CSS 骨架） → todo
- [ ] #2 对话区重构（气泡/头像/流式动画） → todo（依赖 #1）
- [ ] #3 「AI 思考过程」面板适配新布局 → todo（依赖 #2）
- [ ] #4 开发者模式面板（日志/JSON）折叠化 → todo（依赖 #1）
- [ ] #5 响应式适配（移动端断点） → todo（依赖 #2 #4）

## 关键决策
- 前端方案: A（Gradio 自定义主题 + CSS），后端零改动
- 主题: 可配置 gr.themes + 外置 custom.css

## 共享定义
- 入口: ui.py 的 build_ui()；事件流: stream_answer()
```

每个 Issue 用 `templates/issue-template.md`，验收标准示例（#2）：

```markdown
### P0（必须）
- [ ] 流式输出逐字/逐块渲染，无整段闪烁
- [ ] 现有消息内容与 reasoning 不丢失
### P1（核心）
- [ ] 用户/AI 气泡区分，带头像
### P2（边界 & 错误）
- [ ] 超长消息、空消息、工具报错时布局不破
### P3（锦上添花）
- [ ] 进入动画
```

---

## 层 2 · Execute → skill: `execute-implement`

以 Issue #2 为例，一次只做一个 Issue：

1. 读 Issue 与验收标准。
2. **先出测试计划**（见层 3 verify-test），人确认。
3. **按 TDD 改 `ui.py`**：先写失败测试 → 最小实现 → 重构。仅动前端层，不碰 `agent.py`。
4. 补功能测试 + 使用示例。
5. 提交前用 verify-review 自审，写 PR Summary（`templates/pr-summary-template.md`）。

约束提醒：P0 不满足就停下上报，不降标准；中文注释 UTF-8；改 `ui.py` 既有函数先理解原逻辑再改（保留 reasoning 累积逻辑）。

> 反复写不对（≥2 次）→ 委托 explore 子 Agent（`.claude/agents/explore.md`）查 Gradio 主题/CSS 文档。

---

## 层 3 · Verify

### 3a. 三层测试 → skill: `verify-test`

```
- 单元测试：前端纯函数（如消息格式化 _safe_trunc / _mask_coord）正常+边界+异常
- 功能测试：模拟一次问答事件流，断言渲染出气泡 + reasoning 面板（≥1 正常 +1 异常）
- Examples：2-3 个典型对话截图/脚本
```
本地跑：`python -m pytest`（L1 自动验收，替代 CI）。

### 3b. 审查验收 → skill: `verify-review`

review 子 Agent 对照验收标准给 P0-P3 列表（L2）；你只看 P0 + 整体观感（L3，5-10 分钟）。
标准不滑坡：流式渲染闪烁未解决就不能合，不能降级为 P2。

---

## 层 4 · Observe → skill: `observe-session`

会话结束写 Session 摘要到 `docs/session-summaries/`（用模板）：处理的 Issue、用的 skill、错误与解法、token、是否摸鱼。
降质监控：若 #2 连续 review > 4 轮 → 检查 Issue 是否太大或换模型。

---

## 层 5 · Improve → skill: `improve-retro`

Milestone 结束总结：
- 反复出现的问题（如「Gradio 自定义 CSS 在移动端断点反复出错」≥2 次）→ 记入 `docs/issues-log.md`。
- 提炼：是否值得固化一个 `gradio-theming` 能力 skill？→ 若是，按 `reference/SKILL-writing-guide.md` 新建。
- 更新 `docs/improvements/CHANGELOG.md`。

---

## 跨工具一致性

同一套 skill 在三个工具里都能用：
- **Cursor**：读 `.cursor/rules/`（三铁律常驻）+ `.cursor/skills/`。
- **Claude Code**：读 `.claude/skills/` + `.claude/agents/`（5 个 subagent）。
- **Codex**：读根 `AGENTS.md`。

真源是 `skills/`，改完跑 `python scripts/sync-skills.py` 同步。
