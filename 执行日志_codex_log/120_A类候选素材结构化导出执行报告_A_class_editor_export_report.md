# 120 A 类候选素材结构化导出执行报告

## 主结论

已确认：本轮没有重新筛选、没有重新 ASR、没有重建动作知识库；只基于上轮 A 类清单导出剪辑师本地素材包。

- 本地成片/素材包地址：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_live_A_editor_package`
- A 类候选总数：102
- 来源直播录屏数：4
- 实际导出 mp4 数：102
- 导出失败数：0
- 技术校验成功数：102
- 技术校验失败数：0
- 前后段拆分状态：`not_available_from_pair_table_same_time_range`

## 结构分组

- 01_误区错误纠正_错误动作正确动作原因解释: 24
- 02_问题问答_原因解释方法边界: 3
- 03_痛点人群点名_单动作完整循环坚持建议: 15
- 04_工具动作演示_发力口令低压跟练收束: 20
- 05_多动作组合_同一主题推进轻跟练收束: 40
- 06_结果前置_操作过程注意事项风险边界: 0
- 07_待视觉复核_主题不明: 0

## 探针结果

- a_candidate_rows: pass (102)
- pair_rows: pass (211)
- structure_rows: pass (211)
- master_rows: pass (211)
- source_video_count: pass (4)
- ffmpeg_path: pass (/opt/homebrew/bin/ffmpeg)
- ffprobe_path: pass (/opt/homebrew/bin/ffprobe)
- disk_available_gib: pass (866.62)
- front_back_split_usable_count: pass (0)
- output_ignore_status: pass (ignored)
- source_probe: pass (6620.640)
- source_probe: pass (5898.240)
- source_probe: pass (6570.720)
- source_probe: pass (6620.640)

## 生成文件

- `scripts/export_priority_A_live_candidates_for_editor.py`
- `项目事实_project_facts/直播素材筛选_live_material_screening/10_A类素材导出索引_A_class_export_manifest.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/11_A类口播动作配对剪辑说明_A_class_pair_editing_guide.csv`
- `项目事实_project_facts/直播素材筛选_live_material_screening/12_A类剪辑师交付说明_A_class_editor_delivery_readme.md`
- `项目事实_project_facts/直播素材筛选_live_material_screening/13_A类二次剪辑标注表_A_class_secondary_edit_notes.csv`
- `素材解析_pipeline_material_analysis/13_priority_A_editor_export/01_A类导出探针_A_class_export_probe.csv`
- `素材解析_pipeline_material_analysis/13_priority_A_editor_export/02_A类导出校验_A_class_export_validation.csv`

## 失败项

无

## 边界说明

本轮只完成本地素材导出与技术校验。A 类表示“优先给剪辑师处理的候选素材”，不等于健康审核通过、动作规范通过、业务通过、审美包装通过或发布可用。

## 媒体入库规则

`outputs/local_live_A_editor_package/` 已加入 `.gitignore`，本轮 mp4 和本地包说明不进入 Git；Git 只提交脚本、索引、说明、校验表和执行报告。
