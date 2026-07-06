# 改进记录

## 格式

```
### [日期] 问题描述
- **层：** Plan / Execute / Verify / Observe / Improve
- **现象：**
- **根因：**
- **改进动作：**
- **产出：** 新 Rule / 新 Skill / 方法论更新
```

---

### 2026-07-06 基于 Superpowers v6.1.1 直接对比，增量优化核心 skills（字段级）

- **层：** Improve / Verify / Execute
- **现象：** 之前对 superpowers 的借鉴停留在 v6.0.x（2026-06-19 clone），未直接对比 v6.1.1，存在版本混淆风险
- **根因：** 缺「直接对比」证据链；仅依赖公开信息做间接推断
- **改进动作：**
  - 临时 clone `superpowers@6.1.1` 到 `reference/vendored-skills/superpowers@6.1.1/`，与 `superpowers/`（v6.0.x）做关键文件 diff
  - `verify-review`：输出升级为 Review Packet + 证据引用；补充单审查员双裁决
  - `execute-implement`：新增「子代理 dispatch 契约」（model 声明 + 审查边界 + 禁止指示忽略问题）；任务台账路径对齐 v6.1.1
  - `verify-test`：细化 P0 E2E 硬规则与 blocked 判定；新增「把 L1 冒烟当功能验证 → 假绿灯」
  - `SKILL-writing-guide`：补「形式匹配失败类型」可执行样例；头部明确参考基线与直接对比结论
  - 同步：执行 `scripts/sync-skills.py`，`.cursor/skills/`、`.claude/skills/` 与 `skills/` diff=0
- **产出：** 更新后的 `skills/verify-review`、`skills/execute-implement`、`skills/verify-test`、`reference/SKILL-writing-guide.md`；新增执行版计划 `docs/plans/skills-6x-optimization-plan.md`

---

### 2026-07-06 添加 Superpowers v6.X 深度分析文章

- **层：** Improve
- **现象：** 缺乏对主流 AI 编码技能框架（Superpowers）的深度分析，无法借鉴其优化经验
- **根因：** 未系统调研和分析外部优秀框架的演进策略
- **改进动作：**
  - 调研 obra/superpowers 框架的公开信息（GitHub、博客、技术文档）
  - 分析 v6.X 版本的核心改进：性能优化（50% 更快、60% 更便宜）、Vendor-Neutral 重写、Worktree 本地化等
  - 提取可移植到自定义 SKILL.md 工作流的改进建议：合并审查阶段、预烘焙 Review Packet、任务粒度标准化等
  - 创建深度分析文章 `docs/superpowers-v6-analysis.md`
- **产出：** 新文档 `docs/superpowers-v6-analysis.md`，包含 6 个可移植改进建议和实施路线图

---

### 2026-06-19 M4 试点项目验证（旅游助手前端现代化）& 验收硬规则回填

- **层：** Execute / Verify / Improve
- **现象：**
  - 用方法论五层跑通试点项目「langchain1.0 + qwen + agent 旅游助手」前端现代化（方案 A：Gradio 主题 + CSS + 布局重构，后端零改动）。
  - Verify 阶段我只做了「构建冒烟（SMOKE-OK）+ 非阻塞 launch 返回 200」就把 verify 标了近似完成；真实对话联调被推迟到人工。
  - 用户实测才暴露两个**后端旧问题**：① `qwen-turbo-latest` 403 被通义包成 `KeyError: 'request'`（改 `qwen-turbo` 解决）；② 复杂规划触发 MCP 工具时 `city` 未注入（`enforce_city_on_tools` 的 `override` 用法错误），尚待修。
- **根因：**
  - 「构建通过 / 服务能起」被当成「功能不回退」的证据，缺关键路径真实端到端冒烟 → 假绿灯。
  - 试点踩的是 Gradio/DashScope/MCP **栈特定**坑，若直接塞进 playbook 会污染通用沉淀。
- **改进动作：**
  - 验收硬规则：「功能不回退必须真实端到端冒烟，跑不了标 blocked 不标 done」→ 同步进核心文档 §3.1 与 `skills/verify-test`（含常见错误「用构建/起服务冒充功能不回退」），已 sync 到 `.cursor`/`.claude`。
  - 沉淀分流：栈特定坑写进**项目** `docs/issues-log.md`（403/KeyError、city 注入、Gradio 6 迁移三条）；只把抽象流程规则提进 playbook。
  - 试点适配 Gradio 6：theme/css 移至 `launch()`；Chatbot 用 `buttons=["copy"]` 取代 `show_copy_button`、去掉 `type`。
- **产出：** 核心文档 §3 硬规则 + verify-test 更新 + 试点 `PLAN.md`/`issues-log.md` + 验证了方法论端到端可用并形成 Observe→Improve 闭环

### 2026-06-19 M2 Skill 真源 & M3 跨工具适配 & 文档收敛

- **层：** Execute / Improve
- **改进动作：**
  - M2：在 `skills/` 产出 7 个流程 Skill（plan-spec / plan-breakdown / execute-implement / verify-test / verify-review / observe-session / improve-retro）+ 根 `AGENTS.md` + `.cursor/rules/three-iron-laws.mdc`
  - M3：`.claude/agents/` 5 个 subagent；`scripts/sync-skills.py` 把真源同步到 `.cursor/skills/` 与 `.claude/skills/`；`examples/` 端到端示例（旅游助手前端现代化走五层）
  - 文档收敛：删除 `docs/methodology/01-06.md`（与真源重复）与旧 `agents/*.md`（被取代）；更新 CONTEXT_INDEX / README；补 `.gitignore`
- **产出：** 可被 Cursor/Claude Code/Codex 加载的跨工具 skills 套件

### 2026-06-19 M0 收集参考 skills & M1 方法论定稿

- **层：** Plan / Improve
- **现象：** 方法论中「Skill」是抽象概念，与真实工具（Cursor/Claude Code/Codex）的 SKILL.md 机制脱节；P0-P3 分级在正文有处不一致；缺工具落地与本地轻量化说明；核心文档与 methodology/01-06 双份维护
- **根因：** 文档停在「方法论」阶段，未跨到「工具可执行」阶段
- **改进动作：**
  - M0：clone anthropics/skills、obra/superpowers 到 `reference/vendored-skills/`，通读三份权威写作指南，产出 `reference/SKILL-writing-guide.md`
  - M1：核心文档统一 P0-P3 四级；新增「六、工具落地层」概念映射表 + 「七、本地/单人轻量退化版」；确立核心文档为唯一真源，01-06 标注派生副本，更新 CONTEXT_INDEX
- **产出：** SKILL.md 写作规范 + 核心文档 v1.3 + 收敛后的文档结构

### 2026-06-18 飞书文档迁入 & 分层整理

- **层：** Plan / Improve
- **现象：** 飞书在线文档 Agent 无法稳定读取；导出文件含转义字符（`\|`、`\.`）
- **根因：** 需登录 + 飞书 Markdown 导出格式问题
- **改进动作：** 用户导出原文到 `docs/`，拆分为 `methodology/01-06.md`，修正格式，对齐 5 个 Agent 角色
- **产出：** 完整分层文档 + 更新后的 `CONTEXT_INDEX.md` + `agents/` 五角色

### 2026-06-18 项目初始化

- **层：** Plan
- **现象：** 飞书文档在线，Agent 无法稳定读取全文
- **根因：** 飞书需登录，WebFetch 只能获取部分内容
- **改进动作：** 将方法论迁移到本地 Markdown，用 CONTEXT_INDEX 索引
- **产出：** 本仓库 `docs/methodology/`
