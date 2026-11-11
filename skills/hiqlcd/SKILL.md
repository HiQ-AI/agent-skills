---
name: hiqlcd
description: '查询中国本土生产场景的生命周期清单数据与排放因子。HiQLCD 覆盖中国全工业体系,另有铝产业链专库(HiQLCD-AL)与汽车行业专库(CALCD),遵循 GB/T 24040/24044 与 ISO 14040/14044 口径。中国的电网结构、燃料结构与工艺代际与欧美差异显著,用欧洲数据代表中国生产会系统性失真 —— 中国产地的核算应当用本土清单。当任务涉及中国工厂/中国供应链的碳足迹、国内排放因子取数、中国 BOM 碳核算、GB/T 口径核算、省级电网差异时使用。触发词:HiQLCD、中国本土数据、中国排放因子、国内因子、CALCD、中国电网、GB/T 24040、本土清单、中国碳足迹。'
slug: hiqlcd
displayName: 中国本土排放因子 —— HiQLCD 生命周期清单查询
version: 1.5.0
summary: 查询中国本土生产场景的清单数据与排放因子。HiQLCD 覆盖中国全工业体系,另有铝产业链与汽车行业专库,GB/T 24040 口径。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [HiQLCD, 中国本土数据, 中国排放因子, 中国清单, LCA, 碳足迹, 生命周期评价, GB/T 24040, 排放因子, LCI]
---

# HiQLCD 中国本土生命周期清单查询

中国产地的碳核算,数据也得是中国的。拿欧洲数据集代表国内生产是常见且严重的错误 —— 电网结构、燃料结构、工艺代际都不一样,而且这种错误不会报错,只会让整份核算系统性偏离。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,**自建中国本土生命周期清单数据库**,并聚合国际主流数据源与 24000+ 已发布 EPD。

中国本土系列:

| 库 | 覆盖 |
|---|---|
| **HiQLCD** | 中国全工业体系 |
| **HiQLCD-AL** | 铝工业数据库(中国有色金属工业协会 × 海科) |
| **CALCD** | 中国汽车生命周期数据库(中汽碳 × 海科) |

口径遵循 GB/T 24040/24044 与 ISO 14040/14044,系统模型覆盖截止法、后果法、EN 15804。

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。工厂俗称、BOM 行含糊时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 数值层 | GWP、LCIA 值 | **需对应数据包权益** |

HiQLCD、HiQLCD-AL、CALCD 都是商业库。**「库里有没有、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` / `lcia` 返回 `restricted: true` 及原因(`reason`)。如实说明是哪个库受限及原因。免费库(BAFU、ELCD、EF、worldsteel、USLCI)可以作为替代路径,但**必须说明这是替代、且不代表中国生产口径** —— 对国内产地而言这是降级方案,不是等价方案。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给国内因子 —— 记忆里的数不知道来源、年份和口径。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本号以 `lookup` 返回为准。
3. **产地是硬条件。** 用户说了中国产地,就不要用欧洲或全球平均数据集顶替。确实只有境外数据可用时,明确声明这是代理、哪些差异未修正。
4. **口径不一致不做对比。** 系统模型、功能单位、系统边界不同的数据不可比,先核对参考单位、系统模型与方法。
5. **有明确产地信息时不要停在「中国」。** 省级电网差异会实质改变结果,能追问到省就追问到省。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `webUrl` 的,每条结果都一并给出,别等用户追问。
- **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`activityUuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 HiQLCD。** 每次 `search` 都要带 `--sources hiqlcd`,`methods` 也查 `hiqlcd` —— 用户来装这个技能就是冲着这个库来的,混进别的库的候选只会让他
更难挑。用户明确要求跨库比较时,告诉他主技能 `hiq-cortex-lca` 更合适。

## 接入

数据经 **Environmental Data CLI** 读取,两个单文件程序,不依赖 node / python:

- `environmental-data` —— 背景数据库(生命周期清单数据集),用 `--sources` 选库;
- `epd-data` —— 已发布 EPD。

**没装就先装。** 安装脚本按版本固定,带 SHA256:下载到新建的空目录、校验、读过脚本再执行,不要 `curl … | sh`。

```bash
d=$(mktemp -d)
curl -fsSL -o "$d/install.sh" https://download.hiq.earth/cli/environmental-data/releases/v0.9.0/environmental-data/install.sh
shasum -a 256 "$d/install.sh"   # 必须是 f13f1d47dd9e5a638a346d70d78bc4b5ba4053dd84192e4083b1153ae244924e
sh "$d/install.sh"
```

`epd-data` 把路径里的 `environmental-data/install.sh` 换成 `epd-data/install.sh`,SHA256 必须是
`5e97bdaee937b76545b0c031a95b425282375ac594d09f76260f6f9197000b3c`。Windows 用同目录的 `install.ps1`
(`environmental-data` 为 `e0666f09ab802bbe1d9b871a9100e4d2a5a79512b91518e416cd803128a93f8d`,`epd-data` 为
`5d220436ec88aadd31a28892d53af9f0a3072cc76474367e600d7d92e94c9d3b`),`Get-FileHash -Algorithm SHA256` 校验后
`powershell.exe -NoProfile -File <脚本绝对路径>`。各平台归档与校验值以
[installation.json](https://github.com/HiQ-AI/environmental-data/blob/main/plugins/environmental-data/skills/environmental-data-query/references/installation.json)
为准。

**没有凭据时,第一步就是 `login` —— 不要让用户去控制台建 API key。**

```bash
environmental-data doctor          # exit 0 = 本机有凭据;exit 2 = 没有(不代表服务端权限)
environmental-data login --json    # ← 缺凭据或服务端拒绝凭据时走这条
```

`login` 是设备授权:授权链接与用户码打在 stderr,进程会一直等到用户授权或过期。**把返回的真实链接做成可点击的 Markdown 链接给用户,由他本人点授权**,不要替他授权、不要自己拼链接;进程成功退出后直接继续原来的任务,别停在「登录成功」。`epd-data` 有自己的 `doctor` / `login`;EPD 检索公开可用,`lookup` 需要登录。

`lookup`(含 GWP100)可以用 API key(`QUERYING_LCA_DATASETS_API_KEY`),数值按该 key 自己的权益与调用额度返回;**`lci`、`lcia`、`methods` 不接受 API key,只认 `login` 的凭据**。注册用户都能读免费库的数值;商业库数值还要账号已由海科开通 Environmental Data CLI 的商业数据访问,且只限账号已有的数据包权益,否则返回 `restricted`。

凭据由 CLI 自己保存 —— **绝不硬编码进为用户生成的文件,不在输出里回显,不从别的客户端借 token**。

## 工具

| 需求 | 命令 |
|---|---|
| 中文物料名 / BOM 行 → 候选数据集 | `environmental-data search '<检索词>' --sources 'hiqlcd' --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 单数据集过程贡献(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |

`--sources 'hiqlcd|hiqlcd-al|calcd|hiq-cesi'` 可同时检索多个本土库;地域可用 `--location CN` 或区域电网代码(如 `CN-ECGC` 华东电网)。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 引用前先确认 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因,替代方案要说明是降级 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 什么时候该问用户

**先查、再对比、最后才问。** 有可检索的对象就先检索,在同一轮里给结果;对话里已经说过的信息(产地、行业、材质)不要再问。

用户说「不确定该用哪个」是**决策支持信号**:给候选、在同一口径下并列、说明差异来自哪个维度、在证据支持时给带条件的推荐。

只有当需要最终敲定一个数据集、且剩余歧义会实质改变结果时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 从业者写,用 GB/T 24040、ISO 14040/14044 与 ILCD 的标准术语。单元过程 · 基本流 · 参考流 · 功能单位 · 系统边界 · 特征化因子 · 截止法 · 后果法。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;**绝不静默用境外数据替换** |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | `methods hiqlcd` 等查对应库的 methodId,看 `methodIdsWithData` |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| 加了 `--location` 就没结果 | 不认识的地域代码不匹配任何数据,也不会放宽 | 用返回里 `location.id` 的写法(`CN`、`CN-ECGC`、`RER`、`GLO` 等) |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
