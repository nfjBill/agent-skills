# ARK Agent Skills

帮助 coding agent 将已有 ARK 业务项目升级到 ARK 1.x，采用 arkcbuild V2 构建核心。技能名中的 v1 指 ARK 1.x 产品版本，V2 指构建核心代际。

Skill 是供 AI 编程助手读取的操作指引，附带可执行的检查脚本。安装 skill 后，还需要在待升级业务项目里向助手发出升级请求。Skill 不包含 ARK 软件包，也不会在安装时自动升级项目。

## 提供的技能

| 技能 | 用途 |
| --- | --- |
| [ark-v1-upgrade](skills/ark-v1-upgrade/SKILL.md) | 升级 pxnpm 到 7，查询 ARK 最新正式版并执行升级，验证开发、生产构建和微应用 |

保留现有 `arkc`、`arkclib`、`ark-plus`、`pxnpm` 命令、`ark.config.*`、环境变量、框架主版本和部署格式。本技能用于使用 ARK 的业务项目，不用于维护 ARK 构建核心自身。

## 安装

先进入**待升级业务项目的根目录**。以下命令中的仓库地址是示例，请替换成实际发布地址。

### 从 GitHub 安装

```sh
npx skills add YOUR_ACCOUNT/ark-agent-skills --skill ark-v1-upgrade --agent codex
```

### 从 GitLab 安装

```sh
npx skills add https://gitlab.com/YOUR_GROUP/ark-agent-skills.git --skill ark-v1-upgrade --agent codex
```

公司自建 GitLab 可以使用其完整 Git URL。私有仓库要求使用者拥有访问权限，并已配置相应的 Git 登录或 SSH 凭据。

### 从本地目录安装

将 `/path/to/ARK` 替换成你的 ARK 工作区路径：

```sh
npx skills add /path/to/ARK/agent-skills --skill ark-v1-upgrade --agent codex
```

默认安装到当前项目。给 Claude Code 使用时，把 `--agent codex` 改成 `--agent claude-code`；安装到个人目录、供多个项目使用时，可以添加 `--global`。

不使用安装工具时，也可以把完整的 `skills/ark-v1-upgrade/` 文件夹复制到业务项目的 `.agents/skills/ark-v1-upgrade/`（Codex）或 `.claude/skills/ark-v1-upgrade/`（Claude Code）。应一起复制脚本和许可证。

安装工具的来源、参数和支持的客户端见 [skills CLI 官方仓库](https://github.com/vercel-labs/skills)。

## 让助手执行升级

用 coding agent 打开待升级业务项目，发送下面的提示词。默认查询私库的最新正式版；需要指定版本或本地 tarball 时替换目标说明。

```text
请使用 ark-v1-upgrade 技能，将当前业务项目升级到 ARK 1.x（arkcbuild V2）。

先将旧版 pxnpm 升级到 7.x 正式版，再查询私库的 ARK 最新正式版本，
核对 arkc 与 ark-plus 同批后执行 pxnpm update ark <具体版本>。
如果使用 arkclib，请单独更新到同批版本。

先检查项目，再完成必要修改。保留现有命令、ark.config、
环境变量、框架主版本、微应用入口和部署方式。
验证类型检查、单测、开发启动、生产构建及微应用。
最后交付修改说明、验证结果和未验证的具体场景。
```

旧版技能名为 `ark-v2-upgrade`；已安装旧版的业务项目需移除旧技能目录，再按新名称重新安装，避免重复发现。在 Codex 中也可以使用 `$ark-v1-upgrade` 明确调用。技能未出现在选择列表时，可以重启客户端后再试。

升级需要业务项目能访问目标 ARK 包的 registry，或取得对应的本地 tarball。业务构建运行时需要 Node 20.19+ 或 22.12+；下面的检查脚本需要 Python 3，且仅使用标准库。

pxnpm 自身通过 npm 官方仓库升级到 7.x，ARK 最新版本从私库 `dist-tags.latest` 获取，不自动选择 beta。具体安装命令、版本核对及指定版本 / 本地包的处理见 [包管理器与版本升级](skills/ark-v1-upgrade/references/upgrade.md)。

升级时会检查已有的 `.nvm`、`.nvmrc`、`.node-version`。文件锁定不兼容版本时，助手会按项目原有加载方式原地更新，并核对实际执行的 Node、package.json engines 与 CI / Docker 构建版本。满足要求的版本保留，不改变文件名或另建竞争的版本配置。`v20`、`lts/*` 等选择器会提示实际解析与验证，避免只看主版本就认定兼容。

### 单独运行只读检查

在本技能仓库根目录执行，将项目路径替换为待检查业务项目：

```sh
python3 skills/ark-v1-upgrade/scripts/check_project.py /path/to/business-project
```

输出 JSON，包括 ARK 依赖、构建脚本、Node 要求、`nodeVersionFiles` 版本文件清单及需要人工核对的扩展配置。版本文件状态区分 `compatible`、`incompatible`、`needs-resolution` 和 `needs-review`；这只评估文件中的配置，不代表当前终端或 CI 已切换到该版本。脚本不修改项目、不运行 nvm、不执行配置文件，也不读取环境变量值。该检查只提供升级线索，兼容性仍需实际构建和运行验证。

## 发布为独立 Git 仓库

本目录可以整体作为 GitHub 或 GitLab 仓库的根目录：

```text
ark-agent-skills/
├── .gitignore
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

不需要 npm 发布，也不需要构建 ARK。独立仓库仅需本目录的文件。

1. 在 GitHub 或 GitLab 创建空仓库，例如 `ark-agent-skills`。不要在网页中初始化 README 或许可证，以便按下面步骤首次推送。
2. 从 ARK 工作区根目录，将本目录复制到一个新的、尚不存在的目标目录。例如：

   ```sh
   cp -R agent-skills ../ark-agent-skills
   cd ../ark-agent-skills
   ```

3. 把本 README 中的 `YOUR_ACCOUNT`、`YOUR_GROUP` 和示例仓库名替换为真实地址。然后初始化独立仓库并提交：

   ```sh
   git init -b main
   git add .
   git commit -m "Add ARK upgrade skill"
   ```

4. 设置远程地址，再推送。以下是 GitHub 示例；GitLab 使用网页上给出的 Git URL：

   ```sh
   git remote add origin https://github.com/YOUR_ACCOUNT/ark-agent-skills.git
   git push -u origin main
   ```

5. 将 README 中的安装命令和使用提示词分享给业务开发者。公开仓库便于直接安装；私有仓库需要先授予访问权限。

本说明里的 Git 推送命令需要发布者自行执行；目录整理不会创建远程仓库或推送文件。

### 发布前与更新后核对

在独立仓库根目录检查技能能被安装工具发现：

```sh
npx skills add . --list
python3 -m unittest discover -s tests
```

再进入一个临时业务项目，使用本仓库的绝对路径安装，确认技能和检查脚本一同被复制。安装成功不等于升级成功，还需在真实业务项目上执行升级验证。

维护时在 ARK 的 `agent-skills/` 目录修改，再同步到独立发布仓库。当前 ARK 工作区中的 `.agents/skills/ark-v1-upgrade` 是指向本目录的发现链接；独立发布时无需复制该外层链接。

## 许可证

沿用 ARK 项目的 [MIT License](LICENSE)，保留原版权声明。技能文件夹内也附带许可证，便于单独安装和分发时保留许可文本。
