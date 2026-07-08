# 视觉复核后剪辑任务包生成方案

状态：`pending_user_review`
生成时间：2026-07-08 16:11:01

## 本轮结论

本轮从 102 条 `blocked_need_visual_review` 候选里选出 16 条优先样本，生成本地视觉复核材料，并对 contact sheet 做小样本视觉探针。

## 数量

- true_pair_candidate：0
- true_pair_but_action_cycle_incomplete：0
- weak_related_need_manual_review：0
- logic_mismatch_reject：0
- still_blocked_need_human_visual_review：16

## 任务包生成规则

1. 只有 `22_真配对候选_视觉复核后_true_pair_after_visual_review.csv` 中的候选，才允许进入下一轮剪辑任务包草案。
2. 若 true_pair 数量为 0，不生成剪辑师可用包，先组织人工看本地复核材料。
3. `23_视觉复核后仍阻断清单` 只能作为人工复核池，不进入剪辑师交付。
4. `24_视觉复核后逻辑错配清单` 直接剔除或回到算法规则修正。
5. 下一轮生成任务包时必须附上：口播同一点、视觉动作名、动作起止点、动作循环状态、遮挡状态和人工复核项。

## 用户复核入口

本地复核材料目录：

`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_visual_action_review_probe`

优先打开每个样本文件夹里的 `00_contact_sheet.jpg` 和 `03_review_preview_20s.mp4`；需要完整上下文时，再按 CSV 里的 `local_full_context_path` 打开。
