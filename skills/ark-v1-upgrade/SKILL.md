---
name: ark-v1-upgrade
description: 协助已有 ARK 项目升级到 Ark v1 正式版（1.x），升级 pxnpm 到 7，查询最新正式版本并通过 pxnpm update ark 升级，检查运行时、旧构建插件和配置，验证开发、生产构建和微应用。用于 ARK 消费项目升级，不用于维护 ARK 构建核心本身。
---

技能名为 `ark-v1-upgrade`，升级目标为 Ark v1 正式版（1.x）。发布仓库为 [nfjBill/agent-skills](https://github.com/nfjBill/agent-skills)，安装与路径说明见仓库根目录 README。核心与插件保留各自版本线，不将其版本改为前端版本。测试包需由用户明确选择 beta 标签或具体预发布版本。

先检查项目，再按真实失败修复。目标是保持 `arkc`、`arkclib`、`ark-plus`、`pxnpm` 命令，`ark.config.*`、`WORKSPACE_PWD`、`ARK_` / `ARK_PLUS_` 配置和既有部署产物习惯。

1. 读取项目说明、package.json、工作区配置、ark.config 和原构建脚本，同时盘点项目根目录及实际参与构建的子项目的 `.nvm`、`.nvmrc`、`.node-version`。运行 `python3 <本技能目录>/scripts/check_project.py <项目目录>`；这是只读检查，不会执行配置或读取环境变量值。
2. 根据目标 ARK 包的 engines 确认 Node 要求，当前为 `^20.19.0 || >=22.12.0`。检查版本文件与实际执行 Node：已有文件锁定不兼容版本时，按项目原运行时管理方式选择兼容版本，原地更新该文件，保留文件名、格式、注释及加载方式；已满足要求的版本保留。项目使用 `.nvm` 就维护 `.nvm`，先核对脚本如何读取它，不擅自改名或另建 `.nvmrc`。`v20`、`lts/*` 等选择器需要实际解析，若仍选到低版本，安装并切换到兼容版本，必要时按项目习惯锁定具体版本。切换后执行 `node -v` 和 `node -p process.execPath`，再运行安装与构建；同步实际使用的 Dockerfile、CI image 和 package.json engines，确保各入口满足要求。保留用户的包管理器和私有 registry。
3. 按 [包管理器与版本升级](references/upgrade.md) 检查实际执行的 pxnpm，并将旧版升级到 7.x 正式版，同步项目和 CI 中实际使用的版本约束。用户未指定 ARK 版本时，从私库查询最新正式版，核对 arkc 与 ark-plus 同批版本后，在业务工作区根目录执行 `pxnpm update ark <查询到的具体版本>`；用户指定版本或本地 tarball 时遵循该目标。此命令不更新 arkclib，库项目需单独处理。保持框架依赖原主版本；不要顺带升级 Vue 2、React、Svelte 4、Solid 1。执行原安装和构建命令，记录具体失败。新版 pxnpm 的依赖脚本审批报错，以及 ARK `1.0.1-beta.0` 的 Babel 混用报错，按 [安装排错](references/install.md) 处理；验证必须包含正常安装，不能仅用 `--ignore-scripts` 宣称通过。
4. 默认保留 `source.alias`、旧代理 `context` / `onProxyReq` 等回调、生产服务钩子、HTML 的 `htmlWebpackPlugin` / `webpackConfig`、性能分析配置和原环境变量：ARK 已提供兼容。工作区公共配置先合并，应用配置后合并，ARK 环境变量最后覆盖；不要同时重写为不同体系。
5. 对构建插件按失败处理：优先使用包的公开导出，不再深引 `dist` 私有路径；`@rspack/core/dist/config` 的类型改为从 `@rspack/core` 导入。在 `tools.bundlerChain` 或 `modifyBundlerChain` 中，旧 JS/CSS loader 已由 ARK 迁入主 oneOf 分支；若插件直接遍历 `.uses`，改为读取 `CHAIN_ID.ONE_OF.JS_MAIN` / `CSS_MAIN` 后的分支，避免修改 raw/inline 分支。保留 loader 顺序和 options。
6. 对真实 webpack 后端项目，核对插件是否支持 Rspack，然后逐项迁到 `tools.rspack` / `tools.bundlerChain`。无法替代的 webpack 专属插件需要解释具体差异，并保留可运行的旧分支；不能删掉插件后宣称升级成功。不要机械替换任意源码中的“webpack”字符串。
7. 保留 `PUBLIC_` 变量的构建期默认值和 ARK 容器运行期覆盖。开启加密时继续使用项目现有 yk4 地址和协议，不迁移服务或生成新密钥。无现成服务时验证协议模拟，明确真实 yk4 环境未验证。
8. 运行项目已有类型检查、单测、`arkc dev` 和生产构建 / preview。微应用应验证主应用路由、挂载/卸载、子应用资源和异步 chunk 的路径，检查聚合 dist、nginx_ark.conf、.env.gci 中的路由/代理。库应检查 require/import 和声明文件。不执行发布、远程部署或 SSH，除非用户要求。

交付改动、通过的验证、仍有差异的具体功能和原样可用的命令。不要只提供建议，不要把尚未验证的场景写成兼容通过。
