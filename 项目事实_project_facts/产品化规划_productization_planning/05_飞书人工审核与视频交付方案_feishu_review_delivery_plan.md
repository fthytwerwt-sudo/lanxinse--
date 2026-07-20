# 飞书人工审核与视频交付方案

状态：产品方案已设计；项目集成待创建；公司账号能力待验证
外部事实限制：仅引用 open.feishu.cn 官方文档
本轮行为：未创建应用、未调用 API、未填写 app_id/app_secret

## 1. 主结论

推荐产品形态：

    企业自建应用
    + 应用机器人
    + 飞书卡片
    + 多维表格
    + 视频链接/封面
    + 外部正式文件存储

视频存储选择：

- primary_route：F3 混合路线。
- fallback_route：F2 外部私有存储路线。
- conditional_pilot：F1 飞书云空间路线，仅在真实账号 probe 通过后试点。

飞书是审核操作台和协作镜像，不是项目事实源。系统的 review_task、feedback、final_clip 和 execution_record 是业务记录；GitHub main 承载经过验证的最小项目事实包。

## 2. 项目当前状态与官方能力必须分开

| 能力 | 飞书官方能力 | 本项目状态 |
|---|---|---|
| 企业自建应用 | 官方已确认可用于企业内部能力集成 | 待创建 |
| 应用机器人通知 | 官方已确认可发送消息、视频、文件和卡片 | 待创建 |
| 卡片按钮/表单回传 | 官方已确认 card.action.trigger | 待创建 |
| 多维表格记录/字段/附件 | 官方已确认存在服务端 API | 待创建 |
| 飞书云空间普通/分片上传 | 官方已确认 | 待创建，账号待验证 |
| 视频在卡片内直接播放 | 官方已确认不支持 | 禁止按内嵌播放器设计 |
| 飞书内实际视频预览稳定性 | 官方没有给本项目充分保证 | 待验证 |
| 公司租户容量、单文件最终上限、成本 | 官方页面不能给出公司账号事实 | 待验证 |
| 权限与管理员审批 | 官方确认存在两层权限约束 | 待验证 |
| 回调失败自动补推 | 卡片回调官方确认不补推 | 必须自建兜底 |

## 3. 官方能力证据

### 3.1 应用、机器人与消息

- [应用类型与能力](https://open.feishu.cn/document/home/app-types-introduction/overview)：企业自建应用适合企业内部使用，可开启机器人、网页应用、多维表格插件等能力。
- [机器人概述](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/bot-v3/bot-overview)：应用机器人可用于通知和交互。
- [消息概述](https://open.feishu.cn/document/server-docs/im-v1/introduction?lang=zh-CN)：消息 API 支持文本、文件、视频和卡片等类型。
- [自定义机器人使用指南](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN)：群自定义机器人卡片只适合 URL 跳转；本项目的审核动作应使用企业自建应用的应用机器人。

状态解释：这些页面只证明平台能力存在，不证明本项目已接通。

### 3.2 卡片交互

- [卡片回传交互回调](https://open.feishu.cn/document/feishu-cards/card-callback-communication?lang=zh-CN)：按钮或表单可触发 card.action.trigger，服务端应在 3 秒内响应；可先快速响应后延时更新。
- [飞书卡片常见问题](https://open.feishu.cn/document/common-capabilities/message-card/message-card)：不同按钮可用 key/value 区分；表单可一次回传多个字段；卡片回调不补推；卡片不支持内嵌视频直接播放，只能视频链接或封面图＋链接。
- [回调概述](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/event-subscription-guide/callback-subscription/callback-overview)：回调是同步交互，不能假定事件订阅式补推。

重要限制：

- 回调 3 秒内必须响应。
- 延时更新 token 的官方说明为有效 30 分钟、最多更新 2 次。
- 卡片回调失败不会自动重推，客户端会显示错误。
- 卡片整体数据存在大小限制，不应把完整 ASR 全塞进卡片。
- 卡片不直接播放视频；审核视频必须通过链接或封面跳转。

### 3.3 多维表格

- [创建一条记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create)。
- [更新一条记录](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update)。
- [新增字段](https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-field/create?lang=zh-CN)。
- [多维表格接入指南](https://open.feishu.cn/document/server-docs/docs/bitable-v1/notification)。

官方确认记录、字段、附件和权限相关 API 存在；但同一数据表不支持并发写，可能返回 1254291 Write conflict。批量记录操作应按全成功或全失败处理。

产品约束：

- 同一表写操作串行。
- 每次写入带 idempotency_key。
- 写冲突使用限定次数退避重试。
- Base 写成功不等于系统事实写成功；必须回读并比对关键字段。
- 不把无代码自动化当首期硬依赖；公司租户套餐、权限和可用动作待账号验证。

### 3.4 云空间上传和下载

- [上传文件](https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/upload_all?lang=zh-CN)：普通上传到云空间指定文件夹，文件非空且不超过 20 MB；大于 20 MB 需分片。
- [上传素材](https://open.feishu.cn/document/server-docs/docs/drive-v1/media/upload_all?lang=zh-CN)：可向文档或多维表格上传点上传图片、视频等素材，普通上传上限 20 MB。
- [分片上传文件—预上传](https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/multipart-upload-file-/upload_prepare)。
- [分片上传文件—上传分片](https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/multipart-upload-file-/upload_part)。
- [分片上传文件—完成上传](https://open.feishu.cn/document/server-docs/docs/drive-v1/upload/multipart-upload-file-/upload_finish)。
- [下载文件](https://open.feishu.cn/document/server-docs/docs/drive-v1/download/download?lang=zh-CN)。
- [增加协作者权限](https://open.feishu.cn/document/server-docs/docs/permission/permission-member/create)。

产品约束：

- 大于 20 MB 必须预上传、逐片上传、完成上传。
- 分片不得并发；上传事务过期需从预上传重开。
- API scope 与实际文件夹/文件资源权限是两层权限。
- 官方页面未给出可作为本项目事实的统一最终单文件上限、公司租户容量、价格或真实 MP4 预览稳定性。
- 不得写“飞书视频预览稳定通过”。

## 4. 飞书审核台信息架构

### 4.1 处理任务表

| 字段 | 类型建议 | 用途 |
|---|---|---|
| job_id | 文本，唯一 | 任务编号 |
| source_name | 文本 | 素材名称 |
| material_route | 单选 | motion_explanation / speech_only / mixed / unknown |
| route_confidence | 数字 | 路由置信度 |
| job_status | 单选 | 当前处理状态 |
| candidate_count | 数字 | 候选数量 |
| final_count | 数字 | 正式视频数量 |
| pending_review_count | 数字 | 待人工数量 |
| created_at | 日期时间 | 创建时间 |
| owner | 人员 | 负责人 |
| error_status | 文本 | 当前错误摘要 |
| system_record_version | 数字 | 系统镜像版本 |
| fact_sync_status | 单选 | Git 事实同步状态 |

### 4.2 候选视频审核表

| 字段 | 类型建议 | 用途 |
|---|---|---|
| candidate_id | 文本，唯一 | 候选编号 |
| candidate_version | 数字 | 当前候选版本 |
| job_id | 关联/文本 | 所属任务 |
| preview_cover | 图片/附件 | 封面 |
| preview_url | 超链接 | 视频查看入口 |
| preview_expires_at | 日期时间 | 签名链接过期时间 |
| content_classification | 单选 | 候选分类 |
| asr_summary | 多行文本 | 口播摘要 |
| transcript_url | 超链接 | 完整口播/上下文查看入口 |
| selection_reason | 多行文本 | AI 选择理由 |
| ai_confidence | 数字 | AI 置信度 |
| risk_flags | 多选 | 健康、隐私、优惠等风险 |
| review_status | 单选 | pending / approved / changes_requested / rejected |
| reviewer | 人员 | 审核人 |
| feedback | 多行文本 | 人工意见 |
| requested_start | 文本/数字 | 开头调整 |
| requested_end | 文本/数字 | 结尾调整 |
| new_classification | 单选 | 人工修改分类 |
| system_record_version | 数字 | 防止旧页面覆盖新状态 |

### 4.3 正式视频交付表

| 字段 | 类型建议 | 用途 |
|---|---|---|
| final_clip_id | 文本，唯一 | 正式视频编号 |
| job_id | 关联/文本 | 所属任务 |
| approved_candidate_id/version | 文本 | 来源候选版本 |
| preview_url | 超链接 | 审核/预览入口 |
| master_file_url | 超链接 | 高清文件地址 |
| storage_backend | 单选 | feishu / external / hybrid |
| classification | 单选 | 正式分类 |
| reviewer | 人员 | 审核人 |
| delivery_status | 单选 | ready / delivered / confirmed / failed |
| exported_at | 日期时间 | 导出时间 |
| access_policy | 文本 | 下载与访问规则 |
| access_probe_status | 单选 | 是否实际验证可访问 |

### 4.4 失败与重试表

| 字段 | 类型建议 | 用途 |
|---|---|---|
| execution_id | 文本，唯一 | 执行记录 |
| job_id | 文本 | 所属任务 |
| failed_step | 单选 | 失败步骤 |
| error_type | 单选 | 权限、网络、内容、技术等 |
| error_summary | 多行文本 | 脱敏错误 |
| retryable | 复选框 | 是否可重试 |
| retry_count | 数字 | 重试次数 |
| next_retry_at | 日期时间 | 下次重试 |
| owner | 人员 | 当前负责人 |
| resolution_status | 单选 | open / retrying / resolved / blocked |
| system_record_version | 数字 | 镜像版本 |

## 5. 卡片交互设计

### 5.1 新任务/待审核卡片

卡片只放必要摘要：

- job_id、素材名、路线、候选数量、待审数量。
- 候选封面、分类、ASR 摘要、AI 理由和风险标记。
- 查看完整视频、查看原始上下文、查看口播文字的链接。
- 通过、退回、需要重切、分类错误按钮。
- 表单入口填写切点和人工意见。

完整 ASR 和长列表放网页或多维表格，不塞入卡片。

### 5.2 回调事件

每个按钮/表单回传：

- client_event_id。
- review_task_id。
- candidate_id、candidate_version。
- action：approve / reject / recut / classification_error。
- reviewer_id。
- form_values。
- system_record_version。

服务端动作：

1. 3 秒内校验签名、事件格式和幂等键。
2. 已处理事件直接返回已有结果。
3. 快速返回 Toast 或空响应。
4. 耗时重切、上传和正式渲染放任务队列。
5. 系统记录成功后再更新卡片和多维表格。
6. 回调失败时提供“重新提交”和“打开审核详情页”兜底。

### 5.3 一次性动作与并发

- approved/rejected 后将按钮改为不可操作状态。
- 若旧卡片提交的 candidate_version 不是 current_version，拒绝并提示刷新。
- 同一 review_task 只接受第一个合法终态；后续修改需显式 reopen。
- 多维表格写按 table_id 串行，避免 Write conflict。

## 6. 视频存储路线比较

| 维度 | F1 飞书云空间 | F2 外部私有存储 | F3 混合路线 |
|---|---|---|---|
| 普通上传 | 官方确认 ≤20 MB | 由存储服务决定 | 小代理可按实际选飞书或轻量存储 |
| 大文件 | 串行分片，整体上限待验证 | 适合大文件/分片 | 高清走外部 |
| 上传速度 | 受飞书上传接口、租户网络与串行分片约束，待实测 | 可按存储区域、网络和分片策略压测 | 审核代理优先快传，高清异步上传；两端均需记录耗时 |
| 预览 | 卡片不内嵌；云空间实际 MP4 体验待验证 | 需提供受控播放页/链接 | 封面＋链接，代理与高清分层 |
| 权限 | 飞书资源权限复杂，待账号 probe | 签名链接/SSO/ACL 自控 | 两套映射需清晰 |
| 安全 | 依赖租户、应用权限和云空间 ACL；不得假设默认安全 | 密钥、签名、加密、日志和留存策略由公司控制 | 最小权限、短期链接、审计日志；任何一端失败均不得公开降级 |
| 链接过期 | 飞书 token/权限管理 | 临时签名链接需续签 | preview_expires_at 必填 |
| 下载体验 | 待真实账号验证 | 可按公司需求控制 | 正式高清走外部 |
| 成本/容量 | 公司租户事实未知 | 存储、流量和转码成本可测 | 两者平衡 |
| 运维 | 飞书集成和权限 | 播放页、签名、审计 | 维护映射和同步 |
| 失败重试 | 受上传事务和频控约束 | 由项目控制 | 可在两个后端间降级 |
| 当前项目状态 | 待创建、待验证 | 待创建 | 待创建 |

## 7. 主推荐 F3 合同

### 7.1 存储分层

- review_proxy：低码率审核代理视频或封面；可放飞书云空间、公司轻量存储或外部受控存储，具体由账号 probe 决定。
- master_file：正式高清文件，放公司批准的外部私有对象存储、NAS 或文件服务器。
- Feishu Base：只保存状态、封面、可访问链接、权限/过期信息和 file_token（如有）。
- 卡片：只展示封面、摘要、按钮和跳转。

### 7.2 必填映射字段

- storage_backend。
- preview_url。
- preview_expires_at。
- master_file_url。
- master_file_access_policy。
- feishu_file_token，可空。
- upload_status。
- preview_probe_status。
- final_clip_id、candidate_id、candidate_version。

### 7.3 fallback_route

飞书上传、预览或权限任一失败时：

1. 保留系统 candidate/review 状态。
2. 改用 F2 外部受控链接。
3. 更新 preview_url、access_policy 和 expires_at。
4. 在失败与重试表记录飞书错误。
5. 通知审核人使用新链接。
6. 不把“链接已生成”写成“审核已通过”。

## 8. F1 条件试点

只有以下 probe 全部通过，F1 才可在少量审核代理视频上试点：

- 公司管理员批准应用、机器人和所需权限。
- 目标文件夹写权限和审核人读权限成立。
- 小于 20 MB 普通上传通过。
- 大于 20 MB 分片上传通过且可恢复。
- 代表 MP4 在 PC、iOS/Android 可打开、播放、拖动且音画同步。
- 权限外用户不能访问。
- 租户容量、单文件最终上限和成本可接受。
- 上传失败、事务过期、checksum 错误和配额不足均能正确分类。

正式高清文件是否放飞书必须由用户在 probe 后另行确认。

## 9. probe_required（飞书试点最小验证）

1. 创建企业自建应用并完成管理员审批。
2. 验证应用机器人向指定用户/群发送卡片。
3. 验证通过、退回、重切、分类错误和意见表单回调。
4. 验证 3 秒快速响应、延时更新、重复点击幂等和按钮禁用。
5. 建四张多维表格，验证应用读写、附件和高级权限。
6. 验证同表串行写、1254291 退避重试和批量全成全败。
7. 上传小于 20 MB、大于 20 MB、代表候选和代表高清四种文件。
8. 在 PC、iOS/Android 检查首帧、拖动、音画、下载和权限。
9. 验证 F2/F3 签名链接打开、过期、续签和撤权。
10. 核验公司租户真实容量、最终单文件上限、存储成本和生命周期。

## 10. 权限与安全

- app_id、app_secret、token 只能从环境变量或密钥服务读取，禁止进入 Git、飞书表或执行报告。
- API scope 和资源权限分别验证。
- preview_url 使用最小权限和合理有效期。
- Base 不保存永久公开 master_file_url。
- 所有回调验证来源、去重并记录审核人。
- 错误摘要脱敏，禁止记录 token 或签名参数。
- 视频访问撤销后，飞书镜像同步为 access_revoked。
- 飞书管理员操作、业务审核和 Git 提交人分别留痕。

## 11. 失败处理

| 失败 | 是否自动重试 | 处理 |
|---|---|---|
| 回调超时/失败 | 不依赖飞书补推 | 客户端兜底＋系统失败表 |
| 重复按钮事件 | 否 | 幂等返回既有结果 |
| Base Write conflict | 是，限定次数串行退避 | 超限后人工处理 |
| 普通上传 >20 MB | 否 | 改分片上传 |
| upload_id 过期 | 是，从预上传重开 | 记录新 attempt |
| 权限不足 | 否 | blocked_feishu_permission_missing |
| 容量不足/最终上限 | 否 | 降级 F2 |
| 视频不能稳定预览 | 否 | 降级封面＋外部播放页 |
| 签名链接过期 | 可续签 | 更新镜像但不改审核结果 |
| 人工长期未处理 | 提醒/升级 | 永不自动通过 |

## 12. allowed_codex_autonomy

- 在已锁字段内实现 Base 映射、回调 schema、幂等和错误分类。
- 调整卡片布局、字段顺序和普通提示文案。
- 对可重试网络错误实现限定次数退避。
- 在 F3 主路线内选择不改变安全和业务语义的代理视频技术参数。

## 13. forbidden_codex_guessing

- 不得自行创建正式应用、申请权限或写入真实 secret。
- 不得假设飞书视频预览稳定、容量足够或成本可接受。
- 不得改用群自定义机器人承载审核回传。
- 不得让飞书 Base 成为唯一事实源。
- 不得因卡片点击就直接标业务通过。
- 不得无限重试权限、配额、checksum 或确定性失败。
- 不得自行把 F1 升为正式主路线。

## 14. blocked_if_missing

- 企业管理员、试点用户和权限范围未确认。
- 回调接收方式、签名校验和幂等合同未实现。
- review_task/candidate_version 尚未统一，却要接按钮审核。
- 视频访问权限和过期策略缺失。
- 公司没有批准的正式高清视频存储。
- 未做真实账号/设备 probe 却要求确认飞书预览通过。
