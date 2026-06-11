# 00 文件盘点与影响面检查

## 影响面检查结论

- 目标文件夹：已找到
- 解析后的绝对路径：`/Users/fan/Documents/Obsidian Vault/AI协作机制库_AI_collaboration_system`
- 发现文件数：14
- 成功读取：14
- 跳过文件：0
- 不可读文件：0
- 文件类型：全部为 Markdown 文本文件
- 敏感内容扫描：未发现实际 credential、token、private key、支付信息；只发现“旧账号/API key/余额”等机制规则描述
- 重复 / 过期 / 冲突 / 未完成初判：
  - 已确认：没有发现硬冲突或明显已废弃文件。
  - 部分成立：`05_Codex执行单标准模板` 与 `12_常用Codex执行单模板库` 存在有意重复；前者是标准模板，后者是场景模板库。
  - 部分成立：`00_总说明`、`99_索引`、各单篇机制都重复强调“GPT 先判断、Codex 后执行、未验证写待验证”，属于核心规则重复，不是问题。
  - 待验证：是否要把全部 14 篇原文直接放进 GPT Project，需要用户确认；更建议压缩成 Project Instructions + Project Knowledge。
- 最适合构建 GPT Project Instructions 的文件：
  - `00_总说明_如何使用这套机制.md`
  - `01_我的AI分工模型_GPT_Codex_Perplexity.md`
  - `02_P0-P1-P2判断优先级_priority_anchor.md`
  - `03_真实意图澄清闸门_true_intent_gate.md`
  - `04_六层需求确认与实现设计闸门_six_layer_implementation_gate.md`
  - `05_Codex执行单标准模板_codex_prompt_template.md`
  - `10_输出状态与完成度硬规则_output_status_rules.md`
- 不建议原样直接导入 GPT Project Instructions 的文件：
  - `12_常用Codex执行单模板库_codex_templates.md`：太长，更适合放 Project Knowledge 或作为 Codex prompt 模板库。
  - `99_索引_Index.md`：Obsidian 双链较多，更适合作为知识文件，不适合作为高优先级 Instructions。
  - `07_外部资料保真提取与执行桥接_external_material_bridge.md`、`08_原感稿锁定与执行桥接_original_feel_bridge.md`：适合作为专题知识，不建议整篇塞进 Instructions。

## 文件清单

| # | 文件名 | 类型 | 大小 | 修改时间 | 读取状态 | 一句话用途判断 |
|---|---|---:|---:|---|---|---|
| 1 | `00_总说明_如何使用这套机制.md` | `.md` | 4.3 KB | 2026-06-09 17:43:20 +0800 | 已读取 | 机制库总入口，定义 GPT / Codex / 用户三方职责和迁移边界。 |
| 2 | `01_我的AI分工模型_GPT_Codex_Perplexity.md` | `.md` | 3.0 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 定义 GPT、Codex、Perplexity/Web、Obsidian/GitHub 的四层分工。 |
| 3 | `02_P0-P1-P2判断优先级_priority_anchor.md` | `.md` | 2.5 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 定义 P0/P1/P2 优先级，防止历史记忆覆盖本轮输入和当前事实。 |
| 4 | `03_真实意图澄清闸门_true_intent_gate.md` | `.md` | 2.8 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 规定下发 Codex 前必须先确认真实目标、成功/失败/停止条件。 |
| 5 | `04_六层需求确认与实现设计闸门_six_layer_implementation_gate.md` | `.md` | 3.6 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 定义目标层、机制层、Implementation design、流程层、判断标准层、反馈层。 |
| 6 | `05_Codex执行单标准模板_codex_prompt_template.md` | `.md` | 3.1 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 固化 GPT 下发给 Codex 的标准执行单字段。 |
| 7 | `06_方向型输入到可执行机制_direction_to_execution.md` | `.md` | 2.5 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 把“高级感 / 像参考 / 能不能做”这类方向输入转成可执行合同。 |
| 8 | `07_外部资料保真提取与执行桥接_external_material_bridge.md` | `.md` | 2.4 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 规定外部资料先保真、再抽字段，禁止把参考当项目事实。 |
| 9 | `08_原感稿锁定与执行桥接_original_feel_bridge.md` | `.md` | 1.9 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 规定“原感参考层”和“执行桥接层”双层并存。 |
| 10 | `09_失败后路线重判机制_route_replanning.md` | `.md` | 2.0 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 规定失败后先判断失败层级，再修复、降级、改线或 blocked。 |
| 11 | `10_输出状态与完成度硬规则_output_status_rules.md` | `.md` | 2.3 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 定义已确认、部分成立、待验证、推测、blocked 等状态词和完成边界。 |
| 12 | `11_跨项目迁移使用说明_cross_project_migration.md` | `.md` | 2.4 KB | 2026-06-09 17:41:37 +0800 | 已读取 | 规定跨项目只迁移机制，不迁移旧路径、素材、状态、账号/API key。 |
| 13 | `12_常用Codex执行单模板库_codex_templates.md` | `.md` | 5.4 KB | 2026-06-09 17:43:20 +0800 | 已读取 | 提供机制同步、只读审计、Obsidian 导出、失败重判等 Codex 执行单模板。 |
| 14 | `99_索引_Index.md` | `.md` | 5.0 KB | 2026-06-09 17:42:44 +0800 | 已读取 | 机制库导航入口，用问题类型映射到应读取的机制文件。 |

## 读取与跳过明细

- 全部 14 个文件均为相关机制文件，均已读取。
- 未发现 `.txt`、`.json`、`.canvas`、`.yaml`、`.yml` 文件。
- 未发现二进制、媒体、缓存或系统文件。
- 未发生权限阻断。
