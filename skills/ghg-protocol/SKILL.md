---
name: ghg-protocol
description: '为企业温室气体核算(GHG Protocol / ISO 14064)取真实的排放因子。范围一的燃料燃烧、范围二的外购电力与热力、范围三的上游物料与服务,逐项匹配生命周期清单数据集并取 GWP,覆盖 18 个 LCI 数据库。每一项都可追溯到数据库、版本、系统模型、地域与参考流,供 CDP、ISSB、SBTi 与年度报告核查。当任务涉及企业碳盘查、温室气体核算、范围一二三、组织碳排、GHG Protocol、ISO 14064、双碳报告取数时使用。触发词:GHG Protocol、温室气体核算、企业碳盘查、组织碳排、范围一、范围二、范围三、ISO 14064、CDP、SBTi、碳中和报告、排放因子。'
slug: ghg-protocol
displayName: 温室气体核算 GHG Protocol 企业碳盘查取数
version: 1.4.0
summary: 为企业碳盘查取排放因子:范围一燃料、范围二电力热力、范围三上游,逐项可追溯到库与口径,供 CDP/ISSB/SBTi 核查。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [GHG Protocol, 温室气体核算, 企业碳盘查, 范围一, 范围二, 范围三, ISO 14064, LCA, 排放因子, 碳足迹]
---

# GHG Protocol 企业温室气体核算取数

企业碳盘查最后都会卡在同一件事上:**因子从哪来**。用一份来路不明的因子表填完整张清单,报送时经不起追问;逐项去翻数据库,量又太大。

本技能负责因子获取与溯源 —— 范围一、二、三的每一项都落到真实的清单数据集上。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

三个范围的数据可及性不同:

| 范围 | 典型对象 | 数据来源 |
|---|---|---|
| 范围一 | 自有设施的燃料燃烧、工艺排放、逸散 | 免费库覆盖较好(USLCI、ELCD、BAFU) |
| 范围二 | 外购电力、蒸汽、供热供冷 | 按地域取;国内产地优先本土清单 |
| 范围三 | 上游物料与服务、运输、废弃物、差旅 | 跨库,物料类多在商业库 |

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。台账上的原始描述含糊时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等 | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

**范围一与范围二用免费库通常够用**;范围三的物料项精度取决于是否有商业库权益。受限项如实标注,不要用免费库的值悄悄顶上去。

## 硬规则

1. **每个因子都来自本次会话的工具调用。** 不凭记忆填因子表。
2. **每一项都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。报送要逐项追溯。
3. **范围二必须按地域取电力因子。** 电网碳强度地区差异巨大,用全国平均或全球平均代替已知产地是可辨识的错误。有具体厂址就用对应地域。
4. **口径一致才能合计。** 系统模型或边界不同的数据不能相加,先核对参考单位、系统模型与方法。
5. **单位对齐。** 台账单位(度、吨、立方米、公里)与数据集参考单位不一致时先换算,换算依据要写出来。
6. **区分数据性质**:实测 / 数据库直取 / 代理,分别标注。
7. **受限不是错误**,说明是哪个库受限、原因是什么,不静默替代。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `webUrl` 的,每条结果都一并给出,别等用户追问。
- **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`activityUuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

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
| 台账项 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

**批量 lookup**:一次传入全部 key(最多 200 个)。台账项多时先按类别去重(同一种燃料出现在十个厂区只需查一次),再回填。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 逐项记录 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | 直接对应数据质量说明,`low` 必须标注 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 该项标注受限并说明原因 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

产出是一张要交给核查方的因子清单:

- **按范围分组**:范围一 / 范围二 / 范围三,范围三再按类别
- **逐行**:活动项 → 数据集(名称 + 参考流 + 地域)→ 活动量 + 单位 → 因子 → 排放量 → 来源(库 + 版本 + 系统模型)
- **单列**:匹配存疑(`--assist` 的 `fit: low`,或你判定不吻合)、代理数据、受限未取到、用假设换算系数的行
- **数据质量说明**:哪些直取、哪些代理、哪些估算

不要只给总量。核查看的是每一行怎么来的。

## 语气与术语

面向企业碳管理与核查从业者写,用 GHG Protocol、ISO 14064、ISO 14040/14044 的标准术语。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定核算边界与报送义务。** 组织边界(股权法 / 控制权法)、范围三类别取舍、报送口径由用户的核查机构或碳管理负责人确定。本技能负责因子与溯源。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 某活动项搜不到 | 台账描述太笼统(如「辅料」) | 问用户要具体物料,不要自己猜 |
| 范围二找不到对应地域电力 | 该地域数据集缺失 | 用可得的最接近地域并**明确声明代理**,说明未修正的差异 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 标注受限并说明原因 |
| 总量比去年差很多 | 先查因子版本或地域是否换了 | 对比两次取数的基准再下结论 |
| 加了 `--location` 就没结果 | 不认识的地域代码不匹配任何数据,也不会放宽 | 用返回里 `location.id` 的写法(`CN`、`CN-ECGC`、`RER`、`GLO` 等) |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
