# 122 优先候选视觉动作复核执行报告

状态：`visual_action_review_probe_generated_pending_user_review`
生成时间：2026-07-08 16:11:01

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `python3 scripts/check_ali_config_safety.py`
- `python3 scripts/priority_visual_action_review_probe.py`
- `python3 -m py_compile scripts/priority_visual_action_review_probe.py`
- `git diff --check`
- `git diff --cached --check`

## result

- 原 blocked 候选数量：102
- 本轮选择样本数量：16
- 视觉复核方式：`external_model_contact_sheet` when available, otherwise `human_pack`
- 视觉模型可用状态：disabled_after_first_failure:http_403: {"error":{"message":"Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#acces
- 本地视觉材料数量：256
- 本地视觉材料路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_visual_action_review_probe`
- 是否提交媒体：no
- 是否写健康/业务/动作专业性/审美/发布结论：no

- true_pair_candidate: 0
- true_pair_but_action_cycle_incomplete: 0
- weak_related_need_manual_review: 0
- logic_mismatch_reject: 0
- still_blocked_need_human_visual_review: 16

## model_status_counts

{'failed': 1, 'disabled_after_previous_visual_api_failure': 15}

## validation

- 样本数量在 10-20 之间：passed
- 每条样本都有选择原因：passed
- 每条样本都有视觉复核状态：passed
- 本轮本地媒体目录已被 Git 忽略：passed
- 暂存扫描不包含媒体、图片、ASR 缓存或 api_outputs：已复验通过（staged_count=10, forbidden_count=0）

## files_changed

- `.gitignore`
- `scripts/priority_visual_action_review_probe.py`
- `素材解析_pipeline_material_analysis/15_visual_action_review_probe/01_视觉复核样本选择表_visual_review_sample_selection.csv`
- `素材解析_pipeline_material_analysis/15_visual_action_review_probe/02_视觉复核探针_visual_review_probe.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/21_优先候选视觉动作复核总表_priority_visual_action_review_master.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/22_真配对候选_视觉复核后_true_pair_after_visual_review.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/23_视觉复核后仍阻断清单_still_blocked_after_visual_review.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/24_视觉复核后逻辑错配清单_logic_mismatch_after_visual_review.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/25_视觉复核后剪辑任务包生成方案_after_visual_review_editor_task_pack_plan.md`
- `执行日志_codex_log/122_优先候选视觉动作复核执行报告_priority_visual_action_review_report.md`

## failed_items

- 本轮仍需用户人审本地复核材料；contact sheet 小样本视觉探针不等于完整人工验收。
- 若视觉模型返回不确定或无法确认同动作，候选仍保留阻断或人工复核状态。

## blocked reason

无流程级 blocked；内容层按 P0 闸门保守处理。
