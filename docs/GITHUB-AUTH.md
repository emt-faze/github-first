# Codex 和 DSH 共用 GitHub 认证

本指南以 Windows 为例：在同一个 Windows 用户下配置一次 GitHub CLI（`gh`），让 Codex 和 DeepSeek Harness（DSH）通过它查询 GitHub。Token 由本机凭据库管理，不需要复制到两个应用，更不需要写入插件。

这是可选配置。公开项目也能通过宿主的 GitHub 工具或网页搜索调研；使用已认证的 CLI 可以减少匿名 API 访问受限的问题，但仍受 GitHub 限流、Token 权限和网络条件约束。

## 1. 安装 GitHub CLI

从 [GitHub CLI 官网](https://cli.github.com/) 或 [官方 Releases](https://github.com/cli/cli/releases) 安装适合系统的版本。Windows 已有 WinGet 时也可运行：

```powershell
winget install --id GitHub.cli --exact
```

安装后打开新终端，验证：

```powershell
gh --version
(Get-Command gh -ErrorAction Stop).Source
```

记下第二条命令返回的实际路径。如果 Codex 或 DSH 仍使用安装前的 PATH，重启应用，或在规则中填写这个绝对路径。不要照抄他人的用户目录。

## 2. 登录并检查存储位置

先在自己的本机终端运行 `gh auth status`。已经有有效且符合本次用途的账号时，可以直接进入第 3 步，不必替换凭据。

### 已有 Personal Access Token

不要把 Token 发给 AI、写入命令参数或先保存为明文文件。在本机 PowerShell 中运行下面的代码，出现提示后粘贴 Token；输入会隐藏，Token 通过标准输入交给 CLI：

```powershell
$githubSecureToken = Read-Host '请粘贴 GitHub Token（输入隐藏）' -AsSecureString
$githubTokenPointer = [IntPtr]::Zero
try {
    $githubTokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($githubSecureToken)
    $githubPlainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($githubTokenPointer)
    $githubPlainToken | gh auth login --hostname github.com --git-protocol https --with-token
    if ($LASTEXITCODE -ne 0) { throw '登录失败，请检查 Token 类型、权限或网络。' }
} finally {
    if ($githubTokenPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($githubTokenPointer)
    }
    Remove-Variable githubPlainToken -ErrorAction SilentlyContinue
    $githubSecureToken.Dispose()
    Remove-Variable githubSecureToken, githubTokenPointer -ErrorAction SilentlyContinue
}
```

这段代码不会把 Token 文本放入命令历史，但传递时仍会短暂存在于进程内存中。只在自己的可信终端操作，不录制输入或打开命令调试跟踪。

`--with-token` 的官方用法针对 classic PAT，要求 `repo`、`read:org`、`gist` scopes。不要仅为了公开仓库搜索而扩大现有 Token 权限。Fine-grained PAT 的资源范围不同，CLI 官方更推荐通过 `GH_TOKEN` 使用它；不要把权限不足当成需要授权所有仓库。[官方登录说明](https://cli.github.com/manual/gh_auth_login)

如果使用 fine-grained PAT，可以在**自己启动 Codex / DSH 的终端进程中**通过隐藏输入设置 `GH_TOKEN`，让从该终端启动的应用继承；它不会自动进入已运行的应用。不要用 `setx` 持久化明文 Token。本文后续“两边共用凭据库”的步骤仅适用于已完成 CLI 登录、并确认凭据库保存成功的情况。

### 没有 Token，或不希望管理 PAT

可以改用官方浏览器登录：

```powershell
gh auth login --hostname github.com --git-protocol https --web
```

### 确认保存在凭据库

登录后检查：

```powershell
gh auth status --hostname github.com --json hosts --jq '.hosts[][] | {login,active,state,tokenSource}'
```

目标账号应为 `active: true`、`state: "success"`，本指南中的安全存储预期为 `tokenSource: "keyring"`。不要添加 `--show-token`，也不要执行 `gh auth token` 来验证登录。

GitHub CLI 在系统凭据库不可用时可能回退到明文配置文件。若来源显示为配置文件路径，应停止共用配置，使用 `gh auth logout --hostname github.com --user <你的账号>` 退出该账号，修复系统凭据库后重新登录；不要把这个文件复制到仓库。[官方存储说明](https://cli.github.com/manual/gh_auth_login)

如果来源是环境变量，先检查是否设置了 `GH_TOKEN` / `GITHUB_TOKEN`；它们可以覆盖保存的账号。只检查变量是否存在，不输出值。`GH_CONFIG_DIR` 不同也可能使两个宿主使用不同的配置。只有同一操作系统用户、相同 CLI 配置和可访问的凭据库，才能按本文方式共用认证。

## 3. 验证账号和搜索

```powershell
gh api user --jq .login
gh search repos remotion --limit 2 --json fullName,url
```

第一条应返回你自己的 GitHub 用户名，第二条应返回仓库名称和链接。只看到“已登录”还不足以证明搜索可用；认证检查失败时先解决错误，不继续宣称配置成功。

## 4. 让两边的调研流程使用同一个 CLI

先按照 [DSH 指南](DSH.md) 安装技能与常驻规则，再把 [共用认证规则示例](../examples/github-cli-AGENTS.md) **追加合并**到：

- Codex：`~/.codex/AGENTS.md`，设置了 `CODEX_HOME` 时使用对应目录。
- DSH：`~/.dsh/AGENTS.md`，设置了 `DSH_HOME` 时使用对应目录。

保留已有内容，不要覆盖整个文件。规则里只填写 CLI 路径，不填写 Token。示例是可选的本机覆盖规则，安装器不会自动添加它，也不会替你登录。

两边分别打开新会话，发送：

```text
只做认证验证：按全局规则用 GitHub CLI 查询当前账号，再用同一个 CLI
搜索 remotion，最多返回两个仓库名称和链接。不读取或输出 Token，
不创建项目、不安装软件、不使用网页搜索、不派生子代理。
```

检查实际工具调用是否使用了 `gh api user` 和 `gh search repos`，且账号一致。还可以发送“帮我做一个桌面番茄钟工具”，观察是否先调研并等待选择。前者验证认证可用，后者验证调研流程；两者都不代表模型每次一定自动触发。

## 5. 常见问题

| 现象 | 检查方向 |
| --- | --- |
| 终端能运行 `gh`，应用里找不到 | 重启应用刷新 PATH，或在规则中填写 CLI 的实际绝对路径；PowerShell 用 `& '路径'` 调用 |
| 两边显示不同账号 | 检查是否同一系统用户、相同 CLI 路径和 `GH_CONFIG_DIR`，以及环境变量是否覆盖；多账号可用 `gh auth switch --hostname github.com --user <账号>` 切换 |
| GitHub 连接器与 CLI 账号不同 | 它们独立认证；CLI 登录不会改变 Codex 连接器。访问私有仓库前核对所用入口和账号 |
| 401 / 403 / 搜索失败 | 检查 Token 有效期、资源范围、组织授权、限流和网络；不要自动扩大权限 |
| DSH 仍提示缺少 `DEEPSEEK_API_KEY` | 那是模型或搜索供应商配置；GitHub Token 只认证 GitHub。可以用 CLI 查询 GitHub，但它不能替代模型密钥 |
| 容器、WSL、远程主机或另一台电脑无法共用 | 这些环境通常不能直接读取 Windows 凭据库，应在对应环境独立配置，不复制凭据文件 |

更新 Token 时在本机重新执行登录，再验证账号、存储来源和搜索。退出 CLI 可用 `gh auth logout`，但退出本机不等于吊销 Token；需要吊销时到 GitHub 的 Token 设置中操作。[退出说明](https://cli.github.com/manual/gh_auth_logout)

## 验证范围与隐私

本方法曾在 Windows、GitHub CLI 2.103.3 和 DSH 0.2.1-rc.3 上验证：凭据来源为 `keyring`，Codex 和 DSH 分别成功执行账号查询与仓库搜索。其他系统、版本、账号权限和网络环境需要自行验证。仓库不附带个人账号测试日志、Token、凭据文件或本机配置。

仅复制本指南和规则示例，不要上传 `.env`、`hosts.yml`、系统凭据库导出、个人 `AGENTS.md` 或包含认证信息的日志。`.gitignore` 只能减少误提交，不能清除已经提交的秘密；如误泄露，应先吊销 Token，再处理仓库历史。
