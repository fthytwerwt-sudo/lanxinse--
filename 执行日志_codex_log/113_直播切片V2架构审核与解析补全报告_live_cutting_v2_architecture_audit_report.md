# 直播切片 V2 架构审核与解析补全执行报告

状态：`partial_completed_pending_user_review`
生成时间：2026-07-02T16:00:48+08:00

## 1. 边界与仓库

| 项目 | 结果 |
| --- | --- |
| 当前项目仓库 | `fthytwerwt-sudo/lanxinse--` |
| 本地仓库路径 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前分支 | `main` |
| 当前 remote | `origin	https://github.com/fthytwerwt-sudo/lanxinse--.git (fetch)` |
| 素材总目录 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据` |
| ffmpeg | `/opt/homebrew/bin/ffmpeg` |
| ffprobe | `/opt/homebrew/bin/ffprobe` |
| 阿里调用状态 | `reused_existing_ali_recheck_100_no_new_api_call` |
| deep analysis hard limit | `first_100_deep_analysis_hard_limit` |

## 2. 素材类别

- `ai_needed_final_video`：922
- `live_cutting_material`：4
- `negative_sample`：3
- `positive_sample`：30

## 3. 读取状态

- `blocked_unreadable_media`：1
- `read_success`：336
- `read_success_reused_existing_metadata`：622

## 4. 输出数量

| 输出 | 行数 |
| --- | ---: |
| 素材总清单 | 959 |
| 解析覆盖率表 | 959 |
| AI需要的成片前100解析补全 | 100 |
| 正负样本差异结构表 | 33 |
| 直播切片素材结构机会表 | 83 |

## 5. 关键结论

- `已确认`：旧前 100 阿里重看结果可复用，本轮没有新增阿里 API 调用，也没有保存 API 原始输出。
- `部分成立`：0 候选更可能来自固定窗口完整性闸门、缺相邻窗口合并、缺音频/字幕语义，而不是素材全废。
- `已确认`：当前旧解析缺 `content_archetype / route_decision / problem_action_bridge_seconds / tts_action_alignment / repackaging_value_score / needs_adjacent_merge / candidate_status` 等新字段。
- `待验证`：音频转写、TTS 对齐、动作专业性、审美、人感、业务转化和稳定批量运行。

## 6. 边界确认

| 边界 | 结果 |
| --- | --- |
| 是否提交媒体 | 否 |
| 是否提交 contact sheet | 否 |
| 是否提交 API 原始输出 | 否 |
| 是否提交 `.env` | 否 |
| 是否提交 API key | 否 |
| 是否写审美通过 | 否 |
| 是否写动作专业性通过 | 否 |
| 是否写业务通过 | 否 |
| 是否写稳定批量运行 | 否 |
| 是否只把前 100 条写成前 100 条 | 是 |
| 是否把超过前 100 条标为 `pending_not_analyzed` | 是 |

## 7. 验证命令

后续由 Codex 在提交前执行：

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/live_cutting_v2_architecture_audit.py`
- `python3 scripts/live_cutting_v2_architecture_audit.py --dry-run`
- `python3 scripts/live_cutting_v2_architecture_audit.py --limit 100`
- `git diff --check`
- `git status`
