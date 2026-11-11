---
name: iso14067
description: '按 ISO 14067 口径做产品碳足迹时取真实的清单数据,并把每个数值的来源交代到可核验的程度。ISO 14067 要求产品碳足迹报告说明功能单位、系统边界、数据来源、数据质量与分配方法 —— 本技能负责其中的数据获取部分:检索匹配数据集、取 GWP 与 LCIA 指标、记录库与版本与系统模型与地域,并区分实测、数据库直取与代理数据。当任务涉及 ISO 14067、产品碳足迹报告、CFP、第三方核验、数据质量说明、GB/T 24067 时使用。触发词:ISO 14067、GB/T 24067、产品碳足迹、CFP、carbon footprint of a product、核验、数据质量、功能单位、系统边界。'
slug: iso14067
displayName: 碳足迹核算与数据溯源(ISO 14067)
version: 1.4.0
summary: 按 ISO 14067 口径取产品碳足迹数据:检索匹配、取值、记录库与版本与系统模型与地域,区分实测/直取/代理,供第三方核验。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [ISO 14067, GB/T 24067, 产品碳足迹, CFP, LCA, 碳足迹, 排放因子, 生命周期评价, 数据质量, GWP]
---

# ISO 14067 产品碳足迹取数与数据溯源

按 ISO 14067 出的产品碳足迹报告要经得起第三方核验,而核验主要看两件事:**数据从哪来**,以及**你有没有把它说清楚**。一个没有库名、版本、系统模型和地域的数字,在核验环节等于没有。

本技能负责数据获取与溯源这一段 —— 检索、取值、记录基准、标注数据性质。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD,口径遵循 ISO 14040/14044、ISO 14067 与 GB/T 24040/24067。

**默认检索是按名称的词法检索,约一秒返回,不替你判断需求。** 检索词里写活动 / 产品的标准名,库、系统模型、地域用参数限定;每条候选的参考流、地域、边界由你对照需求判定。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等 | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

受限项如实标注并说明原因,**绝不用其他库的值静默替代** —— 核验时数据来源不一致且未说明,是最常见的退回理由。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 报告里的数不能凭记忆。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。这几项直接对应报告里的数据来源说明。
3. **标注数据性质**:实测 / 数据库直取 / 代理。代理数据要写清用了什么代理什么、哪些差异未修正。
4. **口径一致才能合计。** 系统模型或系统边界不同的数据不能相加,先核对参考单位、系统模型与方法。
5. **功能单位与系统边界由用户确定,不要替他决定。** 但每次给数时都要说明当前数据对应的参考流与单位,便于他对齐。
6. **受限不是错误**,说明是哪个库受限、原因是什么,不替代。

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
| 物料 / 工艺 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 过程贡献 / 热点(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 累计清单(基本流) | `environmental-data lci '<key>' [--type output --category air] --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 逐项记入报告 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 标注受限并说明原因 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

产出要能直接支撑报告的数据来源章节:

- **数据清单**:每项 → 数据集名称 + 参考流 + 地域 + 数据库 + 版本 + 系统模型 + 取得日期
- **数据性质**:实测 / 数据库直取 / 代理,分别标注
- **数据质量**:按参考流、地域、时间、技术与需求的吻合程度逐项说明,依据写清楚,不要自己编一个评分
- **未纳入项**:受限未取到的、无法匹配的,如实列出并说明原因

不要输出一个孤立的总量。核验看的是清单。

## 语气与术语

面向 LCA 与核验从业者写,用 ISO 14067、ISO 14040/14044、GB/T 24067 的标准术语。功能单位 · 参考流 · 系统边界 · 单元过程 · 分配 allocation · 数据质量要求 DQR。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定符合性。** 是否满足 ISO 14067、PCR 如何适用、核验机构认不认,这些由用户的核验方确认。本技能负责数据与溯源。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 某项怎么都搜不到 | 描述里没有可识别的材质或工艺 | 换标准名 / 英文名重试;仍不行就问用户,不要猜一个顶上 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 标注受限并说明原因 |
| 结果与同类 EPD 差一个数量级 | 多半是单位或边界不一致 | 核对参考单位与系统边界 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
