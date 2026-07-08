# 124 5月13日直播逻辑优先重筛执行报告

状态：`generated_pending_git_closure`
生成时间：2026-07-08 18:04:51

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 本轮素材路径：`/Volumes/WD_BLACK/完整直播录屏/今年直播素材/5月13日直播素材.MP4`
- 是否只处理 5 月 13 日：yes
- 是否沿用旧 102 条作为入口：no
- ASR 状态：`success_from_local_cache`
- 阿里视觉状态：qwen3-vl-plus=success; qwen-vl-max=success
- 口播单元数量：44
- 视觉动作单元数量：16
- 逻辑链候选数量：16
- true_pair 数量：1
- weak_related 数量：9
- logic_mismatch 数量：4
- manual_review 数量：2
- 本地 true_pair 视频包路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_513_logic_first_video_package`
- 本地人工复核池路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_513_manual_review_pool`
- 实际导出 mp4 数量：48
- 是否提交媒体：no
- 是否写通过类结论：no

## source_probe

- duration_seconds：6620.64
- video：1920x1080 h264 fps=50/1
- audio：pcm_s16be channels=2

## files_changed

- `.gitignore`
- `scripts/restart_513_logic_first_live_screening.py`
- `素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/01_单条直播重筛探针_single_live_rescreen_probe.csv`
- `素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/02_口播单元表_speech_units.csv`
- `素材解析_pipeline_material_analysis/17_single_live_logic_first_rescreen/03_视觉动作单元表_visual_action_units.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/01_5月13日逻辑链候选总表_513_logic_chain_candidate_master.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/02_5月13日真配对清单_513_true_pair_candidates.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/03_5月13日弱相关待复核清单_513_weak_related_pending_review.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/04_5月13日错配剔除清单_513_logic_mismatch_rejects.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/05_5月13日视频素材包索引_513_video_package_manifest.csv`
- `项目事实_project_facts/直播素材重筛_live_rescreen/06_5月13日剪辑师使用说明_513_editor_readme.md`
- `执行日志_codex_log/124_5月13日直播逻辑优先重筛执行报告_513_logic_first_rescreen_report.md`

## validation

- 未沿用旧 102 条作为入口：passed
- 重新生成口播单元、视觉动作单元、逻辑链候选：passed
- 本地视频产物已生成：passed
- true_pair 完整上下文视频技术探针：passed（127.81s, 1920x1080, audio_present=true, decodable=true）
- 媒体/API/ASR 缓存不提交 Git：已复验通过（staged_count=12, forbidden_count=0）

## blocked reason

无流程级 blocked；内容层保留 `pending_user_review`。
