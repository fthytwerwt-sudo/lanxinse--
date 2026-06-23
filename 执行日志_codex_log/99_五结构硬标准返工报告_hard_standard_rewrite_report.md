# 五结构硬标准返工报告

状态：`已生成，DOCX 结构校验通过，DOCX PNG 视觉 QA 未完成，Git 闭环以最终回报和 remote HEAD 读回为准`
生成时间：2026-06-24 03:42:56 CST
任务类型：`rewrite_five_structure_hard_judging_standard_docx`

## 1. 返工原因

上一版方向部分成立，但更像概念型分析文档，没有形成用户需要的硬判断尺。本轮已整体重写为大白话操作手册，重点回答：以后拿到一条视频，怎么判断、怎么打分、怎么剪、怎么决定能不能进入候选池。

## 2. 读取输入

- 上一版 Markdown：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/05_五结构完整成片判断标准_human_readable_standard.md`
- 上一版 / 本轮重写证据矩阵：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/06_正负样片结构证据矩阵_positive_negative_structure_evidence_matrix.csv`
- 上一版 / 本轮重写盲测评分表：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/07_盲测评分表_blind_review_rubric.csv`
- 本地转写目录：`素材整理_asset_management/04_时间码_timecode/本地转写输出_local_transcripts`
- 读取本地 JSON：33 条
- 正样片：30 条
- 负样片：3 条

## 3. 本轮解决的问题

- 把概念解释改成大白话硬标准。
- 每个结构补充推荐时长、最短可用、过长风险线。
- 每个结构补充通过 / 不通过 / 待人工复核条件。
- 补充“怎么剪、从哪里剪、到哪里停”的剪辑边界规则。
- 补充单结构和多结构组合判断。
- 补充桥接字幕规则和结构断裂判断。
- 盲测评分表从泛泛 `0-5` 改为 `0 / 1 / 3 / 5` 分档。
- 证据矩阵扩充到 142 行。

## 4. 新增 / 重写文件

- Markdown：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/05_五结构完整成片判断标准_human_readable_standard.md`
- DOCX：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/05_五结构完整成片判断标准_human_readable_standard.docx`
- 结构时长硬标准表：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/09_结构时长硬标准表_structure_duration_standards.csv`
- 证据矩阵：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/06_正负样片结构证据矩阵_positive_negative_structure_evidence_matrix.csv`，142 行
- 盲测评分表：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/07_盲测评分表_blind_review_rubric.csv`，15 个维度
- 大白话快速判断清单：`项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/10_大白话快速判断清单_plain_language_checklist.md`

## 5. 结构证据统计

- `traffic_hook`（引流钩子）：9 条主体初判证据。
- `course_teaching`（课程讲解）：7 条主体初判证据。
- `objection_response`（异议回应）：4 条主体初判证据。
- `case_trust`（案例信任）：4 条主体初判证据。
- `conversion_push`（促单转化）：1 条主体初判证据。
- `unmapped_clip`（无法映射片段）：8 条主体初判证据。

## 6. DOCX 状态

- DOCX 是否生成：是
- DOCX 结构校验：已通过，zip 包含 `[Content_Types].xml`、`word/document.xml`、`word/styles.xml`、`word/_rels/document.xml.rels`
- DOCX 视觉渲染 QA：未完成，`render_docx.py` 因本机 bundled LibreOffice 缺 `/opt/homebrew/opt/little-cms2/lib/liblcms2.2.dylib` 失败
- 设计预设：`compact_reference_guide`
- 注意：不能把结构校验通过写成 DOCX 视觉阅读体验通过

## 7. 边界确认

- 是否修改原始素材：否
- 是否提交完整转写正文：否
- 是否提交媒体 / 音频 / 缓存：否
- 是否写审美通过：否
- 是否写业务事实通过：否
- 是否写批量稳定：否
- 是否连接 DaVinci：否

## 8. 仍待人工复核

- 画面是否顺。
- 字幕是否舒服。
- 节奏是否自然。
- 动作是否正确。
- 审美和人感。
- 业务事实、价格、权益、退款和效果承诺。
- DOCX PNG 视觉渲染 QA 本轮记录为 `docx_visual_qa_not_completed`，原因是本机 LibreOffice 依赖缺失。

## 9. Git 状态

- commit：本报告随本轮 path-limited commit 入库；为避免 Git hash 自引用不一致，具体 SHA 以最终回报为准。
- push：执行后以最终回报为准。
- remote HEAD：执行后以 `git ls-remote origin refs/heads/main` 读回为准。
