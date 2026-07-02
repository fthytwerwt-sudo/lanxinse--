# 人审反馈表

状态：`待验证` 本表给用户/人工审片使用，不代表 Codex 已确认审美、动作专业性或业务通过。

## 使用方式

每条候选请填写：

| 字段 | 选项/填写 |
| --- | --- |
| `sample_or_candidate_id` | 对应 CSV 里的 id |
| `human_selection_decision` | keep / package / merge / audio_review / reject |
| `why_human_select_or_reject` | 人工真实原因 |
| `hook_ok` | yes / no / unsure |
| `action_or_semantic_ok` | yes / no / unsure |
| `risk_ok` | yes / no / professional_review_needed |
| `packaging_needed` | none / tts / subtitle / diagram / boundary_extension |
| `priority` | P0 / P1 / P2 / P3 |
| `notes` | 具体修改建议 |

## 人审时必须区分

- `素材值得进池` 不等于 `可以发布`。
- `动作看起来清楚` 不等于 `动作专业性通过`。
- `标题有吸引力` 不等于 `口播/字幕证据成立`。
- `本地导出成功` 不等于 `业务目标通过`。
