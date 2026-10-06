# 包管理器与版本升级

## 先升级 pxnpm 到 7

在兼容的 Node 环境中记录 `node -v`、`node -p process.execPath`、`pxnpm --version` 和命令路径（POSIX 使用 `command -v pxnpm`，Windows 使用 `where.exe pxnpm`）。检查项目的 `packageManager`、pxnpm 依赖、安装脚本和 CI / Docker 中的版本固定，区分全局命令与项目局部命令；切换 Node 后要重新核对，避免继续执行旧 Node 环境中的 pxnpm。

pxnpm 自身从 npm 官方仓库发行，ARK 依赖从私库安装。对原本全局安装的旧版 pxnpm，使用当前 Node 随附的 npm：

```sh
npm install --global pxnpm@7 --registry=https://registry.npmjs.org/
pxnpm --version
```

`pxnpm@7` 限定 7.x 正式版，不固定过时 patch，也不自动选择 beta。若项目以局部依赖或 CI 工具管理 pxnpm，则沿用该安装位置升级到 7.x，并同步实际生效的约束；保留 `packageManager` 字段的原格式，具体版本应与已安装版本一致。已有兼容的 7.x 正式版无需重复安装；已有更高主版本时先核对兼容性，不自动降级。用户明确指定 pxnpm 测试版本或本地包时按指定来源安装，不把 ARK 的 beta 选择推定为 pxnpm 的 beta 选择。

安装后再次验证实际命令路径和版本，并运行一次实际安装命令；`--version` 成功不代表原生内核下载、私库访问或依赖安装已经通过。不要改写项目 `.npmrc` 或输出认证信息。pxnpm 7 的发行版使用固定私库和代理，不能通过给 pxnpm 加 `--registry` 切换网络；上面的 registry 参数只用于 npm 安装 pxnpm。安装脚本审批失败按 [安装排错](install.md) 处理。

## 查询 ARK 最新正式版本

ARK 工作区中 `packages/ark-plus/src/main.ts` 的 `UPDATE_REGISTRY_URL` 为：

```text
https://registry-pxnpm.rdc.nfjbill.ren:20021/ark-plus
```

与 `packages/ark-plus/src/update-version.ts` 的渠道规则一致，只读取包元数据的 `dist-tags.latest`，验证是有效的正式 semver；不按发布时间或 `versions` 数组取最大值，也不自动使用 beta。独立分发的技能无需依赖 ARK 源码存在，可用 npm 查询该私库：

```sh
npm view ark-plus dist-tags.latest --json --registry=https://registry-pxnpm.rdc.nfjbill.ren:20021/ --fetch-retries=0 --fetch-timeout=10000
npm view arkc dist-tags.latest --json --registry=https://registry-pxnpm.rdc.nfjbill.ren:20021/ --fetch-retries=0 --fetch-timeout=10000
```

默认目标应为两者一致的 ARK 1.x 正式版本，并核对该具体版本的包元数据和 `engines`。若标签不一致、值为空、是预发布版本、跨越 ARK 主版本，或查询发生网络 / 权限错误，记录具体原因，不猜测版本或静默换源。已安装版本满足目标时不重复更新；目标比现有版本旧时不自动降级。已有预发布安装需要保留用户选择，不能自动转回 latest。

用户已指定具体版本或本地 tarball 时优先遵循，不以 latest 覆盖；测试版本必须由用户明确选择。版本查询只读取元数据，不修改 registry 标签，也不执行发布。

## 用具体版本执行升级

在业务工作区根目录执行，把占位符替换为查询并核对过的实际版本：

```sh
pxnpm update ark <最新正式版本>
```

这是 pxnpm 的 ARK 专用入口，版本是独立的位置参数，不能写成 `ark@latest` 或省略版本。pxnpm 7 将其转换为 `update arkc@<版本> ark-plus@<版本> -r`，递归更新工作区中已有的两个依赖。升级前盘点实际使用这两个入口的子项目；升级后核对 manifest、锁文件和实际安装版本，避免将全局命令或漏装子项目当成升级成功。

该入口不包含 `arkclib`。项目使用 arkclib 时，先核对同批目标版本存在及其 engines，再在相应包中沿用原依赖分类单独更新到该版本。本地 tarball 按项目原安装方式安装对应入口，不把文件路径传给这个要求版本号的专用命令。

正常安装成功后再运行原构建与开发验证；不要删除锁文件、改用其他包管理器或用跳过脚本掩盖失败。交付时记录 pxnpm 的升级前后版本、registry 查询到的标签与具体 ARK 版本、实际升级命令及验证结果。
