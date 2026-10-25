# 创作者结构调研与采用依据

读取日期：2026-10-25。范围为公开 GitHub README、所链接的源码、贡献指南与提交记录。结论基于当日读取的内容；链接使用实际大小写与默认分支。本文是原创分析，不移植创作者身份、统计、商业信息或大段文案。

## 1. 读者先找到入口：antfu 与 ni

- [antfu/antfu：README.md](https://github.com/antfu/antfu/blob/main/README.md) 当前只有居中的文字导航，连接个人网站、文章、项目等入口。它不是常见的长履历或统计卡片主页。
- [antfu-collective/ni：README.md](https://github.com/antfu-collective/ni/blob/main/README.md) 先说明工具解决的问题与安装方法，随后按安装、运行、升级等任务给出命令及其对应行为，并补充配置、实现原理和故障排查。

采用：hrniux 主页用短导航和明确项目入口；GitHub Studio 的命令文档按 `plan`、`apply`、`status` 的用户任务组织。每个命令说明输入、效果与可观察结果。

边界：不能因为 antfu 使用极简导航，就省去 hrniux 尚需建立的项目证据。主页保留少量项目解释与真实状态。

## 2. 个性服务于下一步：Sindre Sorhus 与 Awesome

- [sindresorhus/sindresorhus：readme.md](https://github.com/sindresorhus/sindresorhus/blob/main/readme.md) 使用复古 GIF，包括欢迎图、打字猫与装饰图；正文的主要行动入口是 Mac 应用 Supercharge 和博客。
- [sindresorhus/awesome：readme.md](https://github.com/sindresorhus/awesome/blob/main/readme.md) 提供 Contents，再按领域分类资源；大量条目用一句话说明用途，并链接独立资源和贡献指南。文件也包含应用及赞助展示，不能只把它概括成纯目录。

采用：允许一个原创视觉标识，但主页的重点是进入源码、运行演示、阅读实践。知识索引按 Java/Spring、Agent/RAG/MCP、Mac 工具分组，每条写“解决什么问题”。

边界：不照搬 GIF 素材、应用推广、赞助信息、访问计数或社区规模。没有真实维护记录的链接清单不包装成成熟知识库。

## 3. 用日期展示成果：Simon Willison

- [simonw/simonw：README.md](https://github.com/simonw/simonw/blob/main/README.md) 展示 Recent releases、On my blog、TIL；条目带具体日期并链接原始发布或文章。例如当日读取的发布列表包含 2026-10-24 的 battledrones v14。
- [simonw/simonw：.github/workflows/build.yml](https://github.com/simonw/simonw/blob/main/.github/workflows/build.yml) 明确包含 `push`、`workflow_dispatch` 与 `8 * * * *` 每小时触发，运行 `build_readme.py` 后提交变化。
- [simonw/llm：README.md](https://github.com/simonw/llm/blob/main/README.md) 顶部生成代码明确说明 README 从 `docs/index.md` 通过 Sphinx Markdown 构建生成；正文有用途、安装、快速使用与完整文档入口。

采用：主页只列已有链接与日期的成果；完整记录留在归档。GitHub Studio 用配置、模板与生成结果分开管理，避免在多个文件手改同一份项目事实。

边界：观察到他人的每小时工作流不构成本项目创建定时任务的依据。本次不创建自动调度；缺少发布或文章时直接省略栏目，不用提交日期伪装发布日期。

## 4. 把原理缩成可运行证据：micrograd

源码入口：

- [README.md](https://github.com/karpathy/micrograd/blob/master/README.md)
- [micrograd/engine.py](https://github.com/karpathy/micrograd/blob/master/micrograd/engine.py)
- [test/test_engine.py](https://github.com/karpathy/micrograd/blob/master/test/test_engine.py)

README 先说明标量自动求导的范围与教育用途，然后提供安装、代码及具体输出、完整演示、计算图与测试命令。核心实现保留构图与反向传播的可读性；测试将前向值和梯度与 PyTorch 比较。README 中的行数是作者对规模的描述，不是本次重新统计的结果。

当日最新提交为 [2026-08-03：link to microgpt](https://github.com/karpathy/micrograd/commit/7bc720e951fe422b8f8814aa5aa1b64121d26b4c)，主要补充延伸学习入口；不能据此宣称高频功能迭代。

采用：核保项目展示脱敏输入、结论、证据来源、规则或工具调用路径；Spring 实验展示最小请求与响应；Skills 展示调用前提、示例任务与产物。验证说明链接到真实测试或运行记录，而不是只写“完整测试”。

## 5. 快速体验与完整复现分层：nanoGPT

- [karpathy/nanoGPT：README.md](https://github.com/karpathy/nanoGPT/blob/master/README.md) 按快速入门、完整复现、基线、微调、推理及排障组织内容。快速入门提供 GPU 与 Mac/CPU 路径，并解释配置变化和预期输出；Apple Silicon 路径提到 MPS。
- **当前状态必须保留：** README 顶部明确写明 nanoGPT 已旧且废弃，推荐 nanochat。当日最新提交是 [2025-11-12：添加 nanochat 与废弃说明](https://github.com/karpathy/nanoGPT/commit/3adf61e154c3fe3fca428ad6bc3818b27a3b8291)。正文仍有旧的 “active development” 描述，不能拿它代表当前维护状态。

采用：项目 README 分开写最小本地体验与连接外部服务的完整路径，并标注系统、依赖、配置与限制。Mac 是可复现环境的一个维度；没有实际运行记录时不承诺性能数字。

## 6. 固定栏目与可回溯归档：阮一峰周刊

- [ruanyf/weekly：README.md](https://github.com/ruanyf/weekly/blob/master/README.md) 说明周五发布、Issue 投稿入口，并按年、月和期号建立完整索引。
- [docs/issue-416.md](https://github.com/ruanyf/weekly/blob/master/docs/issue-416.md) 按主题、文章、工具、资源等栏目组织；资源附原始链接、短说明，投稿内容可追溯到 Issue 与投稿者。
- 当日最新提交为 [2026-10-23：release issue 416](https://github.com/ruanyf/weekly/commit/a17ecb0043d312f4b2acc5c56e60d513f6fce40c)。

采用：实践记录固定为“问题、做法、证据、下一步”，日期与源码链接进入索引。主页展示最近少量记录，完整内容进入文档。计划发布的文章不提前写成已发布；没有用户承诺就不设定对外周更承诺。

## 7. 知识路径与低门槛贡献：JavaGuide

- [Snailclimb/JavaGuide：README.md](https://github.com/Snailclimb/JavaGuide/blob/main/README.md) 按 Java、计算机基础、数据库、系统设计等领域导航，并区分常见问题、重要知识详解与源码分析。
- [docs/javaguide/contribution-guideline.md](https://github.com/Snailclimb/JavaGuide/blob/main/docs/javaguide/contribution-guideline.md) 提供纠错、完善、新增方向；小改可在线编辑，大改走 Fork 与 PR，也提供 Issue 建议结构，并强调原创和中文排版。
- 当日最新提交为 [2026-10-16：合并 Maven 过期链接修复 PR](https://github.com/Snailclimb/JavaGuide/commit/50f02a5984c062fe7221629d0a6a40ec15c26fd7)，是持续文档维护的具体证据。

采用：Java/Spring 内容以学习和运行任务导航，而不是堆技术名词。贡献指南让读者能报错、复现、修正文档；报告要求预期、实际、复现步骤与环境。不会移植其受众规模、奖励或商业产品。

## 8. 对 hrniux 公开作品的实际取舍

公开作品具备 Java/Spring、Agent、Skills 与交互实验等方向，但主页需要一条清楚主线。选择“Java/Spring 后端与可解释 Agent 工程实践”：核保提供领域场景，spring-boot-lab 提供基础工程练习，codex-skills 提供工作流复用，其他作品保留探索面。

描述的可信度来自仓库当前默认分支、可运行示例、测试和公开 PR 状态。核保 [Draft PR #2](https://github.com/hrniux/insurance-underwriting-agent/pull/2) 尚未合并，其变化不能写成 `main` 已有能力。公开文档不包含任何非公开仓库的名称、链接、路径或推测。

GitHub Studio 新独立仓库创建遇到 403，当前源码位置是 [hrniux/hrniux 的 github-studio 分支](https://github.com/hrniux/hrniux/tree/github-studio)。它是临时承载位置，不等同于已创建 `hrniux/github-studio`；权限恢复后再迁移，并验证迁移结果。

详细执行取舍见 [PORTFOLIO_STRATEGY.md](PORTFOLIO_STRATEGY.md)。
