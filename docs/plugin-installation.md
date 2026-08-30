# 插件安装、更新与查询

本文说明 Claude Code 插件的安装、更新与查询机制,以及 `plugin@marketplace` 的解析规则。适用于本仓库(claude-skills 市场)的插件用户。

## 核心概念

| 概念 | 含义 |
|------|------|
| **marketplace(市场)** | 一个 URL、本地路径或 GitHub 仓库,根目录含 `.claude-plugin/marketplace.json` 目录文件 |
| **plugin(插件)** | 市场目录中的一个条目,`source` 指向仓库内某个目录(本仓库为 `plugins/<name>/`) |
| **`plugin@marketplace`** | 插件名 @ 市场名,用于指定从哪个市场安装 |

## 关键问题:`dataflow@claude-skills` 指向哪个版本?

以 `claude plugin install dataflow@claude-skills` 为例,解析链条:

```
dataflow@claude-skills
   │        └── 市场名:claude plugin marketplace add zjykzj/claude-skills 注册的
   │            GitHub 仓库 zjykzj/claude-skills
   └── 插件名:该仓库默认分支(main)上 .claude-plugin/marketplace.json 中
        name = "dataflow" 的条目 → source = "./plugins/dataflow"
```

**安装快照的是市场仓库默认分支当时的 HEAD 提交,不是 GitHub Release,也不是 git tag。**

- 安装记录 `~/.claude/plugins/installed_plugins.json` 中保存了 `gitCommitSha` —— 装的是「此刻的 main」,装完后市场仓库再变也不会影响已安装的插件
- 版本号 = 该快照中 `plugin.json` 的 `version` 字段
- GitHub Release 与 tag **不参与安装/更新机制**,纯属变更记录(见 [release-versioning.md](release-versioning.md))

## 命令速查

### marketplace(市场)

```bash
claude plugin marketplace add zjykzj/claude-skills   # 注册市场(URL/路径/GitHub 仓库)
claude plugin marketplace list                       # 列出已配置市场
claude plugin marketplace update [name]              # 从源刷新市场目录(不带 name 则全部刷新)
claude plugin marketplace remove|rm <name>           # 移除市场
```

### plugin(插件)

```bash
claude plugin install dataflow@claude-skills    # 安装(-s user|project|local 指定作用域)
claude plugin list                              # 列出已安装插件(--json 结构化;--available 含市场可用项)
claude plugin details <name>                    # 查看插件组件清单与预估 token 开销
claude plugin update <name>                     # 更新到市场最新 HEAD(需重启会话生效)
claude plugin uninstall|remove <name>           # 卸载
claude plugin enable/disable <name>             # 启用/停用(不卸载)
claude plugin prune|autoremove                  # 清理不再需要的自动安装依赖
claude plugin validate <path>                   # 校验插件或市场清单
```

### 发布辅助(本仓库维护者)

```bash
claude plugin tag plugins/dataflow --push       # 生成 {name}--v{version} 格式 tag(如 dataflow--v2.0.1),
                                                # 校验 plugin.json 与 marketplace 条目一致后推送
```

### 会话内等价命令

`/plugin marketplace add|list|remove`、`/plugin install|uninstall|update|list|enable|disable`,以及 `/reload-plugins`。

## 更新机制:版本闸门

- `claude plugin update <name>` 重新拉取市场默认分支 HEAD;若新快照的 `plugin.json` `version` 与已安装一致,视为无更新
- **因此每次用户可见变更必须 bump `plugin.json` 版本**,否则用户永远收不到(这是 [release-versioning.md](release-versioning.md) 发布流程第一步的原因)
- `claude plugin marketplace update` 只刷新市场目录(让新插件、新条目可见),不更新已安装插件

## 热重载规则

| 改动内容 | 生效方式 |
|----------|----------|
| `SKILL.md` 内容 | 会话内热生效,无需重载 |
| `plugin.json` / `hooks/` | 需 `/reload-plugins` 或重启会话 |

## 安装位置与作用域

- 缓存:`~/.claude/plugins/cache/<marketplace>/<plugin>/<快照标识>/`
- 记录:`~/.claude/plugins/installed_plugins.json`(含 version、gitCommitSha、installPath)
- 作用域:`user`(默认,全机器)/ `project`(仅当前项目)/ `local`(仅当前工作区)

## 与发布规则的关系

安装/更新只认「市场仓库 main 的 HEAD + plugin.json version」;tag 与 GitHub Release 是给人看的记录。两者的分工见 [release-versioning.md](release-versioning.md)。
