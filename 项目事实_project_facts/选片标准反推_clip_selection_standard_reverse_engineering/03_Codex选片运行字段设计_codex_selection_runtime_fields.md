# Codex 选片运行字段设计

状态：`已确认` 这是下一轮 Codex 选片的字段合同；`待验证` 标准仍需用户人审校正。

## 输入字段

- `source_file`：原始直播或成片文件。
- `start_time / end_time / duration_seconds`：候选窗口边界。
- `transcript_text / subtitle_text`：口播与字幕证据；缺失时写 `pending_audio_transcript`。
- `visual_evidence_timecodes`：动作、道具、表情、场景证据时间点。
- `source_neighbors`：前后窗口 id，用于相邻合并。

## 中间判断字段

- `viewer_problem_value`
- `hook_strength`
- `visual_action_value`
- `teaching_action_value`
- `semantic_completeness`
- `problem_action_bridge_seconds`
- `tts_action_alignment`
- `adjacent_merge_score`
- `repackaging_cost`
- `risk_deduction`

## 输出字段

- `content_archetype`
- `route_decision`
- `candidate_status`
- `selection_reason_tags`
- `why_selected`
- `why_rejected`
- `manual_packaging_advice`
- `manual_review_items`

## 候选状态

- `qualified_native_candidate`：原生口播/字幕结构完整，进入人审粗剪。
- `qualified_repackaging`：动作/道具价值成立，但需 TTS/字幕包装。
- `qualified_merge_candidate`：单窗口不完整，需相邻合并。
- `pending_audio_review`：画面有价值线索，但语义证据缺失。
- `reject_unusable`：无剪辑/包装/听审价值或风险过高。

## 导出规则

1. 只导出 `qualified_native_candidate`、`qualified_repackaging`、`qualified_merge_candidate` 的人审素材。
2. `pending_audio_review` 只在抽样听审任务里导出，不进入发布候选。
3. 导出文件必须保留 `pending_user_review` 和风险字段。

## 淘汰规则

1. 无观看理由且无动作/方法证据。
2. 有动作但无法解释目标、方向、发力点或禁忌。
3. 缺上下文且相邻窗口不可补。
4. 健康/业务风险无法通过提示降级。
5. 人工包装成本大于潜在价值。

## 人工复核规则

- 用户人审：判断观感、品牌适配、是否值得继续包装。
- 专业人审：判断动作专业性、禁忌、健康表达。
- 业务人审：判断是否涉及疗效/商业承诺。

## 失败回退规则

- 语义缺失：转 `pending_audio_review`。
- 单窗口不完整：转 `qualified_merge_candidate`。
- 动作可见但无问题：转 `qualified_repackaging` 并要求补问题前置。
- 风险过高：转 `reject_unusable`。
