# 按目标开始

[返回主页与七个公开项目入口](README.md)。每条路线可先留约 30 分钟学习：这是建议的时间盒，不是安装、构建或测试耗时的测量。首次下载依赖、准备运行环境另计；命令均在各自仓库根目录执行，一次选择一条即可。完整说明与后续变化以链接的仓库 README 为准。

## 后端：跑通一次决策，再追踪依据

从 [insurance-underwriting-agent README](https://github.com/hrniux/insurance-underwriting-agent#readme) 开始。准备 Git、JDK 21+、Maven 3.9+ 和浏览器；终端健康检查需要 curl。默认模型与数据均为离线 Mock，不需要 API Key 或外部数据库，首次构建仍需下载 Maven 依赖。

```sh
git clone https://github.com/hrniux/insurance-underwriting-agent.git
cd insurance-underwriting-agent
mvn clean verify
mvn spring-boot:run
```

另开终端运行 `curl --fail http://localhost:8080/actuator/health`，然后打开 [本地演示台](http://localhost:8080/demo/)。选择一个虚构场景，运行核保并沿“规则与证据”查看规则命中、知识引用和七步轨迹，再下载 Markdown 报告。目标是能解释一次结论来自哪些事实与规则；这是学习演示，不能用于真实承保。按 Ctrl+C 停止服务，默认内存数据会随进程退出丢失。

若想先学更小的 HTTP API，改选 [spring-boot-lab README](https://github.com/hrniux/spring-boot-lab#readme)：准备 JDK 21，仓库自带 Maven Wrapper，首次运行需联网下载。

```sh
git clone https://github.com/hrniux/spring-boot-lab.git
cd spring-boot-lab
./mvnw test
./mvnw spring-boot:run
```

另开终端使用 `curl http://localhost:8080/api/tasks`，按其 README 创建、完成一个任务，再追踪 Controller → Service → 测试中的校验和错误响应。这两个后端默认都占用 8080，请先停止前一个；任务仓储同样在重启后清空。

## 游戏：体验一个循环，再读状态变化

无需安装开发环境即可打开 [browser-game-arcade 在线入口](https://hrniux.github.io/browser-game-arcade/)，选择一款游戏并读页面操作提示。想改代码时，查看 [arcade README](https://github.com/hrniux/browser-game-arcade#readme)，用静态服务器加载本地副本：

```sh
git clone https://github.com/hrniux/browser-game-arcade.git
cd browser-game-arcade
python3 -m http.server 8000
```

本地需 Git、Python 3 和浏览器；打开 [本地合集](http://localhost:8000/)，对照所选页面与 `src/js` 阅读输入、状态更新和绘制。个别实验依赖外部 CDN；完整浏览器回归所需的 Node/Chrome 配置另见仓库贡献指南。

若更想研究耕种和存档，改选 [harvest-valley-lite README](https://github.com/hrniux/harvest-valley-lite#readme)，准备 Git、Node.js 22、npm 和浏览器（Node 版本沿用其 CI 配置）：

```sh
git clone https://github.com/hrniux/harvest-valley-lite.git
cd harvest-valley-lite
npm install
npm run dev
```

打开终端给出的 Vite 地址，完成耕地 → 播种 → 浇水 → 睡觉 → 收获的一次循环，再刷新观察存档状态。存档仅留在当前浏览器；受限存储或多标签页冲突会暂停保存，建议只开一个游玩标签页。完整 `npm run check` 含构建和 Playwright 回归，运行前按 README 准备 Google Chrome。

## 知识与证据：把结论和验证范围分开

不需要本地运行环境即可阅读 [math-conjectures README](https://github.com/hrniux/math-conjectures#readme) 与其[学习路线](https://github.com/hrniux/math-conjectures/blob/main/LEARNING-GUIDE.md)。选一个熟悉的条目，写下精确陈述、一个例子与当前状态，再沿条目来源核对。开放问题、已证定理、反例和相对公理独立性需要分别理解；读完条目不等于完成数学证明。

想亲手运行一次证据核验，查看 [verify-authenticity README](https://github.com/hrniux/verify-authenticity#readme)。下面的 JSON 路线只需 Git 与 Python 3.9+，不执行 Maven 构建；必须保留完整 Git 历史，不使用浅克隆。

```sh
git clone https://github.com/hrniux/verify-authenticity.git
cd verify-authenticity
python3 -B scripts/verification_report.py
```

阅读 `historical_rounds`、`screenshots`、`errors` 和 `limitations`，把固定提交字段与截图文件哈希的核验结果分开记录。若缺少历史对象或文件，先查看错误，不把失败报告当作通过。若要运行 Java 演示，另备 JDK 21 与 Maven，再按 README 执行 `bash scripts/verify.sh`。字段或哈希一致不能认证截图事件或真实操作者身份。

## 把学习过程变成可复用工作流

[codex-skills README](https://github.com/hrniux/codex-skills#readme) 提供独立的技能目录。先阅读一个 `SKILL.md`，确认它的路径、平台与权限适合自己的环境；不必为浏览项目安装技能。若要检查本地集合，准备 Git 与 Python 3.9+：

```sh
git clone https://github.com/hrniux/codex-skills.git
cd codex-skills
python3 -B scripts/validate_skills.py
```

该命令检查仓库声明的元数据和本地资源，不会替你安装技能。macOS 本地凭据或 Obsidian 路径相关技能需要按其说明单独配置。
