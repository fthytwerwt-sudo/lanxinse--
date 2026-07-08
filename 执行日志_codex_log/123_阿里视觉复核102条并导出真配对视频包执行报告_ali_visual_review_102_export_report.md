# 123 阿里视觉复核102条并导出真配对视频包执行报告

状态：`generated_pending_git_closure`
生成时间：2026-07-08 17:01:07

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `python3 scripts/ali_visual_review_102_and_export_true_pair_video_package.py`
- `python3 -m py_compile scripts/ali_visual_review_102_and_export_true_pair_video_package.py`
- `python3 scripts/check_ali_config_safety.py`
- `git diff --check`
- `git diff --cached --check`

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 阿里视觉默认路由：`qwen3-vl-plus` -> `qwen-vl-max`
- 禁用模型是否被调用：no
- 原 blocked 候选数量：102
- 本轮按用户新指令实际复核数量：50
- true_pair 数量：2
- weak_related 数量：26
- logic_mismatch 数量：1
- still_blocked 数量：21
- 本地 true_pair 视频包路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_true_pair_video_package`
- 本地人工复核视频池路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_manual_review_video_pool`
- 实际导出 mp4 数量：50
- 是否只输出文本：no
- 是否提交媒体：no
- 是否提交 API 原始输出：no
- 是否写健康/业务/审美/发布类结论：no
- 阿里路由探针：qwen3-vl-plus=success; qwen-vl-max=success

## model_status_counts

{'success': 50}

## p0_gate_counts

{'still_blocked_topic_break': 21, 'weak_related_need_manual_review': 26, 'logic_mismatch_reject': 1, 'true_pair': 2}

## 本地视频产物说明

- true_pair 视频包路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_true_pair_video_package`
- 人工复核视频池路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_manual_review_video_pool`
- 文件夹按视频结构分区，每组含任务卡、完整上下文视频和 contact sheet。
- 这些都不是正式成片，弱相关和阻断项必须人工复核。

## files_changed

- `.gitignore`
- `scripts/ali_visual_review_102_and_export_true_pair_video_package.py`
- `项目事实_project_facts/模型路由_model_routing/01_阿里视觉模型默认路由_ali_visual_model_default_route.md`
- `素材解析_pipeline_material_analysis/16_ali_visual_review_102/01_阿里视觉路由探针_ali_visual_route_probe.csv`
- `素材解析_pipeline_material_analysis/16_ali_visual_review_102/02_视觉复核输入材料清单_visual_review_input_manifest.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/26_阿里视觉复核102条总表_ali_visual_review_102_master.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/27_阿里视觉后真配对清单_true_pair_after_ali_visual.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/28_阿里视觉后弱相关待复核清单_weak_related_after_ali_visual.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/29_阿里视觉后错配剔除清单_logic_mismatch_after_ali_visual.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/30_阿里视觉后仍阻断清单_still_blocked_after_ali_visual.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/31_真配对视频素材包索引_true_pair_video_package_manifest.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/32_剪辑师真配对任务包说明_editor_true_pair_task_pack_readme.md`
- `执行日志_codex_log/123_阿里视觉复核102条并导出真配对视频包执行报告_ali_visual_review_102_export_report.md`

## validation

- 本轮 50 条都有视觉复核结果或模型失败记录：passed
- true_pair / weak / mismatch / blocked 四类表已生成：passed
- 本地视频产物目录存在：passed
- 媒体目录已被 Git 忽略：passed
- 暂存扫描不包含媒体、图片、ASR 缓存、API 原始输出或 `.env`：已复验通过（staged_count=13, forbidden_count=0）

## failed_items

- 无流程级失败

## blocked reason

无流程级 blocked；内容层按 P0 闸门保守分流。
