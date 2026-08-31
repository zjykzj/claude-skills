# 创建一个 Skill

skill 是 `maestro` 插件里可复用指导的基本单元。本文讲三件事:skill 的作用、必须遵循的格式、以及往插件里新增一个 skill 的流程。

## 目的:skill 的作用

每个 skill 把一套可复用的开发流程编码为指令,Claude 按需调用,以 `/maestro:<name>` 命名空间呈现:

| Skill | 编码的流程 |
|-------|---------|
| `/maestro:spec` | SDD(spec-first development)方法论 + 强制执行 hook |
| `/maestro:commit` | Conventional Commit 格式 + CHANGELOG 维护 |
| `/maestro:release` | semver bump + GitHub release |
| `/maestro:claude` | CLAUDE.md 编写规范 |

skill 以插件形式分发而非拷贝文件,有四个原因:

- **带更新的分发**:一次安装送达全部 skill;修复经 `/plugin update` 到达用户,由 `plugin.json` 的 `version` 字段门控。拷贝文件永远不会更新。
- **命名空间**:`/maestro:<name>` 调用不会与项目文件或其他插件冲突。
- **自配置**:每个 skill 以 Bootstrap 一节结尾,首次在新项目使用时,检测该项目 CLAUDE.md 中缺失的 `{{VARIABLE}}` 定义,追加自己的配置块,并汇报检测结果——无需手工设置。
- **可选,从不强制**:没装插件 → 什么都不坏,只是 skill 不可用。这是整个插件的设计原则(见 README "Design: optional, never required")。

## 格式

### 目录布局

每个 skill 位于 `plugins/maestro/skills/<name>/`:

```
plugins/maestro/skills/<name>/
├── SKILL.md        # 必需 —— frontmatter + 指令正文
├── scripts/        # 可选 —— skill 或 hook 要执行的可执行脚本
├── references/     # 可选 —— 按需加载的辅助文档
├── templates/      # 可选 —— skill 要写出的文件模板
```

`spec` 三个可选目录都用到了(`scripts/sdd-reminder.sh`、`references/curation-guide.md`、`templates/spec_template.md`);`commit` 是最简形态——只有一个 `SKILL.md`。

### Frontmatter(YAML,必需)

```yaml
---
name: <name>
description: <何时使用该 skill>
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
---
```

- `name` —— 斜杠命令后缀(`/maestro:<name>`)。插件内必须唯一。
- `description` —— Claude 靠这段文字把任务匹配到 skill,所以要写成"何时使用",并包含触发词。spec skill 的示例:*"Create or modify spec files following project methodology, and drive SDD (spec-first development). Use when writing, editing, or reviewing specs/ files — and BEFORE implementing any feature or behavior change that affects a contract documented in specs/."*
- `allowed-tools` —— 该 skill 作用域内的工具白名单。

### 正文规范

- **可执行流程优于散文**:决策表、分类规则、精确命令——例如 release skill 的 semver 表。
- **`{{VARIABLE}}` 占位符**表示项目级配置,从项目的 CLAUDE.md 解析。
- **以 `## Bootstrap (First Use in a New Project)` 结尾**——首次使用自动配置:grep 项目 CLAUDE.md 查找变量,缺失则追加配置块,并汇报检测结果。要有 degraded mode——绝不因缺配置而卡死。
- **以 `## Required Configuration` 结尾**——列出 skill 消费的每个变量。

## 新增一个 skill:流程

1. 按上述格式创建 `plugins/maestro/skills/<name>/SKILL.md`。
2. 校验:`claude plugin validate .`
3. 本地测试:`claude --plugin-dir plugins/maestro`,然后在会话内调用 `/maestro:<name>`。
4. bump `plugins/maestro/plugin.json` 的 `version` —— **强制**。`/plugin update` 会跳过版本没变的插件,不 bump 就没有任何用户能收到新 skill。
5. 在同一个 commit 里更新 CHANGELOG 的 `[Unreleased]`(按改动类型选小节:Added → Changed → Deprecated → Removed → Fixed → Security;breaking change 标 `(breaking)`)。
6. 用 `/maestro:commit` 提交(conventional commit + 强制 `Co-Authored-By` 行)。

重载行为:`SKILL.md` 改动会话内 hot-reload;`hooks/` 或 `plugin.json` 改动需要 `/reload-plugins`。

## 评估与优化一个 skill

写完只是开始,不是终点。官方 `skill-creator` 插件(安装:`/plugin install skill-creator@anthropics/claude-plugins-official`)定义了优化方法论——评测驱动,分两条线。工具本身的完整学习指南见 [skill-creator.md](skill-creator.md):

### 线 1:description 优化(触发准确率)

frontmatter 的 `description` 是首要触发信号,而模型天生欠触发 skill。用触发评测集来优化它:

1. 写 ~20 条真实口吻的查询:8-10 条**该触发**(同意图的不同说法,包括从不点名 skill 或关键词的场景)和 8-10 条**近失例**——共享关键词或概念但需要别的东西、不该触发的查询。近失例是最难的部分——显然无关的负例测不出任何东西。
2. 与用户一起评审评测集——差的评测查询会产出差的 description。
3. 迭代:测量当前 description 在评测集上的触发率(每条查询跑多次),针对失败样本提出改进,再复测。留出一部分评测集做最终选择,防止过拟合。`skill-creator` 自带 `scripts/run_loop.py` 自动化这条循环。

### 线 2:行为评估(skill 到底有没有用)

1. 起草 2-3 条真实测试 prompt。
2. 每条都跑两版对照:带 skill vs 不带(新建 skill 时基线是"无 skill",改进时基线是"旧版本"),记录输出、assertion、耗时和 token。
3. 给 assertion 评分,打开 HTML 评审器(`eval-viewer/generate_review.py`)让人类逐条看输出、留反馈。
4. 根据反馈改进再重复,直到用户满意、反馈为空、或没有实质进展。

### 进阶:盲测

对"新版真的更好吗?"这类问题,让独立 agent 在不知情的情况下评判两个输出(`agents/comparator.md`)——通常人评循环就够了。

### 改进原则

- **从反馈中泛化**——目标是能跨无数 prompt 工作的 skill,而不是过拟合测试样本
- **保持精简**——删掉没有产出的指令
- **解释每个要求背后的为什么**,而不是堆砌生硬的 MUST
- **沉淀重复劳动**——如果各次测试都反复写同样的辅助脚本,就把它写一次放进 `scripts/`

## 附带脚本与 hook(可选)

skill 可以附带供自己使用的可执行脚本,或往 `plugins/maestro/hooks/hooks.json` 注册 hook。`spec` 两者都做:`scripts/sdd-reminder.sh` 注册为 PreToolUse hook,匹配 `Edit|Write` 且路径含 `specs/` 时触发,经 `${CLAUDE_PLUGIN_ROOT}` 解析——无需项目侧配置。hook 脚本提交时要带 `+x` 位:hook 直接执行脚本,不走 `sh`。
