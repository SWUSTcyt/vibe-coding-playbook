# v0.4.0：安装闭环修复 + Spec 治理瘦身

## 摘要

本次发布修掉「装到项目后模板断链」的安装缺口，并把 Spec 从「随便写一份」收成可执行的轻量治理：四态生命周期、前置分解（Spec 地图）、可选 AC 追踪，以及外部写操作授权与复盘四栏格式。全部按实用性自查过一遍，补齐了「谁置位、怎么编号、增量怎么挂」等执行断点。

## 主要变更

### 1) 安装闭环：`--install` 真正可用

- `scripts/sync-skills.py` 新增 `--install <项目>`：从本仓库装 skill + 模板 + `AGENTS.md`（默认不覆盖已有 `AGENTS.md`）
- `--check` 改为 SHA-256 内容比对，并扫描模板依赖是否齐全
- `--project` 语义说清为「项目内 `.claude → .cursor` 同步」，不是安装入口
- README 以 `--install` 为推荐安装/升级方式

### 2) plan-spec：Spec 生命周期 + 前置分解

- 四态：`Draft` → `Frozen` → `Verified` → `Superseded`，每态标明「谁置位」
- 动笔前先定结构：问「有几个用户能独立感知、且能独立上线的能力」；多个则先出 Spec 地图，只细化最近 1-2 个
- 拆分依据是三条可观察判据（可独立感知 / 可独立上线 / 验收不交叉），不是字数
- 增量场景三分支：新子 Spec / revision / 原地改；单一能力项目免建 `INDEX.md`
- 编号规则：`spec_id` 查 INDEX 最大号 +1；AC 编号 Spec 内唯一，跨 Spec 写 `SPEC-002/AC-001`

### 3) 轻量 AC 关联（可选）

- Spec 验收项可编号；Issue 可声明 `spec:` / `accepts:`
- `verify-review` 声明了 AC 时逐条给证据；全部通过才回写 Spec 为 `Verified`
- `verify-test` 测试计划对上 AC

### 4) 执行与复盘纪律

- `execute-implement`：外部写操作（commit/push/PR/merge/tag/Release/workflow）需逐项授权
- `verify-review`：越权写操作 → P0
- `improve-retro`：问题记录改为 事实 / 推断 / 建议 / 限制 四栏；进 playbook 需回放或第二条独立证据

### 5) PLAN.md 定位收紧

- 统一定位为「当前运行状态唯一真源」（≤500 tokens）
- 需求全貌与历史归 `docs/spec/`；补仓库根 `PLAN.md` 示例

## 一致性

- `.cursor/skills/`、`.claude/skills/` 与 `skills/` 真源一致（`--check` 通过）
- `CHANGELOG.md`、相关模板已同步

## 升级建议

已安装本 playbook 的项目，用 `--install` 重新装一遍（幂等，会修复漂移与缺失模板）：

```bash
python scripts/sync-skills.py --install /path/to/your-project
```

新项目同样用 `--install`，不要再用 `--project` 当安装入口。
