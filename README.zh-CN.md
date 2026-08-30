# claude-skills

一个 [Claude Code](https://code.claude.com/docs) 插件市场,托管可复用的开发工作流技能,以插件形式分发而非拷贝文件。

## 目录结构

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json          # 市场目录(每个插件一条)
├── plugins/
│   ├── maestro/                 # 插件:maestro
│   │   ├── plugin.json           # 清单(name = 技能命名空间前缀)
│   │   ├── skills/               # 插件内置技能
│   │   │   ├── spec/             #   SDD 方法论 + 强制执行钩子脚本
│   │   │   ├── commit/           #   提交格式 + CHANGELOG 维护
│   │   │   ├── release/          #   版本 bump + GitHub Release
│   │   │   └── claude/           #   CLAUDE.md 编写,含开发命令文档
│   │   └── hooks/
│   │       └── hooks.json        # PreToolUse 钩子:编辑 specs/ 时提醒 SDD
│   └── dataflow/                # 插件:dataflow(版本镜像 dataflow-cv)
│       ├── plugin.json           # 清单(name = 技能命名空间前缀)
│       └── skills/
│           └── dataflow-cv/      #   dataflow-cv 库使用技能
```

## 安装

插件技能以插件名作为命名空间前缀 —— `/maestro:spec`、`/maestro:commit`、`/dataflow:dataflow-cv` 等。

**每台机器只需一次:**

```bash
claude plugin marketplace add zjykzj/claude-skills
claude plugin install maestro@claude-skills
claude plugin install dataflow@claude-skills
```

或在会话内执行:`/plugin marketplace add zjykzj/claude-skills`,然后 `/plugin install maestro@claude-skills`(或 `dataflow@claude-skills`)。

**项目级配置(可选):** 上述安装是机器级的,对每个项目都生效 —— 无需任何项目级配置。另有两个可选辅助手段:

- **CLAUDE.md**:在项目的 CLAUDE.md 中记录安装命令,方便贡献者发现。这是推荐做法。
- **团队仓库**:提交含 `extraKnownMarketplaces` + `enabledPlugins` 的 `.claude/settings.json`,可在克隆后(经过工作区信任)自动注册市场并标识插件使用 —— 但安装仍需每个用户手动执行一次安装命令。

两者都不是插件工作的前提;插件缺失时不会有任何损坏。

## 设计:可选,从不强制

这些技能是**辅助工具**。没有它们项目照常开发:

- 未装插件 → 没有钩子、没有技能调用、没有报错。项目 CLAUDE.md 规则自洽。
- 装了插件、项目未配置 → 每个技能首次使用时检测 CLAUDE.md 中缺失的 `{{VARIABLE}}` 定义,并追加自己的配置块(见各 SKILL.md 的 "Bootstrap" 一节)。
- 两者都有 → 完整工作流:SDD 钩子 + 技能流程。

## 维护本仓库

**为 `maestro` 插件新增技能**:创建 `plugins/maestro/skills/<name>/SKILL.md`,然后 bump `plugins/maestro/plugin.json` 的 `version`。用户通过 `/plugin update` 获取。技能格式和完整流程见 [docs/creating-a-skill.md](docs/creating-a-skill.md)。

**开发或优化技能**采用评测驱动:描述触发优化 + 有/无技能对照的行为评测循环,依据官方 `skill-creator` 插件(`/plugin install skill-creator@anthropics/claude-plugins-official`)。完整方法论见 [docs/creating-a-skill.md](docs/creating-a-skill.md)。

**新增插件**:创建 `plugins/<name>/` 目录及各自的 `plugin.json`,然后在 `.claude-plugin/marketplace.json` 中添加条目。用户单独安装 —— 插件粒度是逐项目启用/禁用的单位。

**发布插件**:按插件版本化 —— 每个插件各自 bump、打 tag(`<plugin>--vX.Y.Z`)、发 Release;见 [docs/release-versioning.md](docs/release-versioning.md)。

**安装 / 更新 / 查询插件**:`plugin@marketplace` 的解析规则(市场 HEAD + `plugin.json` version,与 GitHub Release 无关)与完整命令面;见 [docs/plugin-installation.md](docs/plugin-installation.md)。

**技能更新只有 bump 版本后才能到达用户**(plugin.json 的 `version` 是更新门控)。

## 本地测试

```bash
claude plugin validate plugins/maestro          # 清单/schema 校验
claude --plugin-dir plugins/maestro             # 直接加载,无需安装
```

修改后执行 `/reload-plugins`;`SKILL.md` 的改动会话内热加载,但 `hooks/` 或 `plugin.json` 的改动需要 reload。

## License

MIT —— 见 [LICENSE](LICENSE)。Copyright (c) 2026 zjykzj.
