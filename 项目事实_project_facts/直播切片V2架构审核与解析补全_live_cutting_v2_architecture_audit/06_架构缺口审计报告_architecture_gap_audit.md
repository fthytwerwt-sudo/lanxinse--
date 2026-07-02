# 架构缺口审计报告

状态：`architecture_gap_audit_completed_pending_user_review`
生成时间：2026-07-02T16:00:48+08:00

## 主结论

`已确认`：当前架构不是只缺规则，而是规则层厚、runtime 执行层薄。系统已有前 100 成片结构、正负样本证据、五结构字段和候选池规则；但正式模拟运行仍以固定视觉窗口和完整性闸门为主，缺少内容形态前置路由、问题-动作秒级桥接、动作教学再包装分流、相邻窗口合并、音频/字幕/TTS 时间线对齐等执行层。

`部分成立`：上一轮 0 候选不应直接解释为素材全废。112 复审显示 76/76 个窗口均完成阿里视觉审计，但也全部需要前后合并，82 条 rejected 需要转写/音频复审。

## 缺口逐项

| gap_id | gap_name | current_status | evidence | why_it_matters | impact_if_missing | recommended_patch | priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gap_01 | content_archetype_routing_layer | 部分成立：成片样本层已有类型库，formal simulation runtime 未前置路由 | 20_视频结构公式库；22_成片样本类型与结构总表；112 结果复审 | 先判断素材适合原生切片、动作教学、问题解决还是转化，才能避免固定完整性闸门误杀直播中段素材。 | 动作中段、讲解中段会被当成缺开头/缺结尾废弃。 | 在窗口审计前新增 content_archetype 与 route_decision 字段，并让不同 archetype 进入不同候选规则。 | P1 |
| gap_02 | problem_action_bridge_layer | 部分成立：文本规则存在，但未形成秒级 problem->action runtime 判断 | 12_五结构文本判断标准完整手册；07_弃用片段复审表 | 动作教学短视频的关键不是只有完整开中结，而是问题句后几秒内是否接到动作解决方案。 | 可用动作素材被判缺开头/中段证据，或问题和动作硬拼不自知。 | 新增 problem_phrase_time、first_action_frame_time、problem_action_bridge_seconds 与 bridge_status。 | P0 |
| gap_03 | action_teaching_repackaging_route | 部分成立：样本规则可支持，但直播素材救回流程未落地 | 27/32 规则表；112 路线重判 | 直播动作素材可能不适合原生直切，但可通过 TTS、字幕和边界包装成教学短视频。 | 系统只找原生完整片，错过可再包装动作素材。 | 将 action_repackaging_candidate 与 qualified_repackaging 从 native_export_candidate 中拆出。 | P0 |
| gap_04 | adjacent_window_merge_layer | 缺执行层：已有 need_merge_previous/next 标记，但无 merge operator | 04_112结果复审与路线重判：76/76 need_merge_previous=yes 且 need_merge_next=yes | 直播录屏的真实开头和收束常跨窗口，必须向前后找完整表达单元。 | 固定 180 秒窗口打碎连续表达，导致 0 候选。 | 新增相邻窗口合并器，输出 merged_start/end、merge_reason、merge_evidence。 | P0 |
| gap_05 | audio_tts_subtitle_timeline_alignment_layer | 缺失：当前仅视觉抽帧，音频/字幕/TTS 时间线未统一 | 04_112结果复审与路线重判：82 条 rejected needs_transcript_or_audio=yes | 口播、配音、字幕和动作画面对齐是判断教学能否成立的核心证据。 | 无法判断半句话、口播收束、TTS 解释是否真正解决动作画面。 | 引入 transcript/subtitle timeline，输出 tts_action_alignment 与 pending_audio_transcript 状态。 | P0 |
| gap_06 | positive_negative_contrast_layer | 已建立但负样本偏薄：已有正负样片证据矩阵，负样本仅 3 条 | 06_正负样片结构证据矩阵；11_标准缺口对照表 | 好片和坏片的差异能反推出规则边界，避免只学正样本。 | 规则容易过拟合正样本，对失败片段误放行。 | 新增 V2 contrast 表，把 matched_existing_rule 与 missing_new_rule 分开。 | P1 |
| gap_07 | candidate_status_taxonomy | 部分成立：五结构有 candidate_decision，formal simulation 状态未统一 | 13_候选片段字段输出规范；14_候选池规则；04_候选片段表 | 原生切片、再包装、合并候选、待音频转写不能混用一个 decision。 | 报告之间无法对齐，容易把可包装写成已完成原生切片。 | 统一 candidate_status 与 route_decision 枚举。 | P1 |
| gap_08 | field_dictionary_layer | 部分成立：已有主键链路和五结构字段，V2 新字段未入字典 | 02_五结构字段字典；13_候选片段字段输出规范 | 新路线需要可追溯字段，否则无法复盘误杀原因。 | 脚本结果和人工复核表字段不一致。 | 新增 content_archetype、route_decision、problem_action_bridge_seconds 等 V2 字段。 | P1 |
| gap_09 | manual_review_routing_layer | 已建立但需要 V2 路由细化 | 14_候选池规则；02_人工复核清单 | 动作专业性、健康表达、业务转化都不能由模型直接盖章。 | 技术解析容易被误解为审美或业务通过。 | 按原生/再包装/合并/音频待转写拆人工复核清单。 | P1 |
| gap_10 | feedback_to_rule_update_layer | 部分成立：已有回写说明，缺独立 rule delta ledger | 12_五结构文本判断标准完整手册；15_视觉探测记录 | 人审反馈必须沉淀回规则，而不是停在单次报告。 | 109/112/113 的失败经验不会进入下一版脚本。 | 新增 feedback_to_rule_update ledger，记录用户反馈、影响字段、规则修订建议。 | P2 |
