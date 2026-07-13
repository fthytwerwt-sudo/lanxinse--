# 单直播严格盲测执行报告

状态：`blind_test_failed_with_evidence`
生成时间：2026-07-13T16:59:59+08:00

## 主结论

- 唯一视频：`/Volumes/WD_BLACK/带货直播以及短视频练习/带货/6.2私房话.mp4`
- 完整 ASR：`已确认`，缓存路径 `/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/outputs/local_62_private_talk_blind_test_work/retry_motion_sample_30s/asr/full_transcript.json`（ignored_not_committed）
- 视觉动作扫描：`已确认`，视觉单元 60 个
- 最终视频：37 条，全部进入 `08_人工复核`
- 正式剪辑师可用：0 条
- 人工复核：37 条
- 严格盲测结论：`blind_test_failed_with_evidence`，原因是没有任何动作主题自动通过“讲解/方法/动作同题 + 动作循环完整 + 无跳题”的直接可用闸门。
- 用户人审：`pending_user_review`
- 审美 / 动作专业性 / 健康效果 / 业务 / 发布：`待验证`

## 源视频技术信息

- duration_seconds: `4307.466667`
- size: `1738999906`
- video: `hevc` `720x1280` `30/1`
- audio: `aac` channels=`2`
- sha256: `3fe7863367e20eaf3885dea9c8ba276e7789dcfce718c1270648a4928cc4eceb`

## 分类统计

- `01_问题回答后动作`: 0
- `02_痛点原因后动作`: 0
- `03_用途方法后动作`: 0
- `04_误区纠正后动作`: 0
- `05_讲解在前动作在后`: 0
- `06_边讲边做`: 0
- `07_已重排成讲解后动作`: 0
- `08_人工复核`: 37

## Git 与冻结边界

- 实现冻结 commit：`6c2d67290a960f7e4e1d1f28f8d3527eaa5bf682`
- 冻结前语义读取：`no`
- 冻结后核心识别逻辑修改：`no`
- 素材专用关键词 / 句子锚点 / 人工时间码：`no`
- LangGraph / LangChain / runtime：`no`

## technical_retry 记录

- 第一轮运行：默认 motion scan 合并为 1 个视觉单元，视觉模型返回 `no_action_visible`，导出视频 0 条。
- 第二轮运行：未修改核心脚本；仅将通用扫描参数调整为 `motion_sample_seconds=30`、`visual_window_seconds=20`、`max_visual_windows=60`。
- 第二轮结果：视觉单元 60 个，导出人工复核视频 37 条，正式剪辑师直接可用视频 0 条。
- 该重试没有加入素材专用关键词、动作名称、口播句子锚点或人工时间码。

## 输出索引

- 最小视频索引：`/Volumes/WD_BLACK/澜心社剪辑/lanxinse--/项目事实_project_facts/直播素材盲测_blind_test/01_6月2日私房话视频索引_62_private_talk_video_index.csv`
- 媒体文件：`ignored_not_committed`

## 视觉模型状态

- `action_visible_or_unclear`: 36
- `failed`: 1
- `no_action_visible`: 23

## 验证结果

- Python 语法：`passed`
- 通用规则测试：`7 passed`
- 阿里配置安全：`passed`
- 主程序素材专用答案扫描：`passed`
- 最终目录非 MP4 检查：`passed`
- 最终 MP4 全量技术验证：`checked=37 / failed=0`
- 最终视频 Git 忽略检查：`passed`
- ASR / work 缓存 Git 忽略检查：`passed`
- 核心识别脚本冻结后修改：`no`
