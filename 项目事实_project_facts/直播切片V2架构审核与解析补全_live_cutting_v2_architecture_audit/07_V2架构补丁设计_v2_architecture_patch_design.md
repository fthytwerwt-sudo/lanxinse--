# V2 架构补丁设计

状态：`v2_patch_design_completed_pending_implementation`
生成时间：2026-07-02T16:00:48+08:00

## 新版链路

素材入口层 → 全覆盖证据层 → 阿里多模态理解层 → 选品与内容形态路由层 → 音频 / TTS / 字幕时间轴对齐层 → 问题-动作桥接判断层 → 正负样本对照反推层 → 结构规则层 → 相邻窗口合并层 → 候选片段判断层 → 原生切片 / 动作教学再包装分流层 → 剪辑导出层 → 人工复核层 → 反馈回规则层 → GitHub 事实层

| layer_name | purpose | input | output | required_fields | blocked_if | validation |
| --- | --- | --- | --- | --- | --- | --- |
| 素材入口层 | 统一读取素材根和类别映射 | 剪辑解析数据 | material_inventory | source_category, relative_path, read_status | 素材目录缺失或越界 | inventory CSV 必填字段检查 |
| 全覆盖证据层 | 保证素材级证据不跳过 | ffprobe/旧解析/文件清单 | coverage audit | has_existing_parse, needs_reparse | 无法区分已有解析和待解析 | coverage CSV 检查 |
| 阿里多模态理解层 | 复用或调用视觉模型理解关键帧 | contact sheet 或旧阿里结果 | cleaned multimodal matrix | ali_model_called, final_status, evidence | API 不可用且无旧结果 | 调用审计或复用证据 |
| 选品与内容形态路由层 | 先判断素材适合哪种内容形态 | multimodal evidence | content_archetype route | content_archetype, route_decision | archetype unclear | 字段枚举检查 |
| 音频 / TTS / 字幕时间轴对齐层 | 判断声音、字幕和动作是否对齐 | transcript/subtitle/audio/visual timecodes | alignment status | tts_action_alignment | 缺转写且必须判断口播 | pending_audio_transcript 不得脑补 |
| 问题-动作桥接判断层 | 判断问题后是否快速接动作 | problem/action timecodes | bridge score | problem_action_bridge_seconds | 无问题或动作秒点 | bridge 秒数和证据检查 |
| 正负样本对照反推层 | 从好坏样本反推规则差异 | positive/negative samples | contrast table | matched_existing_rule, missing_new_rule | 样本不足 | matched/missing rule 检查 |
| 结构规则层 | 承接五结构和细结构规则 | 20/21/30/31/32 规则 | rule match | rule_id, must_have_evidence | 规则缺证据 | 规则引用检查 |
| 相邻窗口合并层 | 把跨窗口表达合成完整候选 | window rows | merged segment candidate | need_merge_previous, need_merge_next | 非相邻或无转写 | merge_previous/next 检查 |
| 候选片段判断层 | 给出受控候选状态 | routes + evidence | candidate table | candidate_status | 状态不在枚举 | candidate_status 枚举检查 |
| 原生切片 / 动作教学再包装分流层 | 区分 native 和 repackaging | route_decision | native/repackaging queue | route_decision | 把可包装误写成原生 | route_decision 检查 |
| 剪辑导出层 | 只导出通过技术闸门的初剪 | candidate queue | local rough cuts | export_status | 媒体提交风险 | outputs ignored + no media staged |
| 人工复核层 | 保留人审入口 | review queue | manual_review_checklist | manual_review_items | 审美/业务未确认 | 状态词检查 |
| 反馈回规则层 | 把人审结果回写规则 | review feedback | rule delta | feedback_item, affected_rule | 无反馈来源 | rule ledger 检查 |
| GitHub 事实层 | 把事实和验证落库 | CSV/MD/DOCX/report | commit/push/readback | commit_sha, remote_head | 未 push 或 remote 未回读 | git 验证 |
