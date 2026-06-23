# 时间码全量转写执行报告

状态：`待验证`，本报告写入时尚未完成 commit / push / remote HEAD readback；最终 Git 证据以本轮最终回报为准。
任务类型：`batch_timecode_transcription_full_33`
生成时间：2026-06-24 00:15:54 CST

## 1. 本轮结论

`已确认`：本轮已按用户授权，对素材清单中的 33 个视频执行本地全量时间码转写。

`已确认`：33 个视频均生成本地 `.json` 和 `.txt` 带时间码转写输出。

`已确认`：已生成 33 行状态表，每个视频都有明确状态。

`部分成立`：工具运行结果为全量成功；这不代表中文识别质量、时间码颗粒度或剪辑可用性已通过。

`待验证`：自动转写内容需要人工抽检；后续才能决定是否进入五结构判断标准和细致分析。

## 2. 执行范围

| 项目 | 结果 |
|---|---:|
| 应处理视频数量 | 33 |
| 实际找到视频数量 | 33 |
| 成功数量 | 33 |
| 失败数量 | 0 |
| 跳过数量 | 0 |
| 总分段数量 | 848 |
| 总视频时长秒数 | 1511.489 |
| 本地 JSON 输出数量 | 33 |
| 本地 TXT 输出数量 | 33 |
| 音频缓存 WAV 数量 | 33 |

## 3. 使用工具与参数

| 项目 | 值 |
|---|---|
| 转写工具 | `faster-whisper` |
| 模型 | `small` |
| 语言提示 | `zh` |
| device | `cpu` |
| compute_type | `int8` |
| 音频抽取 | `ffmpeg` 抽取 16kHz 单声道 WAV |
| 本地输出目录 | `素材整理_asset_management/04_时间码_timecode/本地转写输出_local_transcripts/` |
| 音频缓存目录 | `素材整理_asset_management/04_时间码_timecode/音频缓存_audio_cache/` |
| 模型缓存目录 | `素材整理_asset_management/04_时间码_timecode/model_cache/` |

## 4. 生成文件

### 4.1 本轮允许提交

- `工具_scripts/批量生成时间码转写_batch_timecode_transcribe.py`：批量时间码转写脚本。
- `素材整理_asset_management/04_时间码_timecode/时间码全量转写状态_batch_timecode_status.csv`：33 个视频转写状态表。
- `素材整理_asset_management/04_时间码_timecode/本地转写输出说明_local_transcripts_readme.md`：本地完整转写结果说明。
- `执行日志_codex_log/99_时间码全量转写执行报告_batch_timecode_transcription_report.md`：本报告。
- `.gitignore`：补充忽略本地完整转写输出目录。

### 4.2 本地生成但禁止提交

- `素材整理_asset_management/04_时间码_timecode/本地转写输出_local_transcripts/`：完整 `.json / .txt` 转写正文。
- `素材整理_asset_management/04_时间码_timecode/音频缓存_audio_cache/`：抽取音频缓存。
- `素材整理_asset_management/04_时间码_timecode/model_cache/`：模型缓存。

## 5. 状态表说明

状态表路径：

```text
素材整理_asset_management/04_时间码_timecode/时间码全量转写状态_batch_timecode_status.csv
```

表内包含：

- `pair_id`
- `source_id`
- `video_file_name`
- `video_path`
- `transcript_json_path`
- `transcript_txt_path`
- `status`
- `segment_count`
- `duration_seconds`
- `language`
- `model_used`
- `compute_type`
- `error_message`
- `needs_manual_review`

`已确认`：33 行均为 `status=success`，且 `needs_manual_review=yes`。

## 6. 失败列表

无。

## 7. 边界确认

- 是否修改原始素材：否。
- 是否修改原始 txt：否。
- 是否移动、删除、重命名素材：否。
- 是否提交完整转写正文：否。
- 是否提交音频缓存：否。
- 是否提交模型缓存：否。
- 是否提交媒体文件：否。
- 是否进入内容分析：否。
- 是否进入五结构分析：否。
- 是否生成成片：否。
- 是否连接 DaVinci：否。
- 是否把自动转写写成准确通过：否。
- 是否把时间码结果写成剪辑可用：否。

## 8. 质量状态

`待人工抽检`：中文识别质量、时间码颗粒度、分段是否适合剪辑，均未在本轮判断。

`待验证`：这些本地转写能否进入五结构候选筛选，必须等人工抽检后再定。

## 9. 验证命令与结果

| 命令 | 结果 |
|---|---|
| `pwd` | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| `git rev-parse --show-toplevel` | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| `git branch --show-current` | `main` |
| `git remote -v` | `origin https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| `git pull --ff-only` | `Already up to date.` |
| `ffmpeg -version` | `ffmpeg version 8.1` |
| `.venv_timecode/bin/python -c "import faster_whisper; print('faster_whisper_ok')"` | `faster_whisper_ok` |
| 状态表统计 | `status_rows=33`，`success=33` |
| 本地输出数量 | JSON `33`，TXT `33` |
| 本地输出目录 ignore 检查 | `本地转写输出_local_transcripts/` 命中 `.gitignore` |

## 10. Commit / push / remote HEAD 状态

- commit hash：`待验证`，本报告写入时尚未提交；实际提交号以最终回报为准。
- push 状态：`待验证`。
- remote HEAD：`待验证`。

## 11. 下一步建议

1. 人工抽检 2 个正样片 + 2 个负样片的转写质量，再决定是否进入五结构判断标准和细致分析。
2. 如果抽检发现中文识别或分段不适合剪辑，再考虑调整 `faster-whisper` 参数或对比阿里 ASR。
