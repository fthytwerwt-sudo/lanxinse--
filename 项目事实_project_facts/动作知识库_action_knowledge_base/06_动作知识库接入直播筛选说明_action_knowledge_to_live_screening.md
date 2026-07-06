# 动作知识库接入直播筛选说明

状态：`bridge_ready_pending_live_material_validation`
生成时间：2026-07-06T16:03:05

## 1. 接入位置

本知识库应接在直播素材候选筛选的“结构初筛”之后、“人工视觉复核”之前：

1. 直播录屏转写/时间码完成。
2. 候选片段命中问题、动作、课程或风险词族。
3. 用本目录 01-04 表补齐 `normalized_action_id`、`problem_category_id`、`bridge_type`、`candidate_status`。
4. 人工看原片/关键帧，确认 `speech_complete_unit`、`action_complete_cycle`、`visual_obstruction_risk`。
5. 只有人工复核通过后，才允许进入剪辑师加工或更高阶自动化。

## 2. 建议新增或复用字段

- `normalized_action_id`
- `problem_category_id`
- `source_file_ids`
- `speech_keyword_family`
- `speech_complete_unit`
- `action_complete_cycle`
- `visual_obstruction_risk`
- `speech_action_sync`
- `bridge_type`
- `transition_status`
- `visual_review_status`
- `health_business_review_required`
- `business_fact_status`
- `candidate_status`
- `manual_review_items`

## 3. 默认状态规则

- 文本命中：`text_keyword_confirmed_visual_pending_review`
- 呈现动作标签命中：`bridge_only_pending_human_review`
- 视觉低置信：`manual_review_only`
- 涉及健康/训练/效果：`screening_candidate_pending_professional_review`
- 涉及客户业务事实：`business_fact_pending_customer_review`
- 涉及成人亲密关系敏感主题：`do_not_auto_publish_high_sensitive`

## 4. 与五结构的桥接

- `错误/误区先抛 + 正确动作对比 + 原因解释`：只在能看出错误/正确差异时使用。
- `痛点问题 + 原因解释 + 方法交付`：适合文本问题类，但必须保留原因链和边界。
- `痛点/人群点名 + 单动作完整循环 + 坚持建议`：必须看到完整动作循环。
- `工具/动作演示 + 发力口令 + 低压跟练收束`：必须看清工具/身体接触点/口令同步。
- `日期/主题不明素材 + 待视觉复核索引`：低置信、无遮挡不足、OCR 不可用时使用。

## 5. 当前源包对直播筛选的限制

- `course pack` 可提供 chunk-level 时间窗口，但大量动作是低置信占位。
- `sentence workspace` 粒度更细，但同样存在 `human_review_needed=yes` 与视觉采样近邻复核要求。
- 源文本可提示“可能是什么问题/主题”，不能证明“画面动作已经可用”。
- 本轮没有复制原始媒体，没有做新的视觉模型复核，没有写动作专业通过。

## 6. 已抽取的关键计数

### top-level source count

| value | count |
|---|---:|
| `课程逐字稿解析工作区_所有课程_20260630_170152` | 10428 |
| `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956` | 5920 |
| `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956 2` | 237 |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack` | 47 |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack 2` | 45 |
| `._神经数字人课程解析交付包_neural_avatar_course_analysis_pack.zip` | 1 |
| `._神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956_pack.zip` | 1 |
| `neural_avatar_sentence_action_latest_path.txt` | 1 |
| `璇剧▼閫愬瓧绋胯В鏋愬伐浣滃尯_鎵€鏈夎绋媉20260630_170152` | 1 |
| `神经数字人课程解析交付包_neural_avatar_course_analysis_pack.zip` | 1 |
| `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956_pack.zip` | 1 |

### bridge intents

| value | count |
|---|---:|
| `course_knowledge_explain` | 2449637 |
| `summary_or_conclusion` | 84979 |
| `question_or_interaction_prompt` | 62540 |
| `course_transition` | 55529 |
| `keypoint_or_risk_reminder` | 43361 |
| `[empty]` | 19424 |
| `course_value_or_offer_material` | 11501 |
| `example_or_case_material` | 8547 |
| `trust_building_material` | 2951 |

### bridge risks

| value | count |
|---|---:|
| `medium_review_needed` | 2717391 |
| `[empty]` | 19424 |
| `low` | 1654 |
