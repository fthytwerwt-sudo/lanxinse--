# 剪辑师真配对任务包说明

状态：`pending_user_review`
生成时间：2026-07-08 17:01:07

## 本轮结论

- true_pair 数量：2
- weak_related_need_manual_review 数量：26
- logic_mismatch_reject 数量：1
- still_blocked / model_failed 数量：21

## 本地路径

- true_pair 视频包：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_true_pair_video_package`
- 人工复核视频池：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_manual_review_video_pool`

## 使用规则

只有 `27_阿里视觉后真配对清单_true_pair_after_ali_visual.csv` 中的候选可以进入 true_pair 视频包。弱相关、错配、模型失败和视觉不清的候选不得交给剪辑师当可用素材。

每个任务组优先看 `00_剪辑任务卡.md`，再看 `03_完整上下文_full_context.mp4` 和 `04_视觉证据_contact_sheet.jpg`。如果任务卡写 `split_status=not_available`，代表本轮没有可靠拆分口播段和动作段，需要人工二次定点。

## 边界

本轮导出的是本地素材包，不是正式成片；仍保留用户人审状态。
