# GitHub Studio

用公开证据整理 GitHub 作品集，并通过可恢复的操作队列维护个人简介、仓库信息与项目导航。

当前源码入口：[hrniux/hrniux 的 github-studio 分支](https://github.com/hrniux/hrniux/tree/github-studio)。独立仓库 `hrniux/github-studio` 的创建曾遇到 HTTP 403，目前保留在操作队列中；它不是当前源码入口。

## 快速开始

在项目根目录运行，需要 Python 3。执行远端操作还需要已安装 GitHub CLI，并已通过 `gh` 登录 `hrniux`；项目不接收或保存 Token。

```bash
# 离线查看计划与本地状态，不调用 GitHub API
python3 scripts/studio.py plan --json
python3 scripts/studio.py status --json

# 执行配置中的远端变更，并保存去敏公开报告
python3 scripts/studio.py apply --report reports/execution-summary.json

# 权限补足后，显式重试被阻止的操作
python3 scripts/studio.py apply --retry-blocked --report reports/execution-summary.json
```

只有 `apply` 执行远端写操作。运行前应阅读 [操作配置](config/operations.json)；`plan` 和 `status` 仅展示同一份配置对应的本地状态，不查询远端是否漂移。执行器首先核验登录账号，再执行操作；每项写入经读回比对后才记录为 `applied`。

## 当前配置

45 项操作包含 20 项公开仓库 Star、16 项现有仓库描述或 Topics 更新、1 项个人 bio 更新、1 项公开仓库创建、6 项手动置顶计划，以及 1 项依赖创建成功的新仓库描述更新。这是配置数量，不代表执行成功数量。

当前结果以 [执行报告](reports/execution-summary.json) 为准。`pending`、`manual`、`applied`、`blocked`、`failed` 的含义及恢复方式见 [运行说明](docs/OPERATIONS.md)。置顶没有本项目可用的受支持 API，保留为之后通过浏览器完成的任务。

默认运行状态保存在已被 Git 忽略的 `.local/state.json`；可用 `--state` 指定路径。执行器面向单进程使用，不应让多个进程同时写同一状态文件。HTTP 401/403 会保留为 `blocked`，普通 `apply` 不会重试这些项目。

## 项目内容

```text
config/                    公开仓库清单、作品集规划和显式操作配置
profile/                   个人主页 README 与展示素材
scripts/studio.py          plan / status / apply 命令入口
studio/operations.py       校验、执行、读回核验和状态持久化
tests/                     执行器行为测试
docs/RESEARCH.md           创作者调研与原始来源
docs/PORTFOLIO_STRATEGY.md  作品集策略与项目叙事
docs/OPERATIONS.md         状态恢复、权限与发布说明
reports/                   去敏公开执行报告
```

阅读 [调研来源](docs/RESEARCH.md) 与 [作品集策略](docs/PORTFOLIO_STRATEGY.md)，了解导航、项目选择和真实成果展示的依据。公开产物只收录公开仓库与可核验内容，不将草稿或未合并代码描述为已发布能力，也不创建定时任务。

## 验证与贡献

仅使用 Python 标准库，无需安装项目依赖：

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖离线查看、账号核验、权限失败与重试、重复执行、写后验证、配置变更、输入边界、手动任务、依赖和请求超时。贡献前请阅读 [贡献指南](CONTRIBUTING.md)。

本项目采用 [MIT License](LICENSE)，许可范围是此新项目，不改变其他已有仓库的许可。
