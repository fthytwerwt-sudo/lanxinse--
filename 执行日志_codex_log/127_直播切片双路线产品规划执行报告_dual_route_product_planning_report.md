# 127 直播切片双路线产品规划执行报告

状态：产品规划合同已完成首次 commit / push / remote HEAD 回读；本报告 closeout commit 由文件外部 Git 证据确认
执行日期：2026-07-20
任务类型：只做产品设计合同，不做业务实现

## 1. 主结论

本轮基于 GitHub main d12f8457761cc27933318ebd1222e316394774d7 的真实事实，完成了“一个入口、两条路线、一个审核与交付出口”的产品规划：

- Route A：运动＋讲解型，以动作主题、完整 ASR 回查、确定性冲突闸门和自动候选成片为主。
- Route B：纯口播型，以完整 ASR、语义结构、候选评分/去重、100% 人工审核和重切版本为主。
- mixed：按时间段拆分并分流。
- unknown：进入人工路由，不强行归类。
- 统一 job、source_asset、material_route、analysis_unit、candidate_clip、review_task、feedback、final_clip、execution_record。
- 飞书采用企业自建应用＋应用机器人＋卡片＋多维表格；视频存储主推荐 F3 混合路线，F2 为备用，F1 只做条件试点。

本轮没有把任何规划能力写成当前已实现能力。

## 2. Impact check

- 执行入口工作目录：/Volumes/WD_BLACK/澜心社剪辑
- Git 仓库根目录：/Volumes/WD_BLACK/澜心社剪辑/lanxinse--
- 分支：main
- remote：https://github.com/fthytwerwt-sudo/lanxinse--.git
- 执行前 local HEAD：d12f8457761cc27933318ebd1222e316394774d7
- 执行前 remote HEAD：d12f8457761cc27933318ebd1222e316394774d7
- git pull --ff-only：Already up to date
- 原有未跟踪目录：outputs/c5826_reference_rhythm_40s/work/、项目事实_剪辑交付计划_clipping_delivery_plans/
- 对原有未跟踪目录的处理：未修改、未暂存
- 修改现有业务代码：no
- 运行视频：no
- 调用 ASR：no
- 调用视觉模型：no
- 调用飞书 API：no
- 创建飞书应用：no
- 安装依赖：no
- 引入 LangGraph：no
- 引入 LangChain：no
- 建设 runtime：no

## 3. 读取的仓库机制

已读取：

- AGENTS.md。
- GPT Project 上传说明、上传清单、协作协议。
- 三层事实源边界和 P0/P1/P2 抗漂移机制。
- GitHub 事实读取和 Codex 落库机制。
- 中文输出、状态词、工作区/remote 边界。
- 真实意图、六层需求确认、长期执行单模板和 AGENTS 迁移说明。

执行口径：

- P0 > P1 > P2。
- GitHub main 是当前项目事实源。
- 外部资料只作为设计依据。
- 技术、内容、人审、审美、业务和交付分层。
- 有仓库改动必须限定路径暂存、commit、push 和 remote readback。

## 4. 读取的运动＋讲解型事实

### 4.1 主要文件

- 项目事实_project_facts/直播素材重筛_live_rescreen/07_动作主题完整链默认路线_action_topic_complete_chain_default_route.md
- 项目事实_project_facts/直播素材筛选_live_material_screening/19_配对逻辑修正规则_pairing_logic_revision_rules.md
- 执行日志_codex_log/125_5月13日动作主题完整链V2执行报告_513_action_topic_complete_chain_v2_report.md
- 项目事实_project_facts/直播切片V2架构审核与解析补全_live_cutting_v2_architecture_audit/06_架构缺口审计报告_architecture_gap_audit.md
- 同目录 07_V2架构补丁设计、09_人工复核清单、10_人读版报告。

### 4.2 commit

- 1a95d7bc3ab163233b4e146e52469802ce16977e：5 月 13 日动作主题 V2 实现路线。
- 7c660cdf4aa007501c8b402c51d4579119eff3a5：动作主题技术验证证据和报告。

### 4.3 结论

- 已确认：动作主题、完整 ASR 回查、真实问答、身体部位/动作名/跳题确定性闸门。
- 部分成立：单素材动作任务组和自动组装。
- 待验证：非 5 月 13 日素材、自动直出质量、抽检比例和批量稳定。
- 当前 3 个代表主题没有有效 true_pair；用户人审、审美、专业、健康、业务和发布均未通过。
- 用户 P0 对当前拆分“整体较好”的判断用于确认产品方向，但不覆盖上述 P1 状态边界。

## 5. 读取的纯口播事实

### 5.1 主要文件

- 执行日志_codex_log/126_6月2日私房话单直播严格盲测视频输出报告_62_private_talk_strict_blind_video_report.md
- 项目事实_project_facts/直播素材盲测_blind_test/01_6月2日私房话视频索引_62_private_talk_video_index.csv
- scripts/run_single_live_strict_blind_test.py
- scripts/验证单直播严格盲测_test_single_live_strict_blind_test.py

### 5.2 commit

- 6c2d67290a960f7e4e1d1f28f8d3527eaa5bf682：冻结未知直播严格盲测通用入口。
- d12f8457761cc27933318ebd1222e316394774d7：记录纯口播盲测失败证据。

### 5.3 结论

- 完整 ASR、60 个视觉单元和 37/37 技术视频可解码：已确认。
- 37 条全部 pending_manual_review，editor_ready_direct=0：已确认。
- 严格盲测结果：blind_test_failed_with_evidence。
- 普通手势、整理头发和胸前微动被动作发现误选，说明纯口播不能继续套动作分类。
- 纯口播语义分类、候选评分、去重、重切和审核后正式输出：待创建。

## 6. 发现的任务级状态冲突

现有 scripts/run_single_live_strict_blind_test.py 的报告聚合逻辑只要 plans 非空就写 completed_video_outputs_pending_user_review；但 d12f845 已正确将“37 个 plan、直接可用 0”改判为 blind_test_failed_with_evidence。

规划合同已增加硬规则：

    plan/candidate 数量大于 0
    且 editor_ready_direct 等于 0
    → 不得进入 completed
    → review_only_result 或 blind_test_failed_with_evidence

本轮只记录并进入产品合同，没有修改现有脚本。

## 7. 仓库飞书与存储事实审计

对 tracked HEAD 精确搜索：

- 飞书 / Feishu：0 个有效项目事实命中。
- 多维表格：0。
- 机器人：0。
- 视频存储 / OSS / 对象存储 / 云空间：0。
- webhook 命中仅为课程 inventory 中 huggingface_hub 依赖噪音，不是项目能力。

因此企业应用、机器人、卡片、多维表格、视频存储和回调全部标待创建；公司权限、上传上限、实际预览、容量和成本标待验证。

## 8. 飞书官方资料核验

仅使用 open.feishu.cn：

- 应用类型与能力、机器人概述、消息概述。
- 卡片回传交互回调和飞书卡片常见问题。
- 多维表格记录/字段相关 API。
- 云空间普通上传、素材上传、分片预上传/上传分片/完成上传、下载和权限。

官方确认边界：

- 企业自建应用＋应用机器人可承载通知和交互卡片。
- card.action.trigger 需在 3 秒内响应；卡片回调失败不自动补推。
- 卡片不支持内嵌视频直接播放，只能链接或封面图＋链接。
- 同一多维表格写操作不应并发。
- 普通上传上限 20 MB；大文件需串行分片。
- 本项目 MP4 预览稳定性、公司容量、最终单文件上限和成本仍需真实账号 probe。

本轮未调用飞书 API。

## 9. 新增规划文件

1. 项目事实_project_facts/产品化规划_productization_planning/01_直播切片双路线产品总方案_dual_route_product_master_plan.md
2. 同目录 02_运动讲解型自动剪辑产品路线_motion_explanation_route.md
3. 同目录 03_纯口播型解析与人工复核路线_speech_only_review_route.md
4. 同目录 04_素材类型路由与统一状态机_material_routing_unified_state_machine.md
5. 同目录 05_飞书人工审核与视频交付方案_feishu_review_delivery_plan.md
6. 同目录 06_阶段实施路线图与验收矩阵_implementation_roadmap_acceptance_matrix.md
7. 执行日志_codex_log/127_直播切片双路线产品规划执行报告_dual_route_product_planning_report.md

## 10. 产品设计覆盖

- 产品定位和双路线事实差异。
- 自动路由、人工覆盖、mixed/unknown 降级。
- Route A 模块、输入、输出、分类、闸门和失败。
- Route B 语义字段分级、13 类候选合同、评分、去重和重切。
- 九个统一实体、多轴状态机、幂等和可重跑。
- 十类人工 feedback 回流。
- 四条完整用户流程和 AI/Codex/人工/飞书/GitHub 分工。
- 飞书四张表、卡片交互、回调和失败处理。
- F1/F2/F3 比较、F3 主推荐、F2 备用和账号 probe。
- Phase 1 至 Phase 6 的输入、输出、验收、失败和下一阶段闸门。
- 技术、语义、动作、候选、直接可用、人审、审美、人感、业务、交付和批量稳定分层。

## 11. 本轮边界验证

- 正式业务代码变更：0。
- 新视频：0。
- 素材运行：0。
- ASR/视觉模型调用：0。
- 飞书 API 调用：0。
- 依赖安装：0。
- LangGraph/LangChain/runtime：0。
- secret 写入：0。
- 媒体写入 Git：0。

## 12. Git 闭环

产品规划首次闭环结果：

- 规划文件存在：yes。
- 内容验证：passed。
  - 6 份规划＋1 份报告存在，AppleDouble `._*` 为 0。
  - 纯口播 21 个语义字段和 13 类候选合同齐全。
  - 四类素材路由、统一状态、7 个产品页面、F1/F2/F3、Phase 1-6 均通过关键词与结构校验。
  - 正式代码、视频、素材运行、模型/API、依赖、secret 和媒体入 Git 均为 0。
- path-limited stage：passed，仅暂存 6 份规划和本报告，共 7 个 Markdown 文件。
- planning_contract_commit：`a98fb7832ae79199d63c3d8ec66bd18a5534f911`。
- push：passed，`origin/main` 从 `d12f8457761cc27933318ebd1222e316394774d7` 前进到 `a98fb7832ae79199d63c3d8ec66bd18a5534f911`。
- remote HEAD readback：passed；local HEAD、`origin/main`、重新 fetch 的 `FETCH_HEAD` 和 `git ls-remote origin refs/heads/main` 四者一致。
- remote file readback：passed；6 份规划和本报告的 7 个 blob 均逐一一致。
- 首次闭环后的工作区：本轮路径无未提交修改；保留两个任务前已存在的 untracked 目录，未暂存、未修改。

说明：包含本段 closeout 内容的最终 commit SHA 无法在文件内部自指记录；必须在提交后用 `git log`、`git push`、`git ls-remote` 和远端文件回读从文件外部确认。
