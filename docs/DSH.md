# 在 DeepSeek Harness（DSH）中使用

DSH 和 Codex 共用 `skills/github-first/SKILL.md` 的完整调研流程。DSH 通过原生文件系统技能加载它；`plugin.json` 和 `.codex-plugin/plugin.json` 用于支持它们的插件宿主，不是 DSH 的 Cordis 插件配置，无需把它们加入 `cordis.patch.yml`。

## 安装

需要 Python 3.9+。克隆本仓库后，在仓库目录运行：

```sh
python scripts/install.py --target dsh --with-rules
```

技能安装至 `~/.dsh/skills/github-first/`，规则合并至 `~/.dsh/AGENTS.md`。支持 `DSH_HOME` 或 `--dsh-home`。安装器仅操作本地文件，不联网、不调用模型、不修改 DSH 程序、账号或模型设置。

如果两端都尚未安装，可以使用同一个共享目录：

```sh
python scripts/install.py --target shared --with-rules
```

这会把技能装到 `~/.agents/skills/github-first/`，并分别合并 DSH 和 Codex 的常驻规则。Codex 规则目录支持 `CODEX_HOME` / `--codex-home`。若 DSH 使用不同的 `DSH_AGENTS_HOME`，默认拒绝共享安装；应统一双方扫描目录或改用 `--target dsh`。自定义 `--agents-home` 后需自行确保两个宿主均会扫描该目录。

已经装有 Codex 云端插件时，推荐 `--target dsh`，避免 Codex 同时出现两个同名技能。两种安装方式复制的核心技能完全相同；不要同时在 DSH 专用目录和共享目录维护不同版本。

## 更新、备份与恢复

```sh
git pull --ff-only
python scripts/install.py --target dsh --with-rules --update
```

默认拒绝覆盖内容不同的已有技能。`--update` 会先保存旧技能；规则修改也会备份原文件，备份路径由命令输出。安装器只替换 `github-first:begin` 和 `github-first:end` 之间由自己管理的段落，保留其他文字。相同版本重复安装不会重复追加规则。

恢复时将备份中的技能目录放回原位置，按备份检查并恢复需要的规则段落。卸载时移除 `github-first` 技能目录和这两个标记之间的规则；保留其他技能和说明。

## 调用和预期行为

打开新的 DSH 会话，在技能选择器中选择 `github-first`，或说：

```text
请使用 github-first 技能，先调研适合我需求的现成项目，比较后让我选择。
```

常驻规则用于提醒自动触发。模型应使用 DSH 当前实际提供的搜索、网页读取和用户提问能力；没有 GitHub 专用工具时可使用可用的网页搜索，不要求 Codex 专用工具。

例如“帮我做一个桌面记账工具”应先调研；“修复这个按钮”不触发；“我选第二个，继续安装”应按选定方案继续。实际搜索需要宿主有可用的搜索或联网能力。

## GitHub 认证

如需让 DSH 和 Codex 共用本机 GitHub Token，参见 [GitHub CLI 认证指南](GITHUB-AUTH.md)。配置后可直接用 CLI 查询 GitHub；这不修改 DSH 的模型供应商，也不能替代 `DEEPSEEK_API_KEY`。请按指南在两个宿主中分别验证账号和实际搜索。

## 验证和限制

本版本针对 DSH `@deepseek-ai/dsh-skill-filesystem` **0.2.1-rc.3** 的实际加载器进行发现、正文加载和调用策略检查；同时检查常驻规则是否被指令发现器找到。该检查不调用模型，不能证明真实模型每次都主动搜索或正确推荐。

可在自己的 DSH 安装上运行同样的只读检查（需 Node.js 与已安装的 DSH 依赖）：

```sh
node scripts/verify-dsh.mjs "<DSH 的 node_modules/@deepseek-ai 目录>"
```

该检查直接调用 DSH 模块，版本变化可能需要调整。未发现技能时检查目录、YAML 头和同名旧版本；界面没有刷新时先打开新会话，必要时重启 DSH。

DSH 技能加载说明：[官方文件系统技能文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)。技能目录包括用户级 `.dsh/skills` 和 `.agents/skills`；同名项按来源优先级选择。
