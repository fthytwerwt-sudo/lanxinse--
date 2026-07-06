# 完整直播素材筛选与口播动作配对执行报告

状态：`screening_tables_generated_pending_user_review`
开始时间：2026-07-06T18:24:23+08:00
生成时间：2026-07-06T18:24:28+08:00

## commands

- `pwd && git rev-parse --show-toplevel && git branch --show-current && git remote -v && git status --short`
- `git pull --ff-only`
- `ffprobe` 元数据读取 4 条录屏
- `ffmpeg -ss 30 -t 2 ... -f null -` 样本解码抽检 4 条录屏
- `.venv_timecode/bin/python scripts/full_live_material_screening_with_action_pairing.py --asr-model small --window-seconds 120`

## result

- 当前项目仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 直播素材目录：`/Volumes/WD_BLACK/完整直播录屏/今年直播素材`
- source_dir_status：`semantic_nested_path_found: exact three prompt paths missing`
- 直播录屏数量：4
- 可读录屏数量：4
- 总候选数：211
- A 类数量：102
- B 类数量：91
- C 类数量：18
- Reject 数量：6
- 口播动作配对组数量：211
- 是否生成本地导出命令：yes
- 是否提交媒体：no
- 是否写健康/业务/动作通过：no

## ASR / Ali visual boundary

- 本地 ASR 日志：首次完整运行已生成 4 份本地转写缓存；最终重跑复用缓存：`rec_001_5月13日直播素材.json`、`rec_002_C5824.json`、`rec_003_C5825.json`、`rec_004_C5829.json`。缓存位于 `api_outputs/full_live_material_screening/asr_transcripts/`，不提交 Git。
- 阿里视觉：历史最小连接报告显示 `qwen3-vl-plus` 连接过；本轮未上传完整视频，未把视觉模型作为动作完整性通过证据。

## files_changed

- `素材解析_pipeline_material_analysis/12_full_live_material_screening/01_直播录屏清单_live_recording_inventory.csv`
- `素材解析_pipeline_material_analysis/12_full_live_material_screening/02_直播口播动作时间轴_live_speech_action_timeline.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/01_直播候选片段总表_live_candidate_segment_master.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/02_口播动作配对表_speech_action_pairing_table.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/03_按剪辑结构归类候选表_candidates_by_clip_structure.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/04_A类优先剪辑清单_priority_A_editor_pick_list.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/05_B类二次加工清单_priority_B_rework_list.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/06_放弃与风险片段清单_rejected_and_risk_segments.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/07_剪辑师人读版报告_editor_readable_screening_report.md`
- `项目事实_project_facts/直播素材筛选_live_material_screening/08_人工复核清单_manual_review_checklist.md`
- `项目事实_project_facts/直播素材筛选_live_material_screening/09_本地候选素材导出命令_local_clip_export_commands.sh`
- `执行日志_codex_log/119_完整直播素材筛选与口播动作配对执行报告_full_live_screening_action_pairing_report.md`
- `scripts/full_live_material_screening_with_action_pairing.py`

## validation

- `python3 -m py_compile scripts/full_live_material_screening_with_action_pairing.py`：passed
- `git diff --check`：passed
- 精确敏感细节扫描：passed，提交表不展开原始 ASR 细节。
- 输出表自检：passed，4 条 inventory、217 个时间轴窗口、211 条候选、211 个配对组、A/B/C/Reject 统计一致。
- `git diff --cached --check`：passed

## failed_items

- 同目录/邻近目录未发现现成 `.srt/.vtt/.json/.csv/.txt` 转写或动作解析。
- 未做全量视频解码；长视频只做 ffprobe + 2 秒样本解码抽检。
- 未做人审视觉通过、动作专业通过、业务通过或发布通过。

## blocked reason

- 无 `blocked`。当前是 `pending_user_review`，不是业务/审美/发布完成。
