# 维护状态摘要

核查时间：2026-10-25T06:03:19.285074Z。这是读取观察，不是写操作执行结果。

| 当前远端观察 | 项数 |
|---|---|
| 已满足 | 1 |
| 与计划不同 | 16 |
| 当前连接读取404 | 2 |
| 无法判断 | 20 |
| 浏览器待办 | 6 |

历史执行检查点仍为38项blocked、6项manual、1项pending，配置与检查点的SHA-256在audit前后相同。

唯一已满足项是 `topics-insurance-underwriting-agent`。历史403写入记录保留为blocked；观察到满足不改写为applied。

两项404来自同一个 `hrniux/github-studio` 目标的创建和描述任务，不表示两个仓库不存在；当前连接的404也不能证明其他授权连接不可见。20项Star观察无权读取，不能据此断定此前是否收藏。

[完整远端观察](remote-audit.json) · [历史执行](execution-summary.json) · [恢复检查点](resume-state.json) · [使用方法](../docs/MAINTENANCE.md)
