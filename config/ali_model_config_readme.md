# 阿里 API 模型配置说明

状态：`partial_connected_with_failed_models（已使用更新后的 .env 重连验证，部分模型仍失败）`

## 1. 用户只需要填写哪里

复制环境变量示例文件：

```bash
cp .env.example .env
```

然后只在本地 `.env` 里填写：

```text
ALI_API_KEY=你的真实阿里 API key
```

不要把真实 key 写进 `.env.example`，也不要提交 `.env`。

## 2. 默认不真实调用 API

`.env.example` 里默认：

```text
ALI_API_ENABLE_LIVE_TEST=false
```

这个状态只做本地配置检查，不调用阿里 API，不上传视频，不消耗额度。

如果用户已经填写 `.env`，并且只想做一次最小文本连接测试，再改成：

```text
ALI_API_ENABLE_LIVE_TEST=true
```

然后运行：

```bash
python3 scripts/check_ali_api_connection.py
```

## 3. 模型配置边界

`config/ali_model_config.yaml` 中 `model_roles` 会记录每次最小连接测试的 `connected` / `failed` / `pending_validation` 状态。

当前配置只表达后续计划使用的任务分层：

- `text_analysis`：文本分析、结构总结、规则归纳、候选解释。
- `vision_analysis`：图片 / 关键帧 / 画面理解。
- `vision_high`：复杂画面和高价值候选复核。
- `audio_analysis`：音频解析和口播内容理解。
- `video_analysis`：视频片段理解和多模态观察。
- `omni_analysis`：音频 + 视频综合理解。
- `structured_output`：JSON 字段归一和供料包清洗。

这些配置只代表最小连接状态，不代表真实素材解析效果、价格、额度、速度或稳定性已确认。

## 4. 不要随便改的字段

建议先不要改这些字段，除非后续 API probe 明确需要：

- `ALI_API_BASE_URL`
- `ALI_MODEL_TEXT_ANALYSIS`
- `ALI_MODEL_VISION_ANALYSIS`
- `ALI_MODEL_VISION_HIGH`
- `ALI_MODEL_OMNI_ANALYSIS`
- `ALI_MODEL_STRUCTURED_OUTPUT`
- `ALI_MAX_VIDEOS_PER_RUN`
- `ALI_MAX_FRAMES_PER_VIDEO`
- `ALI_ALLOW_VIDEO_UPLOAD`

如果连接脚本提示模型不可用，下一步应先检查阿里控制台的模型名、账号权限和服务开通状态，再更新配置。

## 5. 当前明确边界

- 不提交真实 API key。
- 不提交 `.env`。
- 不上传视频。
- 不跑全量解析。
- 只确认最小连接状态，不确认真实素材解析效果。
- 不把 `connected` 写成批量稳定或全量可用。

## 6. `.env` 更新后重连验证最新结果

最近一次最小重连验证报告：

```text
执行日志_codex_log/106_阿里模型重连验证报告_ali_model_reconnect_after_env_update_report.md
```

当前状态：`partial_connected_with_failed_models`

已接通：

- `text_analysis`: `qwen-plus-latest`
- `structured_output`: `qwen-plus-latest`
- `vision_analysis`: `qwen3-vl-plus`
- `vision_high`: `qwen-vl-max`
- `omni_analysis`: `qwen-omni-turbo-latest`
- `fallback_text`: `qwen-plus-latest`

失败 / 待处理：

- `fallback_vision`: `qwen-vl-plus-latest`，`permission_or_account_required`
- `audio_transcription`: `paraformer-v2`，`pending_manual_route_or_local_whisper`

候选测试补充：

- `vision_analysis` 按 qwen3 优先测试，`qwen3-vl-plus` 已 connected。
- `vision_high` 中 `qwen3-vl-max` 仍未接通，`qwen-vl-max` 已 connected，因此当前选中 `qwen-vl-max`。
- `fallback_text` 中 `qwen-turbo-latest` 失败，但 `qwen-plus-latest` 已 connected。
- `fallback_vision` 仍是 `permission_or_account_required`，需要继续检查权限 / 服务开通。

说明：最小连接成功不代表真实直播素材解析效果、成本、额度或稳定性已确认。下一步不能直接全量解析，只能先做 1 条短视频素材 probe。

## 7. 视觉模型候选当前状态

历史视觉迁移报告：

```text
执行日志_codex_log/105_阿里视觉模型迁移验证报告_ali_vision_model_migration_report.md
```

当前视觉候选已按官方视觉接口示例调整为 qwen3 优先：

- `vision_analysis`: `qwen3-vl-plus` -> `qwen-vl-plus` -> `qwen-vl-plus-latest`
- `vision_high`: `qwen3-vl-max` -> `qwen-vl-max` -> `qwen-vl-max-latest`

更新 `.env` 后，视觉候选当前状态以 106 报告为准：

- `qwen3-vl-plus`: `connected`
- `qwen3-vl-max`: `permission_or_account_required`
- `qwen-vl-max`: `connected`
- `qwen-vl-plus-latest`: `permission_or_account_required`
- `qwen-vl-max-latest`: 未继续测试，因为 `qwen-vl-max` 已 connected

`.env` 当前仍使用通用 DashScope OpenAI-compatible endpoint：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

阿里官方推荐部分地域使用 workspace-specific domain，例如东京地域可能是：

```text
https://{WorkspaceId}.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1
```

当前未发现 `.env` 中有 `WorkspaceId`，因此本轮不擅自修改 base URL。下一步应去百炼控制台确认模型权限、工作空间权限和 base_url 地域。
