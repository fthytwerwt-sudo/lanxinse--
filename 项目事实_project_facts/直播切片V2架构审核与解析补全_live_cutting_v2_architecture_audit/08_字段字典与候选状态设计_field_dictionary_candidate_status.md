# 字段字典与候选状态设计

状态：`field_dictionary_candidate_status_completed_pending_runtime_adoption`
生成时间：2026-07-02T16:00:48+08:00

## V2 新增字段

| field | meaning | status |
| --- | --- | --- |
| content_archetype | 内容形态，先判断素材属于单动作教学、原生直播片、动作纠错等哪类 | new_required |
| route_decision | 路线判断，区分原生导出、再包装、相邻合并、正负样本参考、淘汰和待人审 | new_required |
| problem_phrase_time | 问题句或问题字幕首次出现时间 | new_required |
| first_action_frame_time | 动作首次出现时间 | new_required |
| problem_action_bridge_seconds | 问题到动作之间的秒数 | new_required |
| tts_action_alignment | 口播 / 配音 / 字幕与动作画面的同步状态 | new_required_pending_audio |
| repackaging_value_score | 再包装价值分数，只代表可再包装潜力，不代表原生切片完成 | new_required |
| needs_adjacent_merge | 是否需要合并前后窗口 | new_required |
| candidate_status | 受控候选状态，不能混写审美/业务通过 | new_required |

## candidate_status 枚举

| status | meaning |
| --- | --- |
| qualified_native | 原生切片技术候选合格，不等于发布通过 |
| qualified_repackaging | 动作教学再包装候选合格，不等于已生成成片 |
| qualified_merge_candidate | 相邻合并候选，需要 merge 后复核 |
| rejected_missing_bridge | 缺少问题-动作桥接或上下文无法成立 |
| rejected_action_unclear | 动作看不清或关键姿势缺失 |
| rejected_audio_missing | 缺音频/字幕/TTS 证据 |
| rejected_business_risk | 业务或健康表达风险过高 |
| pending_audio_transcript | 待音频转写或口播对齐 |
| pending_user_review | 待用户人审 |

## 关键边界

- `action_repackaging_candidate` 只表示可再包装潜力，不是原生成片完成。
- `pending_audio_transcript` 不能脑补口播内容。
- `pending_user_review` 覆盖审美、动作专业性、健康表达和业务转化复核。
