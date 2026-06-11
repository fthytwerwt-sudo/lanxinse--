# Codex 执行报告：Trae 分步 Prompt 补全

任务：生成资料协助版 PDF，并补全 Trae 分步执行 Prompt

状态：`已确认` 本地文件和验证已完成；`待验证` commit / push / remote HEAD 将在本报告写入后的 Git 闭环中确认。

说明：本报告不能提前写入包含自身的最终 commit SHA，最终 Git 证据以 Codex 最终回报为准。

## 1. 本轮目标

`已确认`：新版资料包已从“执行清单口吻”改为“协助准备口吻”。

`已确认`：正样本和负样本已分开。

`已确认`：填写项已降到轻量数据：私信 / 咨询反馈、互动反馈、发布效果、是否希望 AI 学、来源线索、敏感风险。

`已确认`：完整 Trae 文件已拆为 Prompt 0 到 Prompt 7。

`待验证`：Trae 在对方电脑的本地读取能力、自动匹配来源能力、AI 后续结构解析能力。

## 2. 新版文件

| 文件 | 用途 | 状态 |
|---|---|---|
| `直播切片AI_Skill资料协助与云盘上传清单_material_collaboration_upload_checklist.md` | 新版 PDF 源文件 | `已确认` |
| `直播切片AI_Skill资料协助与云盘上传清单_material_collaboration_upload_checklist.pdf` | 新版资料协助版 PDF | `已确认` |
| `trae本地资料整理与分步解析_prompt.md` | 完整 Trae 分步执行 Prompt | `已确认` |
| `templates/直播解析表_livestream_parse_sheet.csv` | 6 场直播解析表 | `已确认` |
| `templates/正样本轻量标注表_positive_clip_labels.csv` | 正样本轻量标注表 | `已确认` |
| `templates/负样本表_negative_samples.csv` | 负样本表 | `已确认` |
| `templates/对标视频拆解表_reference_video_breakdown.csv` | 对标视频拆解表 | `已确认` |
| `templates/上传前检查表_upload_ready_checklist.csv` | 上传前检查表 | `已确认` |
| `templates/文件清单_file_manifest.csv` | 文件清单 | `已确认` |
| `templates/脱敏检查表_desensitization_checklist.csv` | 脱敏检查表 | `已确认` |

上一版 `client_execution_upload_checklist` 相关文件保留，但状态为 `superseded（已被新版替代）`。

## 3. Trae Prompt 分块

| 分块 | 内容 | 状态 |
|---|---|---|
| Prompt 0 | 初始化资料包和目录 | `已确认` |
| Prompt 1 | 效果好直播解析 prompt | `已确认` |
| Prompt 2 | 普通直播解析 prompt | `已确认` |
| Prompt 3 | 较乱直播解析 prompt | `已确认` |
| Prompt 4 | 正样本成片整理 prompt | `已确认` |
| Prompt 5 | 负样本整理 prompt | `已确认` |
| Prompt 6 | 对标视频整理 prompt | `已确认` |
| Prompt 7 | 上传前检查 prompt | `已确认` |

## 4. 验证结果

| 验证项 | 方法 | 结果 |
|---|---|---|
| PDF 存在 | `file`, `ls -lh` | `已确认` |
| PDF 页数 | `file`, `mdls` | `已确认` 4 页 |
| PDF 可读性 | `qlmanage -t -s 1200` 渲染缩略图并人工查看 | `已确认` |
| PDF 正文称呼 | 源文扫描 | `已确认` 未出现禁用称呼 |
| 正负样本 | 源文扫描 | `已确认` 已分开 |
| 专业结构必填项 | 源文扫描 | `已确认` 未要求配合方填写 |
| AI 自动解析说明 | 源文扫描 | `已确认` 包含“结构后续由 AI 自动解析” |
| 完整 Prompt 路径 | 源文扫描 | `已确认` PDF 中写明完整文件路径 |
| Prompt 0 到 Prompt 7 | 源文扫描 | `已确认` 全部存在 |
| 模板表头 | Python `csv.reader` | `已确认` 全部匹配 |
| 敏感样式 | Python 正则扫描 | `已确认` 未发现密钥样式、手机号样式、邮箱样式 |

## 5. 边界确认

- `已确认` 未读取真实视频、音频、图片素材。
- `已确认` 未上传媒体文件。
- `已确认` 未修改 `.env` 或敏感凭据文件。
- `已确认` 未修改 GPT Project 机制包。
- `已确认` 未把自动匹配能力写成已确认。
- `已确认` 未把 AI Skill 稳定能力写成已确认。

## 6. Git 状态

| 项目 | 状态 |
|---|---|
| path-limited stage | `待验证` 本报告写入后执行 |
| commit | `待验证` 本报告写入后执行 |
| push | `待验证` 本报告写入后执行 |
| remote HEAD readback | `待验证` 本报告写入后执行 |
