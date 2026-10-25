# 运行与恢复

所有命令都在 GitHub Studio 项目根目录运行。只需 Python 3；远端执行还需 GitHub CLI 和已有的 `gh` 登录。项目不收集、接收或保存 Token，也不需要配置全局 Maven 或 JDK。

## 查看计划

```bash
python3 scripts/studio.py plan --json
python3 scripts/studio.py status --json
```

这两个命令读取配置与本地状态，离线运行，不调用 GitHub API，不更新状态文件。它们不是实时远端审计：其他工具改变了 GitHub 后，本地 `applied` 状态不会自动失效。

默认配置是 `config/operations.json`，默认状态是 `.local/state.json`。路径均相对于当前工作目录。可显式指定：

```bash
python3 scripts/studio.py status --config config/operations.json --state .local/state.json --json
```

`.local/` 已被 Git 忽略。自定义 `--state` 时也应使用不提交到公开仓库的本地路径。保留状态文件以便续跑；文件损坏时先备份、检查原因，不要直接删除。每个状态文件仅供一个进程操作，不支持并发合并。

## 执行与权限恢复

先确认已有登录属于 `hrniux`：

```bash
gh auth status --hostname github.com
python3 scripts/studio.py apply --report reports/execution-summary.json
```

只有 `apply` 写远端。执行前会读取登录账号；账号不匹配时停止。操作仅限显式配置中的公开资源，Star 还受 20 项白名单约束。每项写后读回核验，通过才标记 `applied`；状态通过临时文件与原子替换保存。

| 状态 | 含义与下一步 |
| --- | --- |
| `pending` | 尚未执行，或依赖未完成；之后继续 `apply`。 |
| `manual` | 浏览器任务；脚本保留计划，不发起置顶写入。 |
| `applied` | 当前操作配置已执行并读回核验；再次执行会跳过。 |
| `blocked` | 操作遇到 HTTP 401/403；补足权限后使用 `--retry-blocked`。 |
| `failed` | 请求、超时、响应或核验失败；检查原因后再次 `apply`。 |

403 不会触发交互提问，也不会被报告为成功。无依赖的后续操作仍可继续；依赖创建仓库的描述更新会等待创建成功。普通 `apply` 跳过 `blocked`；权限补足后统一恢复：

```bash
python3 scripts/studio.py apply --retry-blocked --report reports/execution-summary.json
python3 scripts/studio.py status --json
```

已应用的相同配置会跳过；修改某项配置后，其指纹变化，该项重新进入待处理。执行器并不回滚已完成的远端操作。

本次已将仅含公开操作编号、配置指纹、状态和原因类别的检查点导出为 `reports/resume-state.json`。从分支或 ZIP 获取项目后，可复用它，无需重新建立上次状态：

```bash
python3 scripts/studio.py apply --state reports/resume-state.json --retry-blocked --report reports/execution-summary.json
```

该命令会更新这份检查点。若希望继续使用默认本地状态，先将它复制到 `.local/state.json` 再运行默认命令。仓库内容发布的结果另见 `reports/publication.json`；参数操作执行器不把这些 Git 提交计入自己的 applied 项数。

退出码 `1` 表示本次结果包含 `failed`，`2` 表示配置、状态、账号或前置请求等错误；`blocked` 和 `manual` 本身不会使退出码非零。判断完成情况必须查看报告中的各项状态，不能只看退出码。

## 置顶与报告

6 项 `manual_pin` 记录建议位置。没有本项目可用的受支持置顶 API，应之后在 GitHub 个人主页通过浏览器完成；再次运行脚本也不会执行这些任务或将其标记为自动完成。

`reports/execution-summary.json` 由指定 `--report` 的 `apply` 写入，只包含公开操作的 `id`、`kind`、`target`、`status` 和固定去敏原因。完整状态留在本地；不要把 Token、原始认证输出或私有仓库名称、URL、路径加入公开报告。报告是对应状态文件的执行记录，不代表另一台机器的最新状态。

## 发布为独立仓库

当前源码保存在 [profile 仓库的 github-studio 分支](https://github.com/hrniux/hrniux/tree/github-studio)。独立仓库创建曾被 HTTP 403 阻止，保留的 `create-github-studio` 操作负责检查和创建它。权限补足后使用上面的统一重试命令，不要另行重复运行创建仓库命令。

仅在创建项显示 `applied`、目标公开仓库已存在后，才从本地项目推送源码。创建操作本身不会发布本地 Git 提交。推送需要 Git，并应先确认当前目录是此项目、提交内容已检查、目标分支没有需要保留的新提交。

如果从源码分支获取项目：

```bash
git clone --branch github-studio --single-branch https://github.com/hrniux/hrniux.git github-studio
cd github-studio
git branch -M main
git push https://github.com/hrniux/github-studio.git main:main
```

如果下载 ZIP 后没有 `.git`，先在解压后的项目根目录建立本地历史，再发布：

```bash
git init
git add .
git commit -m "Add GitHub Studio"
git branch -M main
git push https://github.com/hrniux/github-studio.git main:main
```

如果项目本来已有 `.git`，检查并提交待发布的改动，再使用同一条 `git push`。不使用 force；若推送因远端已有提交而拒绝，先拉取检查并整合历史。

## 本地验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/studio.py plan --json
```

这些命令不会执行远端变更。本项目不创建定时任务，后续维护由明确运行命令触发。MIT 许可只覆盖此项目，不应据此为其他已有公开仓库添加或更换许可。
