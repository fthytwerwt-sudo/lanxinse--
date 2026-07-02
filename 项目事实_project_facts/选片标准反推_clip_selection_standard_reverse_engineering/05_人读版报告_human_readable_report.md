# 选片标准总报告

状态：`已确认` 本轮已生成选片标准、评分矩阵、运行字段和人审反馈表；`待验证` 用户人审是否认可、标准能否稳定用于新直播素材。

## 本轮素材范围

| 项目 | 结果 |
| --- | ---: |
| AI需要的成片非 `成品/` 有效视频 | 165 |
| 已排除 `成品/` 视频 | 757 |
| 跳过 AppleDouble 隐藏视频文件 | 1 |
| 复用前序 AI 成片解析 | 100 |
| 仅标题/元数据层待复核 | 65 |
| C9623 候选 | 43 |
| C9623 本地导出索引 | 43 |
| C9623 实际导出视频 | 20 |
| C9623 人工包装建议 | 20 |
| 弃用/弱样本原因 | 106 |

## 核心结论

1. 别人选片通常不是因为“画面动了”，而是因为开头能指向明确人群/痛点，随后能用动作、字幕、口播或道具兑现。
2. 当前项目应同时保留五条路线：原生口播、动作教学再包装、相邻窗口合并、待音频复核、直接淘汰。
3. 动作教学再包装的价值来自“动作可解释 + 问题可前置 + TTS/字幕能补齐教学 + 风险可控”，不是单纯有动作。
4. 只有静态画面、零散手势、重复动作、缺上下文且不可补、强健康/疗效承诺的片段，不应优先进入剪辑池。
5. 下一轮 Codex 必须用 `viewer_problem_value / hook_strength / visual_action_value / semantic_completeness / problem_action_bridge / repackaging_cost / risk_deduction` 等字段判断。
6. 审美、动作专业性、健康表达、业务转化仍全部 `待验证`。
7. `已确认`：C9623 当前没有 `qualified_native` 原生切片候选，不能把本地导出的人审素材写成原生切片已成立。

## 选片标准

## 标准 A：原生口播切片选片标准

适用条件：直播里本身有完整表达，能较少人工补写。

通过条件：
- 开头 0-8 秒有观看理由
- 口播/字幕说明完整
- 中段兑现问题或方法
- 结尾自然收束
- 画面支撑口播

失败条件：
- 有话题但没有方法
- 只有姿态没有语义
- 结尾突然断掉
- 需要大量补写才成立

淘汰条件：
- 口播不可确认且画面无动作价值
- 健康/业务风险无法降级表达

建议字段：`semantic_completeness`, `hook_strength`, `middle_delivery`, `ending_closure`, `visual_supports_semantic`
## 标准 B：动作教学再包装选片标准

适用条件：直播画面有动作或道具价值，但需要 TTS/字幕/问题前置包装。

通过条件：
- 动作清楚
- 动作循环或关键步骤可见
- 小白能看出方向
- 可补明确问题
- 字幕能标发力点/禁忌/次数

失败条件：
- 动作存在但看不懂目标
- 只有重复摆动
- 道具用途不明
- 包装后仍无法解释价值

淘汰条件：
- 动作风险高且无专业边界
- 视觉证据不足以承载教学

建议字段：`visual_action_value`, `teaching_action_value`, `repackaging_value_score`, `repackaging_cost`, `risk_deduction`
## 标准 C：相邻窗口合并选片标准

适用条件：单窗口不完整，但前后窗口能组成同一问题链路。

通过条件：
- 前窗口有问题引入
- 当前窗口有方法/动作
- 后窗口有总结/收束
- 合并后仍是同一问题
- 合并成本可控

失败条件：
- 前后窗口主题漂移
- 只靠拼接仍缺方法
- 合并后过长或节奏散

淘汰条件：
- 三个窗口合并后仍没有观看理由或教学交付

建议字段：`need_merge_previous`, `need_merge_next`, `adjacent_merge_score`, `semantic_topic_consistency`, `editing_feasibility`
## 标准 D：待音频复核选片标准

适用条件：画面有价值线索，但口播/字幕证据缺失。

通过条件：
- 画面值得听审
- 可能有高价值口播
- 有动作/道具/表情/手势线索
- 听审能决定去留

失败条件：
- 画面线索弱
- 无动作也无互动
- 无法推断可能问题

淘汰条件：
- 听完口播仍无问题、方法、风险说明

建议字段：`audio_transcript_status`, `visual_lead_strength`, `possible_problem_signal`, `listen_review_priority`, `fallback_reject_rule`
## 标准 E：直接淘汰标准

适用条件：不值得剪、不值得包装、不值得听审。

通过条件：
- 动作不清
- 无信息增量
- 缺上下文且不可补
- 风险过高
- 只有静态画面或重复手势
- 包装成本大于价值

失败条件：
- 如果有相邻窗口/音频可救回，不应直接淘汰，应转 C/D

淘汰条件：
- 满足任一硬淘汰条件且没有救回证据

建议字段：`reject_reason`, `rescue_level`, `evidence_missing`, `risk_deduction`, `manual_packaging_cost`


## 本轮边界

- 没有新增外部 API 调用。
- 没有提交视频、音频、关键帧、contact sheet 或 API 原始 JSON。
- 没有把 C9623 本地导出写成发布通过。
- 没有把正样本规律写成绝对正确，只作为反推参考。
- 没有把标题层推断写成视觉/口播内容已确认。


# 可执行评分矩阵

状态：`已确认` 本矩阵用于下一轮选片，不代表任何片段已发布通过。

| 字段 | 中文含义 | 评分范围 | 高分表现 | 低分表现 | 直接淘汰条件 | 示例 |
| --- | --- | --- | --- | --- | --- | --- |
| `viewer_problem_value` | 观众问题价值 | 0-10 | 具体痛点/人群/场景明确 | 泛愿望或无问题 | 无可识别观看理由 | 漏尿尴尬、小肚子凸、盆底松 |
| `hook_strength` | 开头钩子强度 | 0-10 | 0-3 秒建立问题或误区 | 开头只有寒暄/空镜/口号 | 8 秒内仍无观看理由 | 70%女性中招的误区 |
| `visual_action_value` | 画面动作价值 | 0-10 | 动作起止/方向/道具关系清楚 | 静态或零散手势 | 无动作且无语义 | 瑜伽小球动作循环可见 |
| `teaching_action_value` | 教学动作价值 | 0-10 | 能标步骤、发力点、禁忌、次数 | 只看见动但不知道练什么 | 动作风险高且不可解释 | 臀桥呼吸可拆成步骤 |
| `semantic_completeness` | 语义完整度 | 0-10 | 开头-中段-结尾闭合 | 缺开头/中段/结尾 | 无口播/字幕且画面不可解释 | 问题提出后有方法和收束 |
| `problem_action_bridge` | 问题动作桥接 | 0-10 | 0-6 秒进入动作/方法 | 问题和动作断裂 | 没有桥接证据 | 先点痛点，马上演示动作 |
| `editing_feasibility` | 剪辑可行性 | 0-10 | 起止点清楚、可粗剪、时长可控 | 需要大量补拍/补写 | 合并后仍不可剪 | 单动作 30-60 秒或可合并窗口 |
| `repackaging_cost` | 人工包装成本 | 0-10 倒扣 | 低成本补 TTS/字幕即可 | 要重写结构、重配图、重审风险 | 成本大于价值 | 动作清楚但缺问题前置 |
| `risk_deduction` | 风险扣分 | 0-20 扣分 | 风险可通过提示降级 | 疗效/健康承诺强 | 存在不可控健康/商业风险 | 治疗脱垂、越练越紧需谨慎 |
| `selection_priority` | 选片优先级 | P0-P3 | 高问题价值+低风险+低包装成本 | 仅单一维度高 | 淘汰 | P0 原生/P1 再包装/P2 听审/P3 淘汰 |

## 计算建议

- `selection_score = viewer_problem_value + hook_strength + visual_action_value + teaching_action_value + semantic_completeness + problem_action_bridge + editing_feasibility - repackaging_cost - risk_deduction`。
- `P0_native`：语义完整度和桥接高，风险低，可直接粗剪成人审片段。
- `P1_repackaging`：视觉动作价值高，但语义/开头缺口可通过 TTS/字幕低成本补齐。
- `P2_audio_review`：画面线索存在，但语义证据缺失，必须先听审。
- `P3_reject`：无问题、无动作、无语义、风险高或包装成本大于价值。


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
