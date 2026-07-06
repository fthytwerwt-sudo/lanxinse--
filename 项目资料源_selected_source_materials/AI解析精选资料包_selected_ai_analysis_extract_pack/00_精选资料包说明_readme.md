# AI解析精选资料包说明

状态：`selected_extract_pack_generated_pending_user_review`

## 已确认

- 当前实际源目录：`/Volumes/WD_BLACK/AI解析`。
- 用户补充的 `WD_BLACK-AI 解析` 口径已核对；磁盘上 `/Volumes/WD_BLACK/AI 解析` 不存在，本轮按实际存在路径 `/Volumes/WD_BLACK/AI解析` 只读执行。
- 本包不是完整 `AI解析` 目录，也不是移动、删除、重命名原目录。
- 本包只保存当前剪辑项目后续判断动作、问题、剪辑结构需要的精选副本、关键摘录和来源追溯。
- 完整复制的文本副本会统一为 LF 行尾以通过 Git 校验；清单中分别记录 `source_sha256`、`target_sha256` 和 `target_normalization`。

## 处理结果

- A/B 候选文件：44 个。
- 完整复制：6 个。
- 行级摘录：37 个。
- 摘要摘录：1 个。
- 只索引/跳过：0 个。

## 后续 Codex 使用方式

1. 先读 `01_复制文件清单_selected_source_copy_manifest.csv` 判断哪些源文件已完整复制。
2. 再读 `02_摘录资料清单_selected_extract_manifest.csv` 和 `04_大表关键摘录_large_table_extracts/` 获取大表关键字段、来源行号和脱敏摘录。
3. 用 `05_源资料到动作知识库追溯表_source_to_action_traceability.csv` 连接动作、问题、剪辑结构桥接关系。
4. 对任何涉及视觉、健康效果、成人亲密关系、业务承诺的内容，保持 `pending_user_review` 或对应复核闸门。

## 禁止外推

- 本包不代表健康效果成立。
- 本包不代表动作专业性通过。
- 本包不代表审美、人感或业务通过。
- 本包不代表可以直接进入直播候选片段筛选。
