# 发布与版本管理规则

本文说明 claude-skills 仓库的版本与发布规则。适用于仓库内所有插件(当前:maestro、dataflow)。

## 核心原则

1. **仓库没有独立的版本号**。版本号只属于某个插件;CHANGELOG 记录的是各插件的版本更新,不存在仓库级版本。
2. **插件是交付单位**。`/plugin update` 只认各插件 `plugin.json` 的 `version` —— 插件 A 的 bump 不会触发插件 B 的更新。tag、CHANGELOG、GitHub Release 只是把这个已存在的独立交付机制如实记录下来。
3. **谁变更,谁发布**。只改 maestro → 只有 maestro bump/tag/Release;只改 dataflow → 只有 dataflow bump/tag/Release;另一个插件零动作。

## 各插件的版本语义

| 插件 | 版本规则 |
|------|----------|
| `maestro` | 自演进序列:修复/优化 → bump 补丁位;新技能/新能力 → bump 次版本;破坏性变更 → bump 主版本 |
| `dataflow` | 镜像所记录的 dataflow-cv 版本:dataflow-cv 发 2.1.0 → 插件 2.1.0;纯 skill 侧修复只 bump 补丁位(如 2.0.1 → 2.0.2) |

## 发布流程(按插件)

1. **bump** 该插件的 `plugins/<plugin>/plugin.json` 版本(交付闸门:不 bump 则 `/plugin update` 跳过,用户永远收不到变更)
2. **写 CHANGELOG**:在 `CHANGELOG.md` 中新增版本头 `## [<plugin>-X.Y.Z] - YYYY-MM-DD`,下方按 Added → Changed → Fixed → Removed → Security → Docs 顺序写条目;版本号与 plugin.json 一致
3. **打 tag**:`claude plugin tag plugins/<plugin> --push` —— 生成工具原生的 `{name}--v{version}` 格式(如 `dataflow--v2.0.1`),并校验 `plugin.json` 与 marketplace 条目一致(也可手工 `git tag <plugin>--vX.Y.Z`)
4. **发 GitHub Release**:标题 `<plugin> vX.Y.Z: <一句话摘要>`,正文 = CHANGELOG 对应章节 + 末尾引用链接

两个插件同时变更:各自 bump、各自打 tag、各自发 Release。

## 不触发发布的情况

只改市场本身(README、marketplace.json、docs/、CLAUDE.md),插件内容没动:

- 两个插件版本都**不变**,不打 tag、不发 Release
- 条目记入 CHANGELOG `## [Unreleased]`,搭下一次任一插件的发布带出

## 示例时间线

### 只改 maestro(如优化 commit 技能描述)

| 对象 | 变化 |
|---|---|
| maestro | 3.0.1 → 3.0.2 |
| dataflow | 不动 |
| CHANGELOG | `## [maestro-3.0.2]` 头 + 条目 |
| tag / Release | `maestro--v3.0.2` / `maestro v3.0.2` |

用户端:`/plugin update` 只更新 maestro,dataflow 无感。

### 只改 dataflow(如给 dataflow-cv skill 加一条 gotcha)

| 对象 | 变化 |
|---|---|
| dataflow | 2.0.1 → 2.0.2(skill 侧修复,补丁位) |
| maestro | 不动 |
| CHANGELOG | `## [dataflow-2.0.2]` 头 + 条目 |
| tag / Release | `dataflow--v2.0.2` / `dataflow v2.0.2` |

### dataflow-cv 库发新版(如 2.1.0),skill 跟随升级

| 对象 | 变化 |
|---|---|
| dataflow | 2.0.2 → 2.1.0(镜像 dataflow-cv 主次版本) |
| maestro | 不动 |
| CHANGELOG | `## [dataflow-2.1.0]` 头 + 条目 |
| tag / Release | `dataflow--v2.1.0` / `dataflow v2.1.0` |

### 两个插件同时改

各自 bump、各自写 CHANGELOG 头、各打各的 tag(`maestro--v3.0.3` + `dataflow--v2.1.1`)、各发各的 Release。

## 常见问题

**GitHub 的 "Latest release" 标签在两个插件之间跳?** 正常现象 —— 谁最近发布就显示谁,不代表另一个插件过时。

**历史遗留的裸版本 tag(v3.0.0 / v3.0.1)?** 单插件时代打的,语义上属于 maestro,保留原样;对应 Release 的标题已改为 `maestro v3.0.x` 前缀。

**安装/更新究竟看什么?** 看市场仓库默认分支 HEAD 的 `marketplace.json` + 插件 `plugin.json` 的 version;tag 与 GitHub Release 不参与交付机制。详见 [plugin-installation.md](plugin-installation.md)。
