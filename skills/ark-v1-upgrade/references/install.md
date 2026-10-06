# 安装排错

## pxnpm 7 的安装脚本审批

`ERR_PXNPM_IGNORED_BUILDS` 表示依赖已经安装，但有生命周期脚本尚未决定是否允许运行。读取实际工作区的 `pxnpm-workspace.yaml`；`set this to true or false` 是待处理占位值，并不是允许或拒绝。保留其他工作区设置、已有明确决定以及业务依赖的独立审批。

对日志中实际列出的包，核对当前安装版本的 package.json 和脚本用途。ARK 当前依赖图中 `@parcel/watcher`、`esbuild`、`sharp` 的 install/postinstall 用于准备或检查原生二进制，可为这些已核对的包记录 `true`；`core-js`、`svelte-preprocess` 当前版本的 postinstall 只输出提示，可记录 `false`。不要据此自动批准其他包，也不要覆盖项目已有拒绝决定。

在工作区 YAML 的 `allowBuilds` 中合并需要的布尔值，再执行 `pxnpm i`；已安装过且脚本曾被跳过时，用 `pxnpm rebuild <已批准的包名>` 或重新安装验证。pxnpm 7 也支持按名称审批并执行挂起的构建，例如核对这五个包后：

```sh
pxnpm approve-builds '@parcel/watcher' esbuild sharp '!core-js' '!svelte-preprocess'
pxnpm i
```

升级技能不以 `--ignore-scripts`、关闭 `strictDepBuilds` 或批准所有依赖替代实际处理。旧版 pxnpm 没有该命令时，按项目原有安装规则执行。

## 1.0.1-beta.0 的 Babel 版本混用

此批 ARK 的 Babel 与 Solid 插件误声明 Babel 8，而默认预设是 Babel 7，可能出现 `Requires Babel "^7.0.0-0", but was loaded with "8.0.6"`。应升级到包含修复的新批次，或者使用修复后的整批本地归档；同时更新项目使用的 `arkc`、`ark-plus`、`arkclib` 入口。不要给业务项目添加全局 Babel 7 override：编译器及其预设的依赖应由 ARK 自己维护，项目可保留其他工具独立使用的 Babel 版本。

beta 包需要用户明确选择版本。不要修改已经发布的 beta.0，也不要用新的 beta 覆盖正式 latest。构建与开发启动都应在正常安装成功后验证。

同一旧批次的对象 `server.proxy` 还可能丢失路径过滤，把首页和 HMR 请求转发到后端。修复后的 ARK 保留原对象路径、数组 `context`、`pathRewrite` 和 `onProxyReq`；消费项目无需重写代理配置。回归时应确认首页资源与 API 各走正确的路径，区分代理配置错误与测试环境中后端服务未启动。
