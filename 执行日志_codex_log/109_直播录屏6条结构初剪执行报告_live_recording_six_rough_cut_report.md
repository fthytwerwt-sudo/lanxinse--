# 直播录屏 6 条结构初剪执行报告

状态：`completed_with_pending_user_review`
生成时间：2026-06-29 17:14:09
任务类型：`live_recording_structure_rough_cut_probe`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前项目仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `origin	https://github.com/fthytwerwt-sudo/lanxinse--.git (fetch)` |
| 预期直播录屏目录 | `/Volumes/WD_BLACK/澜心社剪辑/WD_BLACK-完整直播录屏` |
| 实际直播录屏目录 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播` |
| 目录定位状态 | `expected_dir_missing_used_discovered_complete_live_dir` |
| 有效录屏数量 | `1` |
| 目标读取数量 | `约 7 条` |
| 缺失录屏记录 | `6` |
| 候选片段数量 | `8` |
| 成功导出初剪数量 | `6` |
| 是否达到 6 条 | `是` |
| 不足 6 条原因 | `不适用；但录屏数量不足 7 条，实际只发现 1 条完整录屏` |
| 源视频技术参数 | `H.264 1920x1080 60000/1001，音频 pcm_s16be` |
| 是否保持原画面比例 | `是，ffprobe 验证 6 条均保持 1920x1080` |
| 是否改变画面 | `否` |
| 是否添加字幕 / 包装 / 调色 / 美颜 / BGM | `否` |
| 是否重新编码 | `否，6 条均使用 ffmpeg -c copy` |
| 是否上传完整视频 | `否` |
| 是否提交媒体 | `否` |
| 阿里 live 调用 | `未执行；.env 中 ALI_API_ENABLE_LIVE_TEST=false，本轮走本地降级 + 既有 connected 报告` |
| 全局浏览证据 | `本地生成 7 帧 contact sheet，覆盖 30/600/1200/1800/2400/3000/3500 秒，不提交 GitHub` |
| 口播精确解析范围 | `复用既有 0-900s 本地 faster-whisper 转写，状态 machine_transcript_pending_manual_review` |

## 2. 生成文件

- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/01_直播录屏素材清单_live_recording_inventory.csv`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/02_候选片段结构匹配表_candidate_segment_structure_match.csv`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/03_六条初剪视频证据报告_six_rough_cut_evidence_report.md`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/04_人工复核清单_manual_review_checklist.md`
- `项目事实_project_facts/直播录屏初剪验证_live_recording_rough_cut_probe/05_初剪结果索引_rough_cut_output_index.csv`
- `scripts/live_recording_rough_cut_probe.py`
- `执行日志_codex_log/109_直播录屏6条结构初剪执行报告_live_recording_six_rough_cut_report.md`

## 3. 本地视频输出

### 初剪视频 01

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_001_scope_action_rec_001_000400_000505.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:04:00-00:05:05` |
| 结构公式 | `痛点问题 + 原因解释 + 方法交付` |
| 时长 | `65.055s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

### 初剪视频 02

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_002_tool_misuse_rec_001_000522_000631.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:05:22-00:06:31` |
| 结构公式 | `错误动作 + 正确动作 + 原因解释` |
| 时长 | `69.041s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

### 初剪视频 03

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_003_tool_setup_rec_001_000730_000848.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:07:30-00:08:48` |
| 结构公式 | `结果前置 + 操作过程 + 注意事项` |
| 时长 | `78.028s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

### 初剪视频 04

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_004_single_action_demo_rec_001_000847_001011.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:08:47-00:10:11` |
| 结构公式 | `人群点名 + 痛点放大 + 单动作演示 + 坚持建议` |
| 时长 | `84.061s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

### 初剪视频 05

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_005_mistake_correction_rec_001_001057_001205.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:10:57-00:12:05` |
| 结构公式 | `错误动作 + 正确动作 + 原因解释` |
| 时长 | `68.024s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

### 初剪视频 06

| 字段 | 结果 |
|---|---|
| 本地路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/live_recording_rough_cut_probe/rough_cut_006_practice_frequency_rec_001_001328_001444.mp4` |
| 来源录屏 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/完整直播/5月7日直播.MP4` |
| 起止时间 | `00:13:28-00:14:44` |
| 结构公式 | `痛点问题 + 原因解释 + 方法交付` |
| 时长 | `76.033s` |
| 宽高 | `1920x1080` |
| 是否保持比例 | `yes` |
| 音频是否保持 | `yes` |

## 4. 验证证据

已执行 / 本脚本内执行：

- `pwd`
- `git rev-parse --show-toplevel`
- `git branch --show-current`
- `git remote -v`
- `git status --short --branch`
- `git pull --ff-only`
- `ffmpeg -version`
- `ffprobe -version`
- `ffprobe` 读取原始完整录屏
- `ffmpeg -ss ... -to ... -c copy` 导出 6 条候选初剪
- `ffprobe` 验证 6 条输出视频宽高、时长、视频轨和音频轨

本轮验证已完成：

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/check_ali_api_connection.py scripts/check_ali_models_live.py scripts/check_ali_config_safety.py scripts/live_recording_rough_cut_probe.py`
- `git diff --check`
- 6 条输出视频逐条 `ffmpeg -v error -i <output> -f null -` 完整解码，无错误输出

Git 闭环状态：

- path-limited stage / commit / push / remote HEAD readback 在本报告写入后执行。
- 最终 commit SHA、push 结果和 remote HEAD 以 Codex 最终回报为准，避免在报告内写自引用哈希。

## 5. 边界确认

| 边界 | 结果 |
|---|---|
| 是否提交源视频 | 否 |
| 是否提交初剪视频 | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否提交 token | 否 |
| 是否提交完整 API 输出 | 否 |
| 是否改变画面比例 | 否 |
| 是否加包装 | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定自动剪辑 | 否 |

## 6. 已知限制

- 预期目录 `WD_BLACK-完整直播录屏` 未命中；实际使用同工作区内的 `剪辑解析数据/完整直播`。
- 目标约 7 条完整录屏，实际只发现 1 条有效录屏；素材清单已把缺失的 6 个录屏位标为 `missing_not_found_in_live_recording_dir`。
- 本轮没有上传完整视频到阿里；由于 `.env` 当前 `ALI_API_ENABLE_LIVE_TEST=false`，只使用既有阿里 connected 报告和本地降级路线。
- 0-900s 之外只做全局低频视觉抽样，未做全场精确口播转写。
- 6 条视频均为结构候选初剪，等待用户人审；不能直接发布。

## 7. 状态标记

```text
completed_with_pending_user_review
```
