# v0.5.0：证据合同、发布安全、人读与执行分离

## 摘要

相对 v0.4.0：执行侧补齐「凭什么算做到了」和「怎么安全进主干」；常驻 skill 把模型/连接器重内容抽到按需 guide；有 UI 的产品在规划期就要定使用路径。人读长文改成 skills 的导出物，Agent 启动不再读它。

## 主要变更

### 1) 证据与失败关闭

- P0/P1 要挂证据合同（真源 / 必备字段 / 失败关闭终态）；「模型说已核验」不当真源
- 事实 / 决定 / 推断 / 外部待办分开写；后两类不能标完成
- 外部依赖图：代码完成 ≠ Issue 完成
- 模板：`templates/evidence-contract-template.md`、`templates/connector-isolation-checklist.md`

### 2) 新增 `verify-release`

发布/合并做成固定阶段：allowlist、可见性、feature 分支、secret 扫描、PR、合并回执；区分单人与协作。commit / push / PR / merge 仍是分权动作。

### 3) skills 瘦身与安装

- 模型/连接器规则收到 `reference/model-and-connector-guide.md`，按需读
- `--install` 会分发被引用的 `reference/*.md`（不只是模板）
- `plan-spec` 任务三档：spike / bounded / architectural

### 4) 用户使用路径

有终端 UI 的产品：Spec 里写核心任务主线、关键路径、主/次布局。PR 和 Milestone 用「用户现在能走通什么」反馈，不只报技术功能。

### 5) 人读方法论

- 执行真源：`skills/`（启动读 `AGENTS.md` + `PLAN.md`）
- 人读导出：`docs/AI 编程方法论 — 人读版.md`（Agent 勿打开；发版后对照 CHANGELOG 可选更新）
- v1.2 飞书迁入稿冻结在 `docs/archive/`

Skill 由 7 个变为 **8 个**（加 `verify-release`）。

## 一致性

`python scripts/sync-skills.py --check` 通过。

## 升级建议

已安装的项目重新跑一次 install（会补 reference 文档和新 skill）：

```bash
python scripts/sync-skills.py --install /path/to/your-project
```
