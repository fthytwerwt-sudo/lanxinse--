# 动作应用规则说明

状态：`completed_with_pending_user_review`
生成时间：2026-07-06T16:03:05

## 1. 本知识库能做什么

- 用 `/Volumes/WD_BLACK/AI解析` 的课程解析派生产物建立动作/问题/剪辑结构的桥接表。
- 区分两类动作：`presenter_avatar_action`（讲师/数字人呈现动作）与 `course_text_action_keyword`（课程文本中的动作或问题关键词）。
- 给直播素材筛选提供候选字段，而不是直接生成最终话术、健康结论、动作专业判断或发布结论。

## 2. 本知识库不能做什么

- 不能写 `publish_ready`、`business_ready`、`professional_action_passed`。
- 不能把 `text_keyword_confirmed` 写成 `visual_action_confirmed`。
- 不能把课程文本里的敏感操作细节搬进仓库；本轮只保留高层词族和风险闸门。
- 不能忽略源数据里的 `confidence`、`review_flag`、`human_review_needed`。

## 3. 使用顺序

1. 先用 `02_动作别名归一表_action_alias_normalization.csv` 把源标签/词族归一到 `normalized_action_id`。
2. 再用 `01_动作问题映射表_action_problem_mapping.csv` 判断它属于呈现动作、课程动作关键词、业务词还是视觉阻断。
3. 再用 `04_动作剪辑结构桥接表_action_clip_structure_bridge.csv` 选择可尝试的结构公式。
4. 最后人工复核画面、口播、字幕、健康/合规/客户事实，不通过则保持 `pending_user_visual_review`。

## 4. 强制闸门

- `low_confidence`、`pending_review`、`no_face_detected`、`ocr_unavailable`：只进入人工复核。
- 涉及训练、健康、身体效果、适用人群：`professional_review_required`。
- 涉及课程名、价格、报名、权益、客户承诺：`customer_review_required` 与 `business_fact_review_required`。
- 涉及成人亲密关系敏感主题：`compliance_review_required`，不得自动改写成直播话术。

## 5. 源数据状态摘要

### usefulness grade

| value | count |
|---|---:|
| `D` | 13254 |
| `C` | 3385 |
| `A` | 35 |
| `B` | 9 |

### source read status

| value | count |
|---|---:|
| `skipped_noise` | 12954 |
| `metadata_only` | 3382 |
| `skipped_duplicate` | 283 |
| `read_for_mapping` | 35 |
| `skipped_unknown` | 15 |
| `read_for_context` | 9 |
| `skipped_archive` | 3 |
| `skipped_appledouble` | 2 |

### action confidence

| value | count |
|---|---:|
| `low` | 8191024 |
| `medium` | 4963 |
| `[empty]` | 6 |

### review flags

| value | count |
|---|---:|
| `待复核_visual_nearest_sample` | 8062503 |
| `human_review_needed=yes` | 2706925 |
| `recommended_review` | 94632 |
| `needs_human_review` | 52801 |
| `human_review_needed=recommended` | 31544 |
| `待复核_action_low_confidence` | 19424 |
| `待复核_visual_action_low_confidence` | 19424 |
| `[empty]` | 6 |
| `待复核_keyword_based` | 2 |
| `ok_after_manual_courseware_review` | 1 |
| `requires_human_review_before_auto_play` | 1 |

## 6. 字段落库边界

- `source_file_ids` 只追溯派生产物文件，不追溯或复制原始媒体。
- `alias_examples` 是归一口径，不是课程原文摘录。
- 后续若接入自动筛选，默认输出 `candidate_status=pending_user_visual_review`，直到人工确认。
