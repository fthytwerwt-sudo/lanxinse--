# 5月7日直播初剪工厂交接包

状态：`rough_cut_factory_version_local_ready`
生成时间：2026-06-24

## 1. 本轮交接结论

`已确认`：本轮已基于 5 月 7 日直播真实录屏生成一条本地初剪预览：

```text
剪辑工厂输出_editing_factory_outputs/5月7日直播_minimum_loop/rough_cut_initial_preview.mp4
```

`已确认`：本地交接包还包含字幕草稿和剪映人工检查清单：

```text
剪辑工厂输出_editing_factory_outputs/5月7日直播_minimum_loop/rough_cut_subtitle_draft.srt
剪辑工厂输出_editing_factory_outputs/5月7日直播_minimum_loop/manual_jianying_checklist.md
```

`已确认`：`剪辑工厂输出_editing_factory_outputs/` 已加入 `.gitignore`，本地媒体、字幕草稿、剪映清单、临时切片和本地转写不提交 GitHub。

`待验证`：画面是否顺、动作是否安全准确、字幕是否舒服、业务事实是否成立、是否可发布。

## 2. 输出文件

| 文件 | 用途 | GitHub 状态 |
|---|---|---|
| `rough_cut_initial_preview.mp4` | 89 秒初剪工厂预览视频 | 不提交 |
| `rough_cut_subtitle_draft.srt` | 粗字幕草稿，一段一条，供剪映二次校正 | 不提交 |
| `manual_jianying_checklist.md` | 剪映人工复核清单 | 不提交 |
| `selected_segments_plan.json` | 本地切片计划和转写片段文本 | 不提交 |
| `tmp_clips/` | 5 个临时切片和 concat list | 不提交 |
| `tmp_transcript/` | 15 分钟音频窗口和机器转写 JSON/TXT | 不提交 |

## 3. 初剪视频技术信息

| 字段 | 结果 |
|---|---|
| 文件 | `rough_cut_initial_preview.mp4` |
| 时长 | `89.376933s` |
| 大小 | `22206773 bytes` |
| 视频 | H.264，1920x1080，约 29.97fps |
| 音频 | AAC，48kHz，2 channels |
| 完整解码 | 已通过 `ffmpeg -v error -i rough_cut_initial_preview.mp4 -f null -` |
| 状态 | `rough_cut_factory_version_local_ready` |

## 4. 初剪结构

| 顺序 | source_time | rough_cut_time | 功能 | 剪映处理重点 |
|---|---:|---:|---|---|
| 1 | `030.0-044.0s` | `000.0-014.0s` | 开头：目标人群与痛点钩子 | 开头可能略突兀，需补标题或前置 1 秒呼吸 |
| 2 | `240.0-257.0s` | `014.0-031.0s` | 承接：适用范围与安全感 | 修正“产后/盆底”等 ASR 错字，弱化绝对承诺 |
| 3 | `333.0-352.0s` | `031.0-050.0s` | 中段：工具作用与误区 | 确认瑜伽球画面清楚，字幕不要压住关键动作 |
| 4 | `512.0-527.0s` | `050.0-065.0s` | 中段：找到发力位置 | 必须做视觉和公开展示适配复核 |
| 5 | `572.0-596.0s` | `065.0-089.0s` | 结尾：动作执行指令 | 补步骤编号、节奏点和安全提醒 |

## 5. 字幕草稿使用说明

字幕草稿路径：

```text
剪辑工厂输出_editing_factory_outputs/5月7日直播_minimum_loop/rough_cut_subtitle_draft.srt
```

字幕状态：

- `machine_transcript_pending_manual_review`
- 每个入选片段先用一条字幕承载完整粗文本。
- 字幕只用于剪映人工校正，不可直接作为发布字幕。

必修正词：

| ASR 常见错误 | 建议修正 |
|---|---|
| `惨后` / `惩后` / `敞后` | `产后` |
| `盘地` / `盘利` / `彭底` | `盆底` |
| `鱼家球` | `瑜伽球` |
| `漏药` | 结合上下文人工判断，多数应为 `漏尿` |

## 6. 剪映人工检查清单摘要

完整清单见本地文件：

```text
剪辑工厂输出_editing_factory_outputs/5月7日直播_minimum_loop/manual_jianying_checklist.md
```

人工必须检查：

- 逐段核对 ASR 字幕。
- 检查 5 个拼接点是否过硬。
- 复核瑜伽球、坐姿、骨盆左右摆动画面是否清楚。
- 复核涉及身体隐私表达的画面是否适合公开发布。
- 检查声音同步、音量、回声和直播互动杂音。
- 复核产后年限、训练效果、工具承重/安全性等业务事实。
- 补标题、封面、字幕样式后仍需进入 `visual_editing_pending_review`。

## 7. 状态边界

| 层级 | 本轮状态 | 说明 |
|---|---|---|
| 文本/时间码 | `minimum_loop_sample_partitioned` | 只覆盖 `0-900s` 样本窗口 |
| 初剪视频 | `rough_cut_factory_version_local_ready` | 本地可播放预览已导出 |
| 字幕 | `draft_pending_manual_correction` | ASR 错字多，必须人工校正 |
| 画面 | `visual_editing_pending_review` | 未做人审视觉通过 |
| 动作专业性 | `待客户确认` | Codex 不判断动作安全有效 |
| 业务事实 | `待客户确认` | 不确认效果、承重、资历等说法 |
| 批量稳定 | `待验证` | 只跑通 1 条直播样本窗口 |
| 发布状态 | `publish_ready=false` | 不能直接发布 |

## 8. 下一步

1. 用户或剪映人工打开本地 `rough_cut_initial_preview.mp4` 进行画面/节奏复核。
2. 在剪映里按 `manual_jianying_checklist.md` 校正字幕、转场、画面裁切和节奏。
3. 若用户认为 89 秒版本方向正确，再决定是否扩展 5 月 7 日直播后续时间段。
4. 若用户认为方向不对，应回到 `16` 分区表从备选段重新选片，而不是直接进入批量。
