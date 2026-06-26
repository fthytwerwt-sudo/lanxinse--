# AI需要的成片全量结构解析报告

状态：`partial_finished_video_analysis_completed_with_pending_items`
生成时间：2026-06-27T00:53:59+08:00
任务类型：`finished_video_structure_formula_full_analysis`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| 输入目录 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/AI需要的成片` |
| mp4 总数 | 618 |
| 成功解析数 | 100 |
| 失败数 | 0 |
| pending 数 | 518 |
| API key 是否读取 | yes，掩码 `sk-2***************************09f9` |
| 使用模型 | `qwen3-vl-plus` 对前 100 条做抽样关键帧结构反推；`qwen-vl-max` 保留为高价值复核模型；`qwen-plus-latest` 用于结构总结边界参考 |
| 是否上传完整视频 | 否 |
| 是否上传真实音频 | 否 |
| 是否上传抽样关键帧 contact sheet | 是，仅用于模型结构反推，本地产物不提交 |
| 是否提交媒体 | 否 |
| 是否提交完整 API 输出 | 否 |

## 2. 视频类型汇总

| 类型 | 数量 | 代表视频 | 常见结构公式 |
|---|---:|---|---|
| `body_care_knowledge` 身体保养知识类 | 44 | fv_0001 30+产后妈妈居家必练动作.mp4；fv_0006 5月26日.mp4；fv_0011 产后漏尿能自己好吗.mp4 | 人群点名 + 痛点放大 + 单动作演示 + 坚持建议 |
| `sports_teaching` 运动教学类 | 32 | fv_0002 35岁以后都去练不管生完多久了每天100个 小肚子平了 臀翘了最重要的是可以锻炼盆底肌.mp4；fv_0003 4月17日(1).mp4；fv_0004 5月26日 (2).mp4 | 人群点名 + 低门槛动作 + 坚持建议 |
| `movement_correction` 动作纠错类 | 17 | fv_0005 5月26日(1).mp4；fv_0007 5月27日 (1).mp4；fv_0008 5月27日.mp4 | 错误动作 + 正确动作 + 原因解释 |
| `problem_solution` 问题解答类 | 3 | fv_0055 产后漏水不用愁一个小球帮你改变.mp4；fv_0065 口子闭合不上一个小球告别困扰.mp4；fv_0080 只需一个小球告别跑跳漏水困扰.mp4 | 痛点可视化 + 解决方案 + 效果对比 + 行动指令 |
| `knowledge_explainer` 知识讲解类 | 2 | fv_0024 40岁的女性练出八爪鱼需要多久？.mp4；fv_0044 一分钟握力测试多少次才算及格呢 切片.mp4 | 痛点问题 + 原因解释 + 方法交付 |
| `pitfall_warning` 避坑提醒类 | 1 | fv_0009 70%女性中招的盆底肌误区.mp4 | 人群点名 + 痛点放大 + 单动作演示 + 坚持建议 |
| `mistake_demonstration` 错误示范类 | 1 | fv_0034 一个瑜伽小球告别跑跳漏氵尴尬6.3（2）.mp4 | 反面案例 + 原因解释 + 正确做法 |

## 3. 结构公式汇总

| 结构公式 | 出现次数 | 代表视频 |
|---|---:|---|
| 人群点名 + 低门槛动作 + 坚持建议 | 33 | fv_0002 35岁以后都去练不管生完多久了每天100个 小肚子平了 臀翘了最重要的是可以锻炼盆底肌.mp4；fv_0004 5月26日 (2).mp4；fv_0017 30岁的女性练八爪鱼要多久6.2（4）.mp4 |
| 痛点可视化 + 解决方案 + 效果对比 + 行动指令 | 23 | fv_0006 5月26日.mp4；fv_0011 产后漏尿能自己好吗.mp4；fv_0033 一个瑜伽小球告别臀凹陷6.4.mp4 |
| 人群点名 + 痛点放大 + 单动作演示 + 坚持建议 | 17 | fv_0001 30+产后妈妈居家必练动作.mp4；fv_0009 70%女性中招的盆底肌误区.mp4；fv_0016 妈妈臀 臀凹陷一个动作饱满臀部.mp4 |
| 痛点问题 + 原因解释 + 方法交付 | 15 | fv_0010 Z宫下垂盆底无力就练臀桥呼吸.mp4；fv_0013 先减肥还是先改善漏尿.mp4；fv_0014 别再疯狂练收紧可能越练越漏尿.mp4 |
| 错误动作 + 正确动作 + 原因解释 | 10 | fv_0003 4月17日(1).mp4；fv_0005 5月26日(1).mp4；fv_0007 5月27日 (1).mp4 |
| 反面案例 + 原因解释 + 正确做法 | 1 | fv_0034 一个瑜伽小球告别跑跳漏氵尴尬6.3（2）.mp4 |
| 结果前置 + 操作过程 + 注意事项 | 1 | fv_0041 一个瑜伽小球肚子平了臀饱满6.10.mp4 |

## 4. 失败 / 待复核

- 失败视频均已在 CSV 中标 `analysis_status=failed`，不写成已解析。
- 本轮按用户最新指令只解析 100 条；未解析视频在 CSV 中标 `pending_not_analyzed`。
- `audio_transcription` 本轮不做完整转写；音频只作为视频是否有音轨的技术字段。
- 视觉抽样不能证明审美通过、动作专业性通过或业务事实通过。

## 5. 生成文件

- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/20_视频结构公式库_video_structure_formula_library.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/21_初剪完整性与素材连续性判断标准_rough_cut_integrity_continuity_standard.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/22_成片样本类型与结构总表_finished_video_type_structure_inventory.md`
- `项目事实_project_facts/自动剪辑五结构成片方案_five_structure_final_video/23_Codex成片解析字段规范_finished_video_analysis_schema.md`
- `素材解析_pipeline_material_analysis/08_finished_video_analysis/成片样本清单_finished_video_inventory.csv`
- `素材解析_pipeline_material_analysis/08_finished_video_analysis/成片结构矩阵_finished_video_structure_matrix.csv`
- `素材解析_pipeline_material_analysis/08_finished_video_analysis/成片证据索引_finished_video_evidence_index.csv`

## 6. 边界确认

| 边界 | 结果 |
|---|---|
| 是否提交媒体 | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否提交完整 API 输出 | 否 |
| 是否写审美通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写全量剪辑稳定 | 否 |

## 7. 下一步

- 用户先复核 `20 / 21 / 22 / 23`。
- 如果结构公式库符合预期，再进入直播录屏解析。
- 如果结构分类不准，回到成片样本结构公式修正。
- 不直接进入全量自动剪辑。
