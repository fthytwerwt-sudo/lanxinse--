# 时间码质量抽检执行报告

状态：`待用户听审确认`；本报告写入时 commit / push / remote HEAD 仍待本轮 Git 闭环验证。
任务类型：`timecode_quality_sample_review`
生成时间：2026-06-24 02:32:23 CST

## 1. 读取文件

- `AGENTS.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/` 机制入口文件
- `素材整理_asset_management/04_时间码_timecode/时间码全量转写状态_batch_timecode_status.csv`
- `素材整理_asset_management/04_时间码_timecode/本地转写输出说明_local_transcripts_readme.md`
- `执行日志_codex_log/99_时间码全量转写执行报告_batch_timecode_transcription_report.md`
- `工具_scripts/批量生成时间码转写_batch_timecode_transcribe.py`（仅编译验证）
- 本地转写 JSON：仅抽检 4 个样片对应文件。

## 2. 抽检样片

| 类别 | pair_id | source_id | 文件名 | 分段数 | 时长秒 | 平均段长 | 最大段长 | 短段比例 | 空文本段 | 时间码递增 | 时长范围内 | 重复提示 | 机械状态 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 正样片 | `pair_0001` | `src_scan_0001` | `10分钟练出紧致 盆底肌.mp4` | 48 | 107.0 | 2.168 | 5.92 | 0.0833 | 0 | yes | yes | yes | `timecode_mechanical_issue_found_needs_user_review` |
| 正样片 | `pair_0032` | `src_scan_0004` | `30岁的女性练八爪鱼要多久.mp4` | 9 | 17.554 | 1.933 | 2.6 | 0.0 | 0 | yes | yes | no | `mechanical_check_passed_pending_user_review` |
| 负样片 | `pair_0033` | `src_scan_0063` | `会跳舞的臀你想拥有吗？.mp4` | 5 | 10.634 | 2.12 | 2.72 | 0.0 | 0 | yes | yes | no | `mechanical_check_passed_pending_user_review` |
| 负样片 | `pair_0030` | `src_scan_0064` | `跑跳漏水尴尬 一个小球告别尴尬.mp4` | 13 | 24.543 | 1.868 | 2.32 | 0.0 | 0 | yes | yes | yes | `timecode_mechanical_issue_found_needs_user_review` |

## 3. 机械检查摘要

- 状态表总行数：33。
- 可用正样片数量：30。
- 可用负样片数量：3。
- 本轮抽检数量：4。
- 机械汇总状态：`timecode_mechanical_issue_found_needs_user_review`。
- 本地听审音频片段：生成 12 个，失败 0 个。

## 4. 本地听审包状态

- 本地路径：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack`。
- 仓库相对路径：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack`。
- 是否提交 GitHub：否。
- `.gitignore` 状态：已补充忽略 `local_review_pack/`。

## 5. 边界确认

- 是否修改原始素材：否。
- 是否修改原始 txt：否。
- 是否修改本地完整转写结果：否。
- 是否提交完整转写正文：否。
- 是否提交音频片段：否。
- 是否提交媒体文件：否。
- 是否进入内容分析：否。
- 是否进入五结构分析：否。
- 是否生成成片：否。
- 是否连接 DaVinci：否。
- 是否把自动转写质量写成已通过：否。

## 6. 生成文件

- `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/时间码质量抽检表_timecode_quality_review.csv`
- `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/时间码质量抽检报告_timecode_quality_review.md`
- `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/本地人工听审包说明_local_review_pack_readme.md`
- `执行日志_codex_log/99_时间码质量抽检执行报告_timecode_quality_review_report.md`
- `.gitignore`

## 7. Commit / push / remote HEAD 状态

- commit hash：`待最终回报确认`。
- push 状态：`待最终回报确认`。
- remote HEAD：`待最终回报确认`。

## 8. 下一步建议

1. 用户打开本地听审包，确认 4 个样片的语音和文字是否基本一致，再决定是否进入五结构分析。
2. 如果任一样片出现明显错识别、漏识别或时间点错位，先调整转写路线，不进入五结构。
