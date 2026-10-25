# 维护检查与远端审计

GitHub Studio 将两种事实分开保存：`status` 展示操作执行记录，`audit` 读取当前远端值。过去一次写入返回403，并不证明当前远端一定与计划不同；其他工具或已有配置也可能使目标已经满足。

## 只读核查

```bash
python3 scripts/studio.py audit --state reports/resume-state.json --json --report reports/remote-audit.json
```

该命令只发起读取，不执行修改、创建、Star或置顶，不更新传入的检查点。报告中包含UTC核查时间、配置指纹，以及每项的 `local_status` 和 `remote_status`。它可以保存本地报告，但不会把观察结果写成 `applied`。

| 远端观察 | 含义 |
|---|---|
| `matches` | 成功读取到的数据满足该项配置；不表示本工具完成过写入。 |
| `differs` | 数据可读，但与预期不同。 |
| `missing` | 对应读取返回404；该资源或账号相对记录在此连接下不可见，不能据此断定其他授权连接也不存在。 |
| `unavailable` | 权限、连接、响应格式、账号或仓库身份检查未通过，无法得出满足与否的结论。 |
| `manual` | 浏览器任务，本命令不执行自动置顶。 |

只比较配置中声明的公开字段，Topics按集合比较；不收集完整个人资料或保存原始API响应。仓库必须公开且返回的规范名称与配置目标一致。所有请求通过现有有界GitHub CLI适配器执行；重复读取在单次核查内复用。

`matches`、`differs`、`missing` 是成功读取后的观察；存在 `unavailable` 时核查命令可返回非零。判断结果请看报告，不以退出码推断所有目标都已满足。

## 检查点与路径

检查点字段损坏时，工具会受控退出并保留原文件，供备份和恢复。不要把任意日志或异常对象塞入状态字段。

配置、检查点和报告必须是不同文件。路径规范化、软链接和硬链接别名也会检查；例如将报告指向 `config/operations.json` 或 `reports/resume-state.json` 会在远端调用前拒绝，以免覆盖恢复材料。

## 从观察继续处理

本轮不重试已经确认无权的写入。权限补足后仍使用原恢复命令：

```bash
python3 scripts/studio.py apply --state reports/resume-state.json --retry-blocked --report reports/execution-summary.json
```

这会明确执行写操作；audit与status不会替代该授权入口。置顶仍是单独的浏览器待办。

最新观察见 [远端审计报告](../reports/remote-audit.json)；历史执行见 [操作结果](../reports/execution-summary.json)。两份报告描述的不是同一个时间或同一种事实，不能互相覆盖。
