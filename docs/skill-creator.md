# skill-creator 学习指南

> 本文是官方 `skill-creator` 插件的学习式总结,供学习参考,并非官方文档镜像。
> 权威来源:[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) → `plugins/skill-creator/skills/skill-creator/SKILL.md`(上游更新后请以官方为准)。
> 与 [creating-a-skill.md](creating-a-skill.md) 的分工:那篇讲**怎么给 maestro 加 skill**,本篇讲**skill-creator 工具本身怎么运作、为什么这么设计**。

## 1. 目的:为什么需要它

skill-creator 解决两个靠人工解决不好的问题:

1. **触发不可控**:skill 的 frontmatter `description` 是模型决定是否调用 skill 的唯一信号,而模型天生"欠触发"——该用的时候不用。靠感觉改描述无法验证效果。
2. **质量不可量化**:"改完感觉更好了"没有数据支撑。skill 面向无数次重复使用,单次人工判断不可靠。

因此它把 skill 开发变成**评测驱动**的循环:

```
草稿 → 测试 → 评审 → 改进 → 重复
```

创建(前半段)和优化(后半段)是同一个循环的两段,不是两个工具。

## 2. 原理

### 2.1 渐进披露:三级加载

skill 的内容分三层,按需进入上下文:

| 层 | 内容 | 加载时机 | 体量建议 |
|---|---|---|---|
| 元数据 | `name` + `description` | 常驻上下文 | ~100 词 |
| 正文 | SKILL.md 指令 | skill 触发时 | **<500 行**(超限就拆层,加跳转指引) |
| 打包资源 | `scripts/`、`references/`、`assets/` | 按需 | 不限,脚本可执行而不加载 |

关键模式:正文里明确指引"什么时候去读哪个 reference 文件";大文件(>300 行)带目录;多领域 skill 按变体组织(如 `references/aws.md`、`gcp.md`),模型只读相关的那份。

### 2.2 触发机制

- skill 以 `name + description` 出现在模型的 `available_skills` 列表里,模型**根据 description 自行决定**是否查阅
- 模型只对"自己搞不定的任务"求助 skill——简单一步查询即使描述完美匹配也可能不触发
- 所以 description 要写得"pushy":写明做什么 + 具体触发场景,显式覆盖"用户没点名 skill 但其实需要它"的情形

### 2.3 双跑基线:对照实验

每次测试都跑两版对照,同时启动(避免时间/负载偏差):

- **新建 skill**:带 skill vs 完全不带(no skill)——证明 skill 有增益
- **改进 skill**:新版本 vs 旧版本快照(`cp -r` 到 `skill-snapshot/` 后改)——证明改动是改进而非退化

### 2.4 量化与盲测:把"感觉"变成数字

- **断言**(assertions):客观可验证、命名清晰,评分结果可读;主观类 skill(文风、设计)不强上断言,靠人评
- **计时**:每次跑批的 `total_tokens` / `duration_ms` 只出现在完成通知里,必须当时抓取(存 `timing.json`),错过不可补
- **聚合**:`aggregate_benchmark.py` 产出 `benchmark.json`/`benchmark.md`——通过率、耗时、token 的均值±方差及差值
- **分析**:analyst 专门找聚合数字掩盖的问题——永远全过的断言(无区分度)、高方差用例(疑似 flaky)、时间/token 权衡
- **盲测**:独立 agent 不知情地评判新旧两版输出(comparator),防止"自己写的自己评"的偏差;可选,人评循环通常够用

### 2.5 描述优化:自动迭代触发率

- 评测集:20 条真实用户口吻的查询——8-10 条**该触发**(同意图的不同说法,含不点名 skill/文件的场景)+ 8-10 条**不该触发的近失例**(共享关键词但应路由别处;近失例是最难也最有价值的部分,显然无关的负例测不出东西)
- `run_loop.py` 自动循环:60/40 切训练/测试集 → 每查询跑 3 次测当前描述的触发率 → 让模型针对失败样本提出改进 → 复测,**最多 5 轮,按测试集分数选 `best_description`**(不用训练分数,防过拟合)

## 3. 操作:完整流程

### 3.1 创建(意图 → 访谈 → 写稿)

1. **意图捕捉**:四问——skill 让 Claude 能做什么?什么时候触发?输出什么格式?要不要测试用例(输出可客观验证的建,主观类可不建)?
2. **访谈调研**:边界情况、输入输出格式、示例文件、成功标准、依赖;可并行子代理检索 MCP/文档
3. **写 SKILL.md**:frontmatter(`name`、`description`、可选的 `compatibility`)+ 正文。写作规范:祈使句;输出格式给精确模板;示例用"输入/输出"对;**解释每个要求的"为什么"**,少用全大写的 ALWAYS/NEVER(是黄牌信号)

### 3.2 测试(双跑 + 断言 + 评审)

工作区布局(`<skill>-workspace/`,与 skill 目录平级):

```
iteration-1/
├── eval-0/                    # 每用例一个目录,起描述性名字
│   ├── with_skill/outputs/    # 带 skill 跑
│   ├── without_skill/outputs/ # 基线(改进时是 old_skill/)
│   ├── eval_metadata.json     # prompt + 断言
│   ├── timing.json            # 从完成通知抓取
│   └── grading.json           # 断言评分(text/passed/evidence 固定字段)
└── benchmark.json / benchmark.md
```

步骤:① 同回合启动全部双跑(含基线)——**先跑带 skill 再补基线会引入偏差**;② 跑批期间草拟断言并给用户解释;③ 完成时抓计时数据;④ 评分、聚合、生成评审器;⑤ 用户评审。

评审器 `eval-viewer/generate_review.py`:Outputs 页逐用例看输出、留反馈;Benchmark 页看量化对比;迭代 2+ 传 `--previous-workspace` 对比上一轮;**无浏览器环境用 `--static` 出静态 HTML**。反馈落 `feedback.json`。

### 3.3 迭代改进

读反馈 → 改进 → 下一轮全量重跑(基线不变)。**改进四原则**:

1. **从反馈泛化**:目标是一个能用一百万次的 skill,不为测试样本过拟合
2. **保持精简**:读转录删掉不产出的指令
3. **解释为什么**:把每个要求的理由讲透,让模型知其所以然
4. **找重复劳动**:若各测试用例都不约而同写了同样的辅助脚本(如 `create_docx.py`),就该把它写一次放进 `scripts/`

停止条件:用户满意 / 反馈为空 / 无实质进展。

### 3.4 描述优化

生成 20 条评测集 → 用 HTML 模板(`assets/eval_review.html`)人工审签 → 后台跑 `run_loop.py`(用**当前会话同款模型**测,才贴近真实体验)→ `best_description` 回写 frontmatter,给用户看前后对比和分数。

### 3.5 打包

`scripts/package_skill.py <skill-folder>` → `.skill` 文件,可直接安装分发。

## 4. 本仓库的实践记录

对 maestro 四个 skill 做了 Line 1(描述优化),全程遵循本方法论:

- **评测集**:每 skill 20 条(10 该触发 + 10 近失例,近失例对准路由边界——commit/release/claude 互相竞争)
- **执行**:`claude -p` 无交互会话 + `stream-json --verbose` 检测 Skill 工具调用
- **教训**:评测会话必须在**沙箱副本**里跑——q13「走发版流程」曾真的执行了 release 技能,把真实仓库的 plugin.json bump 到了 3.0.1(已回退)
- **结果**:应触发率 spec 66%→96%、commit 45%→100%、release 85%→100%,近失例零回归;claude 本已 100% 无需改

## 5. 参考

- 官方 SKILL.md:https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md
- 子代理指令:`agents/grader.md`(断言评分)、`agents/comparator.md`(盲测)、`agents/analyzer.md`(基准分析)
- 数据结构:`references/schemas.md`(evals.json、grading.json 等 schema)
