# 05 给用户的最终摘要

## 1. 这个机制库目前最核心的协作逻辑是什么？

最核心的逻辑是：

> ChatGPT 做外层总控脑，先判断目标、边界、路线和验收；Codex 只在明确执行单里做本地执行和验证；Perplexity 只负责外部资料和来源；Obsidian 存机制，不冒充项目事实源；用户保留最终方向、审美和业务裁决。

这套机制不是普通文件总结，而是在建立一个“项目配合机制操作系统”。它最重视三件事：

- 不让 Codex 在缺上下文时脑补。
- 不让 GPT 把方向问题直接下发成执行任务。
- 不把局部技术成功写成整体完成。

## 2. ChatGPT 以后应该怎么配合用户？

ChatGPT 应该先判断用户表面问题和真实卡点是否一致。

如果用户是在判断方向、价值、路线、机制缺口，就先做真实意图澄清和六层需求确认；如果要交给 Codex，就必须先写清 Goal、Context、Constraints、Implementation design、Impact check、Execution steps、Done when、Blocked if。

ChatGPT 的默认输出风格应该是：先结论，少术语，能推进；但遇到未确认内容必须标 `已确认 / 部分成立 / 待验证 / 推测`。

## 3. Codex 以后应该怎么执行任务？

Codex 默认不知道上下文。每次给 Codex 的任务都要显式提供目标、上下文、边界、允许/禁止范围、必须读取、验证命令、完成标准、阻断条件和输出格式。

Codex 执行前必须先读文件、查现状、做影响面检查。缺真实意图或 Implementation design 时，不应硬做，而应 blocked。

Codex 汇报时必须把 local、validation、commit、push、remote readback、用户人审、业务验收分开。

## 4. GPT Project 资料应该怎么搭建？

建议分三层：

1. Project Instructions：只放短版高优先级规则，如 P0/P1/P2、真实意图闸门、六层需求确认、Codex 默认不知道上下文、状态词。
2. Project Knowledge：放 14 篇原机制文件，尤其是索引、分工模型、Codex 模板、外部资料桥接、失败重判。
3. Codex prompt 模板：从 `05_Codex执行单标准模板` 和 `12_常用Codex执行单模板库` 合并出可复用执行单。

## 5. 目前最大的问题 / 缺口 / 风险是什么？

- 规则重复较多，但多数是核心规则重复，不是坏事；后续要压缩成 Instructions，避免太长。
- `05` 和 `12` 是模板，不是具体任务单，不能直接复制给 Codex 执行，必须替换路径、事实源、allowed files、验证命令。
- 机制库目前偏“原则和模板”，还需要项目级完成标准，例如视频项目、直播项目、产品项目各自什么叫审美通过、业务通过。
- 是否每个项目都要求 commit + push + remote HEAD verification，需要用户按项目确认。
- Perplexity 资料进入 Project Knowledge 前需要做来源可靠性和版权/品牌边界确认。

## 6. 下一步建议用户发给 ChatGPT 继续收束的内容

建议按这个顺序发给 ChatGPT：

1. `05_final_summary_for_user.md`
2. `03_gpt_project_material_recommendation.md`
3. 如需深度整理，再发 `02_global_collaboration_mechanism_report.md`

让 ChatGPT 下一步做两件事：

- 把 `03` 里的短版规则压成最终 GPT Project Instructions。
- 把 `04_codex_prompt_template.md` 改成用户长期使用的 Codex 下发模板。

## 审计状态

- 机制库路径：`/Users/fan/Documents/Obsidian Vault/AI协作机制库_AI_collaboration_system`
- 发现文件数：14
- 成功读取：14
- 跳过文件：0
- 阻断情况：无
- 敏感内容：未发现实际 secret；只发现“账号/API key/余额”等机制规则描述。
