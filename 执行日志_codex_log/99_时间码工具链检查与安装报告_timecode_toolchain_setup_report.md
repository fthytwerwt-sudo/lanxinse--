# 时间码工具链检查与安装报告

状态：`待验证`，本报告写入时尚未完成 commit / push / remote HEAD readback；最终 Git 证据以本轮最终回报为准。
任务类型：`timecode_toolchain_check_and_install`
生成时间：2026-06-23 23:44:42 CST

## 1. 本轮结论

`已确认`：当前仓库、分支和 remote 正确，`git pull --ff-only` 结果为 `Already up to date.`。

`已确认`：`ffmpeg` 已存在，不需要通过 Homebrew 安装。

`已确认`：`python3` 已存在，已创建项目内虚拟环境 `.venv_timecode/`。

`已确认`：已在 `.venv_timecode/` 内安装 `faster-whisper`，并通过 import 验证。

`部分成立`：工具层已具备进入小样本 timecode probe 的基础条件；这不代表时间码质量、中文识别质量或剪辑可用性通过。

`已确认`：本轮未读取视频内容、未转写视频、未修改原始素材、未提交媒体文件。

## 2. 影响面检查

| 项目 | 结果 |
|---|---|
| 当前 `pwd` | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 仓库根目录 | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| 当前 branch | `main` |
| 当前 remote | `origin https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| 当前素材目录 | `/Volumes/WD_BLACK/澜心社剪辑/剪辑解析数据` 存在；本轮只检查存在性 |
| 当前工作区状态 | 有大量既有 dirty files；本轮只允许 stage `.gitignore` 和本报告 |
| 是否存在 `.venv_timecode/` | 已创建，且被 `.gitignore` 忽略 |
| 是否存在 `.gitignore` | 已存在，本轮补充时间码工具链忽略规则 |
| 是否有媒体文件可能被 stage | 已通过 staged 文件检查防止混入 |
| 本轮允许修改文件 | `.gitignore`、本报告 |
| 本轮禁止修改文件 | 原始素材、视频/音频/图片/zip、上一轮素材清单、`.venv_timecode/` |

## 3. 读取文件

- `AGENTS.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/00_GPT_Project上传说明_readme.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/上传清单_manifest.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/00_协作协议_collaboration_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/01_三层架构与事实源边界_three_layer_source_boundary.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/02_P0-P1-P2锚点与抗漂移机制_anchor_priority_anti_drift.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/03_GitHub事实源读取机制_github_fact_source_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/04_Codex执行落库机制_codex_execution_to_repo_protocol.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/07_输出硬规则与中文语义对齐_output_hard_rules.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/08_Codex工作区与远端仓库硬边界_codex_workspace_remote_boundary.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/22_真实意图澄清闸门机制_true_intent_clarification_gate.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/23_六层需求确认与实现设计闸门机制_six_layer_requirement_implementation_gate.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/24_Codex长期执行单模板_codex_task_template.md`
- `GPT项目资料同步包_gpt_project_mechanism_sync/25_AGENTS机制迁移说明_agents_mechanism_migration_note.md`
- `素材整理_asset_management/03_人工确认_manual_review/人工确认问题清单_manual_review_questions.md`
- `素材整理_asset_management/03_人工确认_manual_review/txt时间码抽检结果_timecode_probe.csv`

## 4. 工具检查与安装结果

| 工具 | 状态 | 版本 / 证据 | 是否本轮安装 |
|---|---|---|---|
| `ffmpeg` | `已确认` 可用 | `ffmpeg version 8.1`，路径来自 `/opt/homebrew/Cellar/ffmpeg/8.1_1` | 否，已存在 |
| Homebrew | `已确认` 存在 | `Homebrew 6.0.1` | 否 |
| `python3` | `已确认` 可用 | `Python 3.9.6` | 否，已存在 |
| `.venv_timecode` | `已确认` 可用 | `.venv_timecode/bin/python --version` 返回 `Python 3.9.6` | 是，项目内创建 |
| `pip` | `已确认` 可用 | `.venv_timecode` 内 `pip 26.0.1` | 是，从 `21.2.4` 升级 |
| `faster-whisper` | `已确认` 可 import | `faster_whisper_ok`，版本 `1.2.1` | 是 |
| `ctranslate2` | `已确认` 随依赖安装 | `4.8.0` | 是，pip 依赖 |
| `onnxruntime` | `已确认` 随依赖安装 | `1.19.2` | 是，pip 依赖 |
| `av` | `已确认` 随依赖安装 | `15.1.0` | 是，pip 依赖 |
| `torch` | `部分成立` | 未单独安装；当前 `faster-whisper` 依赖链未要求 `torch` | 否 |

## 5. 安装过程说明

- `ffmpeg` 已存在，因此未执行 `brew install ffmpeg`。
- 使用 `python3 -m venv .venv_timecode` 创建项目内虚拟环境。
- 首次 venv 启动时，外置盘生成的 `._distutils-precedence.pth` 等 AppleDouble 元数据文件导致 Python site 初始化失败。
- 已只在 `.venv_timecode/` 内清理 `._*` 元数据文件；这是虚拟环境内部缓存清理，不涉及原始素材。
- pip 安装完成后再次清理 `.venv_timecode/` 内 AppleDouble 元数据文件 5492 个，随后 venv Python、pip、`faster_whisper` import 均验证通过。

## 6. `.gitignore` 更新

`已确认`：本轮补充以下忽略规则，防止虚拟环境、模型缓存和音频缓存误入 Git：

```text
.venv_timecode/
.cache/
素材整理_asset_management/04_时间码_timecode/音频缓存_audio_cache/
素材整理_asset_management/04_时间码_timecode/model_cache/
```

`已确认`：原有媒体忽略规则已覆盖 `*.mp4`、`*.mov`、`*.m4v`、`*.avi`、`*.wav`、`*.mp3`、`*.aac`、`*.zip`、`*.tar`、`*.gz`、`*.cache`、`.DS_Store`、`._*`。

## 7. 验证命令与结果

| 命令 | 结果 |
|---|---|
| `pwd` | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| `git rev-parse --show-toplevel` | `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--` |
| `git branch --show-current` | `main` |
| `git remote -v` | `origin https://github.com/fthytwerwt-sudo/lanxinse--.git` |
| `git pull --ff-only` | `Already up to date.` |
| `ffmpeg -version` | `ffmpeg version 8.1` |
| `python3 --version` | `Python 3.9.6` |
| `.venv_timecode/bin/python --version` | `Python 3.9.6` |
| `.venv_timecode/bin/python -m pip --version` | `pip 26.0.1` |
| `.venv_timecode/bin/python -c "import faster_whisper; print('faster_whisper_ok')"` | `faster_whisper_ok` |
| `.venv_timecode` ignore check | `.gitignore:2:.venv_timecode/` 命中 |
| timecode cache ignore check | `音频缓存_audio_cache/` 和 `model_cache/` 命中 |
| 素材目录存在性检查 | `material_dir_exists=yes` |

## 8. 边界确认

- 是否修改原始素材：否。
- 是否读取视频内容：否。
- 是否转写视频：否。
- 是否生成时间码：否。
- 是否进入视频内容分析：否。
- 是否进入五结构片段筛选：否。
- 是否生成成片：否。
- 是否连接 DaVinci：否。
- 是否安装 WhisperX：否。
- 是否安装 Homebrew：否。
- 是否提交 `.venv_timecode/`：否，待 Git stage 检查确认。
- 是否提交媒体文件：否，待 Git stage 检查确认。
- 是否把工具安装成功写成时间码质量通过：否。

## 9. 是否可以进入小样本 timecode probe

`部分成立`：从工具层看，可以进入下一轮 2 个正样片 + 2 个负样片的 timecode probe。

`待验证`：中文识别质量、片段分段是否适合剪辑、输出 timecode 是否可用于五结构候选筛选，必须等下一轮小样本 probe 后判断。

## 10. Blocked 状态

- blocked：无。
- `blocked_homebrew_missing`：未触发。
- `blocked_python_missing`：未触发。
- `blocked_pip_install_failed`：未触发。

## 11. Commit / push / remote HEAD 状态

- commit hash：`待验证`，本报告写入时尚未提交；实际提交号以最终回报为准。
- push 状态：`待验证`。
- remote HEAD：`待验证`。

## 12. 下一步建议

1. 下一轮做 2 个正样片 + 2 个负样片的 timecode probe。
2. 小样本 probe 只验证能否生成带 `start/end` 的转写文本和分段质量，不进入全量转写。
