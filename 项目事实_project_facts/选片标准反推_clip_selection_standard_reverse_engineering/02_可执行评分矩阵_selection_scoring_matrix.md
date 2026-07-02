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
