# 素材类型路由与统一状态机

状态：统一合同已设计，实体与执行模块待创建

## 1. 设计原则

- 路由先于内容候选生成。
- 不确定素材不强塞 Route A 或 Route B。
- mixed 以时间段分流，不以整条素材二选一。
- AI 只提供证据和建议；确定性规则、人工覆盖和状态迁移必须显式。
- 不使用 LangGraph、LangChain 或复杂 runtime。
- 首期采用普通 Python 模块、任务清单、文件化 manifest、可重跑步骤和幂等键。
- Feishu 是操作镜像，GitHub main 是项目事实源，两者都不能替代运行中的原始执行记录。

## 2. material_route 枚举

| 值 | 中文解释 | 自动判定方向 | 输出限制 |
|---|---|---|---|
| motion_explanation | 运动＋讲解型 | 稳定目的性动作＋动作身份＋同题教学口播 | 可进入 Route A |
| speech_only | 纯口播型 | 完整语义表达为主体，缺稳定教学动作链 | 进入 Route B，正式输出必须人审 |
| mixed | 混合型 | 不同时间段分别满足 A 与 B | 必须先分段，不整条直出 |
| unknown | 无法确认 | 证据缺失、冲突或低置信度 | 只建路由审核任务 |

## 3. 自动判断依据

### 3.1 路由特征

| 特征 | motion_explanation 倾向 | speech_only 倾向 |
|---|---|---|
| purposeful_motion_ratio | 多个可命名且有循环的目的性动作 | 低，或只有普通手势 |
| action_identity_strength | 动作名、部位、工具和起止清晰 | 无稳定动作身份 |
| instruction_alignment | ASR 有动作口令/方法且与画面同题 | 口播结构不依赖画面动作 |
| semantic_chain_density | 有用途/问题/原因/方法＋动作链 | 有观点/问答/知识/销售/故事链 |
| incidental_gesture_ratio | 低 | 高 |
| visual_dependency | 去掉动作画面会损失核心教学信息 | 仅听口播仍能理解主要内容 |
| route_segment_separation | 单一路线占主导 | 若两类在不同时间段稳定存在则 mixed |

### 3.2 路由证据对象

每次判断必须保存一个 route_evidence（路由证据）对象：

- route_evidence_id、source_asset_id、route_decision_version。
- route_candidate。
- route_confidence。
- motion_evidence_count。
- speech_evidence_count。
- incidental_gesture_count。
- evidence_time_ranges。
- contradictory_evidence。
- model_version、rule_version。
- route_reason。
- route_decision_status。

### 3.3 置信度和自动继续

本合同不预设未经样本验证的固定数值阈值。实现时按以下阶段执行：

1. Phase 1 试点：所有自动路由建议都需人工确认。
2. 积累人工金标准后，离线计算每类 precision、recall、mixed 分段误差和 unknown 比例。
3. 用户确认 auto_route_threshold 和 route_margin 后，只有“单一最高路线达到阈值、与次高路线差距达到 margin、无硬冲突”才可自动继续。
4. 未达到条件一律 unknown 或 mixed_review，不得默认选择。

### 3.4 人工覆盖

人工覆盖必须创建一个 route_override（路由人工覆盖）记录和新的 route_decision_version，并保存：

- route_override_id、route_evidence_id。
- original_route、original_confidence、original_evidence。
- override_route。
- override_by、override_at、override_reason。
- affected_time_ranges。
- invalidate_existing_candidates。

若覆盖发生在候选生成后，旧候选全部标 route_superseded，不能无声复用。

## 4. mixed 分段规则

- 建 route_segment_id，每段有 start/end、material_route、confidence 和证据。
- 分段必须覆盖全部可分析时间轴，允许 noise/unassigned 段。
- A/B 段不得重叠；边界冲突进入 mixed_route_review。
- 单个段低于已确认最小时长时不自动合并到邻段，先按语义/动作完整性判断。
- 跨 A/B 段拼接默认 forbidden；只有人工反馈明确要求并留下理由时允许。
- mixed job 的子候选继承 route_segment_id，最终仍归属同一 job。

## 5. unknown 降级规则

以下任一成立就进入 unknown：

- ASR 不可用且无法判断口播性质。
- 视觉不可用且用户要求判断是否是运动教学。
- 普通手势与教学动作无法区分。
- A/B 证据同时高但无法按时间段分开。
- 自动路由未达到经验证阈值。
- 人工覆盖需要但未提供负责人。

unknown 只允许输出路由证据、待补输入和 review_task，不生成正式候选视频。

## 6. 统一数据模型

### 6.1 job（处理任务）

必填字段：

- job_id、job_version、created_at、created_by。
- source_asset_ids。
- job_status、current_step、requested_routes。
- candidate_count、review_count、final_count、error_count。
- owner、priority、due_status。
- fact_sync_status、feishu_sync_status。

一个 job 可包含多个 source_asset，也可由一个 mixed source_asset 产生多个 route_segment。

### 6.2 source_asset（原始素材）

- source_asset_id、job_id。
- source_name、source_uri、source_hash、size、duration。
- video_codec、audio_codec、has_audio、technical_probe_status。
- access_policy、ingest_status。
- material_route、route_confidence、route_decision_version。
- media_git_policy，固定为 ignored_not_committed。

### 6.3 material_route（素材路线）

- route_decision_id、source_asset_id、version。
- route_value、confidence、decision_status。
- evidence_refs、reason、rule_version、model_version。
- decided_by_type（AI/rule/human）、decided_by。
- supersedes_route_decision_id。

### 6.4 route_segment（混合型时间段）

- route_segment_id、source_asset_id。
- start_time、end_time、route_value、confidence。
- evidence_refs、boundary_reason、review_status。

### 6.5 analysis_unit（解析单元）

- analysis_unit_id、source_asset_id、route_segment_id 可空。
- unit_type：transcript、visual、semantic、interaction、technical。
- start_time、end_time、raw_content、normalized_content。
- semantic_roles、topic_id、action_topic_id。
- evidence_refs、quality_status、confidence。
- producer、model_version、rule_version。

### 6.6 candidate_clip（候选切片）

- candidate_id、candidate_version、job_id、source_asset_id。
- material_route、route_segment_id、parent_candidate_id。
- source_ranges、content_classification、structure_type、assembly_mode。
- title、summary、selection_reason、confidence_breakdown。
- candidate_status、editor_usability_status、risk_flags。
- preview_uri、preview_storage_backend、technical_probe_status。
- current_review_task_id。

### 6.7 review_task（人工审核任务）

- review_task_id、candidate_id、candidate_version。
- review_type：route、content、cut_point、action_pair、professional、business、delivery。
- review_status、assignee、created_at、claimed_at、reviewed_at。
- available_actions、required_checks、sla_status。
- latest_feedback_id、feishu_record_id、feishu_message_id。

### 6.8 feedback（人工反馈）

- feedback_id、review_task_id、candidate_id、candidate_version。
- feedback_type、feedback_text、new_classification。
- requested_start/end、target_layer。
- reviewer、created_at、client_event_id。
- application_status、result_candidate_version。

### 6.9 final_clip（正式视频）

- final_clip_id、job_id、approved_candidate_id、approved_candidate_version。
- final_version、classification、source_ranges。
- master_uri、preview_uri、storage_backend、access_policy。
- technical_probe_status、review_approval_id。
- delivery_status、delivered_at、confirmed_by。

### 6.10 execution_record（执行记录）

- execution_id、job_id、step_name、attempt。
- idempotency_key、input_hash、output_hash。
- started_at、finished_at、status、error_type、error_summary。
- retryable、next_retry_at。
- code_commit、rule_version、model_name、model_version。
- artifact_refs、failure_evidence_refs。

## 7. 实体关系

    job
    ├── 1..n source_asset
    │   ├── 1..n material_route versions
    │   ├── 0..n route_segment
    │   └── 0..n analysis_unit
    ├── 0..n candidate_clip versions
    │   └── 0..n review_task
    │       └── 0..n feedback
    ├── 0..n final_clip
    └── 1..n execution_record

final_clip 必须指向准确 candidate_version；feedback 不得只指向 candidate_id 而忽略版本。

## 8. 统一状态机

### 8.1 为什么采用多轴状态

一个 job 可能“技术导出成功，但内容全待人工”；若只用一个 completed，会重复现有盲测错误。因此状态拆为 job 主状态和五个独立轴。

### 8.2 job_status

| 状态 | 中文含义 | 进入条件 | 可自动离开 |
|---|---|---|---|
| received | 已接收 | job 与 source_asset 已登记 | 是 |
| validating | 技术预检中 | 输入可访问 | 是 |
| routing | 路由判断中 | 技术预检通过 | 是 |
| awaiting_route_review | 等待路由人工确认 | mixed/unknown/低置信度 | 否 |
| analyzing | 路线分析中 | 路由已确认 | 是 |
| candidates_ready | 候选已生成 | 至少一个有效 candidate | 是，需建 review_task |
| awaiting_review | 等待人工审核 | 存在 pending review | 否 |
| revision_requested | 要求修改 | 收到重切/重分类/重解析反馈 | 是 |
| finalizing | 正式视频生成中 | 存在 approved candidate_version | 是 |
| delivery_ready | 可交付 | final_clip 技术通过、审核链完整 | 否 |
| delivered | 已交付 | 接收人确认可访问 | 否 |
| delivered_pending_fact_sync | 已交付但事实未同步 | 交付完成、Git 同步失败/未做 | 是 |
| closed | 项目事实闭环 | 交付和 Git remote readback 均完成 | 否 |
| failed_with_evidence | 失败且有证据 | 无可恢复结果或达到失败标准 | 仅人工重新开启 |
| blocked | 阻断 | 缺关键输入/权限/设计 | 依外部条件 |

### 8.3 独立状态轴

| 轴 | 枚举示例 | 作用 |
|---|---|---|
| route_status | pending、auto_suggested、confirmed、overridden、unknown | 路由事实 |
| analysis_status | pending、running、partial、passed、failed | ASR/视觉/语义处理 |
| candidate_status | proposed、complete、partial、duplicate、rejected、superseded | 候选内容状态 |
| review_status | not_required、pending、claimed、approved、rejected、changes_requested | 人工决定 |
| delivery_status | not_ready、rendering、ready、delivered、confirmed、failed | 视频交付 |
| fact_sync_status | not_started、package_ready、committed、pushed、remote_verified、failed | Git 项目事实 |

任何一个轴通过都不得自动把其他轴写成通过。

### 8.4 关键迁移规则

| 当前状态 | 事件 | 下一状态 | 硬条件 |
|---|---|---|---|
| received | start_validation | validating | source_asset 存在 |
| validating | validation_passed | routing | 技术探针通过 |
| routing | route_low_confidence | awaiting_route_review | 不允许默认路线 |
| routing | route_confirmed | analyzing | 路由决定已版本化 |
| analyzing | candidates_generated | candidates_ready | 候选字段和技术状态完整 |
| candidates_ready | review_tasks_created | awaiting_review | review_task 数量一致 |
| awaiting_review | approve | finalizing | 审核人和 candidate_version 准确 |
| awaiting_review | request_changes | revision_requested | target_layer 和反馈类型明确 |
| revision_requested | revision_generated | awaiting_review | 新 candidate_version 已创建 |
| finalizing | final_probe_passed | delivery_ready | 技术探针、来源、审核链齐全 |
| delivery_ready | recipient_confirmed | delivered | 访问验证通过 |
| delivered | fact_sync_started | delivered_pending_fact_sync | 事实包已生成 |
| delivered_pending_fact_sync | remote_head_verified | closed | commit/push/readback 均成功 |
| 任意可执行状态 | unrecoverable_failure | failed_with_evidence | 保存失败证据 |

### 8.5 completed 禁用规则

- 不使用无定义的 completed 作为任务主状态。
- plan_count 大于 0 不能代表成功。
- editor_ready_direct 为 0 时，动作型严格盲测不得进入完成态。
- pending_manual_review 数量等于全部输出时，只能是 review_only_result 或 awaiting_review。
- closed 只表示项目事实闭环，不表示审美、健康或业务通过；这些另有人工判断记录。

## 9. 幂等与可重跑

### 9.1 idempotency_key

建议组成：

    job_id + step_name + input_hash + rule_version + model_version + parameters_hash

同一 key 已成功时返回已有 output refs，不重复生成。

### 9.2 可重跑边界

- 路由重跑生成新 route_decision_version。
- ASR/视觉/语义重跑生成新 analysis_unit version，不覆盖旧证据。
- 候选重切生成新 candidate_version。
- final_clip 重渲染生成 final_version。
- callback 重复事件按 client_event_id 去重。
- Git 事实包以 output_hash 判断是否需要新 commit。

### 9.3 重试分类

| 错误 | 自动重试 | 处理 |
|---|---|---|
| 网络短暂失败、可重试错误码 | 是，限定次数＋退避 | execution_record 记录 attempt |
| 权限不足、密钥缺失 | 否 | blocked，交人工 |
| schema/输入缺失 | 否 | blocked_input_invalid |
| 内容证据不足 | 否 | 人工复核或 partial |
| 确定性逻辑错配 | 否 | rejected_logic_mismatch |
| 视频解码失败 | 可重渲染限定次数 | 超限后 failed_with_evidence |

## 10. feedback 路由

| feedback_type | 中文含义 | target_layer | 后续动作 |
|---|---|---|---|
| approve | 通过 | review | 当前版本 approved |
| reject | 退回 | review | rejected，保留原因 |
| recut_start | 重新切开头 | cut_point | 新 candidate_version |
| recut_end | 重新切结尾 | cut_point | 新 candidate_version |
| classification_error | 分类错误 | classification | 改分类并重建结构检查 |
| speech_incomplete | 口播不完整 | semantic | 向前后合并或重新解析 |
| action_incomplete | 动作不完整 | action | 重找动作范围或降级 |
| speech_action_mismatch | 口播动作错配 | action_pair | logic_mismatch 或重新配对 |
| duplicate_content | 重复内容 | semantic/dedup | 标 duplicate_of 或缩短 |
| not_publishable | 不适合发布 | business/review | rejected_not_publishable |
| reanalyze | 需要重新解析 | route/ASR/semantic | 新分析版本 |

反馈应用失败时保持 application_status=failed，不得把 review_task 标已解决。

## 11. 飞书同步与 Git 项目事实同步

### 11.1 飞书同步

- 飞书记录保存 job/candidate/review/final 的镜像 ID。
- 系统以 client_event_id、review_task_id、candidate_version 幂等接收操作。
- 飞书写失败不丢系统状态；标 feishu_sync_status=failed 并进入失败重试表。
- 飞书不能直接修改 final_clip 或 Git 文件，必须通过受控反馈应用步骤。

### 11.2 Git 项目事实包

每个已交付 job 至少导出：

- job_summary.json 或 CSV。
- source_asset 和 route_decision 摘要。
- candidate/review/final 索引。
- execution_record 和失败摘要。
- 不含媒体、ASR 全量缓存、secret 和临时签名 URL。

Git 同步步骤：

    fact package generated
    → schema validated
    → path-limited stage
    → commit
    → push
    → remote HEAD readback

未完成 remote readback 时 fact_sync_status 不得是 remote_verified。

## 12. primary_route 和 fallback_route

primary_route：

    显式状态字段
    + 普通 Python 模块
    + 文件化 manifest / JSONL / CSV
    + 可重跑步骤
    + 幂等处理

fallback_route：

- 并发和数据量尚小时，以单 job 工作目录和 append-only execution_record 运作。
- 若未来多用户并发证明文件化 ledger 不足，是否采用 SQLite 或公司批准数据库必须另开产品决策，不由 Codex自行引入。
- 飞书不可用时使用本地/公司内网页或审核 CSV，仍保持同一 review_task/feedback 合同。

## 13. capability_status

- 已确认：现有项目需要分层状态；技术产物不代表内容通过。
- 部分成立：已有多种人工复核状态和 Git 事实闭环纪律。
- 待创建：统一实体、版本、状态迁移、幂等和反馈应用。
- 待验证：路由阈值、mixed 分段准确性、文件化 ledger 的并发边界。
- blocked：缺路由金标准、缺审核责任、缺正式字段字典。

## 14. execution_entrypoints

只设计：

- create_job.py。
- validate_source_asset.py。
- decide_material_route.py。
- split_mixed_route_segments.py。
- run_route_step.py。
- transition_job_state.py。
- apply_feedback.py。
- retry_execution_step.py。
- sync_feishu_mirror.py。
- export_git_fact_package.py。

## 15. validation_commands

| 命令类型 | 中文用途 |
|---|---|
| schema validator | 校验九个统一实体和枚举 |
| state transition tests | 拒绝非法跨状态迁移 |
| multi-axis assertions | 防止技术通过自动覆盖内容/人审/业务状态 |
| route gold-set tests | 验证四种 material_route |
| mixed timeline tests | 验证覆盖、无重叠和边界 |
| idempotency replay | 重放同一事件不重复生成 |
| feedback routing tests | 十类反馈回正确层 |
| fact package safety scan | 排除媒体、secret、ASR 缓存和临时链接 |

## 16. blocked_if_missing

- route 金标准和人工确认流程缺失。
- 实体主键、版本和来源关系未锁定。
- 状态仍以一个 completed 混合所有层。
- 人工重切会覆盖原候选而无版本。
- 飞书被当唯一状态源。
- Git 事实包包含媒体、密钥或临时签名链接。
- 实现要求引入 LangGraph、LangChain 或复杂 runtime。
