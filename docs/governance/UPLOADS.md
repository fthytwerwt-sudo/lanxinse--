# 普通项目资料上传｜V3 上传策略修订 r1

2026-11-02：用户已持续授权主仓库普通非敏感项目资料经自动检查后直接提交和推送，不因仓库Public或文件格式重复要求批准。默认目标main，任务另指定分支时从其要求。此授权不扩展到其他历史仓库或未知甲方仓库。

## 自动检查和直接发布

先核仓库身份、工作区、远端HEAD与用户既有改动，再运行：

```sh
python3 scripts/check_project_upload.py --repo . docs/upload-smoke/20261102_upload_smoke.md
```

检查器只读取明确候选，输出通过/单项复核/阻断、SHA、上传路由及脱敏原因。Python运行时需有pypdf才可提取PDF；优先使用应用已提供的依赖运行时，不改全局环境。可读普通文档通过后限定路径 `git add -- <paths>`、验证并提交。推送HEAD之前，核验 `git merge-base --is-ancestor <实读remote-main> HEAD`，审查 `git log <实读remote-main>..HEAD` 和完整累计diff都在授权范围，才正常 `git push origin HEAD:main`；否则基于实读目标树构造单次限定提交，不把无关分支历史推入main。遇非快进、并发变更、同路径冲突先重新读取，不能force、force-with-lease、reset、clean、stash或静默覆盖。不要提交无关未跟踪工作。

本机Git凭据不可用时，可用已有授权连接器按实读目标树建立blob/tree/commit，以当前HEAD为parent，更新ref使用 `expected_sha` 且 `force=false`。回读分支SHA和具体原文/原始字节哈希，不能仅用成功消息验收。主仓库普通文件的自动内容审查不等于让用户逐文件再批准。

## 按格式选方式

| 文件 | 上传方式 | 内容检查与回读 |
|---|---|---|
| Markdown、UTF-8代码、JSON等 | 普通Git，或UTF-8文件/blob接口 | 查路径、忽略、密钥/隐私标记；逐字或SHA回读 |
| DOCX | 普通Git，或base64 blob→tree→commit | 检查容器XML、属性、批注/修订等；未知嵌入内容需单项复核；原文件字节SHA回读 |
| PDF | 普通Git，或base64 blob→tree→commit | pypdf提取可读文字/元数据/链接；扫描、加密、附件或解析不足列具体覆盖缺口；原文件字节SHA回读 |
| XMind | 普通Git，或base64 blob→tree→commit | 检查ZIP内JSON/XML/文本和附件；原容器字节SHA回读；传输通过不代表XMind应用已打开验证 |

create_file/update_file只接受UTF-8，不可直接塞二进制；base64只是一种传输编码，不是加密或隐私保护。不得因扩展名一律禁DOCX/PDF/XMind。根`.gitignore`不再全局忽略PDF，原素材/缓存/凭据和被明确忽略的目录仍保持排除，逐路径检查 `git check-ignore -v -- <path>`；不要用无差别 `git add -f` 绕过安全边界。

API密钥、私人录音、客户隐私、合同、敏感商业资料、私有Drive入口和未经授权原文不公开。普通“内部使用”说明不自动等于敏感。对确实不明的内容只暂停该文件，给脱敏/提取/授权核对动作，其他普通文件继续。启发式扫描不能证明零泄漏；被阻断文件内容不在日志中复述。

## 大文件

GitHub网页单文件上限25MiB；普通Git大于50MiB会警告，大于100MiB被阻止。超过网页限制用Git或合适API，不误报为权限不足。50MiB以上建议评估LFS，超过100MiB必须先上传真实LFS对象。`.gitattributes`将DOCX/PDF/XMind等标为binary以保留原字节，但不把所有小文档强制变LFS。

确有大文件时，核对本机git-lfs、账号配额和对象大小限制，再仅对目标路径：

```sh
git lfs install --local
git lfs track --filename 'docs/project_materials/specific-large-file.pdf'
git add -- .gitattributes 'docs/project_materials/specific-large-file.pdf'
git lfs fsck
```

随后普通提交和快进推送，核验远端LFS对象可下载且SHA-256/size与原文件一致。不能只推指针冒充大文件已上传，不迁移既有历史、不全局安装或改配置，不以LFS绕敏感保护。工具或配额不可用时只报告对应大文件阻断，其他普通文件继续。

本轮HEAD最大对象约13.4MB，无>50MiB对象，因此未引入LFS依赖或虚构大文件实测；普通小文件上传不依赖LFS。

官方依据：[文件大小限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、[blob的UTF-8/base64编码](https://docs.github.com/en/rest/git/blobs)、[LFS对象与限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)。
