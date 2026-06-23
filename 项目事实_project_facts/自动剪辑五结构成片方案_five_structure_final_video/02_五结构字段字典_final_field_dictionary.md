# 五结构字段字典

状态：`已确认`
用途：统一素材、转写片段、候选片段和剪辑决策之间的字段。

## 1. 主键链路

```text
source_id -> pair_id -> segment_id -> clip_id -> edit_id
```

含义：

- `source_id`：物理素材唯一编号。
- `pair_id`：视频和文本等素材的配对组编号。
- `segment_id`：转写或时间线中的片段编号。
- `clip_id`：候选剪辑片段编号。
- `edit_id`：成片决策编号。

任何阶段缺上游编号，都不得写成可追溯。

## 2. 字段总表

| 字段 | 中文说明 | 必填阶段 | 说明 |
|---|---|---|---|
| `source_id` | 素材唯一编号 | 素材清单 | 每个物理文件一个。 |
| `file_name` | 原始文件名 | 素材清单 | 不改原文件名。 |
| `file_type` | 文件类型 | 素材清单 | 视频 / 文本 / 图片 / 音频 / 其他。 |
| `pair_id` | 配对组编号 | 配对表 | 视频和 txt 的关联组。 |
| `pair_status` | 配对状态 | 配对表 | 已配对 / 缺视频 / 缺文本 / 多候选 / 待人工确认 / 不适用。 |
| `segment_id` | 转写片段编号 | 转写解析 | 来自带时间码转写或人工切分。 |
| `clip_id` | 候选片段编号 | 片段候选 | 从 segment 中筛选出的候选片段。 |
| `edit_id` | 剪辑决策编号 | EDL 草案 | 进入成片大纲后的剪辑决策。 |
| `start_time` | 开始时间 | 转写解析 | 格式建议 `HH:MM:SS.mmm`。 |
| `end_time` | 结束时间 | 转写解析 | 必须晚于 `start_time`。 |
| `original_text` | 原始文本 | 转写解析 | 保留原话，不做事实改写。 |
| `cleaned_text` | 清洗文本 | 转写解析 | 只做可读清洗，不能新增承诺。 |
| `confidence` | 转写置信度 | 转写解析 | 可为空；低置信度必须人工听审。 |
| `timeline_type` | 直播时间线类型 | 时间线解析 | 见枚举。 |
| `structure_type` | 五结构类型 | 五结构映射 | 见枚举。 |
| `selection_reason` | 入选原因 | 片段候选 | 必须能解释为什么进入候选池。 |
| `risk_flag` | 风险标记 | 风险复核 | 如价格、权益、退款、效果承诺等。 |
| `risk_level` | 风险等级 | 风险复核 | `low` / `medium` / `high` / `blocked`。 |
| `business_fact_status` | 业务事实确认状态 | 风险复核 | `待客户确认` / `已确认` / `待验证`。 |
| `needs_manual_check` | 是否需要人工复核 | 全阶段 | `yes` / `no`。高风险默认 `yes`。 |
| `unmapped_reason` | 无法映射原因 | 五结构映射 | `structure_unclear`、`context_missing` 等。 |
| `bridge_subtitle_needed` | 是否需要桥接字幕 | 成片决策 | `yes` / `no`。 |
| `final_video_position` | 成片建议位置 | 成片决策 | opening / body / trust_or_objection / conversion / closing。 |

## 3. timeline_type 枚举

| 值 | 中文说明 |
|---|---|
| `opening_hook` | 开场留人 |
| `course_teaching` | 课程讲解 |
| `pain_amplification` | 痛点放大 |
| `user_interaction` | 用户互动 |
| `comment_response` | 评论回应 |
| `objection_handling` | 异议处理 |
| `case_trust` | 案例信任 |
| `benefit_reminder` | 权益提醒 |
| `price_explanation` | 价格解释 |
| `conversion_push` | 促单转化 |
| `closing` | 收尾 |
| `cold_or_abnormal` | 冷场或异常 |

## 4. structure_type 枚举

| 值 | 中文说明 | 入选判断 |
|---|---|---|
| `traffic_hook` | 引流型结构 | 痛点钩子、结果感、继续观看理由清楚。 |
| `course_teaching` | 课程讲解型结构 | 问题、原因、方法、步骤可独立理解。 |
| `objection_response` | 异议回应型结构 | 回应质疑，有解释和依据，不夸大。 |
| `case_trust` | 案例信任型结构 | 案例背景、变化过程、结果反馈、课程承接清楚。 |
| `conversion_push` | 促单转化型结构 | 权益、适合人群、风险解除、行动提醒合规。 |
| `unmapped_clip` | 无法映射片段 | 不强行塞入五结构。 |

## 5. 风险字段规则

高风险优先于转化价值。

以下情况必须标 `needs_manual_check = yes`：

- 价格、权益、退款、课程交付信息不清。
- 出现效果承诺、夸大收益、虚假稀缺。
- 涉及敏感人群、医疗、教育、资质或强功效表达。
- 片段上下文不足，容易误导。
- 无法判断说话人或转写置信度低。

业务事实未确认时，`business_fact_status` 只能写 `待客户确认` 或 `待验证`。

## 6. unmapped_clip 规则

`unmapped_clip` 不是失败垃圾桶，而是防止强行拼接的安全状态。

以下情况标 `unmapped_clip`：

- 无法判断五结构类型。
- 片段依赖上下文，单独看不成立。
- 风险过高，不适合进入成片。
- 只是互动、铺垫、闲聊或异常段。
- 文件或转写缺时间码，无法稳定定位。
