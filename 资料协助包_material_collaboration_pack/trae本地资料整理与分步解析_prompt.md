# Trae 分步执行 Prompt：直播切片 AI Skill 资料协助包

## 使用方式

请按顺序复制 Prompt 0 到 Prompt 14 到 Trae 执行。

执行原则：

- 只在本地执行。
- 不上传任何文件。
- 不删除任何原始文件。
- 不移动或改名原始文件，除非明确确认。
- 不确定的信息不用硬填。
- 不知道就写“未知”。
- 成片来源不知道就写“待自动匹配”。
- 文件夹分类就是主要标签。
- 正样本文件夹代表希望 AI 学习。
- 负样本文件夹代表不希望 AI 学习。
- 结构判断、敏感风险和学习价值，后续由 AI 项目组解析和复查。
- 自动匹配、结构拆解、AI Skill 稳定性均为待验证能力。
- Prompt 0-7 是资料整理阶段，Prompt 8-14 是 AI 蒸馏解析阶段。
- 没有字幕 / 转写时，不做语义结构解析，统一标记 `blocked_pending_transcript`。
- AI 生成的结构只能作为草稿，必须带 `evidence_text`、`confidence`、`review_status`。

## 信息分层

本资料包采用三层方式：

1. `required_by_file`：通过文件夹分类和文件存在判断，不需要人工解释。
2. `optional_if_known`：知道就填；不知道写“未知”或留空，不阻断上传。
3. `ai_generated_later`：后续由 AI 项目组、Trae 或自动解析流程生成。

不用强行填写不确定的信息。

1. 文件夹分类：
   把文件放进正确文件夹，就是最重要的标签。

2. 自动扫描：
   Trae 只负责扫描文件名、数量、格式、时长、是否有字幕文件等能自动识别的信息。

3. 可选补充：
   私信、咨询、发布效果等，如果知道就填；不知道就写“未知”，不影响上传。

钩子、痛点、卖点、信任背书、异议处理、逼单、适合 AI 学习程度、敏感风险等，不要求配合方填写，后续由 AI 项目组自动解析或复查。

Trae 不要硬解析运营反馈，不要从视频里推断私信、咨询、转化、学习价值或敏感风险。只有在有字幕、转写、备注或明确文本证据时，才能进入 AI 蒸馏解析阶段。

---

## Prompt 0：初始化资料包和目录

```text
你是本地资料整理助手。请只在当前电脑本地执行。

目标：
创建“直播切片 AI Skill 资料协助包”，生成目录、空表格和资料完整度检查入口。

输入：
- 我指定的本地工作目录。
- 本地已有的视频、字幕、转写、业务资料文件夹。

禁止：
- 不上传任何文件。
- 不删除任何原始文件。
- 不移动或改名原始文件，除非我明确确认。
- 不读取账号凭据、登录凭据、浏览器凭据。
- 不要求填写无法确认的运营反馈。
- 不要求填写专业结构分析。

请创建目录：
直播切片AI_Skill资料协助包_日期/
├── 00_说明与清单_notes_manifest/
├── 01_完整直播录屏_6场_raw_livestreams/
│   ├── 效果好_good/
│   ├── 普通_normal/
│   └── 较乱_messy/
├── 02_正样本成片_60条_positive_clips/
├── 03_正样本轻量标注_positive_clip_labels/
├── 04_负样本_不要学习的内容_negative_samples/
├── 05_对标视频_12到20条_reference_videos/
├── 06_字幕与转写_transcripts/
├── 07_业务资料_已脱敏_business_context/
├── 08_盲测直播_2场_blind_test_livestreams/
└── 09_授权与脱敏说明_authorization_desensitization/

请生成文件：
1. 00_说明与清单_notes_manifest/文件清单_file_manifest.csv
2. 00_说明与清单_notes_manifest/上传前检查表_upload_ready_checklist.csv
3. 01_完整直播录屏_6场_raw_livestreams/直播录屏清单_livestream_recording_manifest.csv
4. 03_正样本轻量标注_positive_clip_labels/正样本轻量标注表_positive_clip_labels.csv
5. 04_负样本_不要学习的内容_negative_samples/负样本表_negative_samples.csv
6. 05_对标视频_12到20条_reference_videos/对标视频拆解表_reference_video_breakdown.csv
7. 09_授权与脱敏说明_authorization_desensitization/脱敏检查表_desensitization_checklist.csv
8. 资料完整度检查报告_material_completeness_report.md

输出：
- 已创建的目录清单。
- 已生成的表格清单。
- 还缺哪些资料。

完成标准：
- 目录创建完成。
- 8 个文件已生成。
- 报告里写清当前缺口。
```

---

## Prompt 1：效果好直播扫描 prompt

```text
你是本地直播资料整理助手。请扫描“效果好_good”文件夹中的完整直播。

目标：
记录 2 场效果较好的完整直播的可自动识别信息。文件已经放入效果好文件夹，所以 folder_label 直接写“效果好”。

输入：
- 01_完整直播录屏_6场_raw_livestreams/效果好_good/
- 06_字幕与转写_transcripts/

禁止：
- 不上传文件。
- 不删除、移动、改名原始视频。
- 不要求人工分析专业剪辑结构。
- 不硬判断运营反馈。
- 不推断学习价值或敏感风险。

请填写到 直播录屏清单_livestream_recording_manifest.csv：
- recording_id。
- file_name。
- folder_label：效果好。
- duration_auto：能读取就写时长，无法读取写“待补全”。
- file_format：文件格式。
- has_subtitle_file：是 / 否 / 未知。
- transcript_file：有同名字幕或转写就写文件名，没有写“无”。
- optional_topic_hint：文件名或备注里能看出主题就写，不确定写“未知”。
- optional_notes：可选备注。

输出：
- 扫描到的文件数量。
- 2 场效果好直播记录。
- 缺失字幕或转写的提醒。

完成标准：
- 至少记录 2 场效果好直播；不足时写清缺口。
- 不知道的信息写“未知”或“待补全”。
```

---

## Prompt 2：普通直播扫描 prompt

```text
你是本地直播资料整理助手。请扫描“普通_normal”文件夹中的完整直播。

目标：
记录 2 场普通表现直播的可自动识别信息。文件已经放入普通文件夹，所以 folder_label 直接写“普通”。

输入：
- 01_完整直播录屏_6场_raw_livestreams/普通_normal/
- 06_字幕与转写_transcripts/

禁止：
- 不上传文件。
- 不删除、移动、改名原始视频。
- 不要求人工分析专业剪辑结构。
- 不硬判断运营反馈。
- 不把普通表现写成效果差。

请填写到 直播录屏清单_livestream_recording_manifest.csv：
- recording_id。
- file_name。
- folder_label：普通。
- duration_auto：能读取就写时长，无法读取写“待补全”。
- file_format：文件格式。
- has_subtitle_file：是 / 否 / 未知。
- transcript_file：有同名字幕或转写就写文件名，没有写“无”。
- optional_topic_hint：文件名或备注里能看出主题就写，不确定写“未知”。
- optional_notes：可选备注。

输出：
- 扫描到的文件数量。
- 2 场普通直播记录。
- 缺失字幕或转写的提醒。

完成标准：
- 至少记录 2 场普通直播；不足时写清缺口。
- 不知道的信息写“未知”或“待补全”。
```

---

## Prompt 3：较乱直播扫描 prompt

```text
你是本地直播资料整理助手。请扫描“较乱_messy”文件夹中的完整直播。

目标：
记录 2 场较乱或难度较高直播的可自动识别信息。文件已经放入较乱文件夹，所以 folder_label 直接写“较乱”。

输入：
- 01_完整直播录屏_6场_raw_livestreams/较乱_messy/
- 06_字幕与转写_transcripts/

禁止：
- 不上传文件。
- 不删除、移动、改名原始视频。
- 不要求人工分析专业剪辑结构。
- 不硬判断运营反馈。
- 不把较乱直播直接当成不可用素材。

请填写到 直播录屏清单_livestream_recording_manifest.csv：
- recording_id。
- file_name。
- folder_label：较乱。
- duration_auto：能读取就写时长，无法读取写“待补全”。
- file_format：文件格式。
- has_subtitle_file：是 / 否 / 未知。
- transcript_file：有同名字幕或转写就写文件名，没有写“无”。
- optional_topic_hint：文件名或备注里能看出主题就写，不确定写“未知”。
- optional_notes：可选备注。

输出：
- 扫描到的文件数量。
- 2 场较乱直播记录。
- 缺失字幕或转写的提醒。

完成标准：
- 至少记录 2 场较乱直播；不足时写清缺口。
- 不知道的信息写“未知”或“待补全”。
```

---

## Prompt 4：正样本成片整理 prompt

```text
你是本地成片资料整理助手。请扫描正样本文件夹。

目标：
整理 60 条正样本成片。放进正样本文件夹，就代表希望 AI 学习。

输入：
- 02_正样本成片_60条_positive_clips/
- 如有备注文件，可读取其中明确写出的线索。

禁止：
- 不上传文件。
- 不删除、移动、改名原始视频。
- 不要求人工填写专业剪辑结构。
- 不要求提前知道成片来自哪场直播。
- 不强制填写私信、咨询或发布效果。
- 不推断敏感风险或学习程度。

请填写到 正样本轻量标注表_positive_clip_labels.csv：
- clip_id。
- clip_file。
- folder_label：正样本。
- known_source_status：知道 / 不知道 / 不确定。
- possible_raw_recording：知道就写；不知道写“待自动匹配”。
- optional_manual_hint：可选线索，主题 / 话术 / 画面，不知道写“未知”。
- optional_result_hint：可选效果线索，私信多 / 反馈好 / 团队认可 / 未知。
- should_ai_learn：默认“是”，因为已放入正样本文件夹。
- notes：可选备注。

输出：
- 扫描到的正样本数量。
- 60 条正样本记录；不足时写清缺口。
- 哪些缺少来源线索，需要后续自动匹配。

完成标准：
- 正样本目标为 60 条。
- 所有不知道来源的记录写“待自动匹配”。
- 不出现专业剪辑结构分析。
```

---

## Prompt 5：负样本整理 prompt

```text
你是本地边界样本整理助手。请扫描负样本文件夹。

目标：
整理 30-60 条不希望 AI 学习的内容。放进负样本文件夹，就代表不希望 AI 学习。

输入：
- 04_负样本_不要学习的内容_negative_samples/
- 如有备注文件，可读取其中明确写出的原因。

禁止：
- 不上传文件。
- 不删除、移动、改名原始视频。
- 不要求人工填写专业剪辑结构。
- 不强制填写具体原因。
- 不把负样本理解为差评素材。

请填写到 负样本表_negative_samples.csv：
- negative_id。
- material_file_or_hint：文件名或时间线索。
- folder_label：负样本。
- negative_reason_optional：可选原因，私信少 / 无转化 / 太水 / 重复 / 跑题 / 风险 / 画面声音差 / 未知。
- confirmed_negative：默认“是”，因为已放入负样本文件夹。
- notes：可选备注。

输出：
- 扫描到的负样本数量。
- 30-60 条负样本记录；不足时写清缺口。
- 哪些只是线索，后续需要确认。

完成标准：
- 至少 30 条 / 组，最多建议 60 条 / 组。
- 正样本和负样本分开放。
- 不出现专业剪辑结构分析。
```

---

## Prompt 6：对标视频整理 prompt

```text
你是本地对标资料整理助手。请扫描对标视频文件夹。

目标：
整理 12-20 条对标视频，只记录可选参考方向，不复制对方素材。

输入：
- 05_对标视频_12到20条_reference_videos/
- 如有来源平台、类型、备注，可一起记录。

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不复制对方文案原句。
- 不要求人工分析专业剪辑结构。
- 不把未授权素材当作可复用素材。

请填写到 对标视频拆解表_reference_video_breakdown.csv：
- reference_id。
- reference_file。
- folder_label：对标视频。
- optional_learn_what：可选，节奏 / 字幕 / 包装 / 结构 / 未知。
- optional_do_not_copy：可选，人物 / 品牌 / 文案原句 / UI / 未知。
- notes：可选备注。

输出：
- 扫描到的对标视频数量。
- 12-20 条对标视频记录；不足时写清缺口。
- 哪些只可参考、不可复制。

完成标准：
- 至少 12 条，最多建议 20 条。
- 不知道的信息写“未知”。
```

---

## Prompt 7：上传前检查 prompt

```text
你是本地资料完整度检查助手。请检查资料协助包是否可以上传云盘。

目标：
检查 6 场直播、60 条正样本、30-60 条负样本、12-20 条对标、2 场盲测是否齐全；检查目录结构、字幕情况、脱敏状态、未知比例和需要后续复查的内容。

输入：
- 直播切片AI_Skill资料协助包_日期/
- 所有已生成表格。
- 本地文件数量统计。

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不把未脱敏资料写入可外发报告。
- 不把未知信息当作上传失败。
- 不硬解析运营反馈。

请检查：
- 数量是否够。
- 文件夹是否正确。
- 表格是否生成。
- 字段未知比例。
- 是否有字幕文件。
- 是否有脱敏说明。
- 哪些内容需要后续 AI 项目组复查。
- 是否有 6 场完整直播。
- 是否覆盖 2 场效果好、2 场普通、2 场较乱。
- 是否有 60 条正样本成片。
- 是否有 30-60 条负样本。
- 是否有 12-20 条对标视频。
- 是否有 2 场盲测直播。

请输出 资料完整度检查报告_material_completeness_report.md：
1. 当前资料是否齐全。
2. 已有数量。
3. 缺少数量。
4. 未知或待自动匹配的比例。
5. 需要补的文件。
6. 需要脱敏或授权复查的内容。
7. 需要后续 AI 项目组复查的内容。
8. 可以上传云盘的目录。
9. 上传后需要发送：云盘链接、提取码、文件夹截图、文件清单、已脱敏确认、兜底样本留存确认。

完成标准：
- 报告明确写出“齐全 / 不齐全”。
- 不齐全时列出下一步需要补什么。
- 未知信息不阻断上传。
- 不上传任何文件。
```

---

## Prompt 8：字幕 / 转写可用性检查

```text
你是本地 AI 蒸馏准备检查助手。请检查当前资料是否具备语义解析条件。

目标：
检查直播、正样本、负样本、对标视频是否有字幕 / 转写 / 备注等文本证据，决定哪些内容可以进入 AI 蒸馏解析。

输入：
- 06_字幕与转写_transcripts/
- 00_说明与清单_notes_manifest/文件清单_file_manifest.csv
- 01_完整直播录屏_6场_raw_livestreams/直播录屏清单_livestream_recording_manifest.csv
- 03_正样本轻量标注_positive_clip_labels/正样本轻量标注表_positive_clip_labels.csv
- 04_负样本_不要学习的内容_negative_samples/负样本表_negative_samples.csv
- 05_对标视频_12到20条_reference_videos/对标视频拆解表_reference_video_breakdown.csv

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不读取账号凭据、登录凭据、浏览器凭据。
- 没有字幕 / 转写 / 备注证据时，不做语义结构解析。
- 不把文件名猜测写成内容理解。

请输出 字幕转写可用性检查_transcript_readiness_report.md：
1. 哪些直播有转写。
2. 哪些成片有字幕。
3. 哪些负样本有字幕、转写或备注证据。
4. 哪些对标视频有字幕、转写或备注证据。
5. 哪些资料可以进入 Prompt 9-14。
6. 哪些资料必须标 `blocked_pending_transcript`。
7. 哪些资料只有文件名，只能保留在文件清单，不进入语义蒸馏。

判断规则：
- 有字幕 / 转写 / 备注证据，才可以进入 AI 蒸馏解析。
- 没有字幕 / 转写，只能做文件整理，不能做语义结构解析。
- 缺转写的资料统一标 `blocked_pending_transcript（缺转写，等待补转写）`。
- 不确定时写“待确认”，不要写成已确认。

完成标准：
- 报告列出可解析、不可解析、待补转写三类。
- 每条不可解析资料都有原因。
- 不生成任何语义结构草稿。
```

---

## Prompt 9：直播时间线解析

```text
你是直播内容蒸馏助手。请只基于已有字幕 / 转写，拆出 6 场直播的时间线段落。

目标：
从直播字幕 / 转写中生成可供 AI Skill 蒸馏使用的时间线草稿。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 直播录屏清单_livestream_recording_manifest.csv
- 06_字幕与转写_transcripts/ 中对应直播的字幕或转写文件

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 没有字幕 / 转写的直播，必须写 `blocked_pending_transcript`，不得硬解析。
- 不把 AI 初判写成最终结论。
- 不生成没有 evidence_text 的判断。

请输出 直播时间线解析表_live_timeline_analysis.csv，字段为：
- recording_id
- segment_id
- start_timecode
- end_timecode
- transcript_text
- topic_summary
- segment_type_ai_draft（教学 / 卖点 / 互动 / 闲聊 / 异议处理 / 逼单 / 跑题 / 风险 / 未知）
- value_signal_ai_draft（高 / 中 / 低 / 不确定）
- risk_signal_ai_draft（有 / 无 / 不确定）
- evidence_text
- confidence（高 / 中 / 低）
- review_status（待确认）

解析规则：
- 按自然话题、明显转场、行动引导或语义变化切段。
- 每段必须保留 transcript_text。
- 每个 AI 判断必须有 evidence_text。
- evidence_text 必须来自字幕 / 转写原文，不得编造。
- 置信度低、证据短、风险不确定的段落进入人工复核清单。
- 所有 review_status 默认写“待确认”。

完成标准：
- 可解析直播生成时间线草稿。
- 不可解析直播标 `blocked_pending_transcript`。
- 每条记录都有 evidence_text、confidence、review_status。
```

---

## Prompt 10：正样本 AI 结构草稿

```text
你是正样本蒸馏助手。请只基于正样本成片字幕 / 转写 / 备注证据，生成 AI 结构草稿。

目标：
对 60 条正样本成片生成可复核的结构草稿，帮助 AI 项目组理解“为什么希望 AI 学”。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 正样本轻量标注表_positive_clip_labels.csv
- 02_正样本成片_60条_positive_clips/
- 06_字幕与转写_transcripts/ 中对应成片字幕或转写

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求配合方填写钩子、痛点、卖点、信任背书、异议处理或行动引导。
- 没有字幕 / 转写的成片，必须写 `blocked_pending_transcript`。
- 不把 AI 草稿写成最终判断。
- 不生成没有 evidence_text 的结构字段。

请输出 正样本AI结构草稿_positive_ai_structure_draft.csv，字段为：
- clip_id
- clip_file
- transcript_available
- opening_text
- main_message_ai_draft
- hook_ai_draft
- pain_point_ai_draft
- value_point_ai_draft
- trust_signal_ai_draft
- objection_or_cta_ai_draft
- why_ai_thinks_should_learn
- evidence_text
- confidence（高 / 中 / 低）
- review_status（待确认）

解析规则：
- 这些字段全部由 AI 生成，不要求配合方填写。
- opening_text 必须来自字幕 / 转写开头原文。
- hook、pain_point、value_point、trust_signal、objection_or_cta 都必须基于 evidence_text。
- 没有证据的字段写“未知”，不要硬补。
- why_ai_thinks_should_learn 只能写“AI 草稿原因”，不得写成已确认结论。
- 所有 review_status 默认写“待确认”。

完成标准：
- 有字幕 / 转写的正样本生成结构草稿。
- 缺字幕 / 转写的正样本标 `blocked_pending_transcript`。
- 每条记录都有 evidence_text、confidence、review_status。
```

---

## Prompt 11：负样本边界草稿

```text
你是负样本边界蒸馏助手。请只基于负样本文本、备注或片段上下文，生成“不应该学什么”的边界草稿。

目标：
把负样本整理成 AI Skill 的边界学习材料，帮助后续减少误切、乱切、切废话。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 负样本表_negative_samples.csv
- 04_负样本_不要学习的内容_negative_samples/
- 06_字幕与转写_transcripts/ 中对应字幕或转写
- 如有人工备注，可作为 evidence_text

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不把负样本写成差评素材。
- 没有字幕 / 转写 / 备注证据时，不要强行判断原因。
- 不生成没有 evidence_text 的边界判断。

请输出 负样本边界草稿_negative_boundary_draft.csv，字段为：
- negative_id
- material_file_or_hint
- transcript_available
- do_not_learn_pattern_ai_draft
- negative_reason_ai_draft（铺垫长 / 重复 / 跑题 / 低价值 / 风险 / 画面声音差 / 不完整 / 未知）
- what_ai_should_avoid
- evidence_text
- confidence（高 / 中 / 低）
- review_status（待确认）

解析规则：
- 负样本是边界样本，不是差评素材。
- 只有 evidence_text 能支持时，才写具体边界草稿。
- 只有文件名时，negative_reason_ai_draft 写“未知”，review_status 写“待确认”。
- 低置信度、风险不确定、证据不足的内容进入人工复核清单。

完成标准：
- 可解析负样本生成边界草稿。
- 缺证据负样本标 `blocked_pending_transcript` 或“缺证据待确认”。
- 每条记录都有 evidence_text、confidence、review_status。
```

---

## Prompt 12：对标视频学习点草稿

```text
你是对标视频蒸馏助手。请只基于对标视频字幕、转写、备注或可读取文本，提取可学习点和不能复制点。

目标：
把对标视频转成“学习方法，不复制素材”的草稿清单。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 对标视频拆解表_reference_video_breakdown.csv
- 05_对标视频_12到20条_reference_videos/
- 06_字幕与转写_transcripts/ 中对应字幕或转写
- 如有人工备注，可作为证据

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不复制对方文案原句作为可直接复用内容。
- 不把人物、品牌、UI、未授权素材写成可复制资产。
- 没有证据就写“未知”，不要硬分析。

请输出 对标视频学习点草稿_reference_learning_points_draft.csv，字段为：
- reference_id
- reference_file
- transcript_available
- learnable_layer_ai_draft（节奏 / 字幕 / 结构 / 包装 / 开头方式 / 行动引导 / 未知）
- do_not_copy_ai_draft（人物 / 品牌 / 文案原句 / UI / 未授权素材 / 未知）
- reference_pattern_summary
- evidence_text
- confidence（高 / 中 / 低）
- review_status（待确认）

解析规则：
- 对标只学习方法，不复制素材。
- reference_pattern_summary 要写成方法摘要，不要写成照搬指令。
- evidence_text 必须来自字幕、转写或备注。
- 低置信度进入人工复核清单。

完成标准：
- 可解析对标视频生成学习点草稿。
- 缺证据对标视频标 `blocked_pending_transcript` 或“未知”。
- 每条记录都有 evidence_text、confidence、review_status。
```

---

## Prompt 13：人工复核清单生成

```text
你是 AI 蒸馏复核队列整理助手。请把所有低置信度、缺证据、待自动匹配、敏感风险不确定的项汇总给人工快速确认。

目标：
让人工只确认 AI 草稿，不从 0 填写专业结构。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 直播时间线解析表_live_timeline_analysis.csv
- 正样本AI结构草稿_positive_ai_structure_draft.csv
- 负样本边界草稿_negative_boundary_draft.csv
- 对标视频学习点草稿_reference_learning_points_draft.csv

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求人工从 0 写钩子、痛点、卖点或结构分析。
- 不把 AI 草稿写成已确认。

请输出 人工复核清单_human_review_queue.csv，字段为：
- review_id
- source_file
- source_type（直播 / 正样本 / 负样本 / 对标）
- issue_type（低置信度 / 缺字幕 / 待自动匹配 / 风险不确定 / 结构不确定）
- ai_draft_summary
- evidence_text
- confidence（高 / 中 / 低）
- suggested_action（确认 / 修改 / 忽略 / 补资料）
- review_status（待确认）

生成规则：
- confidence 为“低”的记录必须进入复核清单。
- evidence_text 为空或不足的记录必须进入复核清单。
- 含 `blocked_pending_transcript` 的记录必须进入复核清单。
- 待自动匹配来源的正样本必须进入复核清单。
- 每条复核任务必须短，方便快速确认。

完成标准：
- 人工复核清单只包含需要确认的事项。
- 每条都有 evidence_text、confidence、suggested_action 和 review_status。
- 人工只确认，不从 0 填。
```

---

## Prompt 14：AI 蒸馏包汇总报告

```text
你是 AI Skill 蒸馏准备报告助手。请汇总 Prompt 8-13 的结果，生成给 AI 项目组看的蒸馏准备报告。

目标：
判断当前资料是否足够进入第一轮 AI Skill 蒸馏，并列出缺口和下一步。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 文件清单_file_manifest.csv
- 上传前检查表_upload_ready_checklist.csv
- 直播时间线解析表_live_timeline_analysis.csv
- 正样本AI结构草稿_positive_ai_structure_draft.csv
- 负样本边界草稿_negative_boundary_draft.csv
- 对标视频学习点草稿_reference_learning_points_draft.csv
- 人工复核清单_human_review_queue.csv

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不把 AI Skill 稳定性写成已确认。
- 不把 AI 草稿写成已确认事实。
- 不承诺可以直接训练或自动剪辑。

请输出 AI蒸馏包汇总_report.md，必须包含：
1. 资料数量是否齐。
2. 字幕 / 转写是否够。
3. 正样本可解析数量。
4. 负样本可解析数量。
5. 对标可解析数量。
6. `blocked_pending_transcript` 数量。
7. 低置信度数量。
8. 待自动匹配数量。
9. 最适合进入第一轮蒸馏的样本清单。
10. 暂不适合进入蒸馏的样本清单。
11. 下一步需要补什么。

报告规则：
- 用“已确认 / 待验证 / 待确认 / blocked_pending_transcript”标状态。
- 只汇总 AI 草稿和证据，不写最终业务结论。
- 所有建议都必须能追溯到 evidence_text 或缺失原因。
- 如缺少字幕 / 转写，优先建议补转写，不要硬解析。

完成标准：
- 报告能直接交给 AI 项目组判断蒸馏准备情况。
- 报告清楚区分可进入蒸馏、暂不适合蒸馏、需要人工复核三类。
- 不把待验证能力写成已确认。
```
