# 当前架构地图

状态：`partial_architecture_runtime_gap_confirmed_pending_user_review`
生成时间：2026-07-02T16:00:48+08:00

## 已确认事实

- 当前仓库：`fthytwerwt-sudo/lanxinse--`
- 本地仓库：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 素材根目录：`/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据`
- AI 需要的成片：922 条；本轮只补齐前 100 条。
- 正样本：30 条；负样本：3 条；直播素材：4 条。
- 旧前 100 阿里重看结果可复用：`已确认`。
- 直播正式模拟 0 候选原因：`部分成立`，更像固定窗口 + 缺音频/合并 runtime 的路线缺口，不是素材全废。

## 架构层状态

| gap_id | gap_name | current_status | priority |
| --- | --- | --- | --- |
| gap_01 | content_archetype_routing_layer | 部分成立：成片样本层已有类型库，formal simulation runtime 未前置路由 | P1 |
| gap_02 | problem_action_bridge_layer | 部分成立：文本规则存在，但未形成秒级 problem->action runtime 判断 | P0 |
| gap_03 | action_teaching_repackaging_route | 部分成立：样本规则可支持，但直播素材救回流程未落地 | P0 |
| gap_04 | adjacent_window_merge_layer | 缺执行层：已有 need_merge_previous/next 标记，但无 merge operator | P0 |
| gap_05 | audio_tts_subtitle_timeline_alignment_layer | 缺失：当前仅视觉抽帧，音频/字幕/TTS 时间线未统一 | P0 |
| gap_06 | positive_negative_contrast_layer | 已建立但负样本偏薄：已有正负样片证据矩阵，负样本仅 3 条 | P1 |
| gap_07 | candidate_status_taxonomy | 部分成立：五结构有 candidate_decision，formal simulation 状态未统一 | P1 |
| gap_08 | field_dictionary_layer | 部分成立：已有主键链路和五结构字段，V2 新字段未入字典 | P1 |
| gap_09 | manual_review_routing_layer | 已建立但需要 V2 路由细化 | P1 |
| gap_10 | feedback_to_rule_update_layer | 部分成立：已有回写说明，缺独立 rule delta ledger | P2 |
