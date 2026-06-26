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
