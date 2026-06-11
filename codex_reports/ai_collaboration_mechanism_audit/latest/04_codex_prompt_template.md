# 04 可复用 Codex Prompt 模板

```text
# Goal 目标

本轮任务类型：

本轮真实目标：

本轮不是：

最终要产出的文件 / 结果：

# Context 上下文

项目名称：

当前 workspace：

当前事实源：

相关背景：

P0（用户本轮明确输入）：

P1（当前项目事实 / 验证证据）：

P2（历史记忆 / 外部资料 / 旧项目参考）：

冲突规则：
- P0 > P1 > P2
- P2 不得冒充当前项目事实
- 未验证必须标 `待验证`

# Constraints 边界

允许：
- 

禁止：
- 不要修改未授权文件
- 不要删除、移动、重命名现有文件，除非本轮明确要求
- 不要调用外部 API，除非本轮明确允许
- 不要访问互联网，除非本轮明确允许
- 不要安装新依赖，除非本轮明确允许
- 不要把局部修复扩大成全局重写
- 不要把技术通过写成内容 / 审美 / 业务通过

允许修改范围：
- 

禁止修改范围：
- 

# 真实意图澄清

本轮真正要判断 / 完成：

本轮不判断 / 不完成：

成功标准：

失败标准：

停止条件：

# Implementation design 实现设计层

primary_route：

fallback_route：

capability_status：
- confirmed：
- partially_true：
- pending_validation：

probe_required：

allowed_codex_autonomy：

forbidden_codex_guessing：

required_inputs：

required_outputs：

execution_entrypoints：

validation_commands：

blocked_if_missing：

# Impact check 影响面检查

执行前必须先检查并在报告中记录：

1. 当前工作目录：
2. 目标路径是否存在：
3. Git 状态是否干净 / 是否有无关改动：
4. 允许修改文件：
5. 禁止修改文件：
6. 将读取的文件数量：
7. 将修改 / 新建的文件数量：
8. 是否涉及依赖、API、网络、账号、权限、secret：
9. 是否发现冲突、重复、过期、未完成内容：

# Must read 必须读取

在执行前必须读取：

1. 
2. 
3. 

如果任一必读文件不存在或不可读，必须 blocked，不得猜测内容。

# Execution steps 执行步骤

1. 定位目标文件 / 目录。
2. 建立文件 inventory。
3. 读取 must read 和相关文件。
4. 做影响面检查。
5. 按 primary_route 执行。
6. 如 primary_route 失败，按 fallback_route 或 blocked_if_missing 处理。
7. 运行验证命令。
8. 汇总证据和剩余风险。
9. 按 Output 回报格式输出。

# Done when 完成标准

任务只有在以下条件都满足时才算完成：

1. 已按边界完成指定产物。
2. 未修改禁止范围。
3. 已读取所有必读文件。
4. 已运行约定验证命令。
5. 验证结果已记录。
6. 已明确区分：
   - local_file_exists
   - validation_passed
   - committed
   - pushed
   - remote_head_verified
   - user_review_passed
   - business_goal_passed
7. 所有未确认内容已标 `待验证` 或 `推测`。

# Blocked if 阻断条件

遇到以下情况必须停止并报告，不得硬做：

- 目标路径不存在且无法合理定位。
- 必读文件不可读。
- P0 / P1 / P2 无法区分。
- 缺真实意图。
- 缺 Implementation design。
- 缺 primary_route / fallback_route / capability boundary / probe decision。
- 继续执行会扩大影响面。
- 涉及权限、API、余额、账号、secret，且本轮未明确允许。
- 外部资料没有提供到本轮输入或项目事实源。
- 用户人审 / 业务判断缺失，但任务要求写“通过”。

Blocked 回报必须包含：
- what_was_tried
- what_was_found
- missing_input
- exact_path_or_permission_needed

# Output 回报格式

请用中文回报，保留命令、路径、字段名、状态词的英文原词。

## 执行结果

- status：
- task_type：
- workspace：
- files_read：
- files_changed：
- files_created：
- files_skipped：
- blocked：
- blocked_reason：

## 验证证据

- commands：
- result：
- failed_items：

## 完成度边界

- local_file_exists：
- validation_passed：
- committed：
- pushed：
- remote_head_verified：
- user_review_passed：
- business_goal_passed：

## 关键发现

- 已确认：
- 部分成立：
- 待验证：
- 推测：

## 变更文件

- 

## 剩余风险 / 下一步

- 
```
