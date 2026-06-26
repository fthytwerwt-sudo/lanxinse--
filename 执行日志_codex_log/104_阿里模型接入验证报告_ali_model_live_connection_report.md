# 阿里模型接入验证报告

状态：`partial_connected_with_failed_models`
生成时间：2026-06-26T17:44:29+08:00
任务类型：`ali_api_model_live_connection_setup`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| `.env` 是否存在 | 是 |
| API key 是否读取 | yes，只记录掩码，不写完整 key |
| API key 掩码 | `sk-w************************************************************************************************************nSvk` |
| API base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 测试模型角色数 | 8 |
| connected 数 | 3 |
| failed 数 | 4 |
| pending 数 | 1 |
| 是否上传真实素材 | 否 |
| 是否跑全量解析 | 否 |
| 是否提交 `.env` | 否 |
| 本地 JSON 输出 | `api_outputs/ali_model_live_test_results.json`，不提交 GitHub |
| 最终状态 | `partial_connected_with_failed_models` |

## 2. 模型接入结果表

| role | model_name | status | latency_ms | error_type | 中文说明 | 下一步动作 |
|---|---|---|---:|---|---|---|
| text_analysis | `qwen-plus-latest` | `connected` | 928 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入文本 / 时间码供料小样本 probe |
| structured_output | `qwen-plus-latest` | `connected` | 975 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入文本 / 时间码供料小样本 probe |
| vision_analysis | `qwen-vl-plus-latest` | `failed` | 329 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied | 到阿里控制台检查权限 / 服务开通 |
| vision_high | `qwen-vl-max-latest` | `failed` | 1581 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied | 到阿里控制台检查权限 / 服务开通 |
| omni_analysis | `qwen-omni-turbo-latest` | `connected` | 706 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入 1 条短视频素材 probe，但不得直接全量 |
| audio_transcription | `paraformer-v2` | `pending_validation` | - | `pending_manual_route_or_local_whisper` | paraformer-v2 需要 DashScope 音频转写 SDK 或文件 URL 任务路线；本轮不上传音频，保留 local_faster_whisper fallback。 | 后续走 DashScope 音频转写专用路线或本地 faster-whisper |
| fallback_text | `qwen-turbo-latest` | `failed` | 331 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied | 到阿里控制台检查权限 / 服务开通 |
| fallback_vision | `qwen-vl-plus-latest` | `failed` | 349 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied | 到阿里控制台检查权限 / 服务开通 |

## 3. 边界确认

| 边界 | 结果 |
|---|---|
| 是否打印完整 key | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否上传真实素材 | 否 |
| 是否提交 `api_outputs/` | 否 |
| 是否跑全量解析 | 否 |
| 是否产生媒体文件 | 否 |
| 是否确认模型效果好 | 否 |
| 是否确认成本可接受 | 否 |
| 是否确认全量稳定 | 否 |

## 4. 下一步建议

- 如果文本、视觉、Omni 至少各有一个 `connected`，下一步可以做 1 条短视频素材解析 probe。
- 如果只有文本模型 `connected`，先做文本 / 时间码路线。
- 如果视觉模型失败，先修视觉模型名或账号权限。
- 如果 Omni 失败，不阻断抽帧 + 视觉模型路线。
- 不直接进入全量解析；全量前必须先完成小样本素材 probe。

## 5. 当前限制

本报告只证明最小 API 请求的连通性，不证明真实直播素材解析质量、长视频支持、费用、限额、速度或稳定性。

## 6. 官方文档边界参考

- [阿里云百炼 OpenAI-compatible Chat](https://www.alibabacloud.com/help/en/model-studio/compatibility-of-openai-with-dashscope)：用于文本和可兼容模型的最小 `chat/completions` 请求。
- [阿里云百炼 Qwen-VL OpenAI 兼容接口](https://www.alibabacloud.com/help/en/model-studio/qwen-vl-compatible-with-openai)：用于视觉模型最小图片理解测试。
- [OpenAI Chat API Reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions)：文档说明 OpenAI-compatible Chat API 支持 Qwen large language models、Qwen-VL、Qwen-Omni 等模型族。
- [Paraformer 录音文件识别 Python SDK](https://www.alibabacloud.com/help/en/model-studio/paraformer-recorded-speech-recognition-python-sdk)：属于录音文件识别 SDK / 任务路线，本轮不上传音频，因此标为 `pending_validation`。

## 7. commit / push 状态

```text
local_commit_created=true
git_push_status=blocked_push_failed
git_push_error=remote Invalid username or token. Password authentication is not supported for Git operations.
remote_head_verified=false
```

说明：本地模型接入、live test、配置更新、报告生成和 commit 已完成；远端 push 被 GitHub 凭据阻断，因此不能写 remote completed。
