# 纯口播型解析与人工复核路线

状态：产品路线已设计，语义实现待创建
适用 material_route：speech_only（纯口播型）

## 1. 主结论

Route B 必须停止以动作循环为主标准。它的主链是：

    完整 ASR
    → 语义最小单元
    → 主题与内容角色
    → 结构链识别
    → 相邻单元合并
    → 候选评分与去重
    → 候选视频和完整上下文
    → 100% 人工审核
    → 人工调整分类或切点
    → 正式视频输出

纯口播候选可以自动生成，但在 Route B 完成多素材验证并由用户另行确认前，不允许自动产生无需人工确认的正式视频。

## 2. 为什么不能复用动作路线

6 月 2 日严格盲测的事实是：完整 ASR 已完成、视觉单元 60 个、技术可解码视频 37 条，但前七个动作类均为 0，37 条全部进入人工复核，剪辑师直接可用为 0。

主要误判来自普通手势、整理头发、双手胸前微动等被当作动作候选。该结果证明动作发现和视频导出技术可运行，不证明纯口播内容解析成立。

Route B 的视觉只承担辅助检查：

- 人物与镜头是否连续。
- 是否有长时间遮挡、黑屏、卡顿、跳切风险。
- 口型/画面是否显著与音频脱节。
- 是否出现需要保留的产品、板书或互动画面。

视觉不得以普通手势创建动作主题，也不得覆盖语义边界。

## 3. ASR 优先的 analysis_unit

语义最小单元不是固定 N 秒窗口，而是 sentence_turn（句子/话轮）：

- 必填：unit_id、speaker_role、start_time、end_time、raw_text、normalized_text。
- 必填：topic_id、semantic_roles、evidence_spans、boundary_reason。
- 必填：asr_quality_status、confidence、needs_context_before、needs_context_after。
- 辅助：pause_before/after、interaction_signal、visual_continuity_status。

切分规则：

1. 先按完整 ASR 的句子、停顿、说话人变化和互动事件建立基础单元。
2. 再按主题转折、指代依赖、结构未完成和上下文需求合并相邻单元。
3. 固定时长只用于防止候选无限延长，不能作为内容边界主证据。
4. 不允许因一个关键词出现就标完整结构；每个角色必须引用原文证据跨度。

## 4. 语义字段分级

字段状态含义：

- 必需：进入相关分类时必须存在，或作为通用切分/剔除字段。
- 辅助：可提高分类和排序，但缺失不直接阻断。
- 高误判：需要上下文和证据链，不能按关键词判断。
- 人工确认：候选可自动生成，但该字段的真实性、适合发布性或业务含义必须人审。

| 字段 | 中文解释 | 项目分级 | 可直接形成候选的角色 | 主要误判风险 | 人工要求 |
|---|---|---|---|---|---|
| hook | 开头钩子 | 辅助，高误判 | 可作为候选起点，不可单独成片 | 情绪词或问句不一定是钩子 | 检查是否自然、是否标题党 |
| audience | 目标人群 | 辅助，高误判 | 不能单独成片 | “姐妹”“大家”不等于真实人群 | 业务确认 |
| pain_point | 痛点 | 必需于痛点结构 | 与原因/方案组合 | 一般负面词被误判 | 检查是否真实完整 |
| problem | 问题 | 必需于问题解决结构 | 与 solution/answer 组合 | 症状描述不等于问题链 | 检查上下文 |
| topic | 话题 | 通用必需 | 用于聚类和边界 | 主题过宽或频繁漂移 | 分类错误时人工改 |
| knowledge_point | 知识点 | 必需于知识讲解 | 与解释/结论组合 | 常识句被当知识点 | 专业性人工确认 |
| selling_point | 卖点 | 必需于卖点结构，高误判 | 与 benefit/trust_evidence 组合 | 夸张形容词、产品名命中 | 业务和合规确认 |
| benefit | 用户收益 | 辅助，高误判 | 与方法或卖点组合 | 把效果承诺当已证实收益 | 必须人工确认 |
| trust_evidence | 信任证据 | 辅助，高误判 | 与卖点组合 | 自述、数字、资历不一定可核验 | 必须人工确认真伪 |
| case_story | 案例或故事 | 必需于案例故事，高误判 | 完整人物/情境/变化链 | 假设例子被当真实案例 | 必须人工确认隐私与真实性 |
| objection | 用户异议 | 必需于异议结构 | 与 objection_answer 组合 | 普通疑问不一定是购买异议 | 人工可改分类 |
| objection_answer | 异议处理 | 必需于异议结构 | 与 objection 组合 | 回答未真正处理异议 | 人工确认完整 |
| question | 用户问题 | 必需于问答结构 | 与 answer 组合 | 修辞问句、主播自问 | 人工抽查 |
| answer | 主播回答 | 必需于问答结构 | 与 question 组合 | 时间相邻但答非所问 | 人工确认对应 |
| offer | 优惠或成交方案 | 必需于促单结构，高误判 | 与 urgency/CTA 组合 | 历史优惠、条件不完整 | 必须人工确认有效性 |
| urgency | 促单或紧迫感 | 辅助，高误判 | 与 offer/CTA 组合 | 普通时间词被误判 | 必须人工确认 |
| call_to_action | 行动引导 | 必需于促单结构 | 与 offer 或明确目的组合 | 点赞关注与购买 CTA 混用 | 人工确认用途 |
| emotion_point | 情绪点 | 辅助，高误判 | 与观点/故事组合 | 主观情绪推断 | 人工确认人感 |
| interaction | 直播互动 | 通用辅助 | 可形成互动高光 | 寒暄、点名不等于高光 | 人工确认是否值得发布 |
| repetition | 重复内容 | 通用必需 | 用于降权/去重 | 强调与重复难区分 | 低置信度人工确认 |
| noise | 无效内容 | 通用必需 | 只能剔除或裁切 | 口头禅可能承接语义 | 低置信度不自动删 |

为支持用户要求的“观点＋理由＋结论”和“痛点＋原因＋解决方案”，产品还必须新增：

| 字段 | 中文解释 | 必要性 |
|---|---|---|
| claim | 观点/主张 | 观点结构必需 |
| reason | 理由/原因 | 观点、痛点和解释结构必需 |
| conclusion | 结论 | 观点和知识结构的收束证据 |
| solution | 解决方案 | 问题/痛点结构必需 |
| context_dependency | 上下文依赖 | 防止从中间半句话起切 |
| semantic_boundary | 语义边界 | 保存候选起止理由 |

## 5. semantic_role 认定规则

每个语义角色必须包含：

- role_name。
- evidence_start/end。
- evidence_text。
- role_confidence。
- context_before/after。
- contradiction_flags。
- model_or_rule_version。

以下情形不能判结构成立：

- 只命中关键词，没有谓词、对象和上下文。
- question 与 answer 不对应。
- selling_point 与 trust_evidence 只在不同主题中偶然相邻。
- offer 已过期、缺条件或来自复述他人。
- case_story 只是“比如”引出的假设。
- pain_point 有情绪但没有明确对象。
- 结论需要前文才能理解，却从中段起切。
- 开头和结尾只是固定秒数，不是语义边界。

## 6. 候选生成流程

### 6.1 主题聚类

- 基于完整 ASR 的语义相似、实体、指代和显式转折建立 topic_id。
- 同一主题可包含多个不连续段，但默认只合并相邻或明确回指的段。
- 跨越销售插播、聊天或另一主题的段落不得自动拼接。

### 6.2 结构链识别

每条候选需保存 required_roles、present_roles、missing_roles、evidence_order 和 completeness_status。

completeness_status：

- complete：关键角色、顺序和收束齐全。
- complete_with_context：补齐相邻上下文后完整。
- partial：核心角色缺失。
- contradictory：角色互相矛盾或主题错配。
- noise_or_repeat：无效或高重复。

### 6.3 相邻单元合并

- needs_context_before 为真时向前找最近同 topic 的自然起点。
- needs_context_after 为真时向后找回答、方案、结论或 CTA 的收束。
- 合并必须记录 merged_unit_ids 和 merge_reason。
- 一旦跨 topic_break、长销售插入或人物/音轨断裂，停止自动合并。

### 6.4 候选评分

评分只用于排序，不代替硬闸门。建议分项：

- structure_completeness：结构完整度。
- boundary_quality：起止自然度。
- context_self_containment：脱离直播上下文仍能理解。
- evidence_strength：角色证据强度。
- publish_risk：健康、合规、隐私、优惠时效风险。
- repetition_penalty：与其他候选重复惩罚。
- asr_quality：转写可信度。

任何 publish_risk 为 high 的候选都必须人工确认，不得被高总分抵消。

### 6.5 重复去除

- 先按 source_asset、topic_id、语义摘要和时间重叠聚类。
- 同一观点重复时保留结构最完整、边界最自然、ASR 最清楚的一条为 primary。
- 其他候选标 duplicate_of，不删除证据。
- 强调、补充新证据或不同案例不应被机械去重。

## 7. 纯口播候选视频分类合同

“可直接剪辑”在本表只表示可自动导出候选视频，不表示 final_clip 或业务通过。Route B 正式输出始终需要人工 approved。

| 分类 | 起始信号 | 结束信号 | 内容完整条件 | 可自动导出候选条件 | 必须人工确认 | 失败和错配 |
|---|---|---|---|---|---|---|
| 1 钩子＋痛点＋解答 | 明确反差、问题或痛点钩子 | 解答/方案完成并收束 | hook 可选，pain/problem＋answer/solution 必需 | 同 topic、顺序完整、上下文自足 | 钩子是否过度、解答是否可信 | 只有情绪钩子；解答不对应 |
| 2 问题＋回答 | 明确 question | answer 完成或明确说无法回答 | 问题原文和对应回答齐全 | 问答同题、无插入跳题 | 答案是否准确、是否适合发布 | 修辞问句、答非所问 |
| 3 观点＋理由＋结论 | claim 开始 | conclusion 或明确收束 | claim＋至少一条 reason＋conclusion | 论证顺序可追溯 | 观点风险、逻辑与品牌口径 | 只有态度无理由；无结论 |
| 4 痛点＋原因＋解决方案 | pain_point/problem | solution 完成 | 痛点对象、reason、solution 齐全 | 三者同题且方案可理解 | 健康/专业/效果表达 | 原因猜测；方案不对应 |
| 5 卖点＋信任证据 | selling_point | 证据解释完或回到产品结论 | 卖点、benefit 可选、trust_evidence 必需 | 证据与卖点直接相关 | 证据真伪、夸大、合规 | 自称资历或数字不可核验 |
| 6 异议＋回应 | objection | objection_answer 完成 | 明确异议和针对性回应 | 同一购买/使用异议 | 回应是否充分、承诺风险 | 普通问答误分；回避异议 |
| 7 案例故事 | 人物/情境/冲突出现 | 结果、领悟或当前状态收束 | 人物、背景、变化/冲突、结果至少三段 | 故事线连续且隐私风险已标 | 真实性、授权、隐私 | 假设例子；无结果；跨故事拼接 |
| 8 促单＋优惠＋行动引导 | offer 或明确成交条件 | call_to_action 完成 | offer 条件＋CTA；urgency 可选 | 条件、对象、时效完整 | 优惠有效性、合规、价格 | 历史优惠；只有“快来” |
| 9 知识讲解 | knowledge_point/定义开始 | 解释、例子或结论完成 | 知识点＋解释/理由＋收束 | 不依赖前文且术语清楚 | 专业准确性、健康表达 | 只有结论；半段定义 |
| 10 情绪共鸣 | 明确共同处境或 emotion_point | 安抚、转折或结论收束 | 情境＋情绪＋回应/领悟 | 语义完整、无隐私伤害 | 人感、适合品牌、是否冒犯 | 纯情绪宣泄；断在冲突中 |
| 11 互动高光 | 有意义用户 interaction | 主播回应/结果完成 | 互动内容和回应都可理解 | 非寒暄、非点名噪音 | 是否有传播价值、用户隐私 | 只有点赞欢迎；无回应 |
| 12 人工复核 | 结构接近但缺字段/边界 | 保留足够上下文 | 不要求完整 | 只导出 review proxy | 分类、切点、完整性全部人工定 | 不得升级为直接可用 |
| 13 剔除 | noise/repetition/违规风险/无结构 | 无 | 不适用 | 不导出候选视频，仅留记录 | 低置信度剔除需抽查 | 错把强调、必要铺垫当重复 |

## 8. 人工审核与重切

### 8.1 审核人看到的内容

- 候选视频或可访问链接。
- 完整 ASR 与候选内高亮文字。
- 候选前后上下文。
- AI 分类、结构角色、选择理由和置信度。
- 起止时间、建议切点和版本。
- 重复关系、风险字段和失败原因。

### 8.2 审核动作

- 通过：当前候选版本进入正式剪辑。
- 退回：指定退回层和原因。
- 重新切开头：填写新 start_time 或前移/后移指令。
- 重新切结尾：填写新 end_time 或前移/后移指令。
- 分类错误：选择新 content_classification。
- 口播不完整：回语义合并层。
- 重复内容：标 duplicate_of 或缩短重复段。
- 不适合发布：进入 rejected_not_publishable。
- 需要重新解析：回 ASR/语义层，保留旧版本。

### 8.3 重切版本规则

- candidate_clip 不原地覆盖；每次重切生成 candidate_version。
- 新版本保存 parent_candidate_id、changed_start/end、feedback_id 和生成时间。
- 旧审核结果只对旧版本有效。
- 同一候选只有一个 current_version。
- final_clip 必须指向被 approved 的准确版本。

## 9. primary_route 与 fallback_route

primary_route：

    完整 ASR
    → 语义单元
    → 结构候选
    → 评分去重
    → 自动候选视频
    → 100% 人工审核
    → 正式输出

fallback_route：

| 失败场景 | 处理 |
|---|---|
| ASR 失败或缺段 | blocked，不用画面猜口播 |
| ASR 低质量 | 标记原文不清，生成较长上下文复核任务 |
| 语义分类不清 | content_classification=manual_review |
| 结构角色缺失 | partial，不自动正式剪辑 |
| 切点不清 | 生成 head/tail 可调 review_task |
| 高重复 | 保留 primary，其他候选标 duplicate_of |
| 高风险健康/优惠/证据 | 强制专业或业务审核 |
| 视觉连续性失败 | 候选可保留文字证据，但视频标 visual_review_required |
| 人工长期未处理 | 提醒和升级，不自动通过 |

## 10. capability_status

- 已确认：单素材完整 ASR、纯口播套动作闸门失败证据、37 条技术可解码。
- 部分成立：仓库已有部分语义角色词和人工复核理念，但未形成独立产品路线。
- 待创建：语义字段、主题聚类、结构链、评分、去重、候选版本、审核和正式输出。
- 待验证：各分类准确率、自然切点、人工负担、视频时长、批量稳定性。
- blocked：缺完整 ASR、缺人工审核人、缺高风险业务确认。

## 11. required_inputs

- source_asset、音轨和完整时间轴。
- 完整 ASR 或可运行 ASR 的实现前提。
- 业务主题/品牌敏感词和健康合规规则。
- 有代表性的正候选、负候选和人工切点金标准。
- 审核人、业务负责人和反馈枚举。
- Route B 试点允许的候选时长范围；未确认前作为配置待验证，不硬编码。

## 12. required_outputs

- 完整转写索引与质量状态。
- topic、analysis_unit 和 semantic_role 证据。
- candidate_clip、content_classification、结构完整性和评分分项。
- duplicate cluster、剔除与风险记录。
- review_task、feedback 和 candidate_version。
- final_clip、来源版本、审核人和交付状态。
- execution_record 与可提交 Git 的最小事实包。

## 13. probe_required

1. 选择 6 月 2 日纯口播素材的一小段或另一条已知纯口播样本，只做离线最小语义验证。
2. 由人工先标至少覆盖问答、知识、观点、销售/CTA、互动、重复和噪音的金标准。
3. 验证关键词单点不会判完整结构。
4. 验证 question/answer、objection/answer、卖点/证据的对应性。
5. 验证相邻单元合并和自然起止。
6. 验证重复去除不会删除有新证据的表达。
7. 所有候选 100% 人审，记录分类正确率、切点修改率、剔除率和人均审核负担。
8. 未达到用户确认门槛前，不进入正式批量剪辑。

## 14. allowed_codex_autonomy

- 在锁定字段和结构合同内拆普通 Python 模块。
- 实现 schema、排序、幂等、版本和证据引用。
- 增加单元测试、反例和报告。
- 调整不影响业务语义的文件格式、日志和错误处理。
- 根据人工明确反馈重跑指定候选版本。

## 15. forbidden_codex_guessing

- 不得自行决定哪些健康、案例、证据、优惠或业务表达可发布。
- 不得用一个关键词判完整结构。
- 不得把 AI 置信度当人工通过。
- 不得自行改分类体系、自动通过比例或上线阈值。
- 不得为了增加候选数降低完整性和上下文标准。
- 不得把 37 条技术视频写成 Route B 已有候选成功。
- 不得省略原始上下文和版本记录。

## 16. execution_entrypoints

只设计，不在本轮实现：

- build_transcript_units.py：校验完整 ASR 并建立句子/话轮。
- analyze_speech_semantics.py：生成 topic 和 semantic_roles。
- build_speech_candidates.py：结构链、相邻合并、评分和去重。
- render_review_proxy.py：导出候选审核代理视频。
- apply_review_feedback.py：创建重切/改分类版本。
- finalize_speech_clip.py：只处理 approved candidate_version。
- export_speech_fact_package.py：输出最小项目事实。

## 17. validation_commands

| 命令类型 | 中文用途 |
|---|---|
| transcript coverage test | 检查完整 ASR 是否有缺段和时间重叠 |
| semantic schema test | 检查角色证据、topic 和边界字段 |
| negative rule tests | 验证关键词、修辞问句、假案例、历史优惠不会误通过 |
| candidate boundary test | 与人工金标准比较起止偏差 |
| duplicate clustering test | 检查重复和新信息是否正确区分 |
| version lineage test | 检查重切版本和审核结果不串版 |
| media technical probe | 验证候选和正式视频技术可读 |
| human review metrics | 统计分类修改率、切点修改率、退回率和审核负担 |

## 18. blocked_if_missing

- 缺完整 ASR、时间码或说话内容可追溯性。
- 缺纯口播人工金标准，却要求确定自动通过阈值。
- 缺业务/健康/隐私审核责任人，却要求正式发布。
- 无法区分候选视频、人工通过视频和正式交付视频。
- 仍要求 Route B 以动作循环为主标准。
- 缺 candidate_version，却允许人工重切后覆盖原候选。
