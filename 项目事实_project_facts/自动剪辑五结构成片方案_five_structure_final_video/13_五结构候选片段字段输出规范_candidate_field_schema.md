# 五结构候选片段字段输出规范

状态：`部分成立，待用户复核`
生成时间：2026-06-24
用途：后续 Codex 分析每条视频 / 每个候选片段时必须按字段输出，禁止写成散文判断。

## 1. 总规则

每个候选片段必须先输出结构化字段，再写极短判断。字段不足时不能用自然语言绕过，必须填受控状态词：`已确认`、`部分成立`、`待验证`、`待客户确认`、`visual_editing_pending_review`、`unmapped_clip`。

文本结构通过只表示 `text_structure_status=text_structure_passed`。画面、字幕、动作、节奏、人感、业务事实和发布判断必须另设字段，不得混写。

## 2. 输出对象层级

| level | 说明 | 能否直接入候选池 |
|---|---|---|
| `speech_segment` | 单条转写语音段，只能定位 | 否，必须扩展到结构块 |
| `structure_block` | 几句话完成一个结构功能 | 可以初筛 |
| `structure_sequence` | 多个结构块形成承接链路 | 可以初筛，但桥接需复核 |
| `full_video` | 开头、中段、结尾闭环 | 可作为完整文本候选，仍需画面和业务复核 |

## 3. 字段总表

| 字段 | 用途 | 可选值 / 格式 | 何时必填 | 示例 | 错误示例 | 可空规则 |
|---|---|---|---|---|---|---|
| `candidate_id` | 候选片段编号 | `cand_YYYYMMDD_0001` | 每条候选必填 | `cand_20260624_0001` | `好片1` | 不可空 |
| `source_id` | 素材编号 | `src_scan_0001` | 必填 | `src_scan_0004` | 只写视频名 | 不可空 |
| `pair_id` | 配对编号 | `pair_0001` | 必填 | `pair_0032` | 空白 | 不可空，未知填 `待验证` |
| `video_file_name` | 视频文件名 | 文件名，不含路径也可 | 必填 | `30岁的女性练八爪鱼要多久.mp4` | `那个30岁视频` | 不可空 |
| `start_time` | 片段开始时间 | `HH:MM:SS.mmm` | 必填 | `00:00:00.000` | `0秒` | 不可空 |
| `end_time` | 片段结束时间 | `HH:MM:SS.mmm` | 必填 | `00:00:04.600` | `大概5秒` | 不可空 |
| `duration_seconds` | 片段时长 | 数字，秒 | 必填 | `4.6` | `挺短` | 不可空 |
| `structure_type` | 五结构类型 | `traffic_hook / course_teaching / objection_response / case_trust / conversion_push / unmapped_clip` | 必填 | `traffic_hook` | `好开头` | 不可空 |
| `structure_function` | 本结构承担的功能 | 简短中文 | 必填 | `建立练习多久的观看理由` | `不错` | 不可空 |
| `structure_level` | 结构层级 | `speech_segment / structure_block / structure_sequence / full_video` | 必填 | `structure_block` | `片段` | 不可空 |
| `complete_status` | 完整状态 | `complete / partial / incomplete / pending_validation` | 必填 | `partial` | `差不多` | 不可空 |
| `missing_elements` | 缺失内容 | 数组或分号分隔 | 缺失或 partial 时必填 | `缺适用条件; 缺结果边界` | `不够好` | 可空，仅当 `complete` |
| `minimum_complete_unit_status` | 最小完整表达单元状态 | `成立 / 不成立 / 需要向前扩展 / 需要向后扩展 / 待人工复核` | 必填 | `需要向后扩展` | `看情况` | 不可空 |
| `audience_path_status` | 观众路径状态 | `顺 / 轻微断裂 / 断裂 / 待验证` | 必填 | `轻微断裂` | `还行` | 不可空 |
| `bridge_needed` | 是否需要桥接 | `yes / no / pending` | 多结构或断裂时必填 | `yes` | `可能吧` | 单结构可填 `no` |
| `bridge_type` | 桥接类型 | `问题承接 / 结果承接 / 方法承接 / 信任承接 / 异议承接 / 字幕承接 / 语气承接 / none / pending` | `bridge_needed=yes` 时必填 | `方法承接` | `随便加字幕` | 不需要桥接填 `none` |
| `transition_status` | 前后承接状态 | `smooth / needs_bridge / break / pending_validation` | 多结构必填 | `needs_bridge` | `顺` | 单结构可填 `not_applicable` |
| `transition_break_type` | 断裂类型 | `none / hard_cut / emotional_break / logic_break / topic_break / context_missing / pending` | 有断裂时必填 | `logic_break` | `怪怪的` | 无断裂填 `none` |
| `risk_flags` | 风险标记 | 数组：`price_mentioned`, `benefit_mentioned`, `refund_mentioned`, `effect_claim`, `strong_efficacy_claim`, `sensitive_population`, `medical_or_education_qualification`, `case_authenticity_pending`, `business_fact_pending` | 有风险必填 | `effect_claim; business_fact_pending` | `风险有点高` | 无风险填 `none` |
| `business_fact_status` | 业务事实状态 | `不涉及 / 待客户确认 / 已确认 / blocked_business_fact` | 必填 | `待客户确认` | `没问题` | 不可空 |
| `text_structure_status` | 文本结构状态 | `text_structure_passed / partial / failed / pending_validation` | 必填 | `partial` | `能发` | 不可空 |
| `visual_review_status` | 画面复核状态 | `visual_editing_pending_review / visual_source_missing_pending_probe / visual_probe_initial_observation / reviewed_by_user` | 必填 | `visual_editing_pending_review` | `画面过` | 不可空 |
| `candidate_decision` | 候选池决策 | `enter_candidate_pool / manual_review_required / text_only_candidate / visual_review_required / discard / material_only / needs_bridge / blocked_business_fact / blocked_visual_mismatch_pending` | 必填 | `text_only_candidate` | `可以用` | 不可空 |
| `decision_reason` | 决策理由 | 1-2 句中文，必须引用字段原因 | 必填 | `文本钩子成立，但画面和业务事实未复核。` | `感觉不错` | 不可空 |
| `manual_check_items` | 人工复核项 | 数组或分号分隔 | 有任何待复核时必填 | `画面动作; 字幕重点; 效果承诺` | `人工看看` | 无复核填 `none` |
| `score_hook` | 钩子分 | `0 / 1 / 3 / 5 / not_applicable` | 必填 | `5` | `4` | 不可空 |
| `score_teaching` | 讲解分 | `0 / 1 / 3 / 5 / not_applicable` | 必填 | `3` | `2` | 不可空 |
| `score_trust` | 信任分 | `0 / 1 / 3 / 5 / not_applicable` | 必填 | `not_applicable` | `没有` | 不可空 |
| `score_objection` | 异议分 | `0 / 1 / 3 / 5 / not_applicable` | 必填 | `not_applicable` | `-` | 不可空 |
| `score_conversion` | 转化分 | `0 / 1 / 3 / 5 / not_applicable` | 必填 | `1` | `可以` | 不可空 |
| `score_integrity` | 完整性分 | `0 / 1 / 3 / 5` | 必填 | `3` | `80分` | 不可空 |
| `overall_text_score` | 文本综合分 | `0 / 1 / 3 / 5`，取保守档，不做平均分伪精确 | 必填 | `3` | `4.2` | 不可空 |
| `evidence_ref` | 证据引用 | `source_id + pair_id + start_time + end_time + sample_type + evidence_summary + evidence_role` | 必填 | `source_id=src_scan_0004; pair_id=pair_0032; ...` | `见视频` | 不可空，缺证据填 `待验证` 并说明缺什么 |
| `notes` | 备注 | 短句，仅写边界或异常 | 可选 | `负样片数量有限，失败类型部分成立。` | 大段散文 | 可空 |

## 4. 分数字段硬规则

评分只能取 `0 / 1 / 3 / 5 / not_applicable`，不能取 2、4、4.5。

| 分数 | 含义 | 决策影响 |
|---:|---|---|
| 0 | 完全不成立，或直接淘汰条件出现 | `discard` 或 `material_only` |
| 1 | 有影子，但缺关键结构 | `material_only` 或 `manual_review_required` |
| 3 | 基本成立，但需要人工修或补证据 | `text_only_candidate` 或 `manual_review_required` |
| 5 | 文本结构清楚、证据完整、边界清楚 | 最多 `enter_candidate_pool`，仍需画面和业务复核 |
| `not_applicable` | 当前片段不承担该结构 | 不参与综合分，但必须说明结构类型 |

综合分取保守档：只要风险、业务事实、画面、桥接任一项未确认，就不得把 `overall_text_score=5` 写成最终可发布。

## 5. 示例输出

```yaml
candidate_id: cand_20260624_0001
source_id: src_scan_0004
pair_id: pair_0032
video_file_name: 30岁的女性练八爪鱼要多久.mp4
start_time: 00:00:00.000
end_time: 00:00:04.600
duration_seconds: 4.6
structure_type: traffic_hook
structure_function: 建立30岁女性练习多久的观看理由
structure_level: structure_block
complete_status: partial
missing_elements: 后续方法和业务效果仍需承接
minimum_complete_unit_status: 需要向后扩展
audience_path_status: 顺
bridge_needed: no
bridge_type: none
transition_status: not_applicable
transition_break_type: none
risk_flags: effect_claim; business_fact_pending
business_fact_status: 待客户确认
text_structure_status: partial
visual_review_status: visual_editing_pending_review
candidate_decision: text_only_candidate
decision_reason: 钩子文本成立，但单独剪出仍需后文兑现，画面和业务事实未复核。
manual_check_items: 画面动作; 字幕重点; 效果承诺
score_hook: 5
score_teaching: not_applicable
score_trust: not_applicable
score_objection: not_applicable
score_conversion: not_applicable
score_integrity: 3
overall_text_score: 3
evidence_ref: source_id=src_scan_0004; pair_id=pair_0032; start_time=00:00:00.000; end_time=00:00:04.600; sample_type=正样片; evidence_summary=开头5秒内给出练习多久的观看理由; evidence_role=支持
notes: 文本结构初判，不代表画面和发布通过。
```

## 6. 错误输出示例

```text
这个片段挺好，开头很抓人，可以做候选，后面看看画面。
```

错误原因：

- 没有 `candidate_id / source_id / pair_id / timecode`。
- 没有结构层级和缺失项。
- 没有候选池受控决策。
- 没有业务事实和画面复核状态。
- 没有 evidence_ref。

## 7. 入库检查

后续生成候选池 CSV 或 Markdown 时，任一条候选缺少必填字段，整批标 `blocked_missing_candidate_field`，不得把散文判断当候选池。
