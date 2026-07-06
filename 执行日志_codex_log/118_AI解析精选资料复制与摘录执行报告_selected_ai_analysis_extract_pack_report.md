# AI解析精选资料复制与摘录执行报告

状态：`selected_ai_analysis_extract_pack_generated_pending_user_review`
生成时间：2026-07-06T16:33:02

## 1. 本轮目标

从外部 `AI解析` 源目录中复制/摘录当前剪辑项目后续需要的课程动作资料，形成可追溯、可复用、可给后续 Codex 判断使用的精选资料包。

## 2. 已确认边界

- 仓库：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 源目录实际路径：`/Volumes/WD_BLACK/AI解析`
- `/Volumes/WD_BLACK/AI 解析` 是否存在：`False`
- 源目录处理方式：只读，不移动、不删除、不重命名、不覆盖。
- 本轮不复制媒体、缓存、zip、secret、API 原始输出。
- 完整复制文本副本统一为 LF 行尾，源/目标 hash 分开记录。
- 本轮不写健康效果成立、动作专业性通过、审美通过或业务通过。

## 3. 复制候选探针

- 源目录文件总数：16683
- 源目录体积：43.20GB
- A/B 候选：44
- A 类：35
- B 类：9
- 完整复制：6
- 行级摘录：37
- 摘要摘录：1
- 只索引：0
- 跳过：0

## 4. 输出文件

- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/00_精选资料包说明_readme.md`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/01_复制文件清单_selected_source_copy_manifest.csv`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/02_摘录资料清单_selected_extract_manifest.csv`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/03_精选资料副本_selected_source_files/`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/04_大表关键摘录_large_table_extracts/`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/05_源资料到动作知识库追溯表_source_to_action_traceability.csv`
- `项目资料源_selected_source_materials/AI解析精选资料包_selected_ai_analysis_extract_pack/06_不复制文件说明_skipped_source_files_report.md`
- `项目事实_project_facts/动作知识库_action_knowledge_base/07_动作知识库来源追溯说明_action_source_traceability.md`
- `素材解析_pipeline_material_analysis/11_selected_source_extract_pack/精选复制执行校验_selected_source_copy_validation.csv`
- `素材解析_pipeline_material_analysis/11_selected_source_extract_pack/复制候选探针_copy_candidate_probe.csv`

## 5. 校验摘要

- validation_status：`passed`
- copy_manifest_rows：6
- extract_manifest_rows：38
- traceability_rows：289

| check_id | check_item | status | evidence |
|---|---|---|---|
| VAL001 | source_dir_exists | `passed` | /Volumes/WD_BLACK/AI解析 |
| VAL002 | source_dir_not_modified_by_script | `passed` | before=(1783323360, 1048576); after=(1783323360, 1048576) |
| VAL003 | no_forbidden_output_files | `passed` | no media/cache/archive/env/secret files found |
| VAL004 | copy_manifest_has_hashes | `passed` | copy_rows=6 |
| VAL005 | extract_manifest_has_source_ranges | `passed` | extract_rows=38 |
| VAL006 | traceability_generated | `passed` | trace_rows=289 |
| VAL007 | output_size_not_abnormally_large | `passed` | output_size_bytes=3214052 |
| VAL008 | space_path_probe | `passed` | actual=/Volumes/WD_BLACK/AI解析; space_variant_exists=False |
| VAL009 | appledouble_sidecars_removed | `passed` | removed_sidecars=50 |

## 6. 待用户人审

- 精选副本是否足够后续 Codex 使用：`待验证`。
- 敏感主题是否允许进入直播筛选：`待验证`。
- 视觉、说话连续性、动作专业性、业务承诺：`待验证`。

## 7. commit / push

- 本报告由脚本生成；最终 commit、push、remote HEAD readback 以 Codex 本轮最终回报为准。
