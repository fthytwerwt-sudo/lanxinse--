# 阿里视觉模型迁移验证报告

状态：`permission_or_account_required_or_model_not_available（视觉候选已迁移到 qwen3 优先，但全部最小连接失败）`
生成时间：2026-06-26T18:06:20+08:00
任务类型：`ali_vision_model_migration_live_test`

## 1. 执行结果

| 项目 | 结果 |
|---|---|
| 当前仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| `.env` 是否存在 | 是 |
| API key 是否读取 | yes，只记录掩码，不写完整 key |
| API base URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 是否修改 `.env` | 否 |
| 是否上传真实素材 | 否 |
| 是否跑全量解析 | 否 |
| 是否提交 `api_outputs/` | 否 |
| 视觉候选测试数 | 6 |
| connected 数 | 0 |
| failed 数 | 6 |
| 最终状态 | `permission_or_account_required_or_model_not_available` |

## 2. 配置修正

`vision_analysis` 候选已调整为：

```text
qwen3-vl-plus
qwen-vl-plus
qwen-vl-plus-latest
```

`vision_high` 候选已调整为：

```text
qwen3-vl-max
qwen-vl-max
qwen-vl-max-latest
```

## 3. 视觉候选最小测试结果

| role | model_name | status | latency_ms | error_type | 中文说明 | 下一步动作 |
|---|---|---:|---:|---|---|---|
| `vision_analysis` | `qwen3-vl-plus` | `failed` | 560 | `model_not_available` | 当前 endpoint / 账号下模型名不可用或未映射 | 检查模型名、地域和工作空间 endpoint |
| `vision_analysis` | `qwen-vl-plus` | `failed` | 535 | `model_not_available` | 当前 endpoint / 账号下模型名不可用或未映射 | 检查模型名、地域和工作空间 endpoint |
| `vision_analysis` | `qwen-vl-plus-latest` | `failed` | 284 | `permission_or_account_required` | `access_denied` | 去百炼控制台确认模型权限、工作空间权限和 base_url 地域 |
| `vision_high` | `qwen3-vl-max` | `failed` | 310 | `permission_or_account_required` | `access_denied` | 去百炼控制台确认模型权限、工作空间权限和 base_url 地域 |
| `vision_high` | `qwen-vl-max` | `failed` | 1914 | `model_not_available` | 当前 endpoint / 账号下模型名不可用或未映射 | 检查模型名、地域和工作空间 endpoint |
| `vision_high` | `qwen-vl-max-latest` | `failed` | 261 | `permission_or_account_required` | `access_denied` | 去百炼控制台确认模型权限、工作空间权限和 base_url 地域 |

## 4. base_url 地域提示

已确认：`.env` 当前仍是通用 DashScope OpenAI-compatible endpoint：

```text
https://dashscope.aliyuncs.com/compatible-mode/v1
```

待验证：阿里官方推荐部分地域使用 workspace-specific domain（工作空间专属域名）。例如东京地域可能是：

```text
https://{WorkspaceId}.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1
```

本轮未发现 `.env` 中有 `WorkspaceId`，也没有用户授权我修改真实 `.env`，所以没有擅自改 `ALI_API_BASE_URL`。

## 5. 官方文档参考

- [阿里云百炼 Qwen-VL OpenAI 兼容接口](https://www.alibabacloud.com/help/en/model-studio/qwen-vl-compatible-with-openai)：当前示例优先出现 `qwen3-vl-plus`。
- [OpenAI Chat API Reference](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions)：OpenAI-compatible Chat API 可用于 Qwen-VL 等模型族。

## 6. 边界确认

| 边界 | 结果 |
|---|---|
| 是否打印完整 key | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否提交 token | 否 |
| 是否提交 `api_outputs/` | 否 |
| 是否上传真实素材 | 否 |
| 是否跑全量解析 | 否 |
| 是否确认视觉能力可用 | 否 |

## 7. 下一步

先去百炼控制台确认：

- `qwen3-vl-plus` / `qwen3-vl-max` 是否在当前账号和工作空间开通。
- 当前工作空间是否需要专属 `base_url`。
- 当前地域是否应使用 `ap-northeast-1.maas.aliyuncs.com` 这类 workspace-specific domain。

在视觉模型接通前，不进入真实素材视觉 probe，也不直接全量解析。

## 8. commit / push 状态

本报告生成时处于提交前状态。最终 commit、push 和 remote HEAD readback 以本轮 Codex 最终回报为准。
