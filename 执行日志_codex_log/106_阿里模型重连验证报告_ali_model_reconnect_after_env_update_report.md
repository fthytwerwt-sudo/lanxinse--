# 阿里模型重连验证报告

状态：`partial_connected_with_failed_models`
生成时间：2026-06-26T23:50:24+08:00
任务类型：`ali_api_reconnect_all_models_after_env_update`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| `.env` 是否存在 | 是 |
| API key 是否读取 | yes，只记录掩码，不写完整 key |
| API key 掩码 | `sk-2***************************09f9` |
| API base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 测试模型角色数 | 8 |
| connected 数 | 6 |
| failed 数 | 1 |
| pending 数 | 1 |
| 是否上传真实素材 | 否 |
| 是否跑全量解析 | 否 |
| 是否提交 `.env` | 否 |
| 本地 JSON 输出 | `api_outputs/ali_model_live_test_results.json`，不提交 GitHub |
| 最终状态 | `partial_connected_with_failed_models` |

## 2. 模型接入结果表

| role | model_name | status | latency_ms | error_type | 中文说明 | 下一步动作 |
|---|---|---|---:|---|---|---|
| text_analysis | `qwen-plus-latest` | `connected` | 1820 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入文本 / 时间码供料小样本 probe |
| structured_output | `qwen-plus-latest` | `connected` | 583 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入文本 / 时间码供料小样本 probe |
| vision_analysis | `qwen3-vl-plus` | `connected` | 2114 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入抽帧 + 视觉小样本 probe |
| vision_high | `qwen-vl-max` | `connected` | 853 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入抽帧 + 视觉小样本 probe |
| omni_analysis | `qwen-omni-turbo-latest` | `connected` | 445 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入 1 条短视频素材 probe，但不得直接全量 |
| audio_transcription | `paraformer-v2` | `pending_validation` | - | `pending_manual_route_or_local_whisper` | paraformer-v2 需要 DashScope 音频转写 SDK 或文件 URL 任务路线；本轮不上传音频，保留 local_faster_whisper fallback。 | 后续走 DashScope 音频转写专用路线或本地 faster-whisper |
| fallback_text | `qwen-plus-latest` | `connected` | 773 | `-` | 最小连接成功；不代表真实素材解析效果已确认 | 可进入文本 / 时间码供料小样本 probe |
| fallback_vision | `all_candidates` | `failed` | - | `all_candidates_failed` | qwen-vl-plus-latest permission_or_account_required | 保留错误摘要，先不进入该模型路线 |

## 3. 候选模型逐个测试记录

| role | candidate_model | status | latency_ms | error_type | 摘要 |
|---|---|---|---:|---|---|
| text_analysis | `qwen-plus-latest` | `connected` | 1820 | `-` | - |
| structured_output | `qwen-plus-latest` | `connected` | 583 | `-` | - |
| vision_analysis | `qwen3-vl-plus` | `connected` | 2114 | `-` | - |
| vision_high | `qwen3-vl-max` | `failed` | 224 | `permission_or_account_required` | model_not_found / invalid_request_error / The model `qwen3-vl-max` does not exist or you do not have access to it. |
| vision_high | `qwen-vl-max` | `connected` | 853 | `-` | - |
| omni_analysis | `qwen-omni-turbo-latest` | `connected` | 445 | `-` | - |
| audio_transcription | `paraformer-v2` | `pending_validation` | - | `pending_manual_route_or_local_whisper` | 本轮不上传音频；DashScope 音频转写需专用 SDK / 文件 URL 任务路线。 |
| fallback_text | `qwen-turbo-latest` | `failed` | 247 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied |
| fallback_text | `qwen-plus-latest` | `connected` | 773 | `-` | - |
| fallback_vision | `qwen-vl-plus-latest` | `failed` | 2408 | `permission_or_account_required` | access_denied / access_denied / Access denied. For details, see: https://help.aliyun.com/zh/model-studio/error-code#access-denied |

## 4. 边界确认

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

## 5. 下一步建议

- 如果文本、视觉、Omni 至少各有一个 `connected`，下一步可以做 1 条短视频素材解析 probe。
- 如果只有文本模型 `connected`，先做文本 / 时间码路线。
- 如果视觉模型失败，先修视觉模型名或账号权限。
- 如果 Omni 失败，不阻断抽帧 + 视觉模型路线。
- 不直接进入全量解析；全量前必须先完成小样本素材 probe。

## 6. 当前限制

本报告只证明最小 API 请求的连通性，不证明真实直播素材解析质量、长视频支持、费用、限额、速度或稳定性。
