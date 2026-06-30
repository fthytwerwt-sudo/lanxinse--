# 112 结果复审与路线重判

状态：`completed_route_replanned_pending_transcript_audio_probe`
生成时间：2026-06-30T21:06:41+08:00

## 1. 当前事实

本文件只复审 112 轮已生成的本地分析结果和仓库内 CSV/报告，不重跑 Ali/API，不导出视频，不修改核心脚本，不把素材写成审美、业务或发布通过。

| 项目 | 已确认结果 |
| --- | --- |
| 直播录屏数量 | 2 |
| 全覆盖窗口数量 | 76 |
| coverage_status 分布 | {'covered': 76} |
| 窗口 ali_model_called 分布 | {'yes': 76} |
| analysis_status 分布 | {'success': 76} |
| 阿里审计 primary_status 分布 | {'success': 76} |
| high_review_called 分布 | {'no': 5, 'yes': 71} |
| 候选片段表行数 | 0 |
| 初剪结果索引行数 | 0 |
| 弃用片段行数 | 83 |
| 原始 summary JSON 数量 | 76 |
| 原始 final_json candidate_segments | 0 |
| 原始 final_json rejected_segments | 83 |
| can_be_complete_short_segment 分布 | {'no': 76} |
| need_merge_previous 分布 | {'yes': 76} |
| need_merge_next 分布 | {'yes': 76} |

## 2. 0 候选主因

`已确认`：112 轮不是导出环节漏跑。候选片段表为 0 行，初剪索引为 0 行；同时 76 个窗口均完成覆盖和视觉审计，原始 `final_json` 中 `candidate_segments=0`、`rejected_segments=83`。

`已确认`：脚本的导出闸门要求同一候选同时满足 `decision=export/导出`、时长达标、`complete_score >= 3`、`continuity_score >= 3`、`editing_flow_score >= 3`、开头/中段/结尾摘要齐全，且 `jump_cut_risk` 不高。当前原始模型结果没有生成可进入该闸门的 `candidate_segments`。

`部分成立`：112 的 0 候选主因不是单纯“素材完全不可用”，而是当前路线用视觉 contact sheet 和 180 秒固定窗口去判断“可独立成片的完整短视频结构”。直播录屏天然经常处在连续口播中段，开头理由和结尾收束依赖前后窗口、口播、字幕或上下文，因此会被完整性闸门拦下。

## 3. 弃用原因分布

| missing_part | 数量 |
| --- | --- |
| opening/middle/ending/evidence | 38 |
| opening,middle,ending,evidence | 22 |
| opening/ending/evidence | 7 |
| opening,middle,evidence | 3 |
| opening/middle/ending/evidence/continuity | 3 |
| ending/evidence | 2 |
| opening/ending/evidence/continuity | 2 |
| opening/evidence/continuity | 1 |
| ending,evidence | 1 |
| middle/ending/evidence | 1 |
| ending/continuity | 1 |
| opening, ending, evidence, continuity | 1 |
| opening/middle/ending | 1 |

| could_be_fixed_by_manual_edit | 数量 |
| --- | --- |
| unclear | 79 |
| no | 2 |
| yes | 2 |

| recording_id | 弃用数量 |
| --- | --- |
| rec_002 | 43 |
| rec_001 | 40 |

| 30 分钟时间段 | 弃用数量 |
| --- | --- |
| 000-030m | 27 |
| 030-060m | 24 |
| 060-090m | 20 |
| 090-120m | 12 |

| 关键词 | 出现行数 |
| --- | --- |
| 结尾 | 77 |
| 开头 | 76 |
| 收束 | 76 |
| 中段 | 74 |
| 动作 | 70 |
| 观看理由 | 64 |
| 交付 | 64 |
| 总结 | 42 |
| 方法 | 35 |
| 问题引入 | 33 |
| 前段 | 30 |
| 后段 | 28 |
| 拼接 | 23 |
| 静态 | 21 |
| 证据 | 19 |
| 口播 | 18 |
| 字幕 | 17 |
| 连续 | 8 |
| 无实质交付 | 4 |
| 无信息增量 | 2 |
| 效果 | 2 |
| 漏尿 | 1 |
| 产后 | 1 |

## 4. 可救回复审分布

新增复审表：`素材解析_pipeline_material_analysis/09_live_recording_formal_simulation/07_弃用片段复审与可救回片段表_rejected_segment_recheck_rescue_candidates.csv`。

| recheck_category | 命中行数 |
| --- | --- |
| ending_missing | 81 |
| evidence_missing | 81 |
| opening_missing | 78 |
| middle_missing | 78 |
| possible_manual_extension | 76 |
| unlikely_rescue | 28 |
| medical_or_business_risk | 18 |
| continuity_risk | 18 |

| rescue_level | 数量 |
| --- | --- |
| medium | 68 |
| pending | 12 |
| no | 2 |
| low | 1 |

| needs_transcript_or_audio | 数量 |
| --- | --- |
| yes | 82 |
| no | 1 |

| needs_manual_start_end_extension | 数量 |
| --- | --- |
| yes | 76 |
| no | 7 |

| risk_review_required | 数量 |
| --- | --- |
| no | 65 |
| yes | 18 |

解释边界：`medium` 或 `pending` 只表示“值得进入音频/字幕/前后文复审”，不表示片段可直接剪出；`low/no` 表示在当前视觉证据下不应自动救回或导出。

## 5. 路线重判

`不建议`：直接全局放宽候选规则。原因是大部分 rejected 同时缺开头、结尾和证据，放宽会把直播中段、半句话、半动作或上下文缺失片段误放为初剪，风险比收益大。

`建议 primary_route`：改为“先找高价值片段，再人工扩展起止点”。先从 `medium/pending` 行里挑选有动作/方法/讲解价值、且主要缺开头/结尾/证据的片段，向前后扩展查找真实开头和收束，再决定是否进入剪辑。

`建议 required_evidence_layer`：补 transcript/audio semantic understanding。当前 76/76 个原始窗口都标 `need_merge_previous=yes` 且 `need_merge_next=yes`，说明只看视觉抽帧不足以判定口播结构。下一轮应先做音频/字幕/口播转写或人工听审，再判断开头理由、中段交付、结尾收束。

`不建议`：现在判定这两条素材完全不适合。原因是 rejected 中存在大量“前段含问题引入 / 后段含总结 / 可拼接 / 可作为中段”的救回线索，但这些线索目前缺少音频和前后窗口验证。

`已确认`：未发现脚本统计层面的明显矛盾。覆盖、调用、分析均成功；候选为 0 与原始 summary 的 `candidate_segments=0` 一致。当前更像路线与证据层不足，而不是导出脚本故障。

## 6. 下一步建议

1. 不重跑完整 Ali 视觉窗口，不直接导出视频。
2. 先从复审 CSV 选择 `rescue_level in (medium, pending)` 且 `needs_transcript_or_audio=yes` 的片段，按每条素材 3-5 个小样本做音频/字幕复审。
3. 对每个样本人工或半自动扩展前后窗口，记录“真实开头秒点、真实结束秒点、口播结构证据、风险词”。
4. 只有当同一连续片段具备开头理由、中段交付、结尾收束，并通过健康/业务风险复核后，才进入初剪导出。

## 7. 仍待验证

- `qwen-omni-turbo-latest` 或其他音视频/转写能力是否能稳定读取这些长直播录屏：`待验证`。
- `medium/pending` 片段是否真的可剪出完整短视频：`待验证`，必须经过口播和前后起止点复审。
- 素材审美、人感、动作专业性、健康表达、业务事实、发布可用性：全部 `待验证`。
