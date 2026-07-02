# C9623 直播切片完整验证执行报告

状态：`partial_completed_exports_ready_pending_user_review`
生成时间：2026-07-02T16:41:40+08:00

## Commands

- `python3 scripts/check_ali_config_safety.py`
- `python3 -m py_compile scripts/c9623_live_cutting_full_validation.py`
- `python3 scripts/c9623_live_cutting_full_validation.py --dry-run`
- `python3 scripts/c9623_live_cutting_full_validation.py --probe`
- `python3 scripts/c9623_live_cutting_full_validation.py --run`

## Result

| 项目 | 结果 |
| --- | --- |
| C9623 路径 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据/剪辑测试直播素材/C9623.MP4` |
| 总时长 | `01:43:03.678` |
| 全覆盖窗口 | 37 |
| 候选总数 | 43 |
| 本地导出视频 | 20 |
| 阿里视觉审计 | `reused_112_ali_visual_audit_no_new_api_call` |
| 音频转写 | `pending_audio_transcript` |
| probe_rows | 0 |

## DOCX / 人读版

- 系统 `python3` 未安装 `python-docx`，主脚本先生成 Markdown fallback。
- 已使用 Codex bundled Python 生成 `05_C9623人读版报告_c9623_human_readable_report.docx`。
- 已使用 documents skill 的 `render_docx.py` 渲染 DOCX，输出 1 页 PNG 到 ignored 目录并完成视觉检查。
- DOCX 状态：`docx_export_completed_with_render_check`。

## Validation

- `python3 scripts/check_ali_config_safety.py`：通过。
- `python3 -m py_compile scripts/c9623_live_cutting_full_validation.py`：通过。
- `python3 scripts/c9623_live_cutting_full_validation.py --dry-run`：通过。
- `python3 scripts/c9623_live_cutting_full_validation.py --probe`：通过，生成 3 个本地 ignored probe。
- `python3 scripts/c9623_live_cutting_full_validation.py --run`：通过，导出 20 条本地候选视频。
- CSV 字段与行数校验：通过。
- 导出视频 `ffprobe`：20/20 passed。
- `git diff --check`：通过。

## 边界确认

- 是否提交媒体：否。
- 是否提交 API 原始输出：否。
- 是否提交 `.env`：否。
- 是否提交 API key：否。
- 是否写审美通过：否。
- 是否写动作专业性通过：否。
- 是否写健康表达通过：否。
- 是否写业务通过：否。
- 是否写稳定批量运行：否。
