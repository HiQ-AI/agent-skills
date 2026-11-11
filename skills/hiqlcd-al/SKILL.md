---
name: hiqlcd-al
description: '查询铝工业的生命周期清单数据。HiQLCD-AL 是中国有色金属工业协会与海科数据共建的铝工业数据库(以中国产业链为主),从氧化铝、电解铝到铸轧、挤压、压铸与再生铝,支持截止法与后果法两种系统模型。铝是电力密集型材料,原生与再生、不同电网结构下的碳足迹差异极大,用通用库的"铝"平均值做选材或减排决策会得出错误结论。当任务涉及铝材碳足迹、电解铝、原生铝与再生铝对比、铝型材、铝合金压铸件、铝箔、CBAM 铝品类时使用。触发词:HiQLCD-AL、铝工业数据库、有色金属工业协会、铝、电解铝、原生铝、再生铝、铝合金、铝型材、铝箔、压铸铝、氧化铝、铝碳足迹。'
slug: hiqlcd-al
displayName: 铝工业数据库 HiQLCD-AL(中国有色金属工业协会 × 海科)
version: 1.5.0
summary: 查询铝工业清单数据,中国有色金属工业协会与海科数据共建。氧化铝、预焙阳极、电解铝、铝加工产品,截止法与后果法双模型。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [HiQLCD-AL, 铝工业数据库, 有色金属工业协会, 铝, 电解铝, 再生铝, 铝合金, LCA, 碳足迹, 排放因子, 生命周期评价, CBAM]
---

# HiQLCD-AL 铝产业链清单数据

铝的碳足迹跨度是所有常用金属里最大的:电解环节的电力结构、原生还是再生、后续加工方式,每一项都能把结果推到不同量级。拿一个"铝 XX kg CO₂e/kg"的通用值做选材或减排测算,结论很可能是反的。

HiQLCD-AL 是**中国有色金属工业协会与海科数据共建**的铝工业数据库,能把这些环节分开。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。**HiQLCD-AL 是中国有色金属工业协会与海科数据携手打造的铝工业数据库**,以中国铝产业链为主,系统模型覆盖截止法与后果法。

产业链覆盖:氧化铝、预焙阳极(炭素)、电解铝、铝加工产品(铸轧与热轧、挤压型材、压铸件、铝箔),以及再生铝(废铝重熔)。

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。牌号、型材规格或工厂叫法含糊时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 数值层 | GWP、LCIA 值 | **需对应数据包权益** |

HiQLCD-AL 是商业库。**「库里有没有这道工序、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` / `lcia` 返回 `restricted: true` 及原因(`reason`)。免费库里 ELCD、BAFU 有通用铝数据可作替代,但**必须说明这是替代、且拿不到产业链分环节的细度** —— 做原生与再生对比、或做国内产线核算时,通用值不够用。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给铝的因子 —— 这个材料的数值分布太宽,记忆值几乎必错。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **原生与再生分别报,不要平均。** 用户问"铝多少"时,如果候选里两条路线都有,并列展示并说明差异来自哪个环节,不要自己挑一条。
4. **系统模型不混用。** 截止法与后果法的结果不可相减,一次对比里只能有一个模型;用户没指定时按截止法并写明。
5. **产地要落实。** 铝是电力密集型,电网结构直接决定电解环节的结果,有产地信息就用对应地域。
6. **先读数据集名称和参考流。** 铝锭、型材、板带、箔材、压铸件在库里是不同条目,单位也可能不同。
7. **受限不是错误**,说明是哪个库受限、原因是什么,不静默替代。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `webUrl` 的,每条结果都一并给出,别等用户追问。
- **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`activityUuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 HiQLCD-AL。** 每次 `search` 都要带 `--sources hiqlcd-al`,`methods` 也查 `hiqlcd-al` —— 用户来装这个技能就是冲着这个库来的,混进别的库的候选只会让他
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

数值读取(`lookup` 的 GWP、`lci`、`lcia`)只认 `login` 的凭据:**API key(`QUERYING_LCA_DATASETS_API_KEY`)读不了数值**,设了就 unset 再用 `login`。注册用户都能读免费库的数值;商业库数值还要账号已由海科开通 Environmental Data CLI 的商业数据访问,且只限账号已有的数据包权益,否则返回 `restricted`。

凭据由 CLI 自己保存 —— **绝不硬编码进为用户生成的文件,不在输出里回显,不从别的客户端借 token**。

## 工具

| 需求 | 命令 |
|---|---|
| 牌号 / 工序 → 候选数据集 | `environmental-data search '<检索词>' --sources 'hiqlcd-al' --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| **过程贡献 / 热点(分阶段)** | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |

铝的减排讨论几乎都会落到电解环节,`lcia --contributions` 是这类问题的主力工具。它按阶段分桶(电 / 热、燃料、材料、运输、直接排放等),不给单元过程明细;要看具体温室气体,用 `lci '<key>' --type output --category air`。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读 —— 铝锭与型材是不同条目 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 引用前先确认 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因,替代要说明细度差异 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 什么时候该问用户

**先查、再对比、最后才问。** 材料名拿到就先检索,把候选和它们的区别一次给出来。

"换再生铝能减多少"这类是**决策支持**:并列展示两条路线的候选与数值,说明差异来自哪个环节,在证据支持时给带条件的推荐 —— 不要先问用户要哪条。

只有当需要敲定一条数据集、且剩余歧义会实质改变结论时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 与铝行业从业者写,用 ISO 14040/14044、GB/T 24040 的标准术语,材料用标准牌号与工序名。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;通用库可替代但要说明细度不同 |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | `methods hiqlcd-al` 查 methodId,看 `methodIdsWithData` |
| 候选全是氧化铝或铝土矿 | 检索词落在上游 | 用成品形态(型材 / 板带 / 压铸件)重新检索 |
| 两条路线数值差数倍 | 正常,原生与再生本就如此 | 分别报并说明,不要取平均 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
