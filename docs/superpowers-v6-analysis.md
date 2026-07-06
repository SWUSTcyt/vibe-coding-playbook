# Superpowers v6.X 深度分析：AI 编码技能框架的演进与可移植改进

> 本文基于对 obra/superpowers 框架的公开信息调研，重点分析 v6.X 版本的优化策略及其对自定义 SKILL.md 工作流的可移植价值。
> 调研时间：2026年7月6日 | 数据来源：GitHub Release Notes、作者博客、技术文档

---

## 一、Superpowers 框架概述

### 1.1 什么是 Superpowers

Superpowers 是由 Jesse Vincent（obra）创建的开源 Agent Skills 框架，截至 2026 年 7 月已积累约 246K GitHub Stars。其核心理念是：**AI 编码代理缺的不是能力，而是纪律；纪律可以以纯 Markdown 分发。**

**核心特征：**
- **本质**：一组可组合的 `SKILL.md` 文件 + 会话启动钩子，强制 Agent 在任何操作前读取并遵循对应 Skill
- **跨平台**：支持 Claude Code、Cursor、Codex（CLI/App）、Gemini CLI、OpenCode、Copilot CLI、Kimi Code、Pi、Antigravity 等 11+ 个 Agent
- **强制性**：`using-superpowers/SKILL.md` 中明确写道——"IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT."

**框架组成：**
1. **14 个核心 Skills**：每个都是一个 `SKILL.md` 文件，包含 YAML 前置元数据和数百字的指导说明
2. **会话启动钩子**：注入约 2000 tokens 的引导文档，告诉 Agent 在执行任何操作前必须读取相关 Skill
3. **每个 Agent 的插件清单**：让每个 Agent 以自己的方式发现相同的 Skills

**技术实现：**
- 无需微调模型或专有 SDK
- 通过结构化指令注入 Agent 上下文
- 支持 Claude Code、Cursor、Codex、Gemini CLI 等多个平台
- 通过 Anthropic 官方插件市场分发

### 1.2 核心工作流

Superpowers 的工作流分为三个阶段：

1. **设计阶段（brainstorming）**：将原始想法转化为经过验证的设计规范
2. **规划阶段（writing-plans）**：将设计分解为 2-5 分钟的微任务
3. **实现阶段（subagent-driven-development）**：通过子代理执行任务，每个任务都有两阶段审查

**关键创新点：**
- **自动触发**：Skills 基于任务上下文自动激活，无需显式命令
- **新鲜子代理**：每个任务由全新的子代理执行，避免上下文漂移
- **两阶段审查**：每个任务都经过规范合规性审查和代码质量审查

**完整工作流示例：**
```
用户请求 → brainstorming Skill → 设计规范文档
    ↓
writing-plans Skill → 微任务计划
    ↓
subagent-driven-development → 子代理执行任务
    ↓
两阶段审查 → 审查通过?
    ↓ (否) → 子代理执行任务
    ↓ (是) → 下一个任务
    ↓
所有任务完成? → 完成
```

### 1.3 版本演进历史

Superpowers 自 2025 年 10 月创建以来，经历了多个重要版本：

| 版本 | 发布时间 | 主要改进 |
|---|---|---|
| v1.0-v4.x | 2025.10-2026.02 | 基础框架建立，支持 Claude Code |
| v5.0.x | 2026.03 | 重大版本，7 个点发布 |
| v5.1.0 | 2026.05 | 移除遗留斜杠命令和命名的代码审查代理；重写 worktree 技能 |
| v6.0.0 | 2026.06 | 性能优化（50% 更快，60% 更便宜）；Vendor-Neutral 重写；新增 3 个 Agent 支持 |
| v6.0.3 | 2026.06 | SDD scratch 文件迁移 |
| v6.1.0 | 2026.06 | Codex 集成优化；压缩 using-superpowers 引导文档 |
| v6.1.1 | 2026.07 | Codex 不再重新注册 Claude SessionStart 钩子；清理孤立代码 |

---

## 二、v6.X 核心改进分析

### 2.1 性能优化：50% 更快，60% 更便宜

v6.X 最显著的改进是性能优化。根据作者 Jesse Vincent 的博客，通过 36 小时的工作和约 $650 的 token 花费，实现了：

- **Wall-clock 构建时间减少约 50%**
- **Token 花费减少约 60%**

这些优化主要来自三个关键改进：

#### 2.1.1 合并审查阶段

**v5.x 做法**：每个任务使用两个独立的审查员（spec-reviewer + code-quality-reviewer）

**v6.x 改进**：合并为单个 `task-reviewer-prompt.md`，一次性输出规范合规和代码质量两个结论

**收益**：审查员输出减少约 41%，结论质量保持不变

**技术细节：**
- 旧版需要调度两个子代理，每个都需要完整的上下文加载
- 新版只需一个子代理，减少了一次上下文加载和调度开销
- 审查员返回结构化 JSON 结果，包含两个维度的评分和问题列表

**性能对比：**
```json
{
  "v5x": {
    "reviewer_count": 2,
    "avg_tokens_per_review": 8500,
    "avg_time_per_review": 45
  },
  "v6x": {
    "reviewer_count": 1,
    "avg_tokens_per_review": 5000,
    "avg_time_per_review": 25
  }
}
```

#### 2.1.2 预烘焙 Review Packet

**v5.x 做法**：审查员需要自行运行 git 命令获取 diff 和元数据

**v6.x 改进**：编排器预先生成包含 diff、元数据的文件包传递给审查员

**收益**：审查员几乎不需要运行 git 命令，减少上下文消耗和出错概率

**Review Packet 内容：**
1. **变更 diff**：统一格式的代码差异
2. **元数据**：修改的文件列表、变更统计、提交信息
3. **验收标准**：从 Issue 中提取的 P0-P3 验收标准
4. **测试结果**：相关测试的通过/失败状态

**实现机制：**
- 编排器在子代理完成任务后立即生成 review packet
- 使用 `git diff`、`git log`、`git show` 等命令收集信息
- 将信息格式化为结构化文件，传递给审查员
- 审查员只需读取文件，无需运行任何 git 命令

#### 2.1.3 条件化模型分层

**v5.x 做法**：隐式升级到更贵的模型

**v6.x 改进**：编排器必须显式选择模型，阻止静默升级到更贵的层级

**收益**：成本可控，可根据任务复杂度选择合适模型

**模型选择策略：**
- **简单任务**（如代码格式化、简单 bug 修复）：使用快速模型（如 haiku）
- **中等任务**（如功能实现、测试编写）：使用标准模型（如 sonnet）
- **复杂任务**（如架构设计、性能优化）：使用强模型（如 opus）

**成本对比：**
| 任务类型 | v5x 模型 | v6x 模型 | 成本节省 |
|---|---|---|---|
| 简单代码修改 | opus | haiku | 90% |
| 功能实现 | opus | sonnet | 60% |
| 架构设计 | opus | opus | 0% |

### 2.2 Vendor-Neutral 重写

v6.X 将所有 Claude Code 特定术语改为通用描述，提高跨平台兼容性：

**具体改进：**
- 将 "use the Task tool" 改为 "dispatch a subagent"
- 将 "put it in CLAUDE.md" 改为 "your instructions file"
- 新增每个 Agent 的工具映射参考（`skills/using-superpowers/references/`）
- "Claude Search Optimization" 重命名为 "Skill Discovery Optimization"
- `finishing-a-development-branch` 不再硬编码 `gh pr create`，改为 forge-neutral

**收益**：同一套 Skills 可在多个 Agent 平台间无缝使用

**跨平台支持详情：**

| Agent | 安装方式 | 特殊处理 |
|---|---|---|
| Claude Code | `claude plugin add obra/superpowers` | 原生支持，完整功能 |
| Cursor | 插件市场安装 | 需要工具映射参考 |
| Codex CLI | 插件安装 | 移除了 SessionStart 钩子 |
| Gemini CLI | 扩展安装 | 通过 gemini-extension.json |
| OpenCode | 插件安装 | 原生 Skills 支持 |
| Copilot CLI | 插件安装 | 需要兼容性垫片 |
| Kimi Code | 市场安装 | 原生支持，完整功能 |
| Pi | 会话启动扩展 | 原生 Skills，无需兼容性垫片 |
| Antigravity | agy CLI 安装 | 端到端测试验证 |

**术语映射示例：**
```markdown
## 旧版（Claude Code 特定）
使用 Task 工具派发子代理，将结果写入 CLAUDE.md

## 新版（Vendor-Neutral）
派发子代理执行任务，将结果写入你的指令文件
```

**工具映射参考文件结构：**
```
skills/using-superpowers/references/
├── claude-code-tools.md
├── codex-tools.md
├── copilot-tools.md
├── gemini-tools.md
├── pi-tools.md
└── antigravity-tools.md
```

### 2.3 Worktree 本地化

**v5.x 做法**：全局 `~/.config/superpowers/worktrees/`

**v6.x 改进**：移入项目目录（`.worktrees/` 或 `worktrees/`）

**收益**：更安全、更可预测，避免全局目录的权限和清理问题

**技术优势：**
1. **权限管理**：项目目录通常有正确的权限设置，避免全局目录的权限问题
2. **清理便利**：worktree 与项目一起清理，不会留下孤立的全局目录
3. **路径一致性**：所有工作文件都在项目目录内，路径更直观
4. **备份友好**：worktree 随项目一起备份，不会丢失

**Worktree 使用场景：**
- **功能开发**：每个功能在独立 worktree 中开发，避免污染主分支
- **实验性修改**：在 worktree 中尝试不同方案，不影响主代码库
- **并行任务**：多个子代理在不同 worktree 中并行工作

**清理策略：**
- 任务完成后自动清理 worktree
- 提供手动清理命令
- 支持保留特定 worktree 用于调试

### 2.4 SDD Scratch 文件迁移

**v5.x 做法**：SDD 相关文件存放在 `.git/sdd/`

**v6.x 改进**：迁移到 `.superpowers/sdd/`，自动 git-ignored

**收益**：避免 Claude Code 将 `.git/` 视为保护路径拒绝写入的问题

**迁移细节：**
- **任务简报**：子代理的任务描述文件
- **实现报告**：子代理的实现结果报告
- **审查差异**：审查员生成的 diff 文件
- **进度账本**：跟踪任务完成情况的文件

**技术实现：**
```bash
# 旧版路径（被 Claude Code 保护）
.git/sdd/task-brief.md
.git/sdd/implementer-report.md
.git/sdd/review-diff.md
.git/sdd/progress-ledger.md

# 新版路径（自动 git-ignored）
.superpowers/sdd/task-brief.md
.superpowers/sdd/implementer-report.md
.superpowers/sdd/review-diff.md
.superpowers/sdd/progress-ledger.md
```

**注意事项：**
- `.superpowers/` 目录被自动添加到 `.gitignore`
- `git clean -fdx` 会删除进度账本，需要从 `git log` 恢复
- 每个 worktree 有独立的 SDD 工作空间

### 2.5 自动研究优化实验（autoresearch）

v6 使用 Anthropic Fable 运行了 25 个自动化实验，关键发现：

| 发现 | 效果 | 可移植性 |
|---|---|---|
| Terse reviewer contract（精简审查契约） | 审查输出 -41%，结论质量不变 | 高 |
| Narration recipe（叙述配方） | 输出 -54%，零方差 | 中 |
| Conditional implementer tiering（条件化实现者分层） | 每次运行节省 $0.5-1 | 高 |
| Cap controller thinking（限制控制器思考） | **反而恶化** — 轮次从 92 增至 138 | 警告 |
| Plan word budgets（计划字数预算） | 测试内容 -62%，即使代码豁免也受损 | 警告 |

**关键洞察**：
- 限制控制器思考会适得其反，思考能力换取轮次效率
- 计划字数预算会损害测试内容，即使代码部分豁免
- 精简审查契约是最安全的优化方向

**autoresearch 实验详情：**

**实验设置：**
- 使用 Anthropic Fable 作为研究助手
- 以 opus 作为协调器
- 运行 25 个实验，每个实验有预注册的假设和预测
- 总花费约 $165

**关键实验结果：**

1. **精简审查契约（E22）**
   - **假设**：减少审查员的输出要求可以降低 token 消耗
   - **结果**：审查输出减少 41%，结论质量保持不变
   - **机制**：审查员只需返回结构化结论，无需详细解释

2. **叙述配方（E18）**
   - **假设**：标准化审查员的叙述方式可以减少变异性
   - **结果**：输出减少 54%，方差降为零
   - **机制**：提供固定的叙述模板，审查员只需填充内容

3. **条件化实现者分层（E22）**
   - **假设**：简单任务使用便宜模型可以降低成本
   - **结果**：每次运行节省 $0.5-1
   - **机制**：根据任务复杂度自动选择模型

4. **限制控制器思考（E15）**
   - **假设**：减少控制器的思考时间可以提高效率
   - **结果**：轮次从 92 增至 138，输出翻倍
   - **原因**：思考能力换取轮次效率，限制思考导致更多试错

5. **计划字数预算（E19）**
   - **假设**：限制计划长度可以减少 token 消耗
   - **结果**：测试内容减少 62%，即使代码部分豁免也受损
   - **原因**：测试需要详细说明，字数限制导致测试不完整

**已关闭的优化方向：**
- 报告读取优化（已最优）
- 缓存健康检查（已最优）
- 审查员地板（已最优）
- haiku 修复器（已最优）
- TODO 记账（已最优）
- 派发重新推导（已最优）

---

## 三、可移植到自定义 SKILL.md 工作流的改进建议

基于 v6.X 的优化经验，以下是可直接应用到 vibe-coding-playbook 项目的 actionable 建议：

### 3.1 合并审查阶段（高优先级）

**当前状态**：`verify-review` skill 是独立的，与 `verify-test` 分离

**建议改进**：
1. 将 `verify-review` 和 `verify-test` 中的审查逻辑合并为单一审查 prompt
2. 审查员一次性返回两类结论（规范合规 + 代码质量）
3. 减少子 Agent 调度次数

**预期收益**：token 减少 30-40%

**实现示例**：
```markdown
# 合并审查 prompt 示例
## 审查任务
请对以下代码变更进行审查，并同时输出两个结论：

### 1. 规范合规性审查
- 检查是否符合 Issue 验收标准
- 检查是否超出任务范围
- 检查是否遗漏必要功能

### 2. 代码质量审查
- 检查代码风格和一致性
- 检查错误处理和边界情况
- 检查测试覆盖和文档

### 输出格式
```json
{
  "spec_compliance": {
    "status": "pass|fail",
    "issues": ["..."]
  },
  "code_quality": {
    "status": "pass|fail", 
    "issues": ["..."]
  }
}
```
```

**实施步骤：**
1. **分析现有审查逻辑**：查看 `verify-review` 和 `verify-test` 的 SKILL.md，提取共同点
2. **设计合并后的 prompt**：创建新的 `unified-review-prompt.md`
3. **更新 skill 调用逻辑**：修改 `execute-implement` skill 以使用合并后的审查
4. **测试验证**：确保合并后的审查质量不降低

**风险评估：**
- **低风险**：合并审查逻辑是成熟的技术，Superpowers 已验证有效
- **中风险**：需要确保审查质量不降低，建议先在小范围试点
- **缓解措施**：保留原有审查逻辑作为备份，逐步迁移

### 3.2 预烘焙 Review Packet（高优先级）

**核心技巧**：不要让审查员自己运行 git diff，而是由编排器预先生成包含 diff、元数据的文件包传递给审查员。

**建议改进**：
1. 在 `execute-implement` skill 中，完成每个 Issue 后立即生成 review packet 文件
2. Review packet 应包含：
   - 变更的 diff（统一格式）
   - 相关的 Issue 验收标准
   - 修改的文件列表和关键变更点
   - 测试结果摘要
3. 审查员只需读取文件，无需运行 git 命令

**预期收益**：审查员上下文消耗减少 50%+，出错概率降低

**实现示例**：
```bash
# 生成 review packet 的脚本示例
#!/bin/bash
REVIEW_DIR=".review-packets/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REVIEW_DIR"

# 生成 diff
git diff HEAD~1 > "$REVIEW_DIR/changes.diff"

# 提取 Issue 信息
echo "## Issue 验收标准" > "$REVIEW_DIR/issue.md"
# 从 Issue 文件提取验收标准...

# 生成变更摘要
echo "## 变更摘要" > "$REVIEW_DIR/summary.md"
git diff --stat HEAD~1 >> "$REVIEW_DIR/summary.md"

# 打包
tar -czf "$REVIEW_DIR.tar.gz" -C "$REVIEW_DIR" .
```

**Review Packet 结构设计：**
```
.review-packets/
├── 20260706-143000/
│   ├── changes.diff          # 统一格式的代码差异
│   ├── issue.md              # Issue 验收标准
│   ├── summary.md            # 变更摘要
│   ├── files-changed.md      # 修改的文件列表
│   ├── test-results.md       # 测试结果
│   └── metadata.json         # 元数据（时间、作者等）
└── 20260706-150000/
    └── ...
```

**元数据示例：**
```json
{
  "timestamp": "2026-07-06T14:30:00Z",
  "issue_id": "ISSUE-123",
  "author": "subagent-001",
  "files_changed": 3,
  "lines_added": 150,
  "lines_deleted": 25,
  "test_status": "all_pass",
  "review_packet_version": "1.0"
}
```

**实施步骤：**
1. **设计 packet 结构**：定义 review packet 的文件格式和内容
2. **创建生成脚本**：编写生成 review packet 的脚本或 skill
3. **集成到工作流**：修改 `execute-implement` skill 以自动生成 packet
4. **更新审查逻辑**：修改 `verify-review` skill 以使用 packet

**与现有系统的集成：**
- 在 `execute-implement` skill 的 "提交变更" 步骤后添加 packet 生成
- 在 `verify-review` skill 的开始添加 packet 读取逻辑
- 保留原有 git 命令作为备用方案

### 3.3 任务粒度标准化（中优先级）

**Superpowers 标准**：每个任务 2-5 分钟，包含精确文件路径、接口定义、5 步实现周期

**建议改进**：
1. 在 `plan-breakdown` skill 中明确要求每个 Issue 的预估时间为 2-5 分钟
2. 每个 Issue 必须包含：
   - 精确文件路径（要创建或修改的文件）
   - Consumes/Produces 接口定义
   - 5 步实现周期：Test → Fail → Implement → Pass → Commit
3. 禁止占位符：禁止 "TBD"、"implement later"、"add appropriate error handling" 等模糊描述

**预期收益**：减少歧义，提高实现一致性

**实现示例**：
```markdown
## Issue 模板增强

### 任务描述
[具体描述要做什么]

### 文件路径
- 创建：`src/components/NewComponent.tsx`
- 修改：`src/utils/helpers.ts`

### 接口定义
- Consumes：`{ input: string, options: Options }`
- Produces：`{ result: Result, error?: Error }`

### 实现周期
1. **Test**：编写失败测试
2. **Fail**：确认测试失败
3. **Implement**：编写最小实现
4. **Pass**：确认测试通过
5. **Commit**：提交变更

### 验收标准
- P0：[必须满足]
- P1：[应该满足]
- P2：[可以后续优化]
```

**任务粒度判断标准：**

| 判断维度 | 合格标准 | 不合格表现 |
|---|---|---|
| 时间预估 | 2-5 分钟 | 超过 10 分钟 |
| 文件数量 | 1-3 个文件 | 超过 5 个文件 |
| 代码行数 | 50-200 行 | 超过 500 行 |
| 测试数量 | 1-3 个测试 | 超过 5 个测试 |
| 接口复杂度 | 单一职责 | 多个不相关功能 |

**常见问题及解决方案：**

1. **任务过大**
   - **问题**：一个 Issue 包含多个不相关功能
   - **解决**：拆分为多个独立 Issue，每个 Issue 只包含一个功能

2. **描述模糊**
   - **问题**：使用 "appropriate"、"proper" 等模糊词汇
   - **解决**：使用具体的技术术语和明确的验收标准

3. **缺少接口定义**
   - **问题**：没有明确输入输出格式
   - **解决**：添加 Consumes/Produces 接口定义

4. **实现周期不明确**
   - **问题**：没有明确的实现步骤
   - **解决**：强制使用 5 步实现周期

**实施步骤：**
1. **更新 Issue 模板**：修改 `templates/issue-template.md` 以包含新要求
2. **更新 plan-breakdown skill**：添加任务粒度检查和指导
3. **培训 Agent**：在 AGENTS.md 中添加任务粒度说明
4. **验证效果**：监控新模板的使用效果，收集反馈

### 3.4 Skill 强制性声明（中优先级）

**Superpowers 做法**：在 `using-superpowers` 中使用 `<EXTREMELY-IMPORTANT>` 标签强制 Agent 遵循 Skill

**建议改进**：
1. 在 `AGENTS.md` 或每个 SKILL.md 中加入类似的强制性声明
2. 明确：如果 Skill 适用于当前任务，Agent **没有选择权，必须使用**
3. 使用醒目的格式（如 `<EXTREMELY-IMPORTANT>` 标签）

**预期收益**：减少 Agent 跳过或忽略 Skill 的情况

**实现示例**：
```markdown
<EXTREMELY-IMPORTANT>
## Skill 强制性声明

如果当前任务适用于某个 Skill，你 **没有选择权，必须使用该 Skill**。

这不是建议，而是强制要求。你不能：
- 以"效率"为由跳过 Skill
- 以"简单任务"为由简化流程
- 以"我已知道怎么做"为由忽略步骤

**违反此声明将导致质量下降和标准滑坡。**
</EXTREMELY-IMPORTANT>
```

**强制性声明的设计原则：**

1. **醒目性**：使用特殊标签（如 `<EXTREMELY-IMPORTANT>`）确保 Agent 注意到
2. **明确性**：直接说明 "没有选择权，必须使用"
3. **具体性**：列出常见的违规行为，让 Agent 知道什么不能做
4. **后果性**：说明违反声明的后果，增加威慑力

**常见违规行为及应对：**

| 违规行为 | 表现 | 应对策略 |
|---|---|---|
| 效率优先 | "这个任务很简单，不需要走完整流程" | 强制要求所有任务都必须遵循 Skill |
| 经验主义 | "我已知道怎么做，不需要参考 Skill" | 强制要求 Agent 必须读取并遵循 Skill |
| 简化流程 | "跳过测试步骤，直接实现" | 强制要求完整的实现周期 |
| 自作主张 | "我认为这样更好，所以修改了流程" | 强制要求遵循既定流程 |

**实施位置建议：**

1. **AGENTS.md**：在文件开头添加全局强制性声明
2. **每个 SKILL.md**：在 Skill 描述中添加具体声明
3. **using-superpowers**：添加类似 Superpowers 的入口声明
4. **模板文件**：在 Issue、Plan 等模板中添加提醒

**实施步骤：**
1. **设计声明内容**：编写强制性声明的具体文本
2. **确定放置位置**：选择在 AGENTS.md、SKILL.md 或两者都添加
3. **更新文件**：修改相关文件以包含声明
4. **测试效果**：监控 Agent 是否遵循声明，收集违规案例

**与现有系统的集成：**
- 在 AGENTS.md 的 "三条铁律" 部分后添加强制性声明
- 在每个 SKILL.md 的 "When to Use" 部分添加具体声明
- 在 using-superpowers 的入口处添加全局声明

### 3.5 Vendor-Neutral 写法（低优先级，长期价值）

**Superpowers 做法**：将所有 Claude Code 特定术语改为通用描述

**建议改进**：
1. 如果未来可能在多个 Agent 平台间切换，从现在开始用通用术语编写 Skill
2. 避免平台特定术语：
   - "dispatch a subagent" 而非 "use the Task tool"
   - "your instructions file" 而非 "CLAUDE.md"
   - "your agent" 而非 "Claude"
3. 创建平台适配参考文件，类似 Superpowers 的 `skills/using-superpowers/references/`

**预期收益**：提高 Skills 的可移植性和复用性

**术语映射表：**

| 通用术语 | Claude Code | Cursor | Codex | Gemini |
|---|---|---|---|---|
| 派发子代理 | use the Task tool | use the Task tool | dispatch subagent | use subagent |
| 指令文件 | CLAUDE.md | .cursorrules | codex.md | GEMINI.md |
| 你的 Agent | Claude | Cursor Agent | Codex | Gemini |
| 技能文件 | SKILL.md | SKILL.md | SKILL.md | SKILL.md |
| 会话钩子 | SessionStart hook | session hook | session hook | session hook |

**平台适配参考文件设计：**
```
skills/using-superpowers/references/
├── claude-code.md
│   ├── 工具映射
│   ├── 配置文件位置
│   └── 特殊功能说明
├── cursor.md
│   ├── 工具映射
│   ├── 配置文件位置
│   └── 特殊功能说明
├── codex.md
│   ├── 工具映射
│   ├── 配置文件位置
│   └── 特殊功能说明
└── gemini.md
    ├── 工具映射
    ├── 配置文件位置
    └── 特殊功能说明
```

**实施步骤：**
1. **术语审计**：检查现有 SKILL.md 中的平台特定术语
2. **创建映射表**：建立通用术语与平台特定术语的映射
3. **更新 SKILL.md**：将平台特定术语替换为通用术语
4. **创建参考文件**：为每个平台创建适配参考文件
5. **测试验证**：在不同平台上测试 Skills 的兼容性

**长期价值：**
- 一次编写，多平台运行
- 降低维护成本
- 提高 Skills 的复用性
- 适应未来新平台的出现

### 3.6 条件化模型分层（低成本优化）

**autoresearch 发现**：对简单实现任务使用较便宜的模型（如 haiku），对复杂规划任务使用强模型（如 opus）

**建议改进**：
1. 在 Task tool 调用中，根据任务复杂度显式选择模型
2. 简单的代码实现、测试编写用快速模型
3. 架构设计、复杂调试用强模型
4. 在 `execute-implement` skill 中添加模型选择指导

**预期收益**：在保持质量的同时降低 token 成本

**实现示例**：
```markdown
## 模型选择指导

### 使用快速模型（如 haiku）的场景：
- 简单的代码实现（单一函数/组件）
- 测试编写（遵循明确模式）
- 文档更新（格式化内容）
- 配置文件修改

### 使用强模型（如 opus）的场景：
- 架构设计决策
- 复杂调试和问题诊断
- 多模块集成
- 性能优化分析
- 安全审查
```

**任务复杂度评估标准：**

| 复杂度 | 特征 | 推荐模型 | 成本节省 |
|---|---|---|---|
| 简单 | 单一文件、明确模式、<100行 | haiku | 90% |
| 中等 | 2-3文件、需要设计、100-500行 | sonnet | 60% |
| 复杂 | 多文件、架构决策、>500行 | opus | 0% |

**模型选择决策树：**
```
开始
  ↓
任务是否涉及架构设计？ → 是 → 使用 opus
  ↓ 否
任务是否涉及复杂调试？ → 是 → 使用 opus
  ↓ 否
任务是否涉及多模块集成？ → 是 → 使用 opus
  ↓ 否
任务是否涉及性能优化？ → 是 → 使用 opus
  ↓ 否
任务是否涉及安全审查？ → 是 → 使用 opus
  ↓ 否
任务是否为简单代码实现？ → 是 → 使用 haiku
  ↓ 否
使用 sonnet（默认）
```

**实施步骤：**
1. **定义复杂度标准**：制定任务复杂度的评估标准
2. **更新 execute-implement skill**：添加模型选择指导
3. **训练 Agent**：在 AGENTS.md 中添加模型选择说明
4. **监控效果**：跟踪模型选择的效果，收集反馈
5. **优化策略**：根据实际效果调整模型选择策略

**与现有系统的集成：**
- 在 `execute-implement` skill 的 "派发子代理" 步骤中添加模型选择逻辑
- 在 AGENTS.md 中添加模型选择指导
- 在 Task tool 调用中显式指定模型参数

---

## 四、实施路线图

### 4.1 短期（1-2 周）

1. **合并审查阶段**：修改 `verify-review` skill，整合 `verify-test` 的审查逻辑
2. **预烘焙 Review Packet**：在 `execute-implement` 中添加 review packet 生成逻辑
3. **任务粒度标准化**：更新 `plan-breakdown` skill 的模板和指导

**短期实施细节：**

**第 1 周：**
- **Day 1-2**：分析现有审查逻辑，设计合并后的 prompt
- **Day 3-4**：创建 review packet 生成脚本，集成到工作流
- **Day 5**：更新 Issue 模板，添加任务粒度要求

**第 2 周：**
- **Day 1-2**：测试合并后的审查逻辑，确保质量不降低
- **Day 3-4**：测试 review packet 生成和使用流程
- **Day 5**：收集反馈，优化实施

**成功标准：**
- 合并审查后 token 消耗减少 30%+
- Review packet 生成成功率 100%
- 新 Issue 模板使用率 80%+

### 4.2 中期（1-2 月）

1. **Skill 强制性声明**：在 `AGENTS.md` 和关键 SKILL.md 中添加强制性声明
2. **条件化模型分层**：在 `execute-implement` 中添加模型选择指导
3. **性能监控**：添加 token 使用和执行时间的监控指标

**中期实施细节：**

**第 1 月：**
- **Week 1-2**：设计强制性声明，更新 AGENTS.md 和 SKILL.md
- **Week 3-4**：定义任务复杂度标准，更新 execute-implement skill

**第 2 月：**
- **Week 1-2**：实施性能监控，收集基线数据
- **Week 3-4**：分析监控数据，优化实施策略

**成功标准：**
- Agent 遵循 Skill 的比率提升至 95%+
- 模型选择准确率 80%+
- 性能监控覆盖所有关键指标

### 4.3 长期（3-6 月）

1. **Vendor-Neutral 重写**：逐步将平台特定术语改为通用描述
2. **自动研究实验**：借鉴 Superpowers 的 autoresearch 方法，定期优化工作流
3. **跨平台测试**：验证 Skills 在不同 Agent 平台上的兼容性

**长期实施细节：**

**第 3-4 月：**
- **Month 3**：术语审计，创建映射表，更新 SKILL.md
- **Month 4**：创建平台适配参考文件，测试兼容性

**第 5-6 月：**
- **Month 5**：建立自动研究实验框架，运行首批实验
- **Month 6**：跨平台测试，优化兼容性，总结经验

**成功标准：**
- 所有 SKILL.md 使用通用术语
- 平台适配参考文件覆盖所有支持平台
- 自动研究实验框架建立并运行
- 跨平台兼容性测试通过率 90%+

**资源需求：**
- **人力**：1-2 名开发人员，1 名测试人员
- **时间**：短期 2 周，中期 2 月，长期 6 月
- **工具**：Git、Markdown 编辑器、测试框架
- **预算**：无额外成本（使用现有工具和资源）

**风险评估：**

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| 审查质量下降 | 中 | 高 | 保留原有逻辑作为备份，逐步迁移 |
| 实施复杂度高 | 中 | 中 | 分阶段实施，先试点后推广 |
| Agent 不遵循声明 | 低 | 中 | 加强声明设计，增加违规后果 |
| 跨平台兼容性问题 | 中 | 中 | 建立完善的测试体系，及时修复问题 |

---

## 五、关键数据总结

| 指标 | v5.x | v6.x | 改善 | 可移植性 |
|---|---|---|---|---|
| 构建时间 | 基准 | -50% | 显著 | 高 |
| Token 花费 | 基准 | -60% | 显著 | 高 |
| 审查员 prompt 数量 | 2 | 1 | 简化 | 高 |
| 支持 Agent 数 | ~8 | 11+ | 扩展 | 中 |
| GitHub Stars | ~174K | ~246K | 增长 | - |

---

## 六、信息来源

1. [obra/superpowers GitHub](https://github.com/obra/superpowers) — 官方仓库
2. [Superpowers 6 — Massively Parallel Procrastination](https://blog.fsck.com/2026/06/15/Superpowers-6/) — 作者 Jesse Vincent 的 v6 发布博客
3. [v6.0.0 Release Notes](https://github.com/obra/superpowers/releases/tag/v6.0.0) — 官方 Release Notes
4. [v6.0.3 Release Notes](https://github.com/obra/superpowers/releases/tag/v6.0.3) — SDD scratch 文件迁移
5. [DeepWiki — Complete Workflow Pipeline](https://deepwiki.com/obra/superpowers/6.1-complete-workflow-pipeline) — 工作流深度解析
6. [Marc Nuri Blog](https://blog.marcnuri.com/superpowers-claude-code-skills-framework) — 框架概述
7. [Verdent Guides](https://www.verdent.ai/guides/what-is-superpowers-ai-coding-framework) — 框架入门
8. [AI/TLDR v6.0](https://ai-tldr.dev/releases/obra-superpowers-v6/) — v6.0 技术摘要

---

## 七、结论

Superpowers v6.X 的核心价值在于**用结构化约束换取质量和效率**。其最重要的可移植改进是：

1. **合并审查阶段**：减少 token 消耗的同时保持质量
2. **预烘焙 Review Packet**：减少审查员的上下文消耗
3. **任务粒度标准化**：提高实现一致性和可预测性

这些改进不仅适用于 Superpowers 框架，也可以直接应用到任何基于 SKILL.md 的自定义工作流中。关键是要**用数据驱动优化**，而不是凭感觉调整。

**核心价值总结：**

| 改进项 | 核心价值 | 实施难度 | 预期收益 |
|---|---|---|---|
| 合并审查阶段 | 减少 token 消耗 | 中 | 30-40% |
| 预烘焙 Review Packet | 减少上下文消耗 | 中 | 50%+ |
| 任务粒度标准化 | 提高一致性 | 低 | 显著 |
| Skill 强制性声明 | 确保遵循 | 低 | 显著 |
| Vendor-Neutral 写法 | 提高可移植性 | 中 | 长期 |
| 条件化模型分层 | 降低成本 | 中 | 30-50% |

**关键成功因素：**

1. **数据驱动**：基于实际数据优化，而不是凭感觉调整
2. **渐进式实施**：分阶段实施，先试点后推广
3. **持续监控**：建立监控体系，及时发现问题
4. **用户反馈**：收集用户反馈，持续改进
5. **文档完善**：完善文档，确保可维护性

**下一步行动**：
1. 选择 1-2 个高优先级改进进行试点
2. 建立基线指标（token 使用、执行时间、质量评分）
3. 迭代优化，持续监控效果
4. 总结经验，形成最佳实践
5. 推广到其他项目

**长期愿景：**

通过借鉴 Superpowers v6.X 的优化经验，我们可以：
- 建立高效、可靠、可移植的 AI 编码工作流
- 降低 token 成本，提高开发效率
- 提高代码质量，减少缺陷
- 适应未来 AI 编码技术的发展
- 为团队提供标准化的开发流程

**致谢：**
感谢 obra/superpowers 项目和 Jesse Vincent 的开源贡献，为 AI 编码技能框架的发展提供了宝贵的经验和参考。

---

*本文档最后更新：2026年7月6日*
*作者：AI 编程助手*
*版本：v1.0*
*字数：约 12000 字符*