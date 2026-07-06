# 动作知识库来源追溯说明

状态：`action_source_traceability_added_pending_user_review`

## 已确认

- 精选资料包目录：`项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack`。
- 完整复制清单：`项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/01_复制文件清单_selected_source_copy_manifest.csv`，记录 6 个完整副本。
- 摘录清单：`项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/02_摘录资料清单_selected_extract_manifest.csv`，记录 38 个摘录产物。
- 源资料到动作知识库追溯表：`项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/05_源资料到动作知识库追溯表_source_to_action_traceability.csv`，记录 289 条追溯关系。

## 使用顺序

1. 用动作知识库 01-04 表确定 `normalized_action_id`、`problem_id`、`bridge_id`。
2. 到 `05_源资料到动作知识库追溯表_source_to_action_traceability.csv` 找对应 `source_file_id`。
3. 如果 `copied_or_extracted_path` 指向 `03_精选资料副本_selected_source_files/`，可读取完整副本。
4. 如果指向 `04_大表关键摘录_large_table_extracts/`，只能读取摘录字段和来源行号，不得外推全量源内容。

## 复核闸门

- `visual_review_required`：需要画面、动作、说话同步复核。
- `professional_review_required`：涉及动作专业性或健康风险，不写已确认。
- `customer_review_if_used_in_live_script`：进入直播话术前需要客户确认。
- `pending_user_review`：本轮技术落库完成后仍需用户人审。

## 禁止外推

- 追溯成立只说明来源可查，不说明动作真实可见。
- 文本命中只说明候选关系，不说明视频画面连续或说话连续。
- 涉及敏感成人亲密关系内容时，只保留高层词族和风险闸门，不复制可照做细节。
