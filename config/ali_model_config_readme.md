# 阿里 API 模型配置说明

状态：`ali_api_config_scaffold_created_pending_user_key（阿里 API 配置骨架已创建，待用户填写 key）`

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

`config/ali_model_config.yaml` 中所有模型名状态均为 `待验证`。

当前配置只表达后续计划使用的任务分层：

- `text_analysis`：文本分析、结构总结、规则归纳、候选解释。
- `vision_analysis`：图片 / 关键帧 / 画面理解。
- `vision_high`：复杂画面和高价值候选复核。
- `audio_analysis`：音频解析和口播内容理解。
- `video_analysis`：视频片段理解和多模态观察。
- `omni_analysis`：音频 + 视频综合理解。
- `structured_output`：JSON 字段归一和供料包清洗。

这些配置不代表模型已可用，不代表账号已开通，不代表价格、额度、速度或稳定性已确认。

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
- 不确认模型可用。
- 不确认阿里 API 已接通。
