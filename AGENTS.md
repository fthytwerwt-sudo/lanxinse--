# AGENTS.md

## 文件定位

本文件是 `fthytwerwt-sudo/lanxinse--` 仓库的 AI 接手入口文件。

本文件属于 GitHub `main` 的仓库接手入口，不直接放入 GPT Project 上传包。

本文件只写接手入口、读取顺序、执行纪律、事实源边界，不写具体阶段状态、API 状态、客户需求细节或执行结果。

## 当前项目身份

- 当前仓库：`fthytwerwt-sudo/lanxinse--`
- 当前项目：澜心社自动剪辑 / 澜心社直播 / AI 协作系统
- 本仓库职责：承载当前项目事实、机制同步包、Codex 报告、执行记录、文档和验证证据。

注意：不要在这里写具体阶段状态、API 状态、客户需求细节或执行结果。

## 三层 + 执行层

- 账号记忆：跨项目长期协作偏好。
- GPT Project：当前项目配合机制层。
- GitHub `main`：当前项目事实源。
- Codex：本地执行落库层。

## 默认读取顺序

1. 用户本轮明确输入，也就是本轮 `P0`。
2. 当前仓库根目录 `AGENTS.md`。
3. `GPT项目资料同步包_gpt_project_mechanism_sync/` 中的配合机制文件。
4. 当前仓库的项目事实文件。
5. 当前仓库的 Codex 报告、执行日志、验证记录、风险记录、决策记录。
6. 本轮执行产生的 Git 证据：commit、push、remote HEAD readback。

## 必读机制入口

接手当前仓库任务时，至少读取以下机制入口：

- `GPT项目资料同步包_gpt_project_mechanism_sync/00_GPT_Project上传说明_readme.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/上传清单_manifest.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/00_协作协议_collaboration_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/01_三层架构与事实源边界_three_layer_source_boundary.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/02_P0-P1-P2锚点与抗漂移机制_anchor_priority_anti_drift.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/03_GitHub事实源读取机制_github_fact_source_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/04_Codex执行落库机制_codex_execution_to_repo_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/07_输出硬规则与中文语义对齐_output_hard_rules.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/22_真实意图澄清闸门机制_true_intent_clarification_gate.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/23_六层需求确认与实现设计闸门机制_six_layer_requirement_implementation_gate.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/24_Codex长期执行单模板_codex_task_template.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/25_AGENTS机制迁移说明_agents_mechanism_migration_note.md`

如果上述文件不存在或不可读，必须 `blocked`，不得脑补机制内容。

## P0 / P1 / P2 优先级

- `P0`：用户本轮明确目标、边界、禁止项、完成标准。
- `P1`：当前仓库 GitHub `main` 文件、验证结果、commit / push / remote HEAD 证据。
- `P2`：历史聊天、账号记忆、旧项目机制、外部资料、研究摘要。

冲突时按 `P0 > P1 > P2` 执行。

`P2` 只能作为参考，不得冒充当前项目事实。

## GPT 接手规则

GPT 是外层总控脑，负责：

- 判断真实卡点。
- 区分任务层级。
- 判断目标、边界、验收、风险。
- 必要时触发真实意图澄清。
- 必要时触发六层需求确认。
- 设计 Codex 执行单。
- 从 GitHub `main` 读取项目事实。
- 不把聊天中间态、外部资料、旧项目经验写成当前项目事实。

GPT 输出时必须先给主结论，再说明事实来源和状态词，并区分机制、事实、推测、建议。

## Codex 接手规则

Codex 是执行落库层，负责：

- 读取文件。
- 检查现状。
- 执行任务。
- 生成报告。
- 写入仓库。
- 验证。
- commit / push。
- 回报证据。

Codex 执行前必须检查：

```text
pwd
git rev-parse --show-toplevel
git branch --show-current
git remote -v
git status
```

如果当前仓库不是 `fthytwerwt-sudo/lanxinse--`，或 remote 不指向 `https://github.com/fthytwerwt-sudo/lanxinse--.git`，必须停止并标 `blocked_wrong_workspace_or_remote`。

## 六层需求确认与实现设计闸门

复杂任务、方向不清、机制冲突、反馈失败或 GPT 准备下发 Codex 执行单前，必须检查六层：

1. 目标层
2. 机制层
3. 实现设计层
4. 流程层
5. 判断标准层
6. 反馈层

缺实现设计层时，必须标：

```text
blocked_need_implementation_design_layer
```

不得用更长 prompt 代替实现设计层。不得让 Codex 在执行阶段自行决定核心路线。

## Codex 执行单必须包含

- Goal 目标
- Context 上下文
- Constraints 边界
- 六层需求确认
- Impact check 影响面检查
- Must read 必读文件
- Execution steps 执行步骤
- Done when 完成标准
- Blocked if 阻断条件
- Output 回报格式

缺少真实目标、验收标准或失败判定时，Codex 必须 blocked 或回报缺口，不得猜。

## 项目事实落库规则

以下内容属于项目事实，应写入 GitHub `main` 的项目事实区，不进入 GPT Project 机制包：

- 项目状态
- 执行报告
- 阶段结果
- 验收标准
- 客户需求
- API 状态
- 代码
- 测试结果
- 风险记录
- 决策记录
- Codex 执行日志

以下内容属于配合机制，可进入 GPT Project 机制包：

- 协作协议
- 判断顺序
- 下发格式
- 质量保障机制
- 澄清闸门
- 六层需求确认机制
- Codex 执行模板

GPT Project 只放配合机制，不放项目事实。项目事实必须回 GitHub `main` 当前文件读取。

## Git 纪律

修改仓库前必须确认分支和 remote，并先执行 `git pull --ff-only`。

产生仓库文件改动后：

- 只 stage 本轮相关文件。
- 禁止 `git add .`。
- 必须 commit。
- 必须 push。
- push 成功后必须验证 remote HEAD。

`completed` 必须同时满足：

- commit 已创建。
- push 已成功。
- remote HEAD 已验证。

本地有文件但未 push，不得写 `completed`。

push 失败必须标：

```text
blocked_push_failed
```

## 状态词硬规则

只使用受控状态词：

- `已确认`
- `部分成立`
- `待验证`
- `推测`
- `通用建议`
- `待创建`
- `待补全`
- `blocked`

禁止把 local-only 写成 completed。禁止把技术通过写成内容、审美、人感或业务通过。

## 文件命名规则

自定义文件和目录默认使用：

```text
中文说明_english_slug.ext
```

例外：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `package.json`
- `Dockerfile`
- 第三方工具强制要求的固定文件名

不知道怎么命名时，必须先问或标 `待确认`，不得随便创建纯英文文件名。

## 旧项目迁移边界

旧项目只能迁移：

- 协作机制
- 判断顺序
- 下发格式
- 质量保障机制
- 澄清闸门
- 六层需求确认与实现设计闸门
- Codex 执行模板
- 可复用的 AGENTS 协作纪律

旧项目不能迁移：

- 项目身份
- 项目状态
- 素材路径
- 模型选择
- API 状态
- 验收结果
- 业务方向
- 完成状态
- 执行日志
- 产物能力结论

旧项目只属于 `P2` 机制参考，不得覆盖当前项目 `P0 / P1`。

## 输出回报要求

Codex 回报必须包含：

- commands
- result
- failed_items
- files_changed
- validation
- commit / push / remote status
- blocked reason

GPT 回答必须：

- 先给主结论
- 说明事实来源和状态词
- 区分机制、事实、推测、建议
- 给出下一步可执行动作

## 一句话执行口径

进入本仓库先读 AGENTS，再读机制包，再读 GitHub `main` 项目事实；GPT 负责判断和设计，Codex 负责执行和落库，所有项目事实必须回到当前仓库验证。
