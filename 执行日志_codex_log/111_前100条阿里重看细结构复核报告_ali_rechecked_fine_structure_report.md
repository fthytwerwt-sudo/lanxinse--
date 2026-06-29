# 前100条阿里重看细结构复核报告

状态：`ali_multimodal_recheck_100_completed_pending_user_review`
生成时间：2026-06-30T02:00:26+08:00

## 1. 执行结果

| 项目 | 结果 |
| --- | --- |
| 当前仓库 | fthytwerwt-sudo/lanxinse-- |
| 本地仓库路径 | /Volumes/WD_BLACK/澜心社剪辑/lanxinse-- |
| 输入素材目录 | /Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/AI需要的成片 |
| 本轮处理 | 前 100 条 success |
| 未处理 | 518 条 pending_not_analyzed |
| ffprobe 成功数量 | 100 |
| ffmpeg 解码成功数量 | 100 |
| contact sheet 生成数量 | 100 |
| 阿里调用数量 | 100 |
| 阿里成功数量 | 100 |
| 阿里失败数量 | 0 |
| 高质量视觉复核数量 | 77 |
| 最终状态 | ali_multimodal_recheck_100_completed_pending_user_review |

## 2. 失败项

| video_id | file_name | failed_step | failed_reason | 是否影响整体完成状态 |
| --- | --- | --- | --- | --- |
| - | - | - | 无 | no |

## 3. 生成文件

- `素材解析_pipeline_material_analysis/08_finished_video_analysis/前100条阿里复核素材元数据_ali_recheck_video_metadata_100.csv`
- `素材解析_pipeline_material_analysis/08_finished_video_analysis/前100条阿里调用审计表_ali_call_audit_100.csv`
- `素材解析_pipeline_material_analysis/08_finished_video_analysis/前100条阿里多模态复核矩阵_ali_multimodal_recheck_matrix_100.csv`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/29_前100条阿里逐条视频证据摘要_ali_video_evidence_summary_100.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/30_阿里重看版细结构触发条件库_ali_rechecked_fine_structure_trigger_library.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/31_阿里重看版开头中段结尾衔接规则_ali_rechecked_transition_rules.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/32_阿里重看版Codex初剪细结构规则表_ali_rechecked_codex_rough_cut_rules.csv`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/33_阿里重看版前100条细结构人读版_ali_rechecked_human_readable_report.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/33_阿里重看版前100条细结构人读版_ali_rechecked_human_readable_report.docx`
- `执行日志_codex_log/111_前100条阿里重看细结构复核报告_ali_rechecked_fine_structure_report.md`
- `scripts/ali_recheck_finished_video_structure_100.py`

## 4. 边界确认

| 边界 | 结果 |
| --- | --- |
| 是否只处理前 100 条 | 是 |
| 是否处理 518 条 | 否 |
| 是否每条都调用阿里 | 是 |
| 是否提交视频 | 否 |
| 是否提交图片/contact sheet | 否 |
| 是否提交音频 | 否 |
| 是否提交完整 API 输出 | 否 |
| 是否提交 .env/API key | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定初剪 | 否 |

## 5. 验证记录

已执行：

- `python3 -m py_compile scripts/ali_recheck_finished_video_structure_100.py`：通过。
- `python3 scripts/check_ali_config_safety.py`：通过；未发现真实 key、`.env` staged 或缺失忽略规则。
- CSV 行数与闸门检查：元数据 100 行；审计表 100 行且 `ali_model_called=yes` 100、`final_status=success` 100；复核矩阵 100 行且 `ali_recheck_status=success` 100。
- 视频技术验证：ffprobe 成功 100；ffmpeg 解码成功 100；contact sheet 生成/复用 100。
- DOCX 渲染 QA：`render_docx.py` 成功渲染 13 页 PNG + PDF 到本地忽略目录 `api_outputs/finished_video_ali_recheck_100/docx_render/`；抽检第 1 页、第 4 页、第 13 页，无明显中文乱码、文字重叠、表格越界或末页截断。

待最终回报补充：

- `git diff --check`
- path-limited `git add`
- `git commit`
- `git push`
- remote HEAD readback
