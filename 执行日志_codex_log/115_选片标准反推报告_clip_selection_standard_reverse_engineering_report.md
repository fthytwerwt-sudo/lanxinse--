# 115 选片标准反推报告

任务类型：`clip_selection_standard_reverse_engineering`

状态：`validation_passed_pending_commit_push`

## Impact check

| 项目 | 结果 |
| --- | --- |
| pwd | `/Volumes/WD_BLACK/澜心社剪辑` |
| repo_root | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| branch | `main` |
| remote | `origin	https://github.com/fthytwerwt-sudo/lanxinse--.git (fetch) | origin	https://github.com/fthytwerwt-sudo/lanxinse--.git (push)` |
| git status before write | `?? outputs/c5826_reference_rhythm_40s/work/
?? scripts/clip_selection_standard_reverse_engineering.py
?? "\351\241\271\347\233\256\344\272\213\345\256\236_\345\211\252\350\276\221\344\272\244\344\273\230\350\256\241\345\210\222_clipping_delivery_plans/"` |
| 素材目录 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/AI需要的成片` |
| ffprobe | `/opt/homebrew/bin/ffprobe` |
| 是否读取本地 outputs | 是，仅读取 C9623 导出索引 CSV，不读取/提交媒体 |
| 是否提交媒体 | 否 |
| 是否涉及 secret | 否 |
| 是否新增脚本 | 是，`scripts/clip_selection_standard_reverse_engineering.py` |

## 读取报告

- `执行日志_codex_log/112_两条直播录屏正式模拟运行报告_two_live_recording_formal_simulation_report.md`
- `执行日志_codex_log/113_112结果复审与路线重判报告_112_result_review_route_replanning_report.md`
- `执行日志_codex_log/113_直播切片V2架构审核与解析补全报告_live_cutting_v2_architecture_audit_report.md`
- `执行日志_codex_log/114_C9623直播切片完整验证报告_c9623_live_cutting_full_validation_report.md`

## 读取样本表

- `素材解析_pipeline_material_analysis/10_live_cutting_v2_architecture_audit/03_AI需要的成片前100解析补全_ai_needed_top100_analysis.csv`
- `素材解析_pipeline_material_analysis/10_live_cutting_v2_architecture_audit/04_正负样本差异结构表_positive_negative_structure_gap.csv`
- `素材解析_pipeline_material_analysis/11_c9623_live_cutting_full_validation/05_C9623候选片段评分表_c9623_candidate_scoring.csv`
- `素材解析_pipeline_material_analysis/11_c9623_live_cutting_full_validation/06_C9623导出视频索引_c9623_exported_clip_index.csv`
- `素材解析_pipeline_material_analysis/11_c9623_live_cutting_full_validation/08_C9623人工包装建议表_c9623_manual_packaging_advice.csv`
- `素材解析_pipeline_material_analysis/11_c9623_live_cutting_full_validation/07_C9623弃用片段表_c9623_rejected_segments.csv`

## 输出统计

| 输出 | 数量 |
| --- | ---: |
| 正样本/AI 成片范围视频 | 165 |
| 复用已有解析 | 100 |
| 标题/元数据待复核 | 65 |
| 负样本/弱样本原因 | 106 |
| C9623 候选价值复盘 | 43 |
| C9623 实际导出视频 | 20 |
| 选片理由标签 | 10 |
| 选片标准 | 5 |

## 生成文件

- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/01_样本来源清单_sample_source_inventory.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/02_正样本选片理由表_positive_selection_reason.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/03_弃用弱样本失败原因表_rejected_weak_sample_reason.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/04_选片理由标签库_selection_reason_tag_library.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/05_选片标准样本对照表_selection_standard_sample_matrix.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/06_别人为什么选反推表_why_selected_reverse_engineering.csv`
- `素材解析_pipeline_material_analysis/12_clip_selection_standard_reverse_engineering/07_C9623候选价值复盘表_c9623_candidate_value_review.csv`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/01_选片标准总报告_clip_selection_standard_report.md`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/02_可执行评分矩阵_selection_scoring_matrix.md`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/03_Codex选片运行字段设计_codex_selection_runtime_fields.md`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/04_人审反馈表_manual_review_feedback_sheet.md`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/05_人读版报告_human_readable_report.md`
- `项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/05_人读版报告_human_readable_report.docx`
- `执行日志_codex_log/115_选片标准反推报告_clip_selection_standard_reverse_engineering_report.md`

## 边界确认

- 是否提交媒体：否
- 是否提交 API 原始输出：否
- 是否提交 `.env`：否
- 是否提交 API key：否
- 是否写审美通过：否
- 是否写动作专业性通过：否
- 是否写健康表达通过：否
- 是否写业务通过：否
- 是否写稳定批量运行：否

## 已执行验证

- `python3 -m py_compile scripts/clip_selection_standard_reverse_engineering.py`：通过。
- `python3 scripts/clip_selection_standard_reverse_engineering.py --dry-run`：通过，确认有效视频 165、排除 `成品/` 757、跳过 AppleDouble 1、C9623 实际导出 20。
- `python3 scripts/clip_selection_standard_reverse_engineering.py --run`：通过，生成 14 个本轮产物。
- `unzip -t 项目事实_project_facts/选片标准反推_clip_selection_standard_reverse_engineering/05_人读版报告_human_readable_report.docx`：通过。
- `render_docx.py ... --emit_pdf`：通过，输出 9 页 PNG + PDF 到 ignored 目录 `api_outputs/clip_selection_standard_reverse_engineering/docx_render/`。
- DOCX 视觉抽检：第 1、2、9 页无明显中文乱码、文字重叠、表格越界或末页截断。

## 后续提交验证命令

- `python3 -m py_compile scripts/clip_selection_standard_reverse_engineering.py`
- `python3 scripts/clip_selection_standard_reverse_engineering.py --dry-run`
- `python3 scripts/clip_selection_standard_reverse_engineering.py --run`
- `git diff --check`
- `git status --short`
- `git diff --cached --check`
