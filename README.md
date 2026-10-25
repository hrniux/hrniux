<div align="center">
  <img src="./assets/profile-hero-light-v2.svg#gh-light-mode-only" alt="hrniu" width="100%" />
  <img src="./assets/profile-hero-dark.svg#gh-dark-mode-only" alt="hrniu" width="100%" />
</div>

Java / Spring 后端工程师，专注于可解释智能体系统——RAG、确定性规则、MCP 工具、审计与决策重演。也做浏览器原生小游戏、Codex 工作流，以及一个数学猜想百科。

## 精选项目

下面的文字入口与项目卡片对应，方便直接选择体验方式或阅读路线。

| 想看什么 | 项目与入口 | 从哪里开始 |
|---|---|---|
| Java 智能体的完整业务链路 | [insurance-underwriting-agent](https://github.com/hrniux/insurance-underwriting-agent) | 按 README 启动离线 Mock 演示，在 `/demo/` 对比虚构场景，再追踪规则、证据与人工复核 |
| Spring HTTP 接口实践 | [spring-boot-lab](https://github.com/hrniux/spring-boot-lab) | 先运行 Maven 验证，再从任务 API 阅读 Controller → Service → 测试 |
| 即开即玩的浏览器作品 | [browser-game-arcade 在线入口](https://hrniux.github.io/browser-game-arcade/) · [源码](https://github.com/hrniux/browser-game-arcade) | 从菜单筛选小游戏；开发时按仓库指南运行逻辑检查与浏览器回归 |
| 小型游戏的状态建模 | [harvest-valley-lite](https://github.com/hrniux/harvest-valley-lite) | `npm install`、`npm run dev`，体验耕种循环后阅读游戏状态与边界测试 |
| 可复用的开发工作流 | [codex-skills](https://github.com/hrniux/codex-skills) | 阅读技能说明，按自己的路径与权限配置；先检查再执行本地操作 |
| 数学概念的精确表述 | [math-conjectures](https://github.com/hrniux/math-conjectures) | 从目录按领域与问题状态阅读，区分猜想、定理、反例和独立性 |

后端演示使用虚构数据，供学习和工程讲解；各仓库的运行前提、已验证范围与限制以其 README 为准。

<a href="https://github.com/hrniux/insurance-underwriting-agent">
  <img src="./assets/cards/insurance.svg" width="100%" alt="insurance-underwriting-agent">
</a>

<a href="https://github.com/hrniux/spring-boot-lab">
  <img src="./assets/cards/spring-boot.svg" width="100%" alt="spring-boot-lab">
</a>

<a href="https://github.com/hrniux/browser-game-arcade">
  <img src="./assets/cards/game.svg" width="100%" alt="browser-game-arcade">
</a>

<a href="https://github.com/hrniux/harvest-valley-lite">
  <img src="./assets/cards/harvest.svg" width="100%" alt="harvest-valley-lite">
</a>

<a href="https://github.com/hrniux/codex-skills">
  <img src="./assets/cards/codex.svg" width="100%" alt="codex-skills">
</a>

<a href="https://github.com/hrniux/math-conjectures">
  <img src="./assets/cards/math.svg" width="100%" alt="math-conjectures">
</a>

## 技术栈

Java 21 · Spring Boot · Spring AI · RAG · MCP · Docker · Maven · JavaScript · Canvas · Vite · Playwright

## 当前在做

可解释智能体系统的评估、重演与治理，以及 Java 后端工程实践的沉淀。

## 维护这个主页

```sh
python3 scripts/check_profile.py
python3 -B -m unittest discover -s tests -v
```

检查覆盖本地行内链接、图片替代文字和 SVG 语法，不联网验证外部地址。新增卡片时请同时更新上方文字导航。
