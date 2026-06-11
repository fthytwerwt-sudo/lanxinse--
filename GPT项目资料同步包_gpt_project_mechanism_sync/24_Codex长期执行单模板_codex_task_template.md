# Codex 长期执行单模板

## 文件定位

本文件是当前项目长期复用的 Codex 下发模板。

本文件只承载模板，不承载项目事实。使用时必须替换为本轮真实目标、路径、边界、验证命令和输出要求。

```text
# Goal 目标

本轮任务类型：

本轮真实目标：

本轮不是：

最终产物：

# Context 上下文

当前项目：

当前 workspace：

当前分支：

当前事实源：

P0（用户本轮明确输入）：

P1（GitHub main 当前事实 / 验证证据）：

P2（历史记忆 / 旧项目机制 / 外部资料）：

冲突规则：
- P0 > P1 > P2
- GPT Project 机制包只管机制
- GitHub main 当前文件才是项目事实
- 旧项目只迁移机制，不迁移事实

# Constraints 边界

允许：
- 待填写

禁止：
- 不要复制旧项目事实
- 不要写入当前项目未验证事实
- 不要上传 secret、媒体、缓存、运行产物
- 不要删除、移动、重命名未授权文件
- 不要扩大影响面

允许修改范围：
- 待填写

禁止修改范围：
- 待填写

# 六层需求确认

## 1. 目标层

本轮真正要达成：

本轮不做：

## 2. 机制层

触发条件：

禁止条件：

降级条件：

待验证能力：

## 3. 实现设计层

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

## 4. 流程层

执行顺序：

是否需要多候选 / 最小测试 / 用户回审：

GPT 判断：

Codex 执行：

用户确认：

## 5. 判断标准层

技术通过：

内容通过：

审美 / 人感通过：

失败标准：

## 6. 反馈层

方向错回：

路线错回：

执行错回：

权限 / API / 依赖失败：

blocked 条件：

# Impact check 影响面检查

执行前必须记录：

1. 是否可以访问目标仓库：
2. 当前工作目录 `pwd`：
3. `git rev-parse --show-toplevel`：
4. 当前分支：
5. 当前 remote：
6. 当前路径是否位于“澜心社剪辑”文件夹内：
7. remote 是否指向 `fthytwerwt-sudo/lanxinse--`：
8. 当前 git status：
9. 是否有同名目录或覆盖风险：
10. 是否存在外部工作区创建风险：
11. 是否存在误 push 到其他仓库风险：
12. 将读取哪些文件：
13. 将新增 / 修改哪些文件：
14. 哪些内容属于配合机制：
15. 哪些内容属于项目事实，必须排除：
16. 是否涉及 secret、媒体、缓存、运行产物：

# Must read 必须读取

1. 待填写
2. 待填写
3. 待填写

如果必读文件不存在或不可读，必须 blocked。

# Execution steps 执行步骤

1. 进入目标仓库并确认分支。
2. 拉取最新 `main`。
3. 读取 Must read 文件。
4. 做影响面检查。
5. 按 primary_route 执行。
6. 如 primary_route 不成立，按 fallback_route 或 blocked_if_missing 处理。
7. 运行验证命令。
8. 检查是否混入项目事实、旧项目事实、secret、媒体、缓存。
9. path-limited `git add` 本轮相关文件，禁止 `git add .`。
10. commit。
11. push。
12. remote HEAD readback。

# Done when 完成标准

1. 目标产物已生成。
2. 未修改禁止范围。
3. 未混入旧项目事实。
4. 未混入当前项目未验证事实。
5. 未上传 secret、媒体、缓存、运行产物。
6. 验证命令通过。
7. commit 完成。
8. push 完成。
9. remote HEAD 已验证。
10. 最终 `git status` clean。

# Blocked if 阻断条件

- 无法访问目标仓库。
- 无法读取必需来源。
- 已有同名目录且存在覆盖风险。
- 无法区分机制和项目事实。
- 生成内容混入旧项目事实。
- 生成内容混入当前项目未验证事实。
- 缺真实意图。
- 缺实现设计层。
- 当前路径不在“澜心社剪辑”文件夹内。
- remote 不指向 `fthytwerwt-sudo/lanxinse--`。
- 用户未授权但任务需要在外部路径工作。
- 用户未授权但任务需要上传到其他仓库。
- push 失败。
- 没有 push 权限。
- 远端 HEAD 无法验证。

# Output 回报格式

## 执行结果

- 当前项目仓库：
- 本地仓库路径：
- 新增 / 修改路径：
- 读取文件数：
- 生成文件数：
- 是否成功 push：
- push status：
- remote HEAD verified：
- 当前 git status：

## 文件清单

- 待填写

## 验证证据

- commands：
- result：
- remote HEAD：

## 边界确认

- 是否只迁移机制：
- 是否排除旧项目事实：
- 是否排除当前项目事实：
- 是否发现敏感内容：

## 下一步建议

- 待填写
```

## 模板使用提醒

如果执行单缺实现设计层，不要用更长 prompt 硬推，必须先补六层需求确认，或返回 `blocked_need_implementation_design_layer`。
