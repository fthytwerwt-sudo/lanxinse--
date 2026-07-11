# 动作主题完整链默认路线

状态：`已确认`
生效日期：2026-07-11

## 主路线

完整直播重筛默认按以下顺序执行：

```text
视觉动作主题
-> action_topic_id
-> 完整 ASR 同动作回查
-> 用途 / 问题与回答 / 原因或边界 / 方法 / 动作口令
-> 身体部位、动作名称和跳题冲突检查
-> 本地视频任务组
-> pending_user_review
```

## 动作主题入口

只有视觉证据能够记录动作名称、身体部位、操作方式、起止范围、主体可见性和换动作风险时，才创建动作主题。编号按原片内动作开始时间稳定排序，格式为 `AT<source_id>_<三位序号>`。

## ASR 回查

- 扫描完整 ASR，不使用 150 秒去重。
- 动作名称和别名是主题检索主键；时间距离只能辅助排序。
- 每项证据必须保存原始文本和时间码。
- 多个角色使用同一原始段时，在索引中记录 `shared_source_segment`，不复制假片段。

## 问题问答硬条件

`question_answer_structure` 必须同时存在明确问题原文与时间码、对应回答原文与时间码，并保持同动作或同问题主题。泛化的“动作相关问题”不属于问题证据。没有真实问题时使用 `action_teaching_structure`。

## 确定性冲突闸门

程序必须在视觉模型之后独立检查：

- `body_part_match`
- `action_name_match`
- `problem_evidence_present`
- `purpose_evidence_present`
- `topic_break_present`

身体部位或动作名称不一致、或者存在跳题时，只能进入 `logic_mismatch`。视觉模型不得覆盖该结论。

## 状态边界

- `true_pair_pending_user_review`：完整问答与动作链通过技术和确定性规则，仍待用户人审。
- `action_teaching_group_pending_user_review`：没有伪造问题，动作教学链成立，仍待用户人审。
- `partial_action_task_group`：缺少用途、问题、边界、方法或动作证据。
- `manual_review`：视觉或语义证据不足。
- `logic_mismatch`：存在确定性冲突。

技术生成、本地可播放和 Git 同步均不代表用户人审、审美、动作专业性、健康效果、业务或发布通过。

## 本轮能力边界

- 已验证输入：仅 5 月 13 日直播原片与其本地 ASR 缓存。
- 视觉路线：复用现有视觉动作单元和关键帧；证据不足时才按 `qwen3-vl-plus -> qwen-vl-max` 调用短片关键帧。
- 禁止入口：旧 102 条、第一版真配对结论、本地临时补救视频。
- 未建设：LangGraph、LangChain、runtime、Agent orchestration、RAG、数据库和服务化系统。
- 其他直播批量能力：`待验证`。
