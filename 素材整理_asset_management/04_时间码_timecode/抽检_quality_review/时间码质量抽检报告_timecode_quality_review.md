# 时间码质量抽检报告

状态：`待用户听审确认`
生成时间：2026-06-24 02:32:23 CST

## 本轮结论

`部分成立`：本轮已抽取 2 个正样片 + 2 个负样片，并完成时间码结构、段长、空文本、重复提示等机械检查。机械汇总状态为 `timecode_mechanical_issue_found_needs_user_review`。

`待验证`：中文识别准确度、语音和文字是否基本一致、是否适合进入五结构分析，必须由用户打开本地听审包后确认。

当前能否进入五结构分析：`待用户听审后决定`。

## 抽检样片

| 类别 | pair_id | source_id | 文件名 | 分段数 | 时长秒 | 平均段长 | 最大段长 | 短段比例 | 空文本段 | 时间码递增 | 时长范围内 | 重复提示 | 机械状态 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 正样片 | `pair_0001` | `src_scan_0001` | `10分钟练出紧致 盆底肌.mp4` | 48 | 107.0 | 2.168 | 5.92 | 0.0833 | 0 | yes | yes | yes | `timecode_mechanical_issue_found_needs_user_review` |
| 正样片 | `pair_0032` | `src_scan_0004` | `30岁的女性练八爪鱼要多久.mp4` | 9 | 17.554 | 1.933 | 2.6 | 0.0 | 0 | yes | yes | no | `mechanical_check_passed_pending_user_review` |
| 负样片 | `pair_0033` | `src_scan_0063` | `会跳舞的臀你想拥有吗？.mp4` | 5 | 10.634 | 2.12 | 2.72 | 0.0 | 0 | yes | yes | no | `mechanical_check_passed_pending_user_review` |
| 负样片 | `pair_0030` | `src_scan_0064` | `跑跳漏水尴尬 一个小球告别尴尬.mp4` | 13 | 24.543 | 1.868 | 2.32 | 0.0 | 0 | yes | yes | yes | `timecode_mechanical_issue_found_needs_user_review` |

## 机械检查说明

- `timestamp_order_ok`：检查每段 `start_time / end_time` 是否递增，且 `end_time` 大于 `start_time`。
- `timestamp_within_duration_ok`：检查最大 `end_time` 是否未明显超过视频总时长。
- `short_segment_ratio`：小于 1 秒的片段占比；过高时需要人工关注分段是否过碎。
- `long_segment_count`：超过 30 秒的片段数量；过高时需要人工关注是否过长。
- `repeated_text_warning`：只做机械重复提示，不判断文本语义。

## 本地人工听审包

`已确认`：本地听审包已生成：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack`。

`已确认`：每个样片抽取 3 个片段；本轮共生成音频片段 12 个，失败 0 个。

听审包里的 `.wav` 和对应局部 `.txt` 是 local-only 文件，禁止提交 GitHub。

## 听审片段索引

### 正样片 `pair_0001` / `src_scan_0001` / `10分钟练出紧致 盆底肌.mp4`

本地目录：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌`

| 位置 | segment_index | start_time | end_time | 音频片段 | 对照文本 | 状态 |
|---|---:|---|---|---|---|---|
| start | 1 | 00:00:00.240 | 00:00:06.160 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_start_seg001.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_start_seg001.txt` | generated |
| middle | 25 | 00:01:02.520 | 00:01:04.520 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_middle_seg025.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_middle_seg025.txt` | generated |
| end | 48 | 00:01:45.280 | 00:01:46.960 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_end_seg048.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0001_pair_0001_10分钟练出紧致_盆底肌/正样片_src_scan_0001_pair_0001_end_seg048.txt` | generated |

### 正样片 `pair_0032` / `src_scan_0004` / `30岁的女性练八爪鱼要多久.mp4`

本地目录：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久`

| 位置 | segment_index | start_time | end_time | 音频片段 | 对照文本 | 状态 |
|---|---:|---|---|---|---|---|
| start | 1 | 00:00:00.000 | 00:00:02.600 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_start_seg001.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_start_seg001.txt` | generated |
| middle | 5 | 00:00:08.200 | 00:00:10.000 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_middle_seg005.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_middle_seg005.txt` | generated |
| end | 9 | 00:00:15.500 | 00:00:17.400 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_end_seg009.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/正样片_src_scan_0004_pair_0032_30岁的女性练八爪鱼要多久/正样片_src_scan_0004_pair_0032_end_seg009.txt` | generated |

### 负样片 `pair_0033` / `src_scan_0063` / `会跳舞的臀你想拥有吗？.mp4`

本地目录：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？`

| 位置 | segment_index | start_time | end_time | 音频片段 | 对照文本 | 状态 |
|---|---:|---|---|---|---|---|
| start | 1 | 00:00:00.000 | 00:00:01.640 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_start_seg001.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_start_seg001.txt` | generated |
| middle | 3 | 00:00:03.760 | 00:00:05.600 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_middle_seg003.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_middle_seg003.txt` | generated |
| end | 5 | 00:00:08.320 | 00:00:10.600 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_end_seg005.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0063_pair_0033_会跳舞的臀你想拥有吗？/负样片_src_scan_0063_pair_0033_end_seg005.txt` | generated |

### 负样片 `pair_0030` / `src_scan_0064` / `跑跳漏水尴尬 一个小球告别尴尬.mp4`

本地目录：`素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬`

| 位置 | segment_index | start_time | end_time | 音频片段 | 对照文本 | 状态 |
|---|---:|---|---|---|---|---|
| start | 1 | 00:00:00.000 | 00:00:01.840 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_start_seg001.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_start_seg001.txt` | generated |
| middle | 7 | 00:00:11.200 | 00:00:13.080 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_middle_seg007.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_middle_seg007.txt` | generated |
| end | 13 | 00:00:22.280 | 00:00:24.280 | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_end_seg013.wav` | `素材整理_asset_management/04_时间码_timecode/抽检_quality_review/local_review_pack/负样片_src_scan_0064_pair_0030_跑跳漏水尴尬_一个小球告别尴尬/负样片_src_scan_0064_pair_0030_end_seg013.txt` | generated |

## 边界确认

- 是否包含完整转写正文：否。
- 是否做五结构分析：否。
- 是否做正负样片内容评价：否。
- 是否做业务事实确认：否。
- 是否生成成片：否。
- 是否连接 DaVinci：否。

## 下一步

用户打开本地听审包，确认 4 个样片的语音和文字是否基本一致，再决定是否进入五结构分析。
