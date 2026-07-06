# 不复制文件说明

状态：`skipped_files_index_generated`

## 总体分级

| grade | count |
|---|---:|
| `A` | 35 |
| `B` | 9 |
| `C` | 3385 |
| `D` | 13254 |

## 文件类型 Top 12

| file_kind | count |
|---|---:|
| `tool_cache_or_runtime_dependency` | 12954 |
| `readable_text_reference` | 3521 |
| `duplicate_or_encoding_alias` | 61 |
| `action_core` | 50 |
| `support_report_or_manifest` | 44 |
| `action_core_jsonl` | 20 |
| `other_binary_or_unknown` | 15 |
| `course_text_context` | 13 |
| `archive_bundle` | 3 |
| `appledouble_sidecar` | 2 |

## A/B 候选处理决策

| decision | count |
|---|---:|
| `copy_full` | 6 |
| `extract_rows` | 37 |
| `extract_summary` | 1 |

## 跳过规则

- C 类只在上一轮 inventory/usefulness 表中保留索引，原则上不复制。
- D 类为重复、缓存、运行环境、AppleDouble、不可用文件，不复制。
- 媒体、图片、音频、zip、cache、`.env`、secret、API 原始输出不复制。
- 敏感成人亲密关系内容不复制具体操作细节，只在摘录中保留高层词族、来源行号和复核闸门。

## A/B 未完整复制明细

| source_file_id | grade | decision | relative_path | reason |
|---|---|---|---|---|
| SRC00057 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/06_讲师动作时间轴_presenter_action_timeline.csv` | 行数超过 10000 |
| SRC00060 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv` | 行数超过 10000；体积超过 10MB |
| SRC00087 | B | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv` | 行数超过 10000；课程文本命中敏感词，仅保留高层摘录 |
| SRC00088 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/neural_avatar_bridge_fields.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC00089 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/presenter_actions.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC00091 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/prosody_pacing.jsonl` | 行数超过 10000 |
| SRC00093 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/transcript_timeline.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC00094 | A | `extract_rows` | `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/tri_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC00341 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/06_讲师动作时间轴_presenter_action_timeline.csv` | 行数超过 10000；体积超过 10MB |
| SRC00344 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv` | 行数超过 10000；体积超过 10MB |
| SRC06157 | B | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/live_project_bridge_fields.csv` | 行数超过 10000；体积超过 10MB；课程文本命中敏感词，仅保留高层摘录 |
| SRC06158 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/neural_avatar_bridge_fields.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06159 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/presenter_actions.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06160 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/prosody_pacing.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06162 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0000_0099_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06163 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0100_0199_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06164 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0200_0299_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06165 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0300_0399_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06166 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0400_0499_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06167 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0500_0599_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06168 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0600_0699_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06169 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0700_0799_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06170 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0800_0899_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06171 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0900_0999_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06172 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1000_1099_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06173 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1100_1199_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06174 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1200_1299_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06175 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1300_1399_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06176 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1400_1499_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06177 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1500_1599_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06178 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1600_1699_action_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06198 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/transcript_timeline.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC06199 | A | `extract_rows` | `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/tri_alignment.jsonl` | 行数超过 10000；体积超过 10MB |
| SRC13403 | B | `extract_rows` | `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/08_关键词术语表_terms_glossary.csv` | 课程文本命中敏感词，仅保留高层摘录 |
| SRC13404 | B | `extract_rows` | `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/09_问题_答案_异议_回应_QA_objection_response_bank.csv` | 行数超过 10000；课程文本命中敏感词，仅保留高层摘录 |
| SRC13405 | B | `extract_summary` | `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/10_适合迁入直播项目的桥接字段_live_project_bridge_fields.md` | Markdown 命中敏感成人亲密关系内容，只生成高层摘要摘录。 |
| SRC13454 | B | `extract_rows` | `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/knowledge_points.csv` | 行数超过 10000；课程文本命中敏感词，仅保留高层摘录 |
| SRC13455 | B | `extract_rows` | `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/live_bridge_fields.csv` | 行数超过 10000；课程文本命中敏感词，仅保留高层摘录 |
