# 课程动作资料审计与映射执行报告

状态：`course_action_data_audit_generated_pending_user_review`
生成时间：2026-07-06T16:03:05

## 1. 目标

本轮任务为 `course_action_data_audit_and_mapping`：审计 `/Volumes/WD_BLACK/AI解析`，生成课程动作资料清单、可用性分级、动作知识库和直播筛选接入说明。

## 2. 已确认输入边界

- 源目录：`/Volumes/WD_BLACK/AI解析`
- 仓库目录：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--`
- 源目录只读：yes
- 是否复制源包/媒体/cache/API 原始输出：no
- 是否写健康效果成立：no
- 是否写业务通过：no
- 是否写动作专业性通过：no

## 3. 源目录清点摘要

- 总文件数：16683
- A 类动作核心/JSONL：35
- B 类课程文本上下文：9
- C 类支撑/封装/媒体引用：3385
- D 类重复/缓存/运行环境/不可用：13254

### file_kind top counts

| value | count |
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

## 4. 高价值表抽取摘要

- `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/06_讲师动作时间轴_presenter_action_timeline.csv`：19424 rows
- `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv`：19424 rows
- `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/12_数字人动作触发规则_avatar_action_trigger_rules.csv`：4 rows
- `神经数字人课程解析交付包_neural_avatar_course_analysis_pack/data/live_project_bridge_fields.csv`：19424 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/06_讲师动作时间轴_presenter_action_timeline.csv`：2719045 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/09_逐字稿_课件_动作三线对照表_transcript_courseware_action_alignment.csv`：2719045 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/12_数字人动作触发规则_avatar_action_trigger_rules.csv`：6 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/live_project_bridge_fields.csv`：2719045 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0000_0099_action_alignment.jsonl`：33169 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0100_0199_action_alignment.jsonl`：26405 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0200_0299_action_alignment.jsonl`：31166 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0300_0399_action_alignment.jsonl`：84825 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0400_0499_action_alignment.jsonl`：22396 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0500_0599_action_alignment.jsonl`：145395 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0600_0699_action_alignment.jsonl`：212405 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0700_0799_action_alignment.jsonl`：253659 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0800_0899_action_alignment.jsonl`：151555 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_0900_0999_action_alignment.jsonl`：170037 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1000_1099_action_alignment.jsonl`：48255 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1100_1199_action_alignment.jsonl`：265008 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1200_1299_action_alignment.jsonl`：277116 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1300_1399_action_alignment.jsonl`：262962 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1400_1499_action_alignment.jsonl`：353704 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1500_1599_action_alignment.jsonl`：352814 rows
- `神经数字人逐句动作解析工作区_neural_avatar_sentence_action_workspace_20260703_181956/data/sentence_action_shards/lessons_1600_1699_action_alignment.jsonl`：28174 rows
- `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/08_关键词术语表_terms_glossary.csv`：3373 rows
- `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/09_问题_答案_异议_回应_QA_objection_response_bank.csv`：52801 rows
- `课程逐字稿解析工作区_所有课程_20260630_170152/课程逐字稿解析交付包_course_transcript_analysis_pack/data/knowledge_points.csv`：49844 rows

## 5. 关键判断

- `course pack` 能提供 chunk-level 时间窗口和动作标签库，但大量记录为低置信占位，不能作为自动动作下发依据。
- `sentence workspace` 粒度更细，可用于候选筛选字段，但仍保留 `human_review_needed` 和视觉近邻复核要求。
- 源包同时包含“讲师/数字人呈现动作”和“课程文本动作/问题关键词”；本轮已拆成两个 action_domain，避免混用。
- 成人亲密关系敏感课程词只保留高层词族与风险闸门，不搬运源内操作细节。

## 6. 本轮输出文件

- `素材解析_pipeline_material_analysis/10_course_action_data_audit/课程动作资料文件清单_course_action_source_inventory.csv`
- `素材解析_pipeline_material_analysis/10_course_action_data_audit/课程动作资料可用性分级_course_action_source_usefulness.csv`
- `项目事实_project_facts/动作知识库_action_knowledge_base/01_动作问题映射表_action_problem_mapping.csv`
- `项目事实_project_facts/动作知识库_action_knowledge_base/02_动作别名归一表_action_alias_normalization.csv`
- `项目事实_project_facts/动作知识库_action_knowledge_base/03_问题分类表_problem_taxonomy.csv`
- `项目事实_project_facts/动作知识库_action_knowledge_base/04_动作剪辑结构桥接表_action_clip_structure_bridge.csv`
- `项目事实_project_facts/动作知识库_action_knowledge_base/05_动作应用规则说明_action_application_rules.md`
- `项目事实_project_facts/动作知识库_action_knowledge_base/06_动作知识库接入直播筛选说明_action_knowledge_to_live_screening.md`
- `执行日志_codex_log/117_课程动作资料审计与映射执行报告_course_action_data_audit_report.md`
- `scripts/audit_course_action_data.py`

## 7. 后续使用方式

- 直播素材筛选先用 `02_动作别名归一表` 命中 `normalized_action_id`。
- 再看 `03_问题分类表` 和 `04_动作剪辑结构桥接表` 判断是否进入候选。
- 只要视觉、健康、合规、客户事实任一未确认，就保持 `pending_user_visual_review` 或对应 review gate。

## 8. 待确认项

- 客户是否允许成人亲密关系敏感主题进入直播筛选。
- 哪些课程词族需要合规脱敏或完全禁用。
- 视觉复核是否采用人工、视觉模型或二者组合。
- 业务事实、课程权益、价格、转化话术需要客户另行确认。

## 9. validation result

- `python3 -m py_compile scripts/audit_course_action_data.py`：passed
- `python3 scripts/audit_course_action_data.py`：passed，生成 `inventory_rows=16683`、`action_mapping_rows=14`、`alias_rows=47`、`taxonomy_rows=17`、`bridge_rows=14`
- `python3 scripts/check_ali_config_safety.py`：passed，未发现真实 key、`.env` staged 或缺失忽略规则
- `git diff --check`：passed
- 结构化 CSV 校验：passed，10 个必需产物存在；清单/分级各 16683 行；本轮产物仅 `.csv/.md/.py`
- 关键词边界扫描：只命中“不能写/不代表/禁止写”类防越界说明，未写健康效果成立、业务通过或动作专业性通过

## 10. commit / push

- 本报告由脚本生成；最终 artifact commit、push 和 remote HEAD 以 Codex 本轮最终回报为准。
