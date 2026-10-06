# ARK Agent Skills

帮助 coding agent 将已有 ARK 业务项目升级到 Ark v1 正式版（1.x）。技能发布仓库为 [nfjBill/agent-skills](https://github.com/nfjBill/agent-skills)，技能名为 `ark-v1-upgrade`。

Skill 是供 AI 编程助手读取的操作指引，附带可执行的检查脚本。安装 skill 后，还需要在待升级业务项目里向助手发出升级请求。Skill 不包含 ARK 软件包，也不会在安装时自动升级项目。

## 提供的技能

| 技能 | 用途 |
| --- | --- |
| [ark-v1-upgrade](skills/ark-v1-upgrade/SKILL.md) | 升级 pxnpm 到 7，查询 ARK 最新正式版并执行升级，验证开发、生产构建和微应用 |

保留现有 `arkc`、`arkclib`、`ark-plus`、`pxnpm` 命令、`ark.config.*`、环境变量、框架主版本和部署格式。本技能用于使用 ARK 的业务项目，不用于维护 ARK 构建核心自身。

## 安装

先进入**待升级业务项目的根目录**。

### 从 GitHub 安装

```sh
npx skills add nfjBill/agent-skills --skill ark-v1-upgrade 
```

也可使用完整地址：

```sh
npx skills add https://github.com/nfjBill/agent-skills --skill ark-v1-upgrade 
```

### 从本地目录安装

将 `/path/to/ARK` 替换成你的 ARK 工作区路径：

```sh
npx skills add /path/to/ARK/agent-skills --skill ark-v1-upgrade 
```

若克隆的是独立技能库，在其根目录使用 `npx skills add . --skill ark-v1-upgrade `。

默认安装到当前项目。给 Claude Code 使用时，把 `` 改成 `--agent claude-code`；安装到个人目录、供多个项目使用时，可以添加 `--global`。

不使用安装工具时，也可以把完整的 `skills/ark-v1-upgrade/` 文件夹复制到业务项目的 `.agents/skills/ark-v1-upgrade/`（Codex）或 `.claude/skills/ark-v1-upgrade/`（Claude Code）。应一起复制脚本和许可证。

安装工具的来源、参数和支持的客户端见 [skills CLI 官方仓库](https://github.com/vercel-labs/skills)。

## 让助手执行升级

用 coding agent 打开待升级业务项目，发送下面的提示词。默认查询私库的最新正式版；需要指定版本或本地 tarball 时替换目标说明。

```text
请使用 ark-v1-upgrade 技能，将当前业务项目升级到 Ark v1 正式版（1.x）。

先将旧版 pxnpm 升级到 7.x 正式版，再查询私库的 ARK 最新正式版本，
核对 arkc 与 ark-plus 同批后执行 pxnpm update ark <具体版本>。
如果使用 arkclib，请单独更新到同批版本。

先检查项目，再完成必要修改。保留现有命令、ark.config、
环境变量、框架主版本、微应用入口和部署方式。
验证类型检查、单测、开发启动、生产构建及微应用。
最后交付修改说明、验证结果和未验证的具体场景。
```

在 Codex 中也可以使用 `$ark-v1-upgrade` 明确调用。技能未出现在选择列表时，可以重新加载或重启客户端后再试。

### 从旧名称迁移

旧版技能名为 `ark-v2-upgrade`。使用 skills CLI 安装的旧版，在原安装范围执行：

```sh
npx skills remove ark-v2-upgrade 
npx skills add nfjBill/agent-skills --skill ark-v1-upgrade 
```

全局安装时，两条命令均添加 `--global`。手动复制安装的旧版，先移出旧技能目录，再复制新技能完整目录，核对 `SKILL.md` 中的 `name` 为 `ark-v1-upgrade`。不要同时保留两个可发现的升级技能目录。

### 升级环境

升级需要业务项目能访问目标 ARK 包的 registry，或取得对应的本地 tarball。业务构建运行时需要 Node 20.19+ 或 22.12+；下面的检查脚本需要 Python 3，且仅使用标准库。

pxnpm 自身通过 npm 官方仓库升级到 7.x，ARK 最新版本从私库 `dist-tags.latest` 获取，不自动选择 beta。具体安装命令、版本核对及指定版本 / 本地包的处理见 [包管理器与版本升级](skills/ark-v1-upgrade/references/upgrade.md)。

升级时会检查已有的 `.nvm`、`.nvmrc`、`.node-version`。文件锁定不兼容版本时，助手会按项目原有加载方式原地更新，并核对实际执行的 Node、package.json engines 与 CI / Docker 构建版本。满足要求的版本保留，不改变文件名或另建竞争的版本配置。`v20`、`lts/*` 等选择器会提示实际解析与验证，避免只看主版本就认定兼容。

### 单独运行只读检查

在本技能仓库根目录执行，将项目路径替换为待检查业务项目：

```sh
python3 skills/ark-v1-upgrade/scripts/check_project.py /path/to/business-project
```

从统一 ARK 工作区根目录执行时，需加上 `agent-skills/`：

```sh
python3 agent-skills/skills/ark-v1-upgrade/scripts/check_project.py /path/to/business-project
```

输出 JSON，包括 ARK 依赖、构建脚本、Node 要求、`nodeVersionFiles` 版本文件清单及需要人工核对的扩展配置。版本文件状态区分 `compatible`、`incompatible`、`needs-resolution` 和 `needs-review`；这只评估文件中的配置，不代表当前终端或 CI 已切换到该版本。脚本不修改项目、不运行 nvm、不执行配置文件，也不读取环境变量值。该检查只提供升级线索，兼容性仍需实际构建和运行验证。

## 独立仓库与路径

已发布仓库为 [nfjBill/agent-skills](https://github.com/nfjBill/agent-skills)。需要本地查看或维护时可克隆：

```sh
git clone https://github.com/nfjBill/agent-skills.git
cd agent-skills
```

独立仓库的根目录对应统一 ARK 工作区的 `agent-skills/`：

```text
agent-skills/
├── README.md
├── LICENSE
├── skills/
│   └── ark-v1-upgrade/
│       ├── SKILL.md
│       ├── LICENSE
│       ├── references/
│       │   ├── upgrade.md
│       │   └── install.md
│       └── scripts/
│           └── check_project.py
└── tests/
    └── test_check_project.py
```

统一 ARK 根目录中的技能路径是 `agent-skills/skills/ark-v1-upgrade/`；独立仓库根目录中的技能路径是 `skills/ark-v1-upgrade/`。检查脚本、安装来源和相对链接应按当前所在目录选用，无需重新初始化 Git 仓库或发布 npm 包。

### 更新后核对

在独立仓库根目录检查技能能被安装工具发现：

```sh
npx skills add . --list
python3 -m unittest discover -s tests
```

再进入一个临时业务项目，使用本仓库的绝对路径安装，确认技能和检查脚本一同被复制。安装成功不等于升级成功，还需在真实业务项目上执行升级验证。

维护时在 ARK 的 `agent-skills/` 目录修改，再同步到独立发布仓库。当前 ARK 工作区中的 `.agents/skills/ark-v1-upgrade` 是指向本目录的发现链接；独立发布时无需复制该外层链接。

## 许可证

沿用 ARK 项目的 [MIT License](LICENSE)，保留原版权声明。技能文件夹内也附带许可证，便于单独安装和分发时保留许可文本。
