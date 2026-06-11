# Trae 分步执行 Prompt：直播切片 AI Skill 资料协助包

## 使用方式

请按顺序复制 Prompt 0 到 Prompt 15 到 Trae 执行。

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
- Prompt 0 到 Prompt 7 负责文件归类、数量扫描、完整度检查和上传前整理。
- Prompt 8 到 Prompt 15 负责 AI 自动解析、自动生成草稿、复核清单和验收标准。
- 没有字幕 / 转写时，不做语义结构解析，统一标记 `blocked_pending_transcript`。
- 没有画面抽帧时，不判断裁切、美颜或画面质感，统一标记 `blocked_pending_frame_sample`。
- 没有音频可读信息时，不判断音频质量，统一标记 `blocked_pending_audio_probe`。
- 横向能力字段不是人工填写项，由 AI / Trae 自动解析生成草稿，不由配合方填写。
- AI 生成的结构只能作为草稿，必须带 `evidence`、`confidence`、`review_status`。

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

Trae 不要硬解析运营反馈，不要从视频里推断私信、咨询、转化、学习价值或敏感风险。只有在有字幕、转写、备注、画面抽帧、音频探针或其他明确证据时，才能进入 AI 自动解析阶段。

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
你是本地自动解析准备检查助手。请检查哪些素材具备语义解析条件。

目标：
确认直播、正样本、负样本、对标视频是否有字幕 / 转写 / 备注等文本证据，决定哪些内容可以进入后续自动解析。

输入：
- 06_字幕与转写_transcripts/
- 文件清单_file_manifest.csv
- 直播录屏清单_livestream_recording_manifest.csv
- 正样本轻量标注表_positive_clip_labels.csv
- 负样本表_negative_samples.csv
- 对标视频拆解表_reference_video_breakdown.csv

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不读取账号凭据、登录凭据、浏览器凭据。
- 没有字幕 / 转写 / 备注证据时，不做语义结构解析。
- 不因为缺字幕就删除资料。

请输出 字幕转写可用性检查_transcript_readiness_report.md：
1. 哪些直播有转写。
2. 哪些成片有字幕。
3. 哪些负样本有字幕、转写或备注。
4. 哪些对标视频有字幕、转写或备注。
5. 哪些资料可以进入语义解析。
6. 哪些资料必须标 `blocked_pending_transcript`。
7. 哪些资料只有文件名，只能保留在文件清单，不进入语义解析。

规则：
- 有字幕 / 转写：进入语义解析。
- 没有字幕 / 转写：标 `blocked_pending_transcript`。
- 不确定时写“待确认”，不要写成已确认。

完成标准：
- 报告列出可解析、不可解析、待补转写三类。
- 不生成任何语义结构草稿。
```

---

## Prompt 9：字幕样式自动解析

```text
你是字幕样式自动解析助手。请从成片、对标视频、截图或字幕文件中解析字幕呈现方式。

目标：
生成字幕样式草稿，供 AI 项目组复核；不要让配合方填写字幕样式。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 02_正样本成片_60条_positive_clips/
- 05_对标视频_12到20条_reference_videos/
- 06_字幕与转写_transcripts/
- 如已有截图或抽帧，可作为证据

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求配合方填写字幕位置、颜色、大小、重点词或行数。
- 没有字幕、截图或可读画面证据时，不硬判断字幕样式。

请输出 字幕样式解析表_subtitle_style_analysis.csv，字段为：
- source_id
- source_file
- subtitle_available
- subtitle_position_ai
- subtitle_size_ai
- subtitle_color_ai
- highlight_words_ai
- max_lines_ai
- readability_ai（高 / 中 / 低 / 不确定）
- blocks_face_or_product_ai
- evidence（截图 / 时间点 / 字幕片段）
- confidence（高 / 中 / 低）
- review_status（待确认）

规则：
- 所有字段都是 AI 自动解析草稿。
- evidence 必须写清来自截图、时间点或字幕片段。
- 没有证据写“待确认”，不要补想象。
- 低置信度进入人工复核清单。
```

---

## Prompt 10：画面裁切 / 美颜 / 视觉质感自动解析

```text
你是视觉横向能力自动解析助手。请从视频抽帧或截图中解析画面裁切、美颜、滤镜、直播切边和视觉质感。

目标：
生成画面裁切和美颜滤镜草稿，供 AI 项目组复核；不要让配合方填写美颜参数或裁切判断。

输入：
- 文件清单_file_manifest.csv
- 直播录屏清单_livestream_recording_manifest.csv
- 正样本轻量标注表_positive_clip_labels.csv
- 对标视频拆解表_reference_video_breakdown.csv
- 视频抽帧、截图或可读画面证据

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求配合方填写画面裁切、美颜、滤镜、灯光或质感判断。
- 没有画面抽帧或截图时，不判断裁切、美颜或画面质感。

请输出 画面裁切解析表_visual_crop_analysis.csv，字段为：
- source_id
- source_file
- frame_sample_timecode
- aspect_ratio_ai
- face_position_ai
- product_position_ai
- comment_area_visible_ai
- crop_safe_area_ai
- black_border_or_ui_ai
- recommended_crop_ai
- evidence
- confidence
- review_status

请输出 美颜滤镜参考表_beauty_filter_reference.csv，字段为：
- source_id
- source_file
- skin_smoothing_ai
- skin_tone_ai
- filter_style_ai
- lighting_ai
- over_beauty_risk_ai
- keep_or_adjust_ai
- evidence
- confidence
- review_status

规则：
- 只输出 AI 草稿。
- 不要求配合方给美颜参数。
- 无法抽帧则标 `blocked_pending_frame_sample`。
- 低置信度进入人工复核清单。
```

---

## Prompt 11：音频质量自动解析

```text
你是音频质量自动解析助手。请从音频或视频中检查声音质量，判断是否适合直接切片。

目标：
生成音频质量草稿，供 AI 项目组复核；不要让配合方填写音频质量判断。

输入：
- 文件清单_file_manifest.csv
- 直播录屏清单_livestream_recording_manifest.csv
- 正样本轻量标注表_positive_clip_labels.csv
- 负样本表_negative_samples.csv
- 视频或音频可读信息

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求配合方填写音量、噪音、人声清晰度或敏感口播判断。
- 无法分析音频时，不硬写音频质量。

请输出 音频质量检查表_audio_quality_check.csv，字段为：
- source_id
- source_file
- audio_available
- volume_level_ai（高 / 中 / 低 / 不确定）
- noise_level_ai（高 / 中 / 低 / 不确定）
- speech_clarity_ai
- multiple_speakers_ai
- music_or_background_ai
- sensitive_audio_risk_ai
- publish_ready_audio_ai
- evidence
- confidence
- review_status

规则：
- 无法分析音频则标 `blocked_pending_audio_probe`。
- 敏感风险只标待确认，不写已确认。
- 低置信度进入人工复核清单。
```

---

## Prompt 12：切片边界自动解析

```text
你是切片边界自动解析助手。请从正样本成片、原直播匹配结果、字幕 / 转写中反推起止点边界。

目标：
生成切片边界草稿，供 AI 项目组复核；不要让配合方填写起止点、前后舍弃原因或边界风险。

输入：
- 正样本轻量标注表_positive_clip_labels.csv
- 直播录屏清单_livestream_recording_manifest.csv
- 字幕转写可用性检查_transcript_readiness_report.md
- 成片字幕 / 直播转写 / 匹配结果

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 没有匹配原直播时，不生成边界结论。
- 不把低置信度边界写成已确认。

请输出 切片边界草稿_clip_boundary_draft.csv，字段为：
- clip_id
- clip_file
- matched_recording_id
- matched_status（已匹配 / 待自动匹配 / 低置信度）
- start_timecode_ai
- end_timecode_ai
- start_boundary_reason_ai
- end_boundary_reason_ai
- before_discard_reason_ai
- after_discard_reason_ai
- boundary_risk_ai
- evidence
- confidence
- review_status

规则：
- 没有匹配原直播，不生成边界结论，只标待自动匹配。
- 边界理由必须有证据。
- 低置信度进入人工复核清单。
```

---

## Prompt 13：正负样本自动结构与边界对照

```text
你是正负样本对照自动解析助手。请自动生成正样本结构草稿、负样本边界草稿和正负样本对照。

目标：
把“希望 AI 学什么”和“不希望 AI 学什么”转成可复核的规则草稿；不要让配合方填写专业结构判断。

输入：
- 正样本轻量标注表_positive_clip_labels.csv
- 负样本表_negative_samples.csv
- 字幕转写可用性检查_transcript_readiness_report.md
- 成片字幕、直播转写、负样本备注或其他证据

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不要求配合方填写钩子、痛点、卖点、信任背书、异议处理、逼单。
- 没有证据时，不硬写正负对照规则。

请输出 正样本AI结构草稿_positive_ai_structure_draft.csv，字段为：
- clip_id
- main_message_ai
- hook_ai
- pain_point_ai
- value_point_ai
- trust_signal_ai
- objection_or_cta_ai
- why_should_learn_ai
- evidence
- confidence
- review_status

请输出 负样本边界草稿_negative_boundary_draft.csv，字段为：
- negative_id
- do_not_learn_pattern_ai
- negative_reason_ai
- what_ai_should_avoid
- evidence
- confidence
- review_status

请输出 正负样本对照表_positive_negative_comparison.csv，字段为：
- comparison_id
- positive_clip_id
- negative_id
- comparison_dimension（开头 / 节奏 / 信息密度 / 画面 / 转化 / 风险）
- positive_pattern_ai
- negative_pattern_ai
- rule_draft_ai
- evidence
- confidence
- review_status

规则：
- 这些都是 AI 草稿。
- 不要求配合方填写。
- 低置信度进入人工复核清单。
```

---

## Prompt 14：对标视频分层拆解

```text
你是对标视频分层拆解助手。请把对标视频拆成“学哪一层 / 不学哪一层”。

目标：
生成对标视频分层拆解草稿，只学习方法，不复制素材。

输入：
- 对标视频拆解表_reference_video_breakdown.csv
- 05_对标视频_12到20条_reference_videos/
- 06_字幕与转写_transcripts/
- 对标视频截图、抽帧、字幕或备注

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不复制人物、品牌、文案原句、UI 或未授权素材。
- 没有证据就写“待确认”，不要硬分析。

请输出 对标视频分层拆解表_reference_layer_breakdown.csv，字段为：
- reference_id
- reference_file
- learn_subtitle_ai
- learn_rhythm_ai
- learn_crop_ai
- learn_hook_ai
- learn_packaging_ai
- learn_cta_ai
- do_not_copy_person_ai
- do_not_copy_brand_ai
- do_not_copy_script_ai
- do_not_copy_ui_ai
- evidence
- confidence
- review_status

规则：
- 只学习方法，不复制素材。
- 不确定就标待确认。
- 低置信度进入人工复核清单。
```

---

## Prompt 15：人工复核清单与 AI Skill 验收报告

```text
你是自动解析复核与验收标准整理助手。请汇总所有低置信度、缺证据、待匹配、风险项，并生成 AI Skill 验收标准草稿。

目标：
让人工只复核 AI 草稿，不从 0 填写横向能力字段；同时给 AI 项目组一份可执行的验收标准草稿。

输入：
- 字幕转写可用性检查_transcript_readiness_report.md
- 字幕样式解析表_subtitle_style_analysis.csv
- 画面裁切解析表_visual_crop_analysis.csv
- 美颜滤镜参考表_beauty_filter_reference.csv
- 音频质量检查表_audio_quality_check.csv
- 切片边界草稿_clip_boundary_draft.csv
- 正样本AI结构草稿_positive_ai_structure_draft.csv
- 负样本边界草稿_negative_boundary_draft.csv
- 正负样本对照表_positive_negative_comparison.csv
- 对标视频分层拆解表_reference_layer_breakdown.csv

禁止：
- 不上传文件。
- 不删除、移动、改名原始文件。
- 不让人工从 0 填写字幕、美颜、裁切、音频、边界、对照或对标拆解字段。
- 不把 AI Skill 稳定性写成已确认。
- 不把技术导出写成业务通过。

请输出 人工复核清单_human_review_queue.csv，字段为：
- review_id
- source_file
- source_type
- issue_type（低置信度 / 缺字幕 / 待自动匹配 / 风险不确定 / 边界不确定 / 裁切不确定）
- ai_draft_summary
- evidence
- confidence
- suggested_action（确认 / 修改 / 忽略 / 补资料）
- review_status

请输出 AI_Skill验收标准_skill_evaluation_rubric.md，必须包含：
- 正样本召回率。
- 负样本误切率。
- 起止点偏差。
- 字幕可读性。
- 画面裁切通过率。
- 音频质量通过率。
- 人工修正时长。
- 盲测直播通过率。
- 人审通过率。
- 不能把技术导出写成业务通过。

规则：
- confidence 为“低”的记录必须进入复核清单。
- 缺证据、待自动匹配、blocked_pending_transcript、blocked_pending_frame_sample、blocked_pending_audio_probe 都必须进入复核清单。
- 验收标准是草稿，不是 AI Skill 已稳定结论。
```
