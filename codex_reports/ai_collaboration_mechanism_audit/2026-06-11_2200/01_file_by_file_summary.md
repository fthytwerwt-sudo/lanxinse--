# 01 逐文件机制摘要

## 00_总说明_如何使用这套机制.md

- 主体主题：把 GPT / Codex 长期配合方式从单个项目抽象成可复用操作手册。
- 关键规则：GPT 负责判断、设计和复审；Codex 负责明确边界内执行、验证和落库；用户负责最终方向、审美和业务裁决。
- 触发条件：新项目无协作规则、准备下发 Codex、执行结果和预期不一致、需要判断状态、需要跨项目迁移。
- 禁止行为：没有项目事实源让 Codex 猜；没有真实意图直接执行；没有 Implementation design 让 Codex 自选路线；没有验证写 completed。
- 验收标准：技术、本地、远端、人审、业务结果分开回报；只迁移机制，不迁移旧项目事实。
- 工具关系：GPT 是 planning / critique / continuity 层；Codex 是 execution / verification 层；Obsidian / GPT Project 承载机制但不是项目事实源。
- 稳定性判断：稳定总规则，适合压缩后进入 GPT Project Instructions。

## 01_我的AI分工模型_GPT_Codex_Perplexity.md

- 主体主题：定义判断层、执行层、研究层、沉淀层四层分工。
- 关键规则：GPT 判断目标、边界、实现设计和验收；Codex 处理本地文件、脚本、测试、Git 闭环；Perplexity/Web 只提供外部资料；Obsidian/GitHub 承担沉淀与事实源。
- 触发条件：用户要求规划、判断、让 Codex 执行、查外部资料或沉淀结果。
- 禁止行为：Codex 自己判断方向；GPT 把外部搜索摘要当项目事实；Perplexity 输出未经保真提取就进执行；用户人审未过却写完成。
- 验收标准：每次任务能说明事实来源、本轮不做什么、执行路线、失败后回哪一层。
- 工具关系：清楚划分 GPT / Codex / Perplexity / Obsidian，强调 GPT Project / Obsidian 机制库不覆盖项目当前事实。
- 稳定性判断：稳定基础规则，适合进入 Project Instructions。

## 02_P0-P1-P2判断优先级_priority_anchor.md

- 主体主题：建立冲突优先级，避免历史记忆、旧项目经验和当前事实互相污染。
- 关键规则：P0 是用户本轮明确输入；P1 是当前项目事实源、验证输出、Git/远端 readback；P2 是历史聊天、旧项目、记忆、外部资料、参考机制；冲突时 P0 > P1 > P2。
- 触发条件：用户纠正路径或边界、多轮目标变化、当前文件和历史记忆冲突、需要判断 completed 或能力是否已验证。
- 禁止行为：用户本轮禁止事项被旧任务覆盖；P1 无证据却写已确认；P2 冒充当前事实。
- 验收标准：GPT 下发前列 P0/P1/P2；Codex 执行前确认本轮输入、当前目录、remote、工作树和允许范围。
- 工具关系：GPT 负责优先级判断；Codex 负责在执行前核对当前项目事实。
- 稳定性判断：稳定核心规则，应进入 Project Instructions。

## 03_真实意图澄清闸门_true_intent_gate.md

- 主体主题：防止 GPT 把方向问题直接翻译成 Codex prompt。
- 关键规则：先确认本轮真正要判断什么、成功是什么、失败是什么、停止条件是什么、是否只是能力证明或工具链检测。
- 触发条件：目标/成功标准/失败标准/停止条件不清，任务影响主线或投入，Codex prompt 缺真实目标和验收标准。
- 禁止行为：真实目标不清就下发 Codex；实现设计不清就下发；API / render / 安装依赖权限不清就下发。
- 验收标准：能输出“本轮真正要判断 / 本轮不判断 / 成功标准 / 失败标准 / 停止条件 / 默认假设 / 待确认位”。
- 工具关系：GPT 必须先澄清；Codex 收到缺失执行单时返回 `blocked_missing_true_intent_gate` 或 `blocked_need_implementation_design_layer`。
- 稳定性判断：稳定闸门规则，适合进入 Project Instructions。

## 04_六层需求确认与实现设计闸门_six_layer_implementation_gate.md

- 主体主题：解决“目标和流程有了，但核心实现路线没人锁”的问题。
- 关键规则：六层为目标层、机制层、Implementation design（实现设计层）、流程层、判断标准层、反馈层。
- 触发条件：任务涉及视觉、卡片、动效、声音、剪辑、BGM、调色、自动化、脚本、API、机制修改、候选产物；用户反馈“不对 / 怪怪的 / 没按之前的来”。
- 禁止行为：缺 primary_route / fallback_route / capability boundary / probe decision 就下发；用更长 prompt 代替实现设计；让 Codex 边执行边决定核心路线。
- 验收标准：每层有明确字段；失败能回到目标层、机制层、实现设计层、流程层、判断标准层或反馈层。
- 工具关系：GPT 锁路线、能力边界、fallback、blocked；Codex 只按实现设计执行。
- 稳定性判断：稳定核心机制，应作为 GPT Project Instructions 的骨架。

## 05_Codex执行单标准模板_codex_prompt_template.md

- 主体主题：固定 GPT 下发给 Codex 的执行单格式。
- 关键规则：执行单必须包含 Goal、Context、Constraints、真实意图澄清、Implementation design、Impact check、Must read、Execution steps、Done when、Blocked if、Output。
- 触发条件：需要 Codex 修改文件、写脚本、写文档、跑验证，或任务涉及 API、render、依赖、素材、外部资料。
- 禁止行为：缺 Implementation design 下发；缺 workspace / allowed files / forbidden files 下发；缺验证命令写 completed；让 Codex 自己判断 blocked。
- 验收标准：Codex 先做 workspace check、dirty check、must read、route_decision、implementation_design 完整性检查。
- 工具关系：GPT 负责任务单完整性；Codex 按单执行并证据化回报。
- 稳定性判断：稳定模板，适合改造成未来 Codex prompt 模板。

## 06_方向型输入到可执行机制_direction_to_execution.md

- 主体主题：把方向型输入转成字段、入口、验证和停止条件。
- 关键规则：方向必须转成真实意图、Implementation design、任务类型、输入字段、输出字段、执行入口、验证方式、blocked 条件。
- 触发条件：用户只说方向、GPT 方案没有入口/输出/验证、能力未 probe 却准备完整执行。
- 禁止行为：未验证能力写成已确认；禁止 API/render/安装依赖时还硬做；缺输入字段时编造；缺 implementation design 时继续执行。
- 验收标准：任务类型明确，如 `mechanism_sync`、`read_only_audit`、`component_probe`、`technical_sample`、`toolchain_completion`、`review_pack`、`documentation_export`。
- 工具关系：GPT 把方向翻译成任务合同；Codex 只执行合同化任务。
- 稳定性判断：稳定机制，适合放 Project Knowledge，也可压缩进 Instructions。

## 07_外部资料保真提取与执行桥接_external_material_bridge.md

- 主体主题：防止外部资料被 AI 误用为项目事实。
- 关键规则：资料拆成原始材料、保真事实、执行桥接、推测判断四层；推测必须标 `推测`。
- 触发条件：用户提供参考视频、截图、网页、音频、文案、竞品样片，或资料来源不在项目事实源。
- 禁止行为：复刻第三方 UI、品牌资产、可识别素材；资料真实性不明写已确认；“像它一样”替代具体可执行规则。
- 验收标准：能指出规则来自资料中的哪个可观察事实，并产出输入字段、输出字段、验收标准和禁止项。
- 工具关系：Perplexity/Web 负责资料来源；GPT 负责保真提取和执行桥接；Codex 只读明确提供或项目内资料。
- 稳定性判断：稳定专题规则，适合放 Project Knowledge；Instructions 中只保留摘要。

## 08_原感稿锁定与执行桥接_original_feel_bridge.md

- 主体主题：保留用户“原感”并转译成可执行字段。
- 关键规则：建立原感参考层和执行桥接层，两层并存，不互相覆盖。
- 触发条件：用户说“就要这个感觉”、给出参考文案/口吻/节奏/镜头感、同一份材料既要保留原文又要落地。
- 禁止行为：执行稿覆盖原感稿；把原感直接当执行规则；Codex 根据“高级感 / 像参考”自行猜审美。
- 验收标准：原感关键词、节奏、情绪、不可丢失点、执行字段、验收标准均明确。
- 工具关系：GPT 先锁原感再转译；Codex 不判断原感对错，只按桥接字段执行。
- 稳定性判断：稳定专题规则，适合内容/视频项目知识库。

## 09_失败后路线重判机制_route_replanning.md

- 主体主题：失败后不盲目重试，先判断失败层级。
- 关键规则：失败层包括目标层、机制层、实现设计层、流程层、执行层、权限层、验收层；分别对应回到真实意图、重写规则、改 route/fallback/probe、调步骤、修代码脚本、blocked、补标准或回审。
- 触发条件：同一路线连续失败、验证脚本失败、push 或远端 readback 失败、用户反馈方向不对、技术通过但内容不对。
- 禁止行为：push 失败写 completed；权限/API/余额失败硬做；路线错继续调参数；技术成功替代用户人审。
- 验收标准：输出失败现象、失败证据、失败层级、保留/放弃/降级、新 route、fallback、blocked 条件和下一目标。
- 工具关系：GPT 判断失败层级和改线策略；Codex 修执行层问题，路线/权限/目标问题 blocked。
- 稳定性判断：稳定恢复机制，适合进入 Project Instructions 摘要和 Project Knowledge 详细版。

## 10_输出状态与完成度硬规则_output_status_rules.md

- 主体主题：定义状态词和完成度边界，防止 AI 夸大完成。
- 关键规则：状态词包括 `已确认`、`部分成立`、`待验证`、`推测`、`通用建议`、`blocked`；完成度拆成 local 文件、verification、commit、push、remote HEAD、用户人审、业务目标。
- 触发条件：需要说 completed / blocked / 待验证，涉及本地、远端、技术、人审、业务验收或能力成立。
- 禁止行为：没有验证写通过；没有远端 readback 写 remote completed；没有人审写审美通过；没有多案例验证写稳定能力成立。
- 验收标准：Codex 汇报 commands、result、failed_items、commit/push/remote status、blocked reason。
- 工具关系：GPT 复审证据层级；Codex 证据化汇报，不把技术通过写成业务通过。
- 稳定性判断：稳定硬规则，应进入 Project Instructions。

## 11_跨项目迁移使用说明_cross_project_migration.md

- 主体主题：把机制搬到新项目时避免旧事实污染。
- 关键规则：迁移分机制抽象、项目初始化、执行闭环三步；可以迁移 AI 分工、P0/P1/P2、真实意图、六层确认、Codex 模板、状态词、blocked、外部资料保真方法。
- 触发条件：新建仓库、Obsidian 项目页、GPT Project，或用户希望“以后都按这套来”。
- 禁止行为：迁移旧项目路径、素材、模型选择、验收结果、候选状态、账号/API key、业务身份。
- 验收标准：每次迁移后问“这是方法还是事实”，只有方法可以通用。
- 工具关系：GPT 输出可迁移机制和禁止迁移事实两张清单；Codex 只在新项目路径落库。
- 稳定性判断：稳定迁移规则，适合放 Project Knowledge，Instructions 保留摘要。

## 12_常用Codex执行单模板库_codex_templates.md

- 主体主题：提供常用 Codex 执行单模板。
- 关键规则：所有模板都必须包含 Implementation design；复制模板后必须替换路径、事实源、允许文件、禁止事项和验证命令。
- 触发条件：机制同步、只读审计、文档导出、工具链检查、小范围 probe、失败重判。
- 禁止行为：没有 Implementation design 使用模板；模板路径未替换；模板能力状态未重新确认；旧项目事实进入新任务。
- 验收标准：按任务类型选择模板，并明确 primary_route、fallback_route、blocked_if_missing。
- 工具关系：GPT 填完整模板；Codex 按模板执行，缺字段 blocked。
- 稳定性判断：稳定模板库，但不适合整篇放 Instructions，更适合 Project Knowledge 或单独 Codex prompt 素材。

## 99_索引_Index.md

- 主体主题：机制库导航入口。
- 关键规则：先通过快速选择表定位当前问题，再打开对应机制文档；涉及 Codex 下发时优先检查六层闸门和 Codex 执行单模板。
- 触发条件：用户说“按之前那套机制来”、GPT/Codex 不确定该读哪份机制、执行跑偏需要回机制层定位。
- 禁止行为：只看索引就执行；把索引当项目事实源；把旧项目事实迁入新项目。
- 验收标准：AI 能说出当前问题对应哪一篇机制，并读取具体机制文档。
- 工具关系：GPT 用索引定位机制；Codex 不能只凭索引执行，必须读具体机制和本轮执行单。
- 稳定性判断：稳定导航文件，适合 Project Knowledge，不建议原样作为 Project Instructions。
