# 运动讲解型自动剪辑产品路线

状态：路线方向已确认，通用产品化待实现与验证
适用 material_route：motion_explanation（运动＋讲解型）

## 1. 路线目标

Route A 的目标不是“发现画面有手在动”，而是把同一动作的完整解释证据和动作执行证据组装为分类视频：

    原始直播
    → 完整 ASR
    → 视觉动作发现
    → action_topic_id
    → 同动作口播聚合
    → 结构识别
    → 讲解与动作组装
    → 自动候选成片
    → 人工抽检
    → 正式输出

当前规则可复用，但现有单素材实现和批量能力不能直接写成通用产品已成立。

## 2. 当前可复用事实与缺口

| 项目 | 状态 | 处理决定 |
|---|---|---|
| 视觉动作主题作为入口 | 已确认 | 复用规则 |
| action_topic_id 稳定编号 | 已确认 | 复用概念，改为通用 source_asset 编号 |
| 完整 ASR 同动作回查 | 已确认 | 复用，禁止固定时间窗去重 |
| 用途/问题/原因/边界/方法/动作口令 | 已确认 | 复用为动作解释角色 |
| body_part_match、action_name_match、topic_break_present | 已确认 | 保留为确定性一票否决 |
| 5 月 13 日专用 TOPIC_SPECS 和视觉 ID | 已确认存在 | 禁止作为通用入口 |
| 自动生成分类视频 | 部分成立 | 技术路径存在，质量与跨素材待验证 |
| 当前有效真配对 | 已确认是 0 | 不得写为既有直接可用能力 |
| 人工抽检工作流 | 部分成立 | 有表格和状态，无统一产品 |
| 多直播批量稳定运行 | 待验证 | Phase 6 前不得宣称 |

## 3. primary_route（主路线）

### 3.1 模块合同

| 模块 | 输入 | 输出 | 判断闸门 | 失败处理 |
|---|---|---|---|---|
| A01 素材预检 | source_asset | technical_probe | 文件、音轨、时长、散列均有效 | 技术失败则 blocked |
| A02 完整 ASR | 音轨 | transcript analysis_unit | 覆盖完整、有时间码、质量状态存在 | ASR 失败则 blocked_asr_missing |
| A03 视觉动作发现 | 视频、采样策略 | visual analysis_unit | 有可识别目的性动作，不是普通手势 | 不清则 manual_action_review |
| A04 动作主题建立 | visual units | action_topic_id、动作名、部位、起止 | 动作身份可描述、主体可见、换动作风险可控 | 证据不足不建主题 |
| A05 同动作口播聚合 | 完整 ASR、动作主题 | role evidence spans | 动作名称/别名/部位命中，同题证据可追溯 | 无命中则 partial |
| A06 结构识别 | role evidence、visual evidence | structure_type | 所需角色齐全且无跳题 | 不完整进入人工复核 |
| A07 确定性冲突检查 | 口播与视觉字段 | match flags | 部位、动作名一致；无 topic break | 任一硬冲突进入 logic_mismatch |
| A08 视频组装 | 证据片段、动作片段 | candidate_clip | 角色顺序、切点和音画连续性满足合同 | 组装失败可重跑 |
| A09 技术验证 | candidate video | technical status | 可读、有音视频流、完整解码 | 技术失败自动重试限定次数 |
| A10 人工抽检 | candidate_clip、证据 | review_task | 当前版本人工明确决定 | 不通过回到对应层 |
| A11 正式输出 | approved candidate | final_clip | 来源、版本、审核人和技术探针齐全 | 缺任一字段不得交付 |

### 3.2 动作主题创建硬条件

只有同时保存以下证据才允许创建 action_topic_id：

- observed_action_name（观察到的动作名称）。
- observed_body_part_or_tool（身体部位或工具）。
- action_start/end（动作起止）。
- presenter_visible（主体可见性）。
- action_cycle_status（动作循环状态）。
- action_change_risk（换动作风险）。
- visual_evidence_refs（视觉证据引用）。

普通手势、整理头发、双手放胸前、静止、镜头变化和拿取物品，若没有与教学动作同题的口播和动作循环证据，只能标 incidental_gesture（附带手势）或 noise，不得创建可直出的动作主题。

### 3.3 完整 ASR 回查硬条件

- 扫描完整转写，不使用“150 秒内只留一个口播单元”。
- 动作名、别名、身体部位和操作方式用于证据匹配；时间距离只辅助排序。
- 同一动作的用途、问题、原因、边界、方法和口令可来自不同时间段，但必须有原文和时间码。
- 多个角色复用同一转写段时标 shared_source_segment，不复制假片段。
- 问答必须同时存在明确 question（问题）和对应 answer（回答）；模型生成的泛化问题不算证据。
- 没有真实问题时使用 action_teaching_structure（动作教学结构），不得伪造问答。

### 3.4 自动直出硬闸门

全部为真才可标 editor_ready_direct：

1. material_route 已确认是 motion_explanation。
2. 动作主题有清晰动作身份、身体部位和执行范围。
3. 口播与动作属于同一动作、同一问题或同一目的。
4. method_or_instruction_present 为真。
5. action_cycle_status 为 yes。
6. presenter_visible 为 yes 或经验证允许的 partial。
7. body_part_match 为 yes。
8. action_name_match 为 yes。
9. topic_break_present 为 no。
10. 中间不存在销售、聊天或另一动作造成的逻辑断裂。
11. 技术探针通过。
12. 路由与质量阈值已经在非专用素材 probe 中验证。

第 12 项未完成前，即使前 11 项通过，也只能进入 auto_candidate_pending_sample_review，不得直接批量交付。

## 4. 分类保留、合并与调整

现有名称不能全部继续作为同一层级的“内容分类”。产品应拆为 content_classification（内容分类）、structure_type（结构类型）、assembly_mode（组装方式）和 review_state（审核状态）。

| 现有分类 | 产品决定 | 新字段映射 | 直接可用条件 |
|---|---|---|---|
| 问题回答后动作 | 保留 | content=question_answer；structure=answer_then_action | 真实问题、回答、方法和同题动作齐全 |
| 痛点原因后动作 | 保留 | content=pain_reason_solution；structure=explanation_then_action | 痛点、原因/边界、方法和动作齐全 |
| 用途方法后动作 | 保留 | content=purpose_method；structure=explanation_then_action | 用途、方法和动作齐全 |
| 误区纠正后动作 | 保留 | content=mistake_correction；structure=explanation_then_action | 错误方式、纠正、正确动作齐全 |
| 讲解在前动作在后 | 保留为通用结构 | content=action_teaching；structure=explanation_then_action | 无更具体内容类但完整链成立 |
| 边讲边做 | 保留 | structure=interleaved_explanation_action | 同一连续段内音画同题，动作不被切断 |
| 已重排成讲解后动作 | 从内容分类移出 | assembly_mode=reordered_explanation_then_action | 原始段可追溯，重排无语义跳跃 |
| 人工复核 | 从内容分类移出 | review_state=pending_review | 不能作为内容通过 |
| 逻辑错配剔除 | 保留为终止状态 | candidate_status=rejected_logic_mismatch | 不生成正式视频 |

为兼容历史目录，可继续导出 01 至 08 文件夹，但统一索引必须按新字段记录；历史 07/08 目录名不得继续承担唯一语义。

## 5. 各分类结构条件

| 内容结构 | 起始信号 | 完整条件 | 结束信号 | 失败条件 |
|---|---|---|---|---|
| question_answer_then_action | 明确问题句 | 回答直接回应问题，随后有方法/动作 | 动作一轮完成或明确收束 | 泛化问题、答非所问、动作不同题 |
| pain_reason_then_action | 明确痛点/现象 | 原因或边界＋解决方法＋动作 | 动作完成且话题未跳转 | 只有痛点关键词或原因无动作 |
| purpose_method_then_action | 明确用途/收益 | 用途＋操作方法＋同题动作 | 方法和动作完成 | 用途夸大、无方法、动作不明 |
| mistake_correction_then_action | 错误/误区陈述 | 错误点＋纠正理由＋正确动作 | 正确示范完成 | 只说“不要”但无正确做法 |
| explanation_then_action | 教学解释开始 | 至少目的/问题之一＋方法＋动作 | 动作完成、自然收束 | 解释和动作不是同题 |
| interleaved_explanation_action | 边说边做开始 | 口播持续解释当前动作 | 当前动作自然结束 | 口播属于聊天/销售或动作被遮挡 |

## 6. fallback_route（备用路线）

| 失败场景 | 备用处理 | 允许输出 |
|---|---|---|
| 素材类型不清 | 转 unknown 路由审核 | 路由证据，不输出正式视频 |
| ASR 失败 | 等待重跑或人工提供可用转写 | 技术失败记录 |
| 视觉模型失败 | 人工查看 contact sheet 或原片 | manual_action_review |
| 动作识别不清 | 不创建自动动作主题 | 人工候选或剔除 |
| 口播动作同题不清 | 保存完整上下文 | pending_pair_review |
| 动作循环不完整 | partial_action_task_group | 不得直出 |
| 画面动作可用但讲解分散 | 允许 assembly_mode=reordered，但必须人工抽检 | candidate_clip |
| 切点不确定 | 生成 head/tail 可调审核任务 | 不生成 final_clip |
| 健康或效果表达高风险 | 强制业务/专业人工复核 | 不得自动正式交付 |
| 人工长期未处理 | 提醒、升级负责人 | 保持 pending，不自动通过 |

## 7. capability_status（能力状态）

- 已确认：动作主题规则、完整 ASR 回查原则、真实问答原则、确定性冲突闸门、技术探针分层。
- 部分成立：单素材动作任务组与自动组装能力、人工清单。
- 待验证：非 5 月 13 日素材、自动直出准确率、分类稳定性、人工抽检比例、批量性能。
- 待创建：通用 Route A 入口、统一数据模型、可操作 review_task、正式交付状态。
- blocked：缺音轨、缺完整 ASR、缺动作视觉证据、确定性冲突、来源越界。

## 8. required_inputs（必需输入）

- source_asset 视频及合法访问路径。
- source_asset_id、来源、负责人、录制时间（如可得）。
- 完整音轨。
- 可重跑 ASR 的输入或已验证完整 ASR。
- 视觉采样策略和允许模型配置（实现阶段由用户确认）。
- 动作术语/别名表；没有时可从视觉建立候选，但不能硬猜专业动作名。
- 人工审核人和业务负责人。
- 健康/合规敏感表达规则（正式发布前必需）。

## 9. required_outputs（必需输出）

- material_route 和路由证据。
- transcript analysis_unit 索引。
- visual analysis_unit 索引。
- action_topic 主表。
- 角色证据表和确定性冲突字段。
- candidate_clip 索引、来源时间段、结构、组装模式和降级原因。
- review_task 与 feedback。
- final_clip 索引、来源候选、审核人和技术探针。
- execution_record、失败证据和 Git 事实包。

## 10. probe_required（进入实现前最小验证）

1. 选择至少一条非 5 月 13 日、人工已知为运动＋讲解型的直播。
2. 只运行 Route A 最小链，不先接飞书。
3. 验证动作主题是否来自视觉证据，而非专用 TOPIC_SPECS。
4. 验证完整 ASR 能聚合同动作的多角色证据。
5. 用正例、普通手势负例、部位冲突例和跳题例验证硬闸门。
6. 对自动候选做人工逐条核验，并单列技术、内容、动作、审美和业务结果。
7. 人工通过前，所有输出保持 pending_user_review。

## 11. allowed_codex_autonomy（Codex 允许自主范围）

- 文件命名、目录组织、日志格式和普通 Python 模块拆分。
- 在已锁字段与闸门内实现解析器、校验器、幂等键和可重跑步骤。
- 修复不改变产品语义的异常处理、排序稳定性和 AppleDouble 清理。
- 增加回归测试、结构校验和失败证据。
- 根据技术限制调整转码参数，但不得改变内容选择标准。

## 12. forbidden_codex_guessing（禁止 Codex 猜测）

- 不得自行改变 Route A 的自动通过硬闸门。
- 不得用关键词或时间相邻代替同动作证据。
- 不得自行确定健康表达、专业动作名称、业务通过或发布结论。
- 不得因候选数量少而降低冲突标准。
- 不得决定抽检比例、路由阈值或批量上线门槛。
- 不得把 manual_review、partial 或 logic_mismatch 政名为完成。
- 不得把用户对方向“整体较好”的判断扩写为批量产品已验证。

## 13. execution_entrypoints（后续执行入口设计）

只设计，不在本轮实现：

- route_material.py：读取共享预检结果并输出 material_route。
- analyze_motion_explanation.py：生成动作主题和完整证据。
- build_motion_candidates.py：按分类与 assembly_mode 生成候选计划。
- render_candidate_clip.py：按计划幂等导出候选视频。
- create_review_tasks.py：为抽检和降级项建审核任务。
- finalize_approved_clip.py：只处理 approved 候选。
- export_fact_package.py：生成可落 Git 的最小事实包。

## 14. validation_commands（后续验证命令类型）

| 命令类型 | 中文用途 |
|---|---|
| schema validation | 检查必填字段、枚举和引用完整性 |
| rule unit tests | 验证普通手势不通过、冲突一票否决、无真实问题不伪造问答 |
| idempotency test | 同一 job 重跑不重复创建主题、候选或正式视频 |
| media probe | 用 ffprobe 和全解码证明技术可用 |
| source-range audit | 检查每个片段可回到原始时间码 |
| classification assertions | 检查 content、structure、assembly、review 四层没有混用 |
| regression comparison | 与人工金标准比较误放行和误杀 |
| safety scan | 检查媒体、ASR 缓存、密钥未进入 Git |

## 15. blocked_if_missing（缺失即阻断）

- 缺 source_asset、音轨、完整转写或可追溯时间码。
- 路由仍为 unknown 且无人确认。
- 动作身份、部位或循环证据不足，却要求自动直出。
- 缺人工审核责任人，却要求正式交付。
- 缺健康/合规确认，却要求发布相关视频。
- 仍使用单素材专用锚点作为通用入口。
- 无法区分技术通过、候选通过、人工通过和业务通过。
