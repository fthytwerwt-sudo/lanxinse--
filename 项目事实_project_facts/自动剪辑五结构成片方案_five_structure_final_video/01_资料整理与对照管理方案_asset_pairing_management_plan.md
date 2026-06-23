# 资料整理与对照管理方案

状态：`已确认`
适用范围：五结构连接成片版的首轮资料整理、素材对照和缺口检查

## 1. 管理原则

`已确认`：原始素材不改动，不移动、不删除、不重命名。

`已确认`：视频、txt、数据表和人工对照卡必须通过清单配对，不能只靠 Finder 里文件挨着放来判断。

`已确认`：每组素材必须有 `source_id`；每个视频、txt、数据表和对照卡都通过 `source_id` 串联。

`已确认`：如果创建对照目录，只创建轻量 Markdown / CSV 文档，不复制大视频。

`已确认`：`mp4`、`mov`、`wav`、`mp3`、`zip` 等媒体或压缩包不得 stage / push 到 GitHub。

## 2. 推荐目录结构

```text
素材整理_asset_management/
├── 00_原始素材_raw_assets/
├── 01_素材对照_pair_review/
├── 02_素材清单_manifest/
├── 03_切片分析_clip_analysis/
└── 04_成片决策_final_video_decision/
```

目录用途：

| 目录 | 用途 | Git 边界 |
|---|---|---|
| `00_原始素材_raw_assets/` | 本地原始素材入口，可放完整直播录屏、样本成片、转写文本。 | 默认不入 Git。 |
| `01_素材对照_pair_review/` | 人工查看层，记录哪些视频和 txt 可能对应。 | 只放轻量文档。 |
| `02_素材清单_manifest/` | 存放素材总清单、配对表、缺失异常、解析不明。 | 可入 Git。 |
| `03_切片分析_clip_analysis/` | 后续记录钩子、痛点、卖点、信任点、逼单点分析。 | 只放结构化表和报告。 |
| `04_成片决策_final_video_decision/` | 后续放成片大纲、EDL 草案、字幕标题和桥接说明。 | 只放轻量文档。 |

## 3. source_id 规则

`source_id` 是素材唯一编号，不等于文件名。

推荐格式：

```text
src_YYYYMMDD_序号
```

如果缺日期，则使用扫描顺序：

```text
src_scan_0001
```

同一组视频和 txt 通过 `pair_id` 关联，但每个物理文件仍有自己的 `source_id`。

## 4. 配对规则

配对只做文件级候选判断，不代表内容解析通过。

| 情况 | pair_status | 处理方式 |
|---|---|---|
| 同目录下同名 stem 的视频和 txt 一一对应 | `已配对` | 可进入后续人工抽检。 |
| 有视频但无 txt | `缺文本` | 不进入转写字段验收，记录缺口。 |
| 有 txt 但无视频 | `缺视频` | 不进入视频内容判断，记录缺口。 |
| 一个视频对应多个 txt 或反向多候选 | `多候选` | 必须人工确认。 |
| 文件名相似但不完全一致 | `待人工确认` | 不强行配对。 |
| AppleDouble、缓存、非预期格式 | `不适用` | 标记为非预期或忽略候选。 |

## 5. 对照卡规则

后续可以在 `01_素材对照_pair_review/` 为每个 `pair_id` 建轻量对照卡：

```text
pair_id:
video_source_id:
text_source_id:
topic_guess:
timecode_status:
manual_check_result:
next_action:
```

对照卡只写判断，不复制原始媒体，不改原始文件名。

## 6. 首轮整理输出

首轮至少生成：

- `素材总清单_asset_inventory.csv`
- `素材配对表_pair_manifest.csv`
- `缺失与异常清单_missing_or_conflict_report.md`
- `解析不明与字段缺口清单_parse_unclear_gap_report.md`

如果没有明确素材目录，则只保留表头模板，并在报告中标记 `blocked_material_scan_missing_input`。

## 7. 风险边界

文件存在不等于素材可用。

视频和 txt 文件名相近不等于内容对应。

txt 存在不等于带时间码。

样本成片存在不等于完整直播录屏存在。

文件级配对通过不等于五结构候选足够。
