# 五结构完整成片判断标准

状态：`部分成立，待人工复核`
生成时间：2026-06-24 03:18:25 CST
适用主线：`五结构连接成片版`

## 1. 文件定位

这份文件是澜心社自动剪辑项目的“五结构完整成片判断标准”。它用于后续 Codex 盲测、人工复核、片段候选判断、结构连接和首条 Beta 成片设计。

它不是逐条转写稿，不是最终业务验收报告，也不是最终剪辑方案。它只把 33 个本地带时间码转写中的正负样片结构机制沉淀为可复用判断标准。

核心原则：不要只判断每几秒属于什么结构；必须判断 `structure_block` 是否完整、结构之间是否承接、整条视频是否形成观看闭环。

## 2. 证据来源与边界

- 来源：33 个本地带时间码转写 JSON，均来自 `素材整理_asset_management/04_时间码_timecode/本地转写输出_local_transcripts/`，本轮只读读取，不提交完整正文。
- 样本分布：正样片 30 个，负样片 3 个，总转写段 848 个。
- 用户本轮 P0：用户已确认上一轮时间码抽检可以进入完整分析。
- 文本结构分析不等于画面剪辑通过。画面变化、动作示范、字幕、节奏、语气、表情仍需人工复核。
- 自动转写不等于业务事实确认。价格、权益、退款、效果承诺、强功效表达必须人工或客户确认。
- 正负样片只是归纳样本，不代表批量稳定能力。

file_ref: `00_五结构成片主线锁定_final_route_lock.md` 确认主线和禁止声明。
file_ref: `02_五结构字段字典_final_field_dictionary.md` 确认五结构枚举、风险字段和 `unmapped_clip`。
file_ref: `03_阶段闸门与回退规则_stage_gate_guardrails.md` 确认阶段闸门和“技术可拼接不等于内容通过”。

## 3. 分析层级

### 3.1 speech_segment（语音转写段）

`speech_segment` 只用于定位原话和时间点。它不能直接等同于剪辑片段，也不能直接等同于结构块。一个几秒钟的语音段常常只是半个动作、半个解释或半句承接。

evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:14.960, end_time=00:01:10.000, sample_type=正样片, evidence_summary=一个动作教学需要连续步骤、感受提示和呼吸节奏共同成立

### 3.2 structure_block（结构块）

`structure_block` 才是剪辑判断的基本单位。它通常由多个连续 speech_segment 组成，必须能独立承担一个功能：提出问题、解释方法、回应疑问、建立信任、引导行动，或明确标为 `unmapped_clip`。

evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:19.360, end_time=00:01:10.000, sample_type=正样片, evidence_summary=站位、动作方向、感受提示、呼吸提示要连在一起

### 3.3 structure_sequence（结构链路）

`structure_sequence` 判断多个结构块之间如何承接。看点不是“有没有五类标签”，而是上一块是否自然推出下一块：问题推出方法，方法推出结果，案例推出信任，信任推出行动。

evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:00.240, end_time=00:00:24.240, sample_type=正样片, evidence_summary=开头提出痛点和十分钟承诺，随后立刻进入站位动作

### 3.4 full_video_integrity（完整成片性）

`full_video_integrity` 判断整条视频是否形成观看闭环：开头有理由，中段有兑现，结尾有收束。短视频可以只有一个主结构，但也必须让观众知道“为什么看、看到了什么、下一步做什么”。

evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:00.000, end_time=00:00:17.400, sample_type=正样片, evidence_summary=短视频也能形成问题、方法、工具和互动收束

## 4. 观众观看路径

推荐用以下路径检查一条视频是否成立：`被吸引 -> 听懂问题 -> 相信方法 -> 打消顾虑 -> 愿意行动`。

- `traffic_hook` 负责让观众停下来，但必须给出后续兑现空间。evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:00.000, end_time=00:00:04.600, sample_type=正样片, evidence_summary=用时间预期引发继续观看
- `course_teaching` 负责让观众听懂问题和方法，不能只剩口号或动作次数。evidence_ref: source_id=src_scan_0033, pair_id=pair_0016, start_time=00:00:00.000, end_time=00:00:31.000, sample_type=正样片, evidence_summary=围绕改善问题给出认识身体、探索开发、持续强化三层路径
- `case_trust` 负责让观众相信“这不是空说”，但真实性和风险仍要复核。evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:00:05.600, end_time=00:01:35.200, sample_type=正样片, evidence_summary=学员年龄、关系背景、学习动机、练习后反馈形成案例链
- `objection_response` 负责处理“有没有用、适不适合我、为什么这样做”。evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:00.000, end_time=00:00:29.600, sample_type=正样片, evidence_summary=先提出有用吗，再说明压力、循环、能力和双方感受
- `conversion_push` 负责行动提醒，但必须承接前面的价值或信任。evidence_ref: source_id=src_scan_0045, pair_id=pair_0022, start_time=00:00:46.920, end_time=00:00:55.240, sample_type=正样片, evidence_summary=先完成三点判断，再邀请留言和进入课堂

## 5. 单结构成片标准

单结构成片不是单句成片。它可以只承担一个结构功能，但必须在内部完成最小闭环。

### 5.1 单独 traffic_hook

完整标准：开头必须提出明确痛点、反差、结果感或继续观看理由，并在同一条视频内至少给出一点兑现。只抛强刺激问题，不给解释或承接，属于 `hook_unfulfilled` 风险。

- 入选：问题明确、对象明确、后续有方法/解释/结果承接。
- 排除：只有欲望结果、没有为什么、没有如何做、没有后续兑现。
- 证据：evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:00.000, end_time=00:00:04.600, sample_type=正样片, evidence_summary=用时间预期引发继续观看
- 反例：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:01.640, sample_type=负样片, evidence_summary=只给结果愿望，未建立为什么或如何做到

### 5.2 单独 course_teaching

完整标准：必须包含问题、原因、方法、步骤中的至少三个要素；动作类内容必须保留站位、方向、感受、呼吸或注意事项。只保留一句动作口令，会破坏教学完整性。

- 入选：观众看完能知道“为什么做”和“怎么做”。
- 排除：只有动作次数和确定结果。
- 证据：evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:14.960, end_time=00:01:10.000, sample_type=正样片, evidence_summary=从站位、方向、感受、呼吸到重复练习形成一组教学块
- 反例：evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:00.000, end_time=00:00:24.280, sample_type=负样片, evidence_summary=重复动作加确定结果，缺少原因、条件和适用边界

### 5.3 单独 objection_response

完整标准：必须先承认或提出疑问，再给出解释依据和边界。它不是强行说“有用”，而是回答观众为什么可以信、什么时候需要谨慎。

- 入选：疑问 -> 回答 -> 依据 -> 引导。
- 排除：用强承诺替代解释。
- 证据：evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:00.000, end_time=00:00:29.600, sample_type=正样片, evidence_summary=先提出有用吗，再说明压力、循环、能力和双方感受

### 5.4 单独 case_trust

完整标准：必须有案例背景、变化过程、结果反馈和意义归纳。只说“很多人有效”不够，必须能看到为什么这个案例能支撑当前主张。

- 入选：人群背景、前后变化、学习/实践过程、可信边界。
- 排除：只有结果，没有过程或来源。
- 证据：evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:00:05.600, end_time=00:01:35.200, sample_type=正样片, evidence_summary=学员年龄、关系背景、学习动机、练习后反馈形成案例链

### 5.5 单独 conversion_push

完整标准：必须有铺垫、权益或学习资源说明、适合人群或行动提醒。它可以短，但不能压过前面的价值，不能制造未确认的稀缺或效果承诺。

- 入选：价值已给出，行动提醒自然出现。
- 排除：开头直接卖，或在没有解释时强推结果。
- 证据：evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:55.360, end_time=00:01:11.400, sample_type=正样片, evidence_summary=前文解释后，转到完整视频、学习和实践反馈

## 6. 多结构组合成片标准

多结构组合不是把五类片段拼满，而是让观众路径连续。

### 6.1 traffic_hook -> course_teaching

判断标准：钩子提出的问题或承诺，必须由紧随其后的教学块兑现。中间如果换话题，需要桥接字幕说明“现在开始练/现在解释原因”。

evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:00.240, end_time=00:00:24.240, sample_type=正样片, evidence_summary=开头提出痛点和十分钟承诺，随后立刻进入站位动作

### 6.2 traffic_hook -> case_trust

判断标准：钩子提出结果感后，可以接案例证明“为什么值得继续看”。但案例必须服务于钩子，不能变成另一条故事。

evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:00:05.600, end_time=00:01:35.200, sample_type=正样片, evidence_summary=学员年龄、关系背景、学习动机、练习后反馈形成案例链

### 6.3 case_trust -> conversion_push

判断标准：案例不能突然跳到卖课，要先把案例意义归纳成“可学习/可复制/可跟练”的理由，再给行动入口。

evidence_ref: source_id=src_scan_0059, pair_id=pair_0029, start_time=00:00:18.760, end_time=00:00:47.960, sample_type=正样片, evidence_summary=学员实践反馈转到掌握技巧和底层逻辑

### 6.4 objection_response -> conversion_push

判断标准：先把疑问解释清楚，再给学习资源或咨询入口。没有解释就转化，会像强推。

evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:00.000, end_time=00:00:29.600, sample_type=正样片, evidence_summary=先提出有用吗，再说明压力、循环、能力和双方感受
evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:55.360, end_time=00:01:11.400, sample_type=正样片, evidence_summary=前文解释后，转到完整视频、学习和实践反馈

### 6.5 course_teaching -> conversion_push

判断标准：教学给出足够价值后，转化才是“下一步学习/练习”的延伸。转化语不能替代教学，也不能新增未被前文支撑的效果承诺。

evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:53.520, end_time=00:01:11.400, sample_type=正样片, evidence_summary=讲完价值后再说完整课程和实践

### 6.6 高风险或不推荐连接

- `traffic_hook -> conversion_push`：如果中间没有解释、案例或信任，容易成为硬卖。
- `case_trust -> course_teaching`：可以用，但必须说明案例中哪一点需要被方法化。
- `unmapped_clip -> conversion_push`：不推荐；上下文缺失时直接转化风险高。
- 动作演示 -> 强结果承诺：必须人工复核画面、动作正确性和业务事实。

反例：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=动作和结果之间缺少人群、原因、风险边界

## 7. 五结构逐项判断标准

### 7.1 traffic_hook（引流钩子）

结构目的：建立观看理由，让目标观众愿意继续看。

入选标准：痛点、反差、结果感、时间预期或问题足够清楚，并且后面能兑现。evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:00.000, end_time=00:00:04.600, sample_type=正样片, evidence_summary=用时间预期引发继续观看

排除标准：只有刺激词、只有结果口号、没有对象、没有兑现。evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:01.640, sample_type=负样片, evidence_summary=只给结果愿望，未建立为什么或如何做到

证据要求：至少引用开头 3-8 秒和后续兑现块各一个 evidence_ref。

常见误判：把文件名里的“标题感”当作钩子；把一句强结果当作完整引流；把无承接的开场误判为可直接开片。

最小完整表达单元：钩子本身 + 至少一个兑现方向。不能只剪第一句。

剪辑边界：从观众能听懂“为什么停下”的地方开始，到后续进入解释/方法/案例前结束；若钩子和方法连续，边界应覆盖到兑现开始。

适合位置：opening，也可作为中段重新抓注意力的再钩子。

需要人工复核：标题党感、强功效、敏感表达、画面与文案是否一致。

负样片对照：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=钩子指向结果，但后续没有足够解释和边界

状态：`已确认`（基于文本结构），画面表现 `待人工复核`。

### 7.2 course_teaching（课程讲解）

结构目的：提供实质内容，让观众知道问题是什么、为什么发生、怎么做。

入选标准：包含问题、原因、方法、步骤；动作类要包含站位、方向、感受或注意事项。evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:14.960, end_time=00:01:10.000, sample_type=正样片, evidence_summary=从站位、方向、感受、呼吸到重复练习形成一组教学块

排除标准：只有动作次数、只有“做了就会怎样”、没有适用条件和解释。evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:00.000, end_time=00:00:24.280, sample_type=负样片, evidence_summary=重复动作加确定结果，缺少原因、条件和适用边界

证据要求：至少引用一个完整教学块，而不是单个 speech_segment。

常见误判：把“前后移动 100 次”这种口令当完整课程；把结果承诺当方法；把短视频中间一段孤立剪出导致观众不知道为什么做。

最小完整表达单元：问题/目标 + 操作步骤 + 关键感受或注意点。

剪辑边界：从动作或方法的前置条件开始，到该方法完成一次闭环或进入下一主题为止。

适合位置：body 主体，也可在 hook 后立即出现。

需要人工复核：动作示范是否正确、画面是否能看清、字幕是否覆盖关键动作点。

正样片证据：evidence_ref: source_id=src_scan_0033, pair_id=pair_0016, start_time=00:00:00.000, end_time=00:00:31.000, sample_type=正样片, evidence_summary=围绕改善问题给出认识身体、探索开发、持续强化三层路径

状态：`已确认`（文本结构），动作画面 `待人工复核`。

### 7.3 objection_response（异议回应）

结构目的：处理观众的怀疑、犹豫、误区或反向问题。

入选标准：先提出或承认疑问，再给解释依据、适用边界和下一步引导。evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:00.000, end_time=00:00:29.600, sample_type=正样片, evidence_summary=先提出有用吗，再说明压力、循环、能力和双方感受

排除标准：没有疑问对象；只说“有用”；用强结果承诺代替解释。evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:01.840, end_time=00:00:17.000, sample_type=负样片, evidence_summary=只用动作次数推导结果，缺少回应质疑的证据链

证据要求：疑问本身和解释依据必须都能定位到时间码。

常见误判：把普通讲解当异议回应；把“当然有用”单句当完整回应；忽略风险边界。

最小完整表达单元：质疑/疑问 + 回答 + 至少一个理由。

剪辑边界：从疑问出现处开始，到解释完成并进入资源/行动之前结束。

适合位置：trust_or_objection，也适合 conversion 前化解顾虑。

需要人工复核：医疗、功效、敏感承诺、个人经验是否被误作事实。

状态：`部分成立`。现有样本有明显证据，但异议类型还需要更多直播场景补充。

### 7.4 case_trust（案例信任）

结构目的：用案例、实践反馈或生活场景建立可信度。

入选标准：有背景、过程、变化和意义归纳；能支撑前文主张。evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:00:05.600, end_time=00:01:35.200, sample_type=正样片, evidence_summary=学员年龄、关系背景、学习动机、练习后反馈形成案例链

排除标准：只说“很多人都有效”；没有人群背景；没有过程；结果过强且无法复核。

证据要求：至少有一个案例背景证据和一个变化/反馈证据。

常见误判：把夸张结果当案例；把单句反馈当案例；忽略真实性和适用人群边界。

最小完整表达单元：案例对象 + 问题/动机 + 行动/过程 + 反馈/意义。

剪辑边界：从案例对象或场景出现处开始，到讲者完成意义归纳处结束。

适合位置：body 后段、trust_or_objection，尤其适合接 conversion。

需要人工复核：案例真实性、授权、效果边界、是否过度承诺。

正样片证据：evidence_ref: source_id=src_scan_0059, pair_id=pair_0029, start_time=00:00:03.600, end_time=00:00:30.640, sample_type=正样片, evidence_summary=会员群实践和学员反馈支撑方法兴趣

状态：`部分成立`。文本结构可用，案例真实性 `待客户确认`。

### 7.5 conversion_push（促单转化）

结构目的：在价值、信任或异议处理之后给出行动提醒。

入选标准：前文已完成价值交付或信任铺垫；行动提醒清楚；不新增未确认权益或效果承诺。evidence_ref: source_id=src_scan_0045, pair_id=pair_0022, start_time=00:00:46.920, end_time=00:00:55.240, sample_type=正样片, evidence_summary=先完成三点判断，再邀请留言和进入课堂

排除标准：未铺垫就卖；用恐惧、虚假稀缺或强承诺促单；业务事实无法确认。

证据要求：必须同时引用转化前的价值块和行动提醒块。

常见误判：把“评论区留言”都当促单；忽略它前面是否有足够价值；把工具出现当成交。

最小完整表达单元：价值/信任铺垫 + 行动入口 + 风险边界。

剪辑边界：从转化承接句开始，到行动提醒结束；不要把未解释的强效果句拼进转化。

适合位置：conversion / closing。

需要人工复核：价格、权益、退款、课程边界、效果承诺。

正样片证据：evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:55.360, end_time=00:01:11.400, sample_type=正样片, evidence_summary=前文解释后，转到完整视频、学习和实践反馈

状态：`部分成立`。文本承接可判断，业务事实 `待客户确认`。

### 7.6 unmapped_clip（无法映射片段）

结构目的：防止把不适合的片段强塞进五结构。

入选标准：无法判断结构、缺上下文、转写异常、语言不匹配、风险过高、或只是音乐/闲聊/异常段。evidence_ref: source_id=src_scan_0067, pair_id=pair_0031, start_time=00:00:09.180, end_time=00:00:15.680, sample_type=负样片, evidence_summary=英文音乐歌词与五结构文本目标不匹配

排除标准：不是垃圾桶；如果能明确承担钩子、讲解、异议、信任或转化，就不应标 unmapped。

证据要求：必须写 `unmapped_reason`，例如 `context_missing`、`language_mismatch`、`visual_or_text_mismatch_pending`。

常见误判：为了凑五结构，把英文音乐、动作碎片、强结果口号强行标成钩子或转化。

最小完整表达单元：不适用；它是安全状态，不进入成片候选，除非人工补证后重新分类。

剪辑边界：保留原时间码范围，等待人工复核，不进入 EDL。

适合位置：候选池外，或人工复核队列。

状态：`已确认`（防错规则），具体片段是否可另用 `待人工复核`。

## 8. 结构块边界识别规则

1. 结构块从功能开始处开始：观众能听出“现在在提出问题/讲方法/讲案例/促行动”的第一个时间点。
2. 结构块到功能完成处结束：该问题、方法、案例或行动提醒完成最小闭环。
3. 不能只剪一句话的情况：动作教学、案例、异议回应、转化承接、任何需要上下文才不误导的内容。
4. 用 `start_time / end_time` 精准定位时，要先确定 `structure_block`，再回到 speech_segment 精修边界。
5. 判断结构块是否被剪坏：如果剪后需要观众脑补主语、原因、动作条件、风险边界或行动对象，就是被剪坏。

证据：evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:19.360, end_time=00:01:10.000, sample_type=正样片, evidence_summary=站位、动作方向、感受提示、呼吸提示要连在一起

## 9. 结构连接与桥接规则

### 9.1 问题承接

当上一块提出问题，下一块必须回答问题，不能直接跳到结论或成交。evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:00.240, end_time=00:00:24.240, sample_type=正样片, evidence_summary=开头提出痛点和十分钟承诺，随后立刻进入站位动作

### 9.2 结果承接

当上一块给结果感，下一块要解释结果从哪里来。否则容易变成过度承诺。evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:05.600, end_time=00:00:10.600, sample_type=负样片, evidence_summary=结果表达缺少案例、机制或过程支撑

### 9.3 方法承接

当上一块给方法，下一块可以接动作示范、注意事项、案例反馈或学习入口。evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:53.520, end_time=00:01:11.400, sample_type=正样片, evidence_summary=讲完价值后再说完整课程和实践

### 9.4 信任承接

案例或反馈之后，要把案例意义归纳出来，再转行动。evidence_ref: source_id=src_scan_0059, pair_id=pair_0029, start_time=00:00:18.760, end_time=00:00:47.960, sample_type=正样片, evidence_summary=学员实践反馈转到掌握技巧和底层逻辑

### 9.5 异议承接

回应疑问后可以进入转化，但转化必须是“进一步学习/练习/咨询”，不能新增未解释的强承诺。evidence_ref: source_id=src_scan_0047, pair_id=pair_0023, start_time=00:00:00.000, end_time=00:00:29.600, sample_type=正样片, evidence_summary=先提出有用吗，再说明压力、循环、能力和双方感受

### 9.6 转化承接

促单前必须有价值、信任或解释铺垫；如果只有钩子和促单，中间需要补讲解或案例。evidence_ref: source_id=src_scan_0045, pair_id=pair_0022, start_time=00:00:46.920, end_time=00:00:55.240, sample_type=正样片, evidence_summary=先完成三点判断，再邀请留言和进入课堂

### 9.7 桥接字幕何时需要

- 两个结构块主题不同，但可由同一观众问题连接时，需要桥接字幕。
- 从案例转方法、从讲解转成交、从痛点转动作时，需要桥接字幕。
- 桥接字幕只能说明承接关系，不能虚构视频里没有的承诺或事实。

### 9.8 三类断裂

- 硬切断裂：前后主题直接跳转，观众不知道为什么换话题。
- 情绪断裂：前一块情绪还在痛点/信任，后一块突然促单或强刺激。
- 逻辑断裂：结论出现，但中间缺少原因、方法或条件。

反例：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=动作和结果之间缺少人群、原因、风险边界

## 10. 正样片学习点

1. 正样片常把开头做成明确观看理由，而不是只喊口号。evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:00.000, end_time=00:00:04.600, sample_type=正样片, evidence_summary=用时间预期引发继续观看
2. 正样片的教学块会保留操作链和感受链，尤其动作类内容不只是一句口令。evidence_ref: source_id=src_scan_0001, pair_id=pair_0001, start_time=00:00:14.960, end_time=00:01:10.000, sample_type=正样片, evidence_summary=从站位、方向、感受、呼吸到重复练习形成一组教学块
3. 正样片的信任建立通常依赖案例背景、过程和反馈，而不是孤立结果。evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:00:05.600, end_time=00:01:35.200, sample_type=正样片, evidence_summary=学员年龄、关系背景、学习动机、练习后反馈形成案例链
4. 正样片的转化更自然地出现在解释或信任之后，而不是一开头硬卖。evidence_ref: source_id=src_scan_0045, pair_id=pair_0022, start_time=00:00:46.920, end_time=00:00:55.240, sample_type=正样片, evidence_summary=先完成三点判断，再邀请留言和进入课堂
5. 正样片也不等于绝对正确；涉及规模、效果、身体改善等表达时仍需客户或人工复核。evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:02:20.680, end_time=00:02:31.440, sample_type=正样片, evidence_summary=规模和效果类表达需要客户或业务事实确认

## 11. 负样片失败类型

### hook_unfulfilled（钩子未兑现）

现象：开头给出目标或结果，但后续没有解释为什么、怎么做、适合谁。

为什么影响完整成片：观众被吸引后得不到兑现，会觉得内容空或像广告。

如何避免：钩子后必须接方法、解释、案例或明确行动路径。

证据：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=钩子指向结果，但后续没有足够解释和边界

剪辑处理建议：可作为开头素材备选，但必须接一个能兑现的教学或案例块。

### structure_incomplete（结构不完整）

现象：只有动作、次数、结果，缺少原因、条件、注意事项。

为什么影响完整成片：观众无法判断动作是否适合自己，也无法判断结果是否可信。

如何避免：补齐问题、原因、方法、步骤，或降级为动作素材待人工复核。

证据：evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:00.000, end_time=00:00:24.280, sample_type=负样片, evidence_summary=动作、次数、结果重复出现，但结构停在单点动作

### transition_break（结构断裂）

现象：多个动作或结论并列，但没有递进关系。

为什么影响完整成片：看起来像素材堆叠，不能形成观看路径。

如何避免：每个动作之间增加“为什么换动作/这个动作解决什么”的承接。

证据：evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:03.840, end_time=00:00:18.880, sample_type=负样片, evidence_summary=多次“又一个”并列，缺少递进和承接解释

### context_missing（上下文缺失）

现象：缺少适合人群、动作条件、风险边界或前因后果。

为什么影响完整成片：片段单独看容易误导。

如何避免：剪辑时保留前置说明，或标 `unmapped_clip` 等待补证。

证据：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:01.640, end_time=00:00:08.320, sample_type=负样片, evidence_summary=不知道适合谁、怎么做、注意什么

### hard_sell_too_early（成交过早）

现象：工具、课程或行动入口出现得太早，前面价值铺垫不足。

为什么影响完整成片：观众还没相信方法，就被推向行动。

如何避免：先给方法、结果边界或案例，再给行动入口。

证据：evidence_ref: source_id=src_scan_0004, pair_id=pair_0032, start_time=00:00:08.200, end_time=00:00:12.100, sample_type=正样片, evidence_summary=工具出现较早，需依赖前后解释避免像硬推

### proof_missing（缺少信任证据）

现象：给出结果，但没有案例、机制或过程支撑。

为什么影响完整成片：结果像口号，难以建立信任。

如何避免：补案例、补机制解释，或降低承诺强度。

证据：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:05.600, end_time=00:00:10.600, sample_type=负样片, evidence_summary=结果表达缺少案例、机制或过程支撑

### risk_overclaim（承诺过强）

现象：用确定性表达承诺身体改善或效果。

为什么影响完整成片：高转化但高风险，可能越过客户和合规边界。

如何避免：标 `needs_manual_check=yes`，业务事实状态只能是 `待客户确认` 或 `待验证`。

证据：evidence_ref: source_id=src_scan_0064, pair_id=pair_0030, start_time=00:00:01.840, end_time=00:00:24.280, sample_type=负样片, evidence_summary=多处确定性结果表达需业务和合规复核

### single_point_only（只有单点，没有完整表达）

现象：只有一个观点或一个刺激句，不能独立完成结构。

为什么影响完整成片：观众得到的是观点碎片，不是完整视频。

如何避免：只能作为钩子或中段素材，必须接解释、案例或行动。

证据：evidence_ref: source_id=src_scan_0053, pair_id=pair_0026, start_time=00:00:00.000, end_time=00:00:07.129, sample_type=正样片, evidence_summary=一个观点短句可做钩子，但不能直接当完整标准

### visual_or_text_mismatch_pending（画面与文本是否匹配待复核）

现象：动作类片段文字看似成立，但无法仅凭文本确认画面动作、节奏、字幕是否匹配。

为什么影响完整成片：自动剪辑最终依赖画面和声音，不只是文本。

如何避免：进入人工画面复核；未复核前不得写审美通过或剪辑可用。

证据：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=动作类文本必须回看画面验证动作匹配

## 12. minimum_complete_unit（最小完整表达单元）

定义：一个片段被剪出后，至少还能让观众理解“这段在解决什么、用什么方法、为什么可信、下一步是什么”。

不同结构的最小单元：

- `traffic_hook`：痛点/反差/结果感 + 兑现方向。
- `course_teaching`：问题/目标 + 方法步骤 + 关键注意点。
- `objection_response`：疑问 + 回答 + 依据。
- `case_trust`：对象/背景 + 过程 + 反馈/意义。
- `conversion_push`：价值承接 + 行动入口 + 风险边界。
- `unmapped_clip`：不形成最小完整单元，只保留证据等待复核。

证据：evidence_ref: source_id=src_scan_0033, pair_id=pair_0016, start_time=00:00:00.000, end_time=00:00:31.000, sample_type=正样片, evidence_summary=改善类内容至少保留问题、原因路径和方法层级

## 13. 文本结构通过 ≠ 画面剪辑通过

当前分析主要基于转写文本和时间码。它可以判断结构、承接、风险和候选边界，但不能替代画面复核。

仍需人工复核：画面变化、字幕重点、镜头切换、停顿、语气、表情、动作示范、音乐节奏、口型和转写是否一致。

因此本轮禁止写“审美通过”“人感通过”“可直接剪辑”。

证据：evidence_ref: source_id=src_scan_0063, pair_id=pair_0033, start_time=00:00:00.000, end_time=00:00:10.600, sample_type=负样片, evidence_summary=动作类短片仅凭文字无法验证动作画面是否匹配

## 14. 风险与业务事实边界

高转化但高风险的片段不能直接进入最终候选。涉及价格、权益、退款、课程交付、效果承诺、强功效表达、敏感人群时，必须人工或客户确认。

业务事实未确认时，只能写 `待客户确认` 或 `待验证`。

风险优先于转化价值；如果一个片段同时有强转化和强风险，先进入风险复核，不进入最终成片候选。

证据：evidence_ref: source_id=src_scan_0009, pair_id=pair_0004, start_time=00:02:20.680, end_time=00:02:31.440, sample_type=正样片, evidence_summary=规模和效果类表达需要客户或业务事实确认

## 15. AI 和人工分工

AI / Codex 负责：

- 读取带时间码转写。
- 合并 speech_segment 为 structure_block 候选。
- 归纳结构规则和失败类型。
- 标记风险和 `unmapped_clip`。
- 生成候选、证据矩阵、盲测评分表。

人工负责：

- 听审中文识别准确度。
- 复核画面、动作、字幕和节奏。
- 判断审美、人感和客户品牌调性。
- 确认业务事实、课程权益、退款和效果边界。
- 决定最终发布或首条 Beta 是否通过。

file_ref: `03_阶段闸门与回退规则_stage_gate_guardrails.md` 明确用户未做人审不得写审美、人感或业务通过。

## 16. 盲测评分表说明

盲测一条新视频时，不要先逐秒贴标签，而要按四层分析：

1. 先看整条视频想完成什么结构目标。
2. 再把 speech_segment 合并成 structure_block。
3. 判断 structure_sequence 是否承接。
4. 最后判断 full_video_integrity 是否闭环。

盲测维度见：`07_盲测评分表_blind_review_rubric.csv`。

关键通过线：结构识别清楚、单结构完整、多结构承接自然、观众路径闭合、风险已标、画面和业务事实留给人工复核。

## 17. 下一步执行建议

如果要进入正式片段分析，需要输入：33 个本地带时间码转写、素材配对表、风险规则、以及用户确认的五结构标准。

如果要进入首条 Beta 成片设计，需要额外验收：结构候选池、风险复核、人工画面复核、桥接字幕草案、首条成片大纲，而不是只看几秒语音段。

仍为 `待验证` 的状态：画面剪辑效果、字幕节奏、中文识别逐句准确性、业务事实、审美/人感、批量稳定能力。

## 附录 A. 本轮输出索引

- Markdown 源文件：`05_五结构完整成片判断标准_human_readable_standard.md`
- Word 文档：`05_五结构完整成片判断标准_human_readable_standard.docx`
- 证据矩阵：`06_正负样片结构证据矩阵_positive_negative_structure_evidence_matrix.csv`
- 盲测评分表：`07_盲测评分表_blind_review_rubric.csv`

## 附录 B. 证据矩阵说明

证据矩阵中的 `evidence_summary` 只保留短摘要，不复制完整转写正文。完整转写仍为 local-only，不进入 GitHub。
