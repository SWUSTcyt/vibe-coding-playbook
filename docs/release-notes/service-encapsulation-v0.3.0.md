# v0.3.0：融入服务化封装与工程骨架管理原则（框架无关）

## 摘要

本次发布把「从模块能跑通到别人能用上」的交付纪律融入 playbook 五层 skill，全部为语言/框架无关的范式（提炼自 AI 应用开发课程第 05 课，零框架专有 API）。

## 主要变更

### 1) plan-spec：接口契约前置
- 新增「接口契约三问」：输入是什么 / 输出与错误是什么（4xx = 调用方错，5xx = 服务方错）/ 怎么调用
- 载体采用行业标准（OpenAPI、类型化 Schema），不自创规范
- 版本化变更策略：契约一经发布不改，要变加 `/v2`

### 2) plan-breakdown：重构类任务拆分范式
- 服务化/工程化重构按关注点逐个剥离（配置 → prompt/资源 → 装配边界 → 接入协议）
- 每个 Issue 结束时代码必须可运行、可验证
- 常见错误新增：重构一把梭 → 出错无法定位

### 3) execute-implement：工程纪律
- 密钥纪律（硬规则）：敏感信息永不进代码库，`.env` 不进 git、`.env.example` 进 git
- 配置三层覆盖：代码默认值 ← 配置文件 ← 环境变量
- 职责分层看「不该做什么」+ 封装边界（调用方不出现内部实现词）

### 4) verify-review：审查判据
- 审查清单新增 3 项：封装边界泄漏检查 / 「小改动动三处 = 分层错」（P1）/ 密钥入库（P0）

### 5) verify-test + e2e-verify-guide：可消费性验收
- 健康检查端点可用且不依赖业务模块
- 错误码语义正确、响应符合 Spec 契约、有版本前缀
- e2e-verify-guide 附可直接运行的检查代码

### 6) 新增参考文档
- `reference/service-refactor-guide.md`：渐进演进路线表 + 语言对位表（Python/Go/Node.js/Java）+ 反模式清单，按需引用不占常驻上下文

## 一致性

- `.cursor/skills/`、`.claude/skills/` 与 `skills/` 真源 diff=0
- `CONTEXT_INDEX.md`、`CHANGELOG.md` 已同步更新

## 升级建议

已安装本 playbook skill 的项目，重新同步即可：

```bash
python scripts/sync-skills.py --project /path/to/your-project
```
