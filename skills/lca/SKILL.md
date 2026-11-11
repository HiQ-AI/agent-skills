---
name: lca
description: '做生命周期评价(LCA)时取真实的清单数据与全套影响评价指标。不只是碳:除 GWP 外还可取酸化(AP)、富营养化(EP)、臭氧消耗(ODP)、水耗(WDP)、资源消耗(ADP)等 LCIA 指标,覆盖 18 个生命周期清单数据库与 24000+ 已发布 EPD。用于完整 LCA 研究、多指标环境评价、生态设计权衡分析、分阶段过程贡献(热点)识别。当任务涉及生命周期评价、LCA 研究、清单分析、影响评价、多指标评价、环境热点、ISO 14040/14044 时使用。触发词:LCA、生命周期评价、生命周期评估、清单分析、LCI、影响评价、LCIA、酸化、富营养化、环境影响、ISO 14040。'
slug: lca
displayName: 生命周期评价(LCA)数据与多指标影响评价
version: 1.4.0
summary: 做 LCA 取清单数据与全套 LCIA 指标:GWP 之外还有酸化、富营养化、臭氧消耗、水耗、资源消耗,以及累计清单与分阶段过程贡献。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [LCA, 生命周期评价, LCI, LCIA, 影响评价, 酸化, 富营养化, 碳足迹, 排放因子, ISO 14040]
---

# LCA 生命周期评价数据与多指标影响评价

碳只是一个影响类别。一份只报 GWP 的 LCA 不是 LCA —— 换材料常常是把碳降下去、把水耗或资源消耗顶上来,不看其他指标就看不见这种转移。

本技能负责 LCA 的数据侧:清单数据获取、多指标影响评价取值、分阶段过程贡献(热点)。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

可访问:

- **18 个生命周期清单数据库**,11 个免费。含中国本土数据(HiQLCD 覆盖中国全工业体系、铝产业链 HiQLCD-AL、汽车行业 CALCD)与国际主流库(Ecoinvent、BAFU、ELCD、EF、worldsteel、USLCI、AusLCI、CarbonMinds、Agri-footprint)。
- **24000+ 已发布 EPD**(EPDItaly、ECO Platform、EPD Norge)。
- 口径遵循 ISO 14040/14044 与 GB/T 24040/24044,系统模型覆盖截止法、后果法、APOS、EN 15804。

**默认检索是按名称的词法检索,约一秒返回,不替你判断需求。** 检索词里写活动 / 产品的标准名,库、系统模型、地域用参数限定;每条候选的参考流、地域、边界由你对照需求判定。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 全部 18 库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI、NEEDS、ozLCI、bioenergiedat、recycledplastics | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

**LCIA 覆盖各库差别很大** —— 有的库指标数以百计,有的只有 GWP,少数只有 LCI 层没有 LCIA 层。做多指标评价前先看目录层给出的指标覆盖,别在只有 GWP 的库上找酸化。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 GWP、LCIA 值。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **方法按库取。** methodId 先用 `methods <库代码>` 查,不要拿一个库的 methodId 去查另一个库 —— 特征化方法跨库不通用。
4. **口径不一致不做对比。** 系统模型、功能单位、系统边界不同的数据不可比,先核对参考单位、系统模型与方法。
5. **多指标结论要并列呈现,不要合成单一分数。** 加权成一个总分需要价值判断,那是用户和委托方的事,不是取数环节该替他做的。
6. **受限不是错误**,说明是哪个库受限、原因是什么,不静默替代。

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

数值读取(`lookup` 的 GWP、`lci`、`lcia`)只认 `login` 的凭据:**API key(`QUERYING_LCA_DATASETS_API_KEY`)读不了数值**,设了就 unset 再用 `login`。注册用户都能读免费库的数值;商业库数值还要账号已由海科开通 Environmental Data CLI 的商业数据访问,且只限账号已有的数据包权益,否则返回 `restricted`。

凭据由 CLI 自己保存 —— **绝不硬编码进为用户生成的文件,不在输出里回显,不从别的客户端借 token**。

## 工具

| 需求 | 命令 |
|---|---|
| 材料 / 工艺 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| **非 GWP 的 LCIA 指标**(AP/EP/ODP/WDP/ADP) | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| **过程贡献 / 热点(分阶段)** | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 累计清单(基本流) | `environmental-data lci '<key>' [--type output --category air] --json` |
| 已发布 EPD 检索 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

单个数据集可用 `--category` / `--indicator` 按影响类别或指标筛选;多个 key 批量时只能加 `--method`。`--contributions` 可以换 methodId —— 找热点时不要只看 GWP,同一个产品在不同指标下的热点环节可能完全不同。它按阶段分桶(电 / 热、燃料、材料、运输、直接排放等),不给单元过程明细。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因,替代要说明 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |
| `methodIdsWithData` | 该数据集有结果的方法 | 选 `--method` 前先看 |

## 输出形态

多指标结果并列成表,一列一个指标,并注明各自的特征化方法来源与所在库。指标之间出现权衡(碳降了、水耗升了)时明确指出来 —— 这正是做多指标评价的意义,不要只挑对结论有利的指标报。

## 什么时候该问用户

**先查、再对比、最后才问。** 有可检索的对象就先检索,在同一轮里给结果。

用户说「不确定该用哪个」是**决策支持信号**:给候选、在同一口径下并列、说明差异来自哪个维度、在证据支持时给带条件的推荐。

只有当需要敲定一个数据集、且剩余歧义会实质改变结果时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 从业者写,用 ISO 14040/14044、ILCD、GB/T 24040 的标准术语。单元过程 unit process · 基本流 elementary flow · 中间流 intermediate flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | 先 `methods <库代码>` 看该库的方法与指标覆盖;没有 LCIA 层的库(如 recycledplastics)只能取 `lci` |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;**绝不静默替换** |
| 几个候选数值跨多个数量级 | 功能单位混杂 | 逐条核对参考单位,换算有依据再比 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
| `429` | 按地址限流 | CLI 会自动退避;不要并发或无界循环 |
