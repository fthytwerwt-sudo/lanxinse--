# 当前成片全量结构适配性复审执行报告

状态：`generated_pending_git_closeout`
生成时间：2026-07-05T23:45:58

## commands

- `git pull --ff-only`
- `读取 AGENTS.md、机制文件与旧结构事实文件`
- `ffprobe 当前素材目录全量视频扩展名文件`
- `ffmpeg 首帧解码探针（不生成媒体产物）`
- `生成 inventory/matrix/fit score/revision/editor/bridge/report`

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 当前素材目录：`/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/AI需要的成片`
- 当前视频扩展名匹配文件数：166
- 可读视频数：165
- 失败视频数：1
- pending 视频数：165
- 是否使用视觉模型：no
- 是否上传完整视频：no
- 是否提交媒体：no
- 是否提交 API 原始输出：no
- 是否读取/提交 `.env`：no / no
- 是否写审美通过：no
- 是否写业务通过：no
- 是否写动作专业性通过：no
- 是否写批量稳定：no

## failed_items

- AppleDouble 或不可读视频文件数：1
- 视觉模型/API 未使用：结构内容判断均标 `pending_visual_review`。

## files_changed

- `素材解析_pipeline_material_analysis/09_current_finished_video_full_review/当前成片素材清单_current_finished_video_inventory.csv`
- `素材解析_pipeline_material_analysis/09_current_finished_video_full_review/当前成片结构解析矩阵_current_finished_video_structure_matrix.csv`
- `素材解析_pipeline_material_analysis/09_current_finished_video_full_review/结构公式适配评分表_structure_formula_fit_score_table.csv`
- `素材解析_pipeline_material_analysis/09_current_finished_video_full_review/关键帧待人审索引_keyframe_manual_review_index.csv`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/34_当前成片全量结构适配性复审报告_current_finished_video_structure_fit_audit.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/35_结构公式修正映射表_structure_formula_revision_map.csv`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/36_剪辑师可用结构表_editor_usable_structure_table.csv`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/37_成片结构到直播素材筛选桥接说明_finished_video_to_live_screening_bridge.md`
- `执行日志_codex_log/116_当前成片全量结构适配性复审执行报告_current_finished_video_structure_fit_execution_report.md`
- `scripts/audit_current_finished_video_structure_fit.py`

## validation

- 脚本生成时完成：inventory rows=166，matrix rows=166。
- 后续必须运行：`python3 -m py_compile scripts/audit_current_finished_video_structure_fit.py`
- 后续必须运行：`python3 scripts/check_ali_config_safety.py`
- 后续必须运行：`git diff --check`、`git diff --cached --check`
- 后续必须校验：CSV 表头、行数、状态字段、staged files 无媒体/secret/cache。

## commit / push / remote status

- commit：待本报告生成后执行。
- push：待本报告生成后执行。
- remote HEAD：待 push 后验证。
- 说明：commit hash 无法在被提交文件内自指记录，本轮最终 Git readback 以 Codex 最终回报为准。

## blocked reason

- 无 blocked。当前降级原因是未使用视觉模型，因此内容结构为 `pending_visual_review`，不是阻断。
