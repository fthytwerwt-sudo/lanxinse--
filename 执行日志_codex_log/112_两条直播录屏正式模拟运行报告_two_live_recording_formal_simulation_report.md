# 两条直播录屏正式模拟运行报告

状态：`completed_no_qualified_segments_pending_user_review`
生成时间：2026-06-30T19:06:22+08:00

## 1. 执行结果

| 项目 | 结果 |
| --- | --- |
| 当前仓库 | fthytwerwt-sudo/lanxinse-- |
| 本地仓库路径 | /Volumes/WD_BLACK/澜心社剪辑/lanxinse-- |
| 直播素材目录 | /Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/剪辑测试直播素材 |
| 素材目录发现方式 | preferred_dir_missing_used_authorized_discovered_dir |
| 直播录屏数量 | 2 |
| 总时长秒数 | 12744.231 |
| 窗口长度/重叠 | 180.0s / 10.0s |
| 窗口数量 | 76 |
| 窗口覆盖率 | 100% |
| 阿里窗口调用数量 | 76 |
| 阿里窗口成功数量 | 76 |
| 阿里窗口失败数量 | 0 |
| 候选片段数量 | 0 |
| 导出初剪数量 | 0 |
| 弃用片段数量 | 83 |
| 是否不限制条数 | 是 |
| 是否保持画面比例 | 是 |
| 是否提交媒体 | 否 |
| 是否提交 API 原始输出 | 否 |
| 是否提交 secret | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定初剪 | 否 |
| qwen-omni-turbo-latest | 当前脚本未直连完整音视频，标为待验证未使用 |
| commit / push / remote HEAD | 由最终 Codex 回报补充；文件内容随本轮提交进入 GitHub |

## 2. 生成文件

- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/01_直播录屏素材清单_live_recording_inventory.csv`
- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/02_全覆盖窗口清单_full_coverage_window_manifest.csv`
- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/03_阿里窗口分析审计表_ali_window_analysis_audit.csv`
- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/04_候选片段表_candidate_segment_table.csv`
- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/05_弃用片段表_rejected_segment_table.csv`
- `素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/06_初剪结果索引_rough_cut_output_index.csv`
- `项目事实_project_facts/直播录屏正式模拟运行_live_recording_formal_simulation/01_初剪候选视频证据报告_rough_cut_evidence_report.md`
- `项目事实_project_facts/直播录屏正式模拟运行_live_recording_formal_simulation/02_人工复核清单_manual_review_checklist.md`
- `项目事实_project_facts/直播录屏正式模拟运行_live_recording_formal_simulation/03_两条直播录屏正式模拟运行人读版_two_live_recording_formal_simulation_human_report.docx`
- `执行日志_codex_log/112_两条直播录屏正式模拟运行报告_two_live_recording_formal_simulation_report.md`
- `scripts/live_recording_formal_simulation_2_videos.py`

## 3. 验证命令

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/live_recording_formal_simulation_2_videos.py`
- `ffmpeg -version`
- `ffprobe -version`
- coverage CSV 闸门：无 `coverage_status != covered`，无 `ali_model_called != yes`，无 `analysis_status != success`
- rough cut output index 闸门：无 `aspect_ratio_preserved != yes` 或 `resolution_preserved != yes`
- `git diff --check`
- `git status`

## 4. 边界确认

| 边界 | 结果 |
| --- | --- |
| 是否完整看完 2 个录屏 | 是，按全覆盖窗口抽帧并逐窗阿里审计 |
| 是否存在未覆盖窗口 | 否 |
| 是否每个窗口都调用阿里 | 是 |
| 是否输出视频比例保持 | 无导出 |
| 是否提交视频 | 否 |
| 是否提交 contact sheet | 否 |
| 是否提交完整 API 输出 | 否 |
| 是否提交 .env | 否 |
| 是否提交 API key | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定初剪 | 否 |
