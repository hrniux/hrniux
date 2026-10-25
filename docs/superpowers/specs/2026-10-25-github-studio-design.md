# GitHub Studio 设计

用户明确授权全部做主、使用多代理、不询问问题。权限失败保留可重试任务。

## 定位与风格
hrniux 是 Java/Spring 后端与可解释 Agent/RAG/MCP 的实践者。借鉴 antfu 的简短导航、simonw 的真实成果与日期、Karpathy 的最小可运行示例、JavaGuide 的知识路径。原创文本和SVG，不移植履历、粉丝或商业信息。

## 交付
1. 新 Python3 标准库项目 github-studio：公开仓库清单、规划、profile源码、原始调研来源、操作配置、可恢复执行器和测试。
2. 实际更新 hrniux/hrniux 的 README 与新增原创SVG；展示3个核心项目、其他作品、真实实践入口；PR#2明确未合并。
3. 尝试应用公开仓库description/topics与个人bio。缺权限保存blocked，不询问、不伪报成功。
4. 新仓库创建已被403阻止，项目保存到现有profile仓库的独立github-studio分支；未来可发布为hrniux/github-studio。
5. 保留上轮20个AI Star任务与6个UI置顶计划；没有受支持的pin API，置顶归manual，不发明API。
6. 修正核保README的Maven Wrapper命令与Verify README已核实的旧owner提交链接；不改业务逻辑，不合并既有PR。

## 工具契约
scripts/studio.py 提供 plan、apply、status。config/operations.json是显式操作列表，schemaVersion=1、owner=hrniux、operations数组。kind限repo_metadata/repo_topics/user_profile/star/create_repository/manual_pin。操作id唯一，每项含id、kind、target、desired，依赖用depends_on可选。
repo_metadata仅description与homepage；repo_topics为topics数组(最多20，小写数字连字符，每项1..50，实际建议<=20字符)；user_profile仅bio(<=160字符)；star目标必须在公开20项名单；create_repository仅hrniux/github-studio public；manual_pin不调用写API。
默认plan/status无远端写。apply才执行，用gh api --hostname github.com，通过stdin传JSON。先验账号hrniux，超时有界，不输出令牌；所有写后读回比对才能applied。支持状态原子落盘、已完成项跳过、配置内容改变须重新判定，blocked只在--retry-blocked时重试。403/401 => blocked，其他异常=>failed；manual操作永不执行。失败不阻止无依赖的后续项，依赖未完成的项保持待办。拒绝未知kind、其他owner目标(Star白名单除外)、越界配置和任意shell命令。不要创建调度任务。

公开文件只包含公开仓库、提案和去敏执行结果。私有仓库的名称/URL/路径不得进入公开产物。运行状态默认为.local/state.json且gitignored，完整诊断也只存.local。reports/execution-summary.json只输出公共id、kind、target、status和非敏感原因。不得将未合并的Draft代码当main已发布能力。

## 验收
Python行为测试先失败再实现：dry-run无写、错误账号无写、403持久化后能重试、applied再次运行跳过、写后不一致不成功、配置改变不误跳过、未知操作/跨owner被拒绝、manual无写、依赖/原子状态、gh超时不会挂起。完整套件、实际plan与受控fake-gh执行通过。远端profile/分支/每项metadata写都须回读确认。最终提供源代码与执行报告/ZIP、已完成和待权限项的准确清单。
