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

### 2026-10-23 确认门禁补洞、视觉证据、依赖总等待、审查模型档位

- **层：** Execute / Verify / Observe
- **现象：** 旅游助手项目一轮开发（10-19 至 10-23，前端改版、工具调用限制、补坐标、发布）复盘：三次在用户确认前改了产品代码（10-19 上下文改动、10-21 地图与工具几轮、10-22 白点和滑动条），事后补 Issue，其中一次 Agent 自己把「不对啊」当成很急，改上的东西被用户要求撤销；白点的单测只断言样式文件里的字符串，测试通过后用户三次说「白点还在」；外部地图服务连不上时，一次是超时后退回不限时调用、界面卡死，一次是补查 12 次 × 10 秒最多卡 120 秒，后者由换成高级模型的审查发现；README 跨多个 Issue 没同步，审查列为 P1；`PLAN.md` 仍写「界面以 v0.11 原型为准」，实际布局已由后两份 Spec 改掉。
- **根因：** 确认门禁只写了「拆分确认前不写代码」，没说用户反馈不算确认、没定义「很急」能省什么；视觉验收没排除源码字符串断言；外部依赖只要求单次超时和可见失败，没有整体不可用时的总等待；审查没有模型档位要求；会话摘要不记工具和模型，换工具又换模型后无法归因。
- **改进动作：** `execute-implement` 新增「确认门禁」：改代码前写出 Issue 路径和用户确认原话，反馈不是确认，「很急」五步（复述、只省写 Issue、先写复现测试、测试通过才交付、补记）；`plan-breakdown`、Issue 模板记用户原话、要改/不改、效果图位置、确认原话；`verify-test` 与 UI 指南要求视觉证据读渲染结果；连接器指南加总等待上限与负例；`verify-review` 规定合入前审查用高级模型、对外说明不同步按 P1；`observe-session` 加「绕过确认」信号、工具与模型分栏归因、「以谁为准」同步；会话摘要与 PR 摘要模板加工具与模型栏；`AGENTS.md` 加两条关键约定。
- **证据强度：** 单一项目、单轮；本轮工具（Codex → Cursor）和编码模型同时换了，长会话、上下文压缩 3 次，前端返工多。确认门禁三次绕过、白点三次复发有原文支撑；「是模型还是工具造成」分不清，只要求以后分栏记录。同一会话里规则写进 `PLAN.md` 且压缩后被重读过，10-22 仍被绕过，所以改成「改代码前写出确认原话」这种看得见的步骤，而不是只再加一条文字规则。
- **未采纳：** Windows 下 `bash -lc` 进 WSL git 造成 CRLF（环境专属；`git diff --check` 实测能查出，问题是这次没跑，规则已有）；改静态资源后要重启（Gradio 专属）；README 展示信息（截图、话题标签）属项目偏好；「阶段 → 最低模型等级」表只落了审查一档（用户决定），规划和编码证据不足；审查不强制新上下文（PR #3 审查和编码在同一对话里，只换了模型）；不新增 `.cursor/rules`（`AGENTS.md` 在 Cursor 里已常驻）；Codex 安装位不处理。
- **产出：** 方法论更新，未新增 skill。

---

### 2026-10-20 安装器补发 E2E 指南，安装检查改为按内容比对

- **层：** Improve
- **现象：** 法律项目重装 v0.6.0 后自查发现：`verify-test` 引用的 `docs/e2e-verify-guide.md` 不随安装分发，项目留着旧版（没有产品入口、就绪等待、视口检查）；`--install --check` 对模板和参考文档只查文件在不在，旧版文件也报「一致」。
- **根因：** 安装器只扫描 `templates/` 和 `reference/` 的引用；依赖检查只做存在性检查，内容比对只覆盖 skill。
- **改进动作：** `sync-skills.py` 新增 `SHARED_DOCS` 白名单，只分发被 skill 引用、由 playbook 维护的 `docs/` 指南（目前 `e2e-verify-guide.md`），不碰 `docs/issues-log.md` 等项目自有文件。`--install --check` 对模板、参考文档、共享指南都按内容哈希比对，不一致报「内容过旧」并返回非 0。
- **产出：** 脚本修改 + README 安装说明更新。未改 skill。

---

### 2026-10-20 UI/前端：原型评审、真实入口验收、检查运行位置与索引维护

- **层：** Plan / Verify / Observe
- **现象：** 一个真实项目完成 UI 改版和前端迁移后复盘：两个原型文件用途混淆，一句「删掉上面那个」被扩大成重做导航；设计预览带外框和固定宽度，产品页面的比例和滚动问题要到用户自己的浏览器里才发现；CI 只检查旧脚本语法，前端测试、类型检查和产品构建都只在本地跑，容易被当成「CI 已覆盖」；浏览器测试把「页面加载完」当成「应用就绪」，失败的测试漏撤一个登录凭据；项目索引仍指向几个阶段前的「当前」。
- **根因：** playbook 只要求用文字写主线和主次布局，没有原型评审、真实入口验收、测试装置与凭据的规则；L1 把本地和 CI 混写；阶段收尾只更新 PLAN，不更新索引。
- **改进动作：** 新增按需读的 `reference/ui-frontend-guide.md`。`plan-spec` 要求布局有取舍时先交可点击原型（唯一入口和版本、四种状态、按位置复述、记录确认范围），Spec 模板加三行。`verify-test` 新增「有终端界面时」：在产品入口按视口矩阵验收、等应用就绪并先分诊、测试凭据在 finally 撤销并核对残留；`e2e-verify-guide` 前端示例同步修改。PR 摘要加「检查与运行位置」，`verify-review` 的 L1 要求写明 CI 还是仅本地。`observe-session` 在阶段收尾更新项目索引的「当前」条目，旧文件只加历史快照标签。规则不只服务重构：`plan-spec` 要求有界面时在原型确认后、冻结前推荐一套前端技术方案（框架、分层、状态、接口、权限、样式、测试、发布方式），每项写理由、代价和没选什么，等用户确认；Spec 模板「技术约束」加「理由与代价」「谁定的」两列。`plan-breakdown` 要求第一个 Milestone 就真实走通一条路径，新项目和改版都按路径推进。`verify-test` 补真实失败/空/无权限状态与键盘路径。
- **产出：** 新参考文档 + 现有 skill/模板补充，未新增 skill。不预设技术栈，不上提部署检查表。

---

### 2026-10-17 Spec 阶段补业务 Agent 方案

- **层：** Plan
- **现象：** 做会调用模型的产品时，Spec 可以只写功能就冻结，控制方式、记忆和调用路径要到实现时才第一次决定。
- **改进动作：** `plan-spec` 在冻结前按需读 `reference/agent-design-guide.md`，把决定写进同一份 Spec。含控制方式、记忆，以及有知识库时的业务库、是否用向量库、切分与召回。单轮、无工具、不查外部资料才写「不需要」（宿主先检索再答一次也要写知识库与召回）。`plan-breakdown` 要求 Issue 和「合理用户会踩」的测试能指回这些决定。框架官方编程资料在选定并冻结后引进项目，不写入 Spec，也不预置进 playbook。
- **产出：** 新参考文档 + Spec 模板「Agent 方案」小节（不需要时写「不需要」，不删节）。未新增 skill。

---

### 2026-10-17 计划记决策，并补上规格没点名的失败

- **层：** Plan / Verify
- **现象：** 对照 Superpowers v6.4–v7，拆分可以写成实现稿，规格没点名的输入也可以不测；技术约束可能被写成用户已经同意。
- **改进动作：** `plan-breakdown` 规定 Issue 只记文件、签名、规格值和断言，拆完等人确认再实现；每个 Issue 最多 5 条「合理用户会踩」的失败并落到测试。`verify-review` 规定这类失败不能因规格没写就降成 P3。`plan-spec` 要求猜测和技术选型标明谁拍板，冻结前用实现者视角分三堆。`execute-implement` 在拆分未确认时不写生产代码。
- **产出：** 写入现有 skill 与 Issue/Spec 模板，未新增 skill。

---

### 2026-08-21 发布 v0.5.0

- **层：** Improve
- **现象：** v0.4.0 之后已有证据合同、verify-release、瘦身、用户路径、人读/执行分离，README 仍写「master 未打 tag」。
- **改进动作：** 打 tag `v0.5.0`，release notes 见 `docs/release-notes/evidence-release-human-v0.5.0.md`。
- **产出：** GitHub Release v0.5.0。

---

### 2026-08-21 人读导出换路径，v1.2 迁入稿归档

- **层：** Improve
- **现象：** 人读总览仍占用 v1.2 文件名，看起来像执行真源；内容也落后于 8 个 skill。
- **根因：** 飞书迁入稿与「当前人读导出」挤在同一个路径。
- **改进动作：** 旧文件 `git mv` 到 `docs/archive/` 并加冻结声明。新建 `docs/AI 编程方法论 — 人读版.md`（从现行 skills 导出，文首 Agent 勿读）。CONTEXT_INDEX / README / 发布清单改指新路径。`AGENTS.md`、铁律、skill 不加入新路径。
- **产出：** 人读与执行单向分离；历史稿可查、不再更新。

---

### 2026-08-21 人读方法论与 skills 分离（Agent 启动不读）

- **层：** Improve
- **现象：** 即使改了「唯一真源」称呼，skill 文末和 AGENTS/PLAN 仍挂人读长文路径，启动仍可能打开它，分离失败。
- **根因：** 把「给人看的导出物」写进了 Agent 启动路径和 skill 参考。
- **改进动作：** 8 个 skill 去掉对那份文档的引用。`AGENTS.md` / `PLAN.md` / 铁律规则启动路径不再给路径。`CONTEXT_INDEX` 仅保留「人读导出（Agent 勿打开）」。发布清单加人读更新为「仅人、Agent 跳过」，不作为 verify-release 完成条件。
- **产出：** 执行与人读单向分离；人读版仍是 skills 导出物，不反向约束 skills。

---

### 2026-08-21 起源文档去「唯一真源」口径

- **层：** Improve
- **现象：** skills 已迭代多轮（证据合同、verify-release、用户路径等），v1.2 正文未跟上，但 AGENTS/CONTEXT_INDEX/skill 文末/Claude agents 仍称该文档为「唯一真源」，子 Agent 可能按过时章节执行。
- **根因：** 自举时把飞书整理版定为方法论真源；可执行流程迁到 skills 后，称呼没改。
- **改进动作：** 不改正文。入口改为「执行真源 = skills/」；起源文档标为人读完整版、非操作手册。7 个 skill 文末「方法论出处：唯一真源」改为「起源（执行以本 skill 为准）」；`verify-release` 注明无对应起源章节。Claude agents 改为指向对应 skill。`PLAN.md`「当前运行状态唯一真源」保留（另一层含义）。
- **产出：** 口径修正，无新 skill。

---

### 2026-08-21 用户使用路径与宏观价值反馈

- **层：** Plan / Observe
- **现象：**（用户反馈）真实项目开发到测试期才发现界面主次错位——核心问答与对话记录挤在一屏，而非 GPT 式「核心居主、历史入侧栏」。根因是规划只想「怎么拆怎么实现」，没设计「用户怎么用」。另外阶段完成后只反馈「issue-xx 实现了什么功能」，缺「从用户视角现在能走通哪条使用路径」的宏观反馈。
- **根因：** plan-spec 无面向终端用户的使用路径/信息架构环节；PR/Milestone 反馈只到技术功能层，没到用户可完成路径层。
- **改进动作：**
  - **前期设计**：`plan-spec` 新增流程步骤 4 与「用户使用路径与信息架构」节（条件触发，仅有 UI 的产品，spike 跳过）——核心任务主线 / 关键路径步骤 / 主次信息布局 / 端到端可验收场景；硬规则「有 UI 缺核心主线+主次布局不得冻结，布局主次停下等用户确认」。`spec-template` 加同名可删小节。
  - **宏观反馈**：`pr-summary-template` 加「用户视角（本次让用户能做什么）」一行；`milestone-template` 加「用户使用路径增量」小节；`observe-session` PR Summary 注明必填用户视角、Milestone 完成时输出使用路径增量并映射回 Spec 步骤。
  - **来源挂钩**：`plan-breakdown` 拆 Milestone 补「标注用户使用路径增量（映射 Spec 关键路径步骤）」。
  - 全部轻量内联，不新增 skill、不新增参考文档、不引入 persona/线框图；无 UI 项目条件跳过、小节可删，不受影响。
- **验证：** sync 8 skill、`--check` 一致。
- **产出：** 3 skill + 3 模板增量（plan-spec/plan-breakdown/observe-session、spec/pr-summary/milestone 模板），已 sync。

---

### 2026-08-20 skills 瘦身 + 证据合同去法律化 + 任务三档分流

- **层：** Improve / Plan
- **现象：**（上一条强化后自查 + 用户反馈）上一轮把大量规则内联进 skill 正文，`verify-test` 从 64→114 行、`plan-spec`/`execute-implement` 也明显膨胀；其中「失败关闭/连接器/四层数据/三层不变量」只对「接模型/外部服务」的项目生效，纯前端/CRUD 项目永远不触发却每次被读进上下文，违反铁律 2「信息触手可及，而非全部塞入」。另外证据合同模板示例带法律味（法规/条号/法律结论），让非法律项目误判为项目专属。
- **根因：** 通用规则与「仅特定项目类型生效」的重规则混在同一常驻正文；示例用了领域词汇而非中性表达。
- **改进动作：**
  - **去法律化**：`templates/evidence-contract-template.md` 示例1 改为「权威来源逐字核验类（RAG 引用/标准条款/版本化文档）」+ 适用域说明；示例2「确定法律结论」→「确定性结论」。模式通用（RAG 引用核验、RFC/ISO、药品说明书、监管文件），不再像项目专属。
  - **瘦身**：新建 `reference/model-and-connector-guide.md` 收纳失败关闭门禁+负例、三层不变量、四层数据隔离、连接器协议；`execute-implement`（113→102）与 `verify-test`（114→88）删除这些整段，只留触发指引 +「详见 guide」。纯通用项（可证伪测试、能力矩阵、证据资格审查、事实/推断分离、发布安全）保持内联。
  - **修分发隐患**：`scripts/sync-skills.py` 新增扫描并分发/校验被引用的 `reference/*.md`（`--install` 分发到 `<项目>/reference/`，`--check` 校验），顺带修好 `service-refactor-guide.md` 长期未被安装分发的断链隐患（`reference/vendored-skills/` 仍排除）。
  - **任务三档分流**：`plan-spec`「何时使用」升级为 spike / bounded / architectural 三档，轻任务跳过重仪式，每档都停下等用户确认边界（对齐 Superpowers v6.3.0）。
  - CONTEXT_INDEX 增 guide 条目；相关 skill「参考」区指向 guide。
- **验证：** `sync` 8 skill；`--check` 一致；临时目录 `--install` 分发 8 skill + 10 模板 + 3 参考文档 + AGENTS，`--install --check` 一致；脚本 lint 无错。
- **产出：** 1 份新参考文档 + 2 个 skill 瘦身 + 模板去法律化 + 脚本分发能力增强 + plan-spec 三档分流，已 sync 到 `.cursor`/`.claude`

---

### 2026-08-20 skills 瘦身 + 证据合同去法律化 + 任务三档分流

- **层：** Improve / Plan / Execute
- **现象：** 上一轮把复盘经验并入后，verify-test 从 64 涨到 114（+78%）、execute-implement 涨到 113，其中「失败关闭/连接器/四层数据/三层不变量」只对"接模型/外部服务"的项目生效，却常驻加载，违反铁律 2「信息触手可及而非全部塞入」；证据合同示例带法律味，非法律项目误以为项目专属不敢用。
- **根因：** 通用规则与"仅特定项目触发"的重内容混在常驻 skill 正文；示例措辞未去领域化。
- **改进动作：**
  - **去法律化**：`templates/evidence-contract-template.md` 示例1 改「权威来源逐字核验类（RAG 引用/标准条款/版本化文档）」+ 适用域说明，示例2「确定法律结论」→「确定性结论」，模式通用（RAG/RFC/药品说明书/监管文件）。
  - **瘦身**：新建 `reference/model-and-connector-guide.md`（68 行，按需读取），收纳失败关闭门禁+负例、三层不变量、四层数据隔离、连接器协议；`execute-implement`（113→102）、`verify-test`（114→88）删重段改触发指引+指向 guide。通用内联项（可证伪测试、能力矩阵、证据资格审查、事实/推断分离、发布安全）保持不动。
  - **修分发隐患**：`scripts/sync-skills.py` 新增扫描分发+校验被引用的 `reference/*.md`（`--install` 分发到项目 `reference/`，`--check` 校验），顺带修好 `service-refactor-guide.md` 同样的未分发断链。
  - **任务三档分流**：`plan-spec`「何时使用」升级为 spike/bounded/architectural 三档，轻任务跳过重仪式，每档停下等用户确认边界（对齐 Superpowers v6.3.0）。
- **验证：** sync 8 skill、`--check` 一致（skill+模板+参考依赖）；`--install <临时目录>` 分发 10 模板 + 3 参考文档，`--install --check` 一致。
- **产出：** 1 新参考文档 + 2 skill 瘦身 + 1 模板去法律化 + 脚本分发增强 + plan-spec 分档 + CONTEXT_INDEX，已 sync。

---

### 2026-08-20 证据合同与发布安全强化（基于 Codex 项目复盘 + Superpowers v6.2/6.3）

- **层：** Plan / Execute / Verify / Observe / Improve
- **现象：**（来自 `pj-legal_assistant` 的 Codex 项目复盘：`docs/retrospectives/2026-08-20-codex-project-retro/`）高风险问题都不是「少写 prompt」，而是信息跨层丢失——证据不足却输出 verified、事实/推断/决定/外部待办混写、模型调用前无失败关闭、外部 connector 污染普通测试、诊断暴露认证头、范围与外部依赖后置暴露、实现完成却未安全发布合并。
- **根因：** 现有 skills 覆盖流程，但缺「结论算不算数的证据契约」「失败关闭门禁」「凭据/连接器隔离」「发布/合并作为验收阶段」等强制约束与对应测试。
- **改进动作：**（只沉淀通用规则；中国法律条文、WorkBuddy 配置、合同类型/立场、G1-G3 门禁留在项目侧；未新建 Agently 命名 skill）
  - **P0-1 证据合同**：新增 `templates/evidence-contract-template.md`（含法源/connector/模型质量/blocked 四示例）；`plan-breakdown` 加「证据合同（P0/P1 前置）」硬规则（缺 source_of_truth/required_fields/fail_closed_state 不得进完成态）；`plan-spec` 加证据等级标注；`verify-review` 加「模型说已核验不能作 source_of_truth」
  - **P0-2 四类信息分离**：`improve-retro` 记录格式补 decision/external_blocker/next_owner，硬规则「inference/external_blocker 不写进 verified/complete」
  - **P0-3 失败关闭门禁**：`execute-implement` 加「失败关闭与调用前门禁」（先宿主 preflight 再外部请求、互斥终态、异常可见）；`verify-test` 加「失败关闭负例」（`model_calls==0` + 四态一致断言）
  - **P0-4 连接器/凭据/诊断隔离**：新增 `templates/connector-isolation-checklist.md`；`verify-test` 加「外部连接器协议」（进程级 autouse 断网、`RUN_REAL_*` 隔离、回执白名单）；`execute-implement` 密钥纪律补「诊断字段白名单」（禁止整体序列化 headers/auth/payload）
  - **P0-5 发布/合并安全**：新增 `skills/verify-release/SKILL.md`（现状→协作感知→allowlist→可见性→feature branch→secret 扫描→单 PR→合并门禁→合并回执）+ `templates/release-safety-checklist.md`（七种停止点）；含单人 vs 协作场景区分与破坏性操作打字确认
  - **P1-1** `plan-spec` + `spec-template` 加能力矩阵（verified/planned/unsupported/pending_external）+ 范围变更协议
  - **P1-2** `plan-breakdown` + `issue-template` 加外部依赖/证据依赖图（dependency_type/blocking_level/evidence_required/substitute_allowed/owner/rollback）
  - **P1-3** `execute-implement` 加三层不变量（领域/外部契约/宿主状态机）；任务台账改 plan-scoped
  - **P1-4** `verify-test` 加质量数据四层隔离（fixture/regression/calibration/blind set）+ 可证伪测试规范
  - **P1-5** `verify-review` 加证据资格审查（真源/逐字回读/分母资格/状态一致/失败在调用前/范围一致/无法从 diff 验证）
  - **P1-6** 重写 `templates/session-summary-template.md` 为结构化必填字段；`observe-session` 加模板自检（`template_missing_fallback`）与 `incomplete_observation` 规则
  - **工具/校验**：`scripts/sync-skills.py --check` 增 session summary 必填字段校验（正负路径已验证）；clone `superpowers@6.3.0` 到 vendored 参考；`docs/superpowers-v6-analysis.md` 补 v6.2/6.3 通用增量；更新 CONTEXT_INDEX/AGENTS/PLAN
- **明确不做（本轮）：** P2 问题指纹经验库、milestone 自动对话索引；不新建 Agently 命名 skill；不复制客户内容/真实 token/WorkBuddy 原始结果/未脱敏法律文件
- **产出：** 8 个 skill（新增 verify-release）+ 3 个新模板 + 3 个模板更新 + 脚本校验增强 + Superpowers 参考更新，已 sync 到 `.cursor`/`.claude`（8 个 skill，check 一致）

---

### 2026-07-26 plan-spec 补前置分解步骤（Spec 地图）

- **层：** Plan
- **现象：** `plan-spec` 只有「需求过大就拆子 Spec」这种事后补救，没有动笔前判断该写几份 Spec 的步骤。多能力项目会被硬塞进一份 Spec，边界互相污染；写歪的边界还会被继承进后来补拆的子 Spec。
- **根因：** 拆分触发条件挂在「篇幅过大」这个结果信号上，而不是「需求本身有几个独立能力」这个前置判据。
- **改进动作：**
  - `plan-spec` 流程插入第 2 步「先定 Spec 结构，再写内容」，并新增「Spec 分解」小节：先问「有几个用户能独立感知、且能独立上线的能力」，多个则先出 Spec 地图（项目级 Spec + 子 Spec 清单，每个只写标题与一句话），确认后只细化最近要做的 1-2 个
  - 拆分依据改为三条可观察判据（用户可独立感知 / 可独立上线 / 验收互不交叉），显式禁止按代码模块、排期、字数拆；500 字与 7 条功能降级为「兜底信号」而非依据
  - 「目录与拆分」改为「目录布局」，给出单一能力与多能力两种形态（后者含 `docs/spec/PROJECT.md`）；新增表格区分项目级 Spec 与子 Spec 各写什么，子 Spec 全局约束写「继承 parent」不复制
  - `templates/spec-template.md`：加双用途说明、「子 Spec 清单」小节、非功能性/技术约束的继承注释
  - `plan-breakdown`：有 Spec 地图时一份子 Spec 对应一个 Epic，不重新划边界
  - 两处各补常见错误条目
- **产出：** `plan-spec` / `plan-breakdown` / `spec-template` 更新，已 sync 到 `.cursor`/`.claude`

---

### 2026-07-26 Spec 治理的可执行性补齐（自查发现）

- **层：** Plan / Verify
- **现象：** 对上一条改动做实用性自查（模拟真实项目走一遍流程）暴露 6 处执行不了的地方：
  - `Verified` 是死状态——四态定义了它，但没有任何 skill 说谁在何时置位，实际跑起来 Spec 永远停在 Frozen
  - status 三处维护（子 Spec front matter / 项目级 Spec 的子 Spec 清单 / INDEX.md / PLAN.md 共四处），必然漂移
  - `spec_id` 与 AC 编号没有分配规则，Agent 会给每份 Spec 都写 `SPEC-001`
  - 「已有项目加新功能」是 plan-spec 的明示场景，但分解步骤只覆盖了从零开始
  - 单一能力项目被强制建 `INDEX.md`，一份 Spec 也要维护索引
  - 单一能力项目不建 INDEX 后，增量流程「先读 INDEX.md」会读到不存在的文件（执行断点）
- **根因：** 上一条改动只定义了结构，没有把每个字段/状态的「谁写、何时写、冲突了看谁」落到具体步骤上。
- **改进动作：**
  - 生命周期表加「谁置位」列；`verify-review` 新增「回写 Spec 状态」收尾节：最后一个 Issue 合入且 P0/P1 AC 全通过时转 Verified，有 blocked 则维持 Frozen
  - 明确 status 真源为各 Spec front matter、`INDEX.md` 为镜像；子 Spec 清单去掉 status 列，`PLAN.md` 活跃 Spec 表去掉状态列（只列 Frozen）
  - 新增「编号怎么取」：spec_id 查 INDEX 最大号 +1、只增不复用；AC 编号 Spec 内唯一，跨 Spec 写 `SPEC-002/AC-001`，review 表头注明所属 Spec
  - 新增「增量需求怎么挂」三分支：新独立能力 → 新子 Spec（必要时补建 PROJECT.md 与 INDEX）、语义变更 → revision、补充说明 → 原地改
  - 单一能力项目免建 INDEX，出现第二份时补建；增量入口注明「还没建就直接看 docs/spec/ 下已有 Spec」
  - 各处补对应常见错误条目
- **产出：** `plan-spec` / `verify-review` / `spec-template` / `spec-index-template` / `plan-document-template` 更新，已 sync

---

### 2026-07-26 安装闭环修复 + 治理瘦身（v0.4）

- **层：** Execute / Verify / Improve
- **现象：**（来自一次真实项目复盘审计）
  - 装到项目后 skill 引用的六个模板全部缺失 → `templates/xxx.md` 引用断链
  - `--project` 被 README 写成安装方式，实际只是项目内 `.claude → .cursor` 同步，不从本仓库取 skill、不分发模板
  - `--check` 只比目录名，副本内容漂移查不出来
  - `issue-template` 的「P2（边界 & 错误处理）」与 plan-breakdown 的「P2 = 可后续 PR」冲突，诱导把错误处理降级
  - Spec 缺状态与父子关系，冻结后被原地改；PLAN.md 被当成项目全量真源使用
- **根因：** 发布包不闭合（skill 与依赖资产分离分发）；Spec 层缺最小治理约定
- **改进动作：**（已按「只沉淀通用规则」裁剪，排除企业级方案）
  - `scripts/sync-skills.py`：新增 `--install <项目>` 真正从本仓库装 skill + 模板 + AGENTS.md（默认不覆盖已有 AGENTS.md）；`--check` 改为 SHA-256 内容比对并扫描模板依赖；保留 `--project` 但语义说清为项目内同步
  - `README.md`：安装以 `--install` 为准，三种模式列表区分
  - `templates/issue-template.md`：P0-P3 标题与分级表对齐，加注释「边界/错误处理若阻塞属 P0/P1」
  - PLAN.md 统一定位为「当前运行状态唯一真源」（`AGENTS.md`、`plan-breakdown`、`plan-document-template`），并补上仓库根 `PLAN.md`
  - `plan-spec` + `spec-template`：四态生命周期（Draft/Frozen/Verified/Superseded）、`spec_id`/`parent`/`version` 字段、冻结后新 revision、放宽字数改为「过大拆子 Spec」；新增 `templates/spec-index-template.md`
  - 轻量 AC 关联：Spec 验收项可编号 AC，Issue 可声明 `accepts`，`verify-review` 加逐 AC 证据表，`verify-test` 要求测试计划对上 AC
  - `execute-implement` 加「外部写操作授权」（commit/push/PR/merge/tag/Release/workflow 逐项授权）；`verify-review` 加越权检查项
  - `improve-retro`：记录格式改为 事实/推断/建议/限制 四栏，新增「进 playbook 的门槛」（需回放或第二条独立证据，栈特定经验不上提）
- **明确不做：** 新增 release-publish/git-publish skill、REQ→AC 全链路机器门禁、`traceability.yaml`、observe-session 快照协议大改、token/返工率统计
- **产出：** 安装脚本闭合 + 6 个 skill/模板更新 + 新增 `PLAN.md` 与 spec 索引模板，已 sync 到 `.cursor`/`.claude`

---

### 2026-07-19 融入服务化封装与工程骨架管理原则（框架无关）

- **层：** Plan / Execute / Verify / Improve
- **现象：** playbook 缺「从模块能跑通到别人能用上」的交付纪律：契约未前置、重构易一把梭、密钥/分层/封装边界无审查判据
- **根因：** 五层 skill 覆盖了流程，但未沉淀「服务化交付」这一横切架构纪律
- **改进动作：**（提炼自 AI 应用开发课程第 05 课，仅取语言/框架无关的范式，不含任何 Agently 专有 API）
  - `plan-spec`：新增「接口契约三问」（输入/输出与错误/调用方式）+ 行业标准载体 + 版本化变更策略（契约不改、要变加 v2）
  - `plan-breakdown`：新增重构类任务拆分范式「按关注点逐个剥离、每步可运行」；常见错误加「重构一把梭」
  - `execute-implement`：新增「工程纪律」小节（密钥纪律硬规则 / 配置三层覆盖 / 分层「不该做什么」/ 封装边界）
  - `verify-review`：审查清单加 3 项（封装边界泄漏 / 小改动动三处 = 分层错 / 密钥入库 = P0）
  - `verify-test` + `docs/e2e-verify-guide.md`：补「可消费性验收」（健康检查不依赖业务、错误码语义、契约校验、版本前缀）
  - 新增 `reference/service-refactor-guide.md`（渐进演进路线 + 语言对位表 + 反模式，按需引用不占常驻上下文）
- **产出：** 5 个 skill 字段级更新 + 1 份参考文档 + CONTEXT_INDEX 更新，已 sync 到 `.cursor`/`.claude`

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
