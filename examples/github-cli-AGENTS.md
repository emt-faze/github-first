## 本机 GitHub CLI 认证（可选，Codex / DSH 共用）

- 执行 github-first 调研时，优先使用已配置认证的本机 GitHub CLI（`gh`）查询 GitHub。先用 `gh api user --jq .login` 核实当前账号，再执行 `gh search repos` 或只读 `gh api` 查询。
- CLI 路径：默认使用 PATH 中的 `gh`。如果当前应用找不到它，在此填入本机 `Get-Command gh` 返回的实际路径；PowerShell 用 `& '绝对路径'` 调用。
- 搜索示例：`gh search repos 'pomodoro windows' --limit 10 --json fullName,description,url,updatedAt`。继续检查 README、Releases、Issues 和许可证，不只看搜索结果。
- 未登录、认证过期或网络失败时如实说明，可使用其他可用的 GitHub 或网页工具；不把失败说成没有现成项目，不擅自扩大 Token 权限。
- Codex GitHub 连接器与 CLI 独立认证，可能使用不同账号。访问私有仓库前核对所用入口，不擅自切换连接器。
- Token 不写入技能、项目、仓库、命令参数或日志；不执行或输出 `gh auth token`、`--show-token`，不读取凭据文件来显示内容。
- GitHub Token 不能替代 DSH 的模型或网页搜索供应商密钥。需要 GitHub 调研时可以直接使用已认证的 CLI。
- 共用认证不改变原有“先调研、再选择、再实施”流程，安装或开发仍须遵循用户选择。
