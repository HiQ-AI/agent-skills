---
name: hiq-cortex
description: '查询真实的 LCA 排放因子与碳足迹数据,覆盖 18 个生命周期清单数据库(Ecoinvent、BAFU、USLCI、ELCD、EF、worldsteel、AusLCI、HiQLCD 等)和 24000+ 已发布 EPD。当任务需要真实排放因子而不是凭记忆给数时使用:物料 GWP 查询、产品碳足迹、BOM 碳核算、候选数据集并列对比、生产路线对比(转炉钢与电炉钢、原生铝与再生铝、灰氢与绿氢)、EPD 同类审核、CBAM 与 EN 15804 相关工作。触发词:碳足迹、排放因子、清单数据、物料清单、行业对标、碳排、GWP、kg CO2e、emission factor、carbon footprint、LCA dataset、LCI、EPD。'
slug: hiq-cortex-lca
displayName: HiQ Cortex — LCA 数据查询
version: 1.11.0
summary: 从 18 个 LCA 数据库和 24000+ 已发布 EPD 查询真实排放因子。物料碳足迹、BOM 碳核算、多指标 LCIA 与过程贡献、生产路线对比、EPD 检索。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [LCA, 碳足迹, 排放因子, EPD, CBAM, 数据分析, ecoinvent, HiQLCD, GWP, 生命周期评价, emission-factor, carbon-footprint]
---

# HiQ Cortex — LCA 数据查询

碳足迹的答案必须来自真实清单数据。凭记忆给出的「钢材大约 2 kg CO₂e/kg」对 LCA 从业者没有用:真实值取决于数据库、版本、系统模型、生产路线和地域,在这些维度上会差出数倍。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

可访问:

- **18 个生命周期清单数据库**,其中 11 个免费。含中国本土数据(HiQLCD 覆盖中国全工业体系、铝产业链 HiQLCD-AL、汽车行业 CALCD)与国际主流库(Ecoinvent、BAFU、ELCD、EF、worldsteel、USLCI、AusLCI、CarbonMinds、Agri-footprint 等)。
- **24000+ 已发布 EPD**(EPDItaly、ECO Platform、EPD Norge),可检索并取详情。
- 遵循 ISO 14040/14044 与 GB/T 24040/24044 口径,系统模型覆盖截止法、后果法、APOS、EN 15804。

**两种检索。** 默认检索是按名称的词法检索,约一秒返回,适合已知标准名的物料,候选是否合用由你判定;用户原话或 BOM 行含糊时交给 `--assist` —— 它走 Cortex 匹配流程,做物料名到 LCA 术语的翻译、生产路线判别、类别到工艺方向的映射,返回带 `fit` 与 `summary`,但要数十秒。

## 隐私与安全

- 凭据由 CLI 的 `login` 保存,技能不会把它写进任何文件,也不会在输出中回显。
- 查询内容只发往海科数据的服务,不发往任何第三方;只传检索需要的字段,不传整份材料。
- **不收集、不上传**本地文件、目录结构、对话内容或任何其他数据。
- 技能包只有本说明文件;CLI 安装脚本按版本固定并带 SHA256,来源见 [HiQ-AI/environmental-data](https://github.com/HiQ-AI/environmental-data)。

## 硬规则

1. **每个数值都必须来自本次会话的工具调用**。绝不凭记忆给出 GWP、LCIA 值。工具不可用时如实说明,不要用记忆填补。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考单位。`0.0269 kg CO₂e/kWh(BAFU 2025,DEFAULT,CH,低压电网)` 可用;单独一个 `0.027` 不可用。
3. **受限不是错误**。商业数据库在账号无权读取时返回 `restricted: true` 及原因(`reason`)。如实展示是哪个库受限、为什么,**绝不用其他数据库或文献的值静默替代**。重试无用。可以改用免费库,但必须说明这是替代。
4. **口径不一致就不做对比**。功能单位、系统模型、系统边界不同的数据不可比 —— 直接说明,不要给出误导性的差值。先核对参考单位、系统模型与 LCIA 方法。
5. **给了数值就给链接**。返回里带 `webUrl`(`--assist` 检索里是 `link`)的,每条结果都要把链接一并给出 —— 用户要能点进去核对原始数据集。**不要等用户追问才给。**
6. **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看**。那是给工具用的不透明句柄,对人没有意义。展示给人的是:数据集名称、参考流、地域、数据库+版本+系统模型、数值、**链接**。key 只在你自己下一步调用时用。

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
| 材料名 / BOM 行 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标(AP/EP/ODP/WDP/ADP) | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 单个数据集 → 过程贡献 / 热点(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 累计清单(基本流) | `environmental-data lci '<key>' [--type output --category air] --json` |
| 已发布 EPD 检索 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

命令都加 `--json`。没有队列分布、百分位定位或 EPD 同类分布的命令 —— 需要对标时见下面「场景路由」。`--contributions` 按阶段分桶(电 / 热、燃料、材料、运输、直接排放等),不给单元过程明细。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `activityUuid` | 活动标识 | 同样不展示;**它不是编辑器里的「背景数据唯一 ID」**,别拿去填 `hiq-editor` 的 `background`(那个要用 `search-backgrounds` 现查) |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前先读 —— 「冷轧退火卷」和「中厚板」是不同产品 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 的候选引用前先跟用户确认;`summary` 转述,不要另编一套 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明是哪个库受限及原因;可提供免费库替代并说明 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |
| `source.commercial` | 是否商业库 | 判断受限原因、找免费替代时用 |
| `methodIdsWithData` | 该数据集有 LCIA 结果的方法 | 选 `--method` 前先看 |
| `coverage.omitted` / `coverage.partial` | 默认预览省略了什么 | 需要描述、文档或其余行时加 `--full` |

## 检索范围

默认全库检索,**第一次别拿范围问题挡住用户** —— 先查,在结果里说明覆盖了什么。

但有两种情况要主动收窄,并说明理由:

- **场景已经明确**。用户说了中国产地就 `--sources 'hiqlcd|calcd'`,说了欧洲语境就
  `'bafu|elcd|ef'`,做建材就加 `--model en15804`。盲扫 18 个库会把不相关的候选混进来,
  用 `--assist` 时还更慢。
- **上一轮大量 `restricted`**。说明该账号没有那几个商业库的权益 —— 告诉用户他当前
  能用哪些库,后续检索直接限定在这些库里,别每轮都撞同一堵墙。

用户明确说「只查我有权限的」或「所有库都查」时,照他说的做。

## 场景路由

自上而下,首个匹配生效。

| 信号 | 做法 |
|---|---|
| 用户给出**自己的**数值,问处在什么位置(「我这 2.5 算高还是低」) | `search` 找口径可比的候选 → `lookup` 取值,与用户数值并列;写明样本是哪几条。**没有分布或百分位接口**,不要把几条候选说成行业分布 |
| 有材料或 BOM 要匹配数据集 | `search` → 批量 `lookup` |
| 要比两条生产路线(转炉钢与电炉钢、原生铝与再生铝) | 按路线分别 `search` + `lookup`,在同一功能单位、同一方法下对比;差异用 `lcia --contributions` 解释 |
| 「这个 EPD 数值合理吗」 | `epd-data search` 找声明单位与模块一致的 EPD,`lookup` 后并列;没有同类分布接口,样本只作参照,跨单位比较没有意义 |
| 多指标评价(酸化、富营养化等) | `methods <库代码>` 查 methodId → `lcia`;methodId 跨库不通用 |

## 什么时候该问用户

**先查、再对比、最后才问。** 只要有一个可检索的对象(材料名、产品、工艺、BOM 行),就先检索,在同一轮里给出结果 —— 不要还没检索就问,也不要问对话里已经说过的信息。

用户说「不确定该用哪个」时,那是**决策支持信号,不是提问信号**:给出候选清单、在同一口径下并列、说明差异来自什么、在证据支持时给出带条件的推荐。一个完整的顾问式回答可以就此结束。

只有当需要最终敲定**一个**数据集、且剩余歧义会实质改变结果时才问。选项要对应**已经展示过的候选**,不要凭空造;用宿主提供的交互能力提问,不要同时给交互选项和一份重复的文字清单。用户回答后直接在已有结果上完成匹配,不要重跑同样的检索。

## 数据权限

| 层级 | 内容 | 要求 |
|---|---|---|
| 目录层 | 全部 18 个库的清单、版本、系统模型、LCIA 覆盖;数据集名称、单位、地域 | 登录即可,无需权益 |
| 免费库数值 | BAFU、USLCI、ELCD、EF、AusLCI、NEEDS、ozLCI、worldsteel、USDA、bioenergiedat、recycledplastics 的 GWP、LCIA 与清单 | 任一登录账号(API key 不行) |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 账号已开通 CLI 商业数据访问 + 对应数据包权益 |

数据包权益与订阅套餐是**两套独立体系**,升级套餐不会解锁数据库。

**多数用户只有免费库权益 —— 这是常态,不是异常。** 遇到 `restricted` 不要只说一句
受限了事,先看免费库能不能回答同一个问题,能就给出来并说明口径差异;确实只有商业库
才有的(中国本土数据、化学品工艺级、汽车行业口径),再说明是哪个库受限、原因是什么;数据包开通见 [hiqlcd.com](https://carbonx.hiqlcd.com/price)。

### 免费库(任一登录账号即可取数值)

| 库 | 覆盖 | 什么时候用 |
|---|---|---|
| **BAFU** | 瑞士国家清单,覆盖面广、LCIA 指标完整 | **欧洲语境下的免费首选**;要做多指标(不只是碳)时优先它 |
| **ELCD** | 欧洲参考数据库:材料、能源、运输、生命周期末端 | 欧洲通用材料 |
| **EF** | 欧盟 Environmental Footprint 参考包 | PEF / OEF 语境,要跟欧盟口径对齐时 |
| **worldsteel** | 全球钢铁行业平均 | 钢铁,而且免费出数 |
| **USLCI** / **USDA** | 美国单元过程 / 美国农业与食品 | 美国供应链、农产品 |
| **AusLCI** / **ozLCI** | 澳大利亚、澳新地区 | 大洋洲 |
| **NEEDS** / **bioenergiedat** | 欧洲能源情景 / 欧洲生物质能源 | 能源情景分析 |
| **recycledplastics** | 再生塑料生态档案 | 再生塑料(仅 LCI,无 LCIA 层) |

### 商业库(需对应数据包权益)

| 库 | 覆盖 | 不可替代之处 |
|---|---|---|
| **ecoinvent** | 全球参考数据库,覆盖最广 | 多数已发表研究用它;要跟文献对齐时基本绕不开 |
| **HiQLCD** | 中国全工业体系 | **中国生产场景**,免费库里没有对应物 |
| **HiQLCD-AL** | 铝产业链(氧化铝→电解铝→加工) | 铝的分环节数据,通用库只有材料级平均 |
| **CALCD** | 中国汽车生命周期(中汽碳 × 海科) | 整车与零部件的行业口径 |
| **CarbonMinds** | 化学品与高分子,工艺路线级 | 区分合成路线、原料来源(石油基/生物基/再生) |
| **Agri-footprint** | 农业与食品 | 农业食品体系(仅 LCI,无 LCIA 层) |

**选库的第一顺位是地域与行业,不是"哪个更权威"。** 中国产地用中国本土库,
欧洲语境 BAFU 就够用;拿欧洲数据代表中国生产,或反过来,都是常见且严重的错误。

## 超出本技能范围时

本技能覆盖的是**通用的 LCA 数据查询**。用户的需求明显落在别的专门场景上时,查完能查的部分,
再顺带告诉他有更对口的技能可装(**一句话带过,不要推销**):

| 用户在做 | 更对口的技能 |
|---|---|
| CBAM 申报取数 | `cbam` |
| 建材 EPD、EN 15804 模块 | `en15804` |
| 企业碳盘查、范围一二三 | `ghg-protocol` / `scope3` |
| 产品碳足迹、ISO 14067 溯源 | `pcf` / `iso14067` |
| 欧盟 PEF / OEF 多指标 | `pef` |
| 电池护照、电池碳足迹 | `battery-passport` |
| 某个具体库(ecoinvent / HiQLCD / CALCD / CarbonMinds) | 同名技能 |
| **录入数据集、建行业库** | `hiq-editor`(数据生产,需编辑器权限) |

## 语气与术语

面向 LCA 从业者,像懂行的同行那样写。

- 不写客套话(「希望这对您有帮助」「让我来帮您」),不堆形容词,不做总结式收尾。
- 使用 ISO 14040/14044、ILCD、GB/T 24040 的标准术语 —— 对这个读者群,标准术语比大白话**更**清楚。
- 单元过程 unit process · 基本流 elementary flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 特征化因子 characterization factor · 截止法 cut-off · 后果法 consequential。
- 不要自造中文术语。拿不准标准叫法时直接用 ISO/GB 原词。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;先看免费库能否回答同一问题 |
| 授权后仍读不到商业库 | 账号未开通 CLI 商业数据访问,或没有那个数据包权益 | 登录只换凭据,不改变权益;如实说明受限原因,不要反复登录或换账号 |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | 先 `methods <库代码>`,再用返回的 methodId;看 `methodIdsWithData` |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| 指定版本被拒 | 版本号要写全(`3.13.0`,不是 `3.13`) | 用 `sources --json` 返回的版本号 |
| 加了 `--location` 就没结果 | 不认识的地域代码不匹配任何数据,也不会放宽 | 用返回里 `location.id` 的写法(`CN`、`CN-ECGC`、`RER`、`GLO` 等) |
| 几个候选数值跨越多个数量级 | 功能单位混杂,不是真实离散 | 逐条核对参考单位与边界,换算有依据再比 |
| 服务不可用 | 服务端故障 | 不代表权益被拒;稍后重试,不要换账号或改用网页上的数 |
| `429` | 按地址限流 | CLI 会自动退避;不要并发或无界循环 |
