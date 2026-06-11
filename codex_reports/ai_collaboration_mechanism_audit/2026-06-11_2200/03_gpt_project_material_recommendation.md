# 03 GPT Project 材料推荐稿

## 1. 推荐放进 GPT Project Instructions 的内容

建议只放高优先级、短句、可执行规则：

```text
你是用户的外层总控脑 / planning / critique / continuity 层。

默认职责：
- 先判断用户真实目标，再给方案或下发 Codex。
- 区分 P0 / P1 / P2：P0=用户本轮明确输入，P1=当前项目事实和验证证据，P2=历史记忆、旧项目、外部资料；冲突时 P0 > P1 > P2。
- 未确认事项必须标注：已确认 / 部分成立 / 待验证 / 推测。
- 不把技术通过写成内容通过，不把本地完成写成远端完成，不把用户未人审写成已通过。

下发 Codex 前必须检查：
- 真实意图是否清楚。
- Goal / Context / Constraints 是否清楚。
- Implementation design 是否清楚。
- primary_route / fallback_route / capability_status / probe_required / blocked_if_missing 是否清楚。
- Impact check、Must read、Execution steps、Done when、Blocked if、Output 是否清楚。

Codex 默认不知道上下文。任何交给 Codex 的任务都必须显式提供目标、上下文、边界、允许/禁止文件、必须读取、验证命令、完成标准、阻断条件和回报格式。

如果缺真实意图，先澄清；如果缺 Implementation design，不下发 Codex；如果只是方向型输入，先转成可执行合同。

Perplexity / Web 只负责外部资料和来源，不直接变成项目事实。外部资料必须先拆成原始材料、保真事实、执行桥接、推测判断。

Obsidian 存机制和长期工作法；项目仓库 / 当前文件 / 验证输出才是当前项目事实源。
```

## 2. 推荐放进 Project Knowledge 文件的内容

建议作为知识文件，而不是系统指令：

- `00_总说明_如何使用这套机制.md`
- `01_我的AI分工模型_GPT_Codex_Perplexity.md`
- `02_P0-P1-P2判断优先级_priority_anchor.md`
- `03_真实意图澄清闸门_true_intent_gate.md`
- `04_六层需求确认与实现设计闸门_six_layer_implementation_gate.md`
- `05_Codex执行单标准模板_codex_prompt_template.md`
- `07_外部资料保真提取与执行桥接_external_material_bridge.md`
- `08_原感稿锁定与执行桥接_original_feel_bridge.md`
- `09_失败后路线重判机制_route_replanning.md`
- `10_输出状态与完成度硬规则_output_status_rules.md`
- `11_跨项目迁移使用说明_cross_project_migration.md`
- `12_常用Codex执行单模板库_codex_templates.md`
- `99_索引_Index.md`

建议把 `99_索引_Index.md` 改成 Project Knowledge 的入口索引，让 ChatGPT 知道遇到不同问题该查哪篇机制。

## 3. 不建议直接放进 Project Instructions 的内容

- 整篇 `12_常用Codex执行单模板库`：太长，会稀释高优先级规则。
- 整篇 `99_索引_Index`：Obsidian 双链多，适合知识导航，不适合作为执行指令。
- 各文件里的完整“可复制模板”：适合调用时使用，不适合塞进常驻 Instructions。
- 旧项目路径、素材、模型、任务状态、账号/API key、候选状态、业务身份。

## 4. 需要用户确认后才能写入的内容

- 是否所有项目都要求 commit + push + remote HEAD verification 才算完成。
- 哪些任务 Codex 可以自动补全，哪些必须先问用户。
- 哪些 Perplexity 资料可以进入长期 Project Knowledge。
- 哪些 Obsidian 机制卡片已经是最新版，哪些只是历史草稿。
- 内容/视频/直播项目中“审美通过 / 人感通过 / 业务通过”的具体人审标准。

## 5. 适合做成 Codex prompt 模板的内容

- `05_Codex执行单标准模板`：作为通用模板。
- `12_常用Codex执行单模板库`：
  - mechanism_sync
  - read_only_audit
  - obsidian_documentation_export
  - route_replanning
- `06_方向型输入到可执行机制`：作为方向输入转执行合同模板。
- `09_失败后路线重判机制`：作为失败复盘与改线模板。

## 6. 适合做成 Obsidian 长期机制卡片的内容

- GPT / Codex / Perplexity / Obsidian 四层分工卡。
- P0/P1/P2 优先级卡。
- Prompt 输出前需求确认闸门卡。
- 需求不确定阻断与澄清闸门卡。
- 六层需求确认与 Implementation design 卡。
- Codex 默认不知道上下文卡。
- 外部资料保真提取卡。
- 原感稿锁定与执行桥接卡。
- 失败后路线重判卡。
- 输出状态与完成度硬规则卡。

## 推荐搭建顺序

1. 先把上面的短版规则放进 GPT Project Instructions。
2. 再把 14 篇原始机制文件作为 Project Knowledge 上传。
3. 单独整理一份 `Codex执行单模板.md`，从 `05` 和 `12` 合并精简。
4. 后续每次项目复盘，只把“机制变化”写入机制库，把“项目事实”留在项目自己的 repo / Obsidian 项目页。
