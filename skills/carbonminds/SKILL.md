---
name: carbonminds
description: '查询化学品与塑料的工艺级生命周期清单数据。CarbonMinds 覆盖化学品与高分子材料,建模细度到工艺路线层级,适合区分同一聚合物的不同合成路线、原料来源(石油基 / 生物基 / 再生)与地域。用于塑料件与化工产品的碳足迹、材料替代评估、生态设计选材、包装碳排。当任务涉及化学品排放因子、塑料碳足迹、聚合物 LCI、树脂、单体、生物基塑料、再生塑料时使用。触发词:CarbonMinds、化学品、塑料、聚合物、树脂、单体、PP、PE、PET、PVC、ABS、PA、生物基塑料、再生塑料、化工碳足迹。'
slug: carbonminds
displayName: 化学品与塑料 LCA 数据 —— CarbonMinds 工艺级清单
version: 1.4.0
summary: 查询化学品与高分子材料的工艺级清单数据,区分合成路线、原料来源与地域,用于塑料件与化工产品碳足迹。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CarbonMinds, 化学品, 塑料, 聚合物, 树脂, LCA, 碳足迹, 排放因子, 生命周期评价, LCI]
---

# CarbonMinds 化学品与塑料工艺级清单

塑料的碳足迹不是一个数。同一种 PP,石油基与生物基不同,不同合成路线不同,不同产地的能源结构也不同 —— 拿一个"通用 PP"的值套所有场景,在材料替代评估里会直接得出相反结论。

CarbonMinds 的价值就在这里:它把化学品与高分子建模到工艺路线层级,能把这些区分做出来。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 CarbonMinds 在内的 18 个国际主流数据源与 24000+ 已发布 EPD。

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。商品名、牌号要映射到化学名时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | CarbonMinds 的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 数值层 | GWP、LCIA 值 | **需 CarbonMinds 数据包权益** |

CarbonMinds 是商业库。**「库里有没有这条工艺、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` / `lcia` 返回 `restricted: true` 及原因(`reason`)。如实说明;免费库(BAFU、ELCD、EF)也有常见聚合物的数据,可作替代路径,但**必须说明这是替代,且工艺细度不同** —— 免费库通常只有材料级平均值,做不了路线区分。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给聚合物的 GWP。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本以 `lookup` 返回为准。
3. **路线不同的数据分别报,不要平均。** 用户问某种塑料时,如果候选里有多条不同工艺路线,把它们并列展示并说明区别来自哪个维度,不要自己挑一条或取中间值。
4. **先读数据集名称和参考流。** 单体与聚合物、粒料与制品、不同牌号在库里是不同条目。
5. **受限不是错误**,说明是哪个库受限、原因是什么,不静默替代。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `webUrl` 的,每条结果都一并给出,别等用户追问。
- **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`activityUuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 CarbonMinds。** 每次 `search` 都要带 `--sources carbonminds`,`methods` 也查 `carbonminds` —— 用户来装这个技能就是冲着这个库来的,混进别的库的候选只会让他
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
| 材料名 / 牌号 → 候选数据集 | `environmental-data search '<检索词>' --sources 'carbonminds' --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 过程贡献 / 热点(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读 —— 单体与聚合物是不同条目 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 引用前先确认 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因,替代方案要说明细度差异 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 什么时候该问用户

**先查、再对比、最后才问。** 材料名拿到就先检索,把候选和它们的区别一次给出来。

材料替代评估("换成再生料能减多少")属于**决策支持**:并列展示各路线的候选与数值,说明差异来自哪个维度,在证据支持时给带条件的推荐 —— 不要上来就问用户要哪条路线。

只有当需要敲定一条数据集、且剩余歧义会实质改变结论时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 与材料工程从业者写,用 ISO 14040/14044 与 ILCD 的标准术语。单元过程 · 参考流 · 功能单位 · 系统边界 · 截止法 cut-off。化学品用标准名(聚丙烯 / polypropylene),牌号只在用户给出时沿用。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;免费库可替代但要说明细度不同 |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | `methods carbonminds` 查 methodId,看 `methodIdsWithData` |
| 候选里全是单体 | 检索词落在原料层 | 用聚合物名或制品描述重新检索 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
