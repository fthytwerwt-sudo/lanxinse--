# 阿里视觉模型默认路由

状态：`已确认`
生成时间：2026-07-08 17:00:00

## 默认路由

1. 第一优先：`qwen3-vl-plus`
2. 第二优先：`qwen-vl-max`

## 禁用模型

- `qwen-vl-plus-latest`
- `qwen3-vl-max`

## 执行规则

- 本项目视觉复核脚本必须显式使用默认路由，不允许被 `.env` 中旧模型名覆盖。
- 单条候选先调用 `qwen3-vl-plus`；失败后只 fallback 到 `qwen-vl-max`。
- 禁止上传完整长直播，只允许上传本地抽帧、contact sheet 或短片关键帧材料。
- API 原始输出、媒体文件和 `.env` 均不得提交 Git。
- 视觉结果只作为动作证据，不写发布、人感、业务或健康效果确认。

## 来源

- `执行日志_codex_log/106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md`
- 本轮 `01_阿里视觉路由探针_ali_visual_route_probe.csv`
