<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/icon-dark.svg">
  <img src="assets/icon.svg" width="88" height="88" alt="GitHub 优先">
</picture>

# GitHub 优先 · GitHub First

**让 AI 开发前先找现成方案，深入比较，再由你决定。**

做一个工具之前，GitHub 上可能已经有能直接使用或稍加改造的项目。这个插件让 Codex 先调研已有方案，说明取舍，等你选定后再安装或开发，减少重复开发和不必要的成本。

这是一个流程技能插件，复用宿主已有的 GitHub、网页搜索等能力，无需为插件单独部署服务器或配置 API 密钥。宿主本身的模型、搜索服务仍可能需要账号或产生费用。

## 它会做什么

1. 理解需求和现有项目，明确真正需要的功能。
2. 多轮搜索 GitHub 的现成应用、项目、库和插件。
3. 核对文档、许可证、发布记录和关键 Issues，必要时查看源码。
4. 综合比较功能、安装难度、成本、维护情况和改造空间，给出证据链接与推荐。
5. **等待你选定**，再继续安装、改造或自行开发。

不固定偏好免费、功能最多或学习用途，以具体任务要求为准。找不到合适方案时说明原因；搜索失败时说明限制，不把失败说成“没有现成项目”。

| 请求 | 默认行为 |
| --- | --- |
| “帮我做一个桌面记账工具” | 先调研现成应用与可复用项目 |
| “给现有应用加完整 OCR 功能” | 先比较可复用的 OCR 方案 |
| “修复这个按钮的点击事件” | 直接处理小修复 |
| “这次为了学习，从零写，不搜索” | 遵循本次明确要求 |
| “我选第二个，继续安装” | 按既有选择继续，不反复询问 |

## 在 Codex 中使用

### 方式一：安装核心技能

可以直接让 Codex 的技能安装器处理：

```text
使用 $skill-installer 从 https://github.com/emt-faze/github-first 安装 skills/github-first 技能。
```

也可以手动安装。先克隆仓库：

```sh
git clone https://github.com/emt-faze/github-first.git
cd github-first
```

Windows PowerShell：

```powershell
$skillRoot = Join-Path $env:USERPROFILE '.agents\skills'
$skillTarget = Join-Path $skillRoot 'github-first'
if (Test-Path -LiteralPath $skillTarget) { throw '该技能已存在，请先备份并检查是否需要更新。' }
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
Copy-Item -LiteralPath '.\skills\github-first' -Destination $skillTarget -Recurse
```

macOS / Linux：

```sh
mkdir -p "$HOME/.agents/skills"
if [ -e "$HOME/.agents/skills/github-first" ]; then
  echo "该技能已存在，请先备份并检查是否需要更新。"
else
  cp -R skills/github-first "$HOME/.agents/skills/github-first"
fi
```

在技能列表中确认出现 `github-first`；未出现时重启 Codex。可以显式调用：

```text
$github-first 帮我调研适合 Windows 的本地知识库工具，比较之后让我选择。
```

本地技能目录和显式／隐式调用方式参见 [Codex 官方技能文档](https://learn.chatgpt.com/docs/build-skills)。请避免同时安装多个同名副本。

### 方式二：复用完整插件包

仓库包含标准 `plugin.json`、Codex 兼容清单、技能和浅色／深色图标。支持 Agent Plugins 1.0 的宿主或插件创建流程可以复用这些文件。

通过 GitHub 下载源代码后，若宿主要求插件 ZIP，将 `plugin.json`、`.codex-plugin/`、`skills/`、`assets/` 和 `LICENSE` 打包到 ZIP 根目录，按该宿主的导入流程安装。各宿主的安装入口不同；仓库公开不代表已进入官方插件商店。

## 让“先搜索”成为默认习惯

技能允许隐式调用，但模型不一定每次都自动选用。安装后可以把 [examples/AGENTS.md](examples/AGENTS.md) 中的规则**追加合并**到用户级 `~/.codex/AGENTS.md`；只想对某个项目生效时，合并到该项目的 `AGENTS.md`。

保留已有规则，不要用示例覆盖整个文件。若设置了自定义 `CODEX_HOME`，用户级规则应放在对应目录。打开新会话验证规则是否加载。详见 [官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

这些是模型行为规则，并非拦截所有代码写入的强制开关。其他设备需要独立安装和配置；网页端也不会读取本机规则。

## 文件说明

```text
plugin.json                         标准插件清单
.codex-plugin/plugin.json           Codex 兼容清单
skills/github-first/SKILL.md         核心工作流程
skills/github-first/agents/          技能显示和调用配置
assets/                             青绿色浅色／深色 SVG 图标
examples/AGENTS.md                  可选的常驻规则示例
LICENSE                             MIT 许可证
```

## 验证与反馈

发布前检查了 JSON/YAML 格式、图标引用、包内文件和个人路径泄露。此插件没有独立程序运行时；不同模型、宿主和网络条件下的实际搜索质量需要在使用中验证。

欢迎通过 [Issues](https://github.com/emt-faze/github-first/issues) 提交漏触发、误触发或改进建议，也欢迎 Pull Request。报告时附上宿主版本、触发提示和预期行为，隐藏密钥及私人信息。

## License

[MIT](LICENSE) © 2026 emt-faze。允许使用、修改和分发，请保留许可证声明。

## English overview

GitHub First is an instruction-only plugin for researching existing solutions before building new tools, apps, or major features. It compares suitability, deployment effort, costs, maintenance and licensing, then waits for the user to choose before implementation. Minor fixes are excluded; explicit task instructions take precedence.

Install `skills/github-first` into `~/.agents/skills/`, or reuse the full plugin package in a compatible host. Optionally merge `examples/AGENTS.md` into your Codex instructions for a stronger default. The workflow is written in Chinese. It uses the host's existing search tools and does not guarantee automatic invocation. MIT licensed.
