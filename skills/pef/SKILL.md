---
name: pef
description: '按欧盟产品环境足迹(PEF / OEF)口径取清单数据与多指标结果。PEF 要求用 Environmental Footprint 参考包的数据与特征化方法,并报告一整套环境影响类别而不只是碳。本技能负责数据获取:用 EF 参考包及其他清单库检索匹配数据集、取 GWP 与酸化富营养化等 LCIA 指标,并把库、版本、系统模型、地域逐项交代清楚。当任务涉及 PEF、OEF、产品环境足迹、EF 参考包、欧盟环境足迹、PEFCR、多指标环境评价时使用。触发词:PEF、OEF、产品环境足迹、Environmental Footprint、EF 3.1、PEFCR、欧盟环境足迹、多指标评价、LCIA。'
slug: pef
displayName: 产品环境足迹 PEF 数据与多指标评价
version: 1.4.0
summary: 按 PEF/OEF 口径取数:EF 参考包数据集、GWP 与多项 LCIA 指标,库与口径逐项交代。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [PEF, OEF, 产品环境足迹, Environmental Footprint, EF, LCIA, 多指标评价, LCA, 碳足迹, 排放因子]
---

# PEF 欧盟产品环境足迹数据与指标

PEF 和一般的碳足迹不是一回事:它要求一整套环境影响类别一起报,而且对用哪套数据、哪套特征化方法有明确要求。只报一个 GWP 交不了差。

本技能负责 PEF 的数据侧 —— 用 EF 参考包及其他清单库取数,并把多指标结果一并拿全。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

**EF(Environmental Footprint)参考包免费开放**,任一登录账号即可取数值 —— 这是 PEF 语境下的基准数据源。需要更细的工艺级数据时可再看 ecoinvent、CarbonMinds 等商业库,国内生产场景可看本土清单。

**默认检索是按名称的词法检索,约一秒返回,不替你判断需求。** 检索词里写活动 / 产品的标准名,库、系统模型、地域用参数限定;每条候选的参考流、地域、边界由你对照需求判定。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| **EF 参考包数值** | GWP 与聚合统计 | **任一登录账号,无需数据包** |
| 其他免费库 | BAFU、ELCD、USLCI、USDA、worldsteel、AusLCI 等 | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 LCIA 值。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **多指标一起报,不要只挑碳。** PEF 的意义就在于看见指标之间的权衡 —— 碳降了水耗升了这种情况必须指出来。
4. **方法按库取。** methodId 先用 `methods <库代码>` 查,不要拿一个库的 methodId 去查另一个库,特征化方法跨库不通用。
5. **不要把多指标加权成单一分数。** 加权涉及价值判断,由用户和 PEFCR 决定,不是取数环节该替他做的。
6. **口径不一致不做对比。** 先核对参考单位、系统模型与方法。
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
| 物料 / 工艺 → 候选数据集 | `environmental-data search '<检索词>' --sources 'ef' --json` |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| **多项 LCIA 指标** | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 过程贡献 / 热点(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

单个数据集可用 `--category` / `--indicator` 按影响类别筛选;多个 key 批量时只能加 `--method`。

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
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |
| `methodIdsWithData` | 该数据集有结果的方法 | 选 `--method` 前先看 |

## 输出形态

多指标结果排成表:一列一个影响类别,注明各自的特征化方法来源与所在库。指标之间出现权衡时明确写出来,并说明是哪个环节造成的(可用 `lcia --contributions` 看分阶段贡献)。

不要用一个"综合环境得分"代替这张表。

## 语气与术语

面向 LCA 从业者写,用 PEF 方法学、ISO 14040/14044、ILCD 的标准术语。影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor · 参考流 reference flow · 功能单位 functional unit。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定 PEFCR 适用性与符合性。** 用哪份 PEFCR、是否满足要求、由谁验证,由用户和验证方确定。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | `methods ef` 查 methodId;用别的库时用那个库的 methodId,特征化方法跨库不通用 |
| EF 库里找不到某物料 | EF 参考包覆盖有限 | 换其他库检索,并说明这不是 EF 数据 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 用了商业库且无权益:如实说明;EF 部分不受影响 |
| 几个候选数值跨多个数量级 | 功能单位混杂 | 逐条核对参考单位,换算有依据再比 |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
