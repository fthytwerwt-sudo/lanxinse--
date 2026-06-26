# Codex 成片解析字段规范

状态：`已创建，待用户复核`
生成时间：2026-06-27T00:53:59+08:00

## 1. 必填字段

| 字段 | 中文说明 | 取值规则 |
|---|---|---|
| `video_id` | 视频编号 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `file_name` | 文件名 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `source_path` | 来源路径 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `duration_seconds` | 视频时长 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `resolution` | 分辨率 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `aspect_ratio` | 画面比例 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `analysis_status` | 解析状态 | success / failed / pending |
| `video_type_primary` | 一级视频类型 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `video_type_secondary` | 二级视频类型 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `structure_formula` | 视频结构公式 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `opening_type` | 开头类型 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `opening_0_3s_function` | 前三秒功能 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `opening_reason` | 前三秒为什么成立 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `middle_delivery_type` | 中段交付类型 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `middle_delivery_evidence` | 中段交付证据 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `ending_closure_type` | 结尾收束类型 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `ending_next_action` | 结尾动作 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `source_integrity_score` | 素材完整感评分 | 仅允许 1 / 3 / 5 |
| `visual_speech_continuity_score` | 画面与说话连续性评分 | 仅允许 1 / 3 / 5 |
| `emotion_continuity_score` | 情绪连续性评分 | 仅允许 1 / 3 / 5 |
| `editing_flow_score` | 剪辑顺畅度评分 | 仅允许 1 / 3 / 5 |
| `jump_cut_risk` | 跳切风险 | low / medium / high |
| `why_complete_or_incomplete` | 为什么完整/不完整 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `how_to_make_complete` | 怎样做完整 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `how_middle_avoids_jump` | 中段怎样不跳 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `usable_as_reference` | 是否可作参考 | yes / no / pending_review |
| `manual_review_items` | 人工复核项 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `evidence_timecodes` | 证据时间码 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `evidence_frame_summaries` | 关键帧摘要 | 必填；不足填 pending / 待验证，不可空泛散文 |
| `notes` | 备注 | 必填；不足填 pending / 待验证，不可空泛散文 |

## 2. 输出纪律

- 每条视频必须有状态，失败也要写失败原因。
- 不允许只凭文件名分类；文件名只能作辅助。
- 关键帧抽样只能证明初步观察，不能写审美通过。
- 涉及效果、健康、课程、价格、权益、案例真实性，一律写 `待客户确认` 或人工复核。
- `connected` 模型结果不代表批量稳定，也不代表真实素材解析质量稳定。
