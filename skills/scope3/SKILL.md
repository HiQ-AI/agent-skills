---
name: scope3
description: '为企业范围三(Scope 3)温室气体核算取真实的排放因子。采购清单、供应商物料表、外购能源与运输量,逐行匹配生命周期清单数据集并取 GWP,覆盖 18 个 LCI 数据库与 24000+ 已发布 EPD。每一行都可追溯到数据库、版本、系统模型、地域与参考流,供 CDP、ISSB、SBTi 与年度报告核查。当任务涉及范围三、Scope 3、供应链碳排、采购商品与服务、外购品排放、上游排放、企业碳盘查取数时使用。触发词:Scope 3、范围三、供应链碳排放、采购商品与服务、上游排放、企业碳盘查、GHG Protocol、CDP、排放因子。'
slug: scope3
displayName: 范围三 Scope 3 供应链排放因子取数
version: 1.4.0
summary: 为企业范围三核算取真实排放因子:采购清单逐行匹配清单数据集、取 GWP、可追溯到库与口径,供 CDP/ISSB/SBTi 报送。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [Scope3, 范围三, 供应链碳排, 企业碳盘查, GHG Protocol, LCA, 排放因子, 碳足迹, CDP, emission-factor]
---

# Scope 3 范围三供应链排放因子取数

范围三的难点是量:一张采购清单几百上千行,每一行都要落到一个真实的排放因子上,而且报送时每一行都得说得清来源。用行业均值一把梭,核查环节过不去;逐行手查,人力上做不完。

本技能负责把这批取数做完并保持可追溯。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

**物料行含糊时交给 `--assist` 匹配。** 默认检索是按名称的词法检索,约一秒返回,适合已经知道标准名的行;采购清单上的原始描述**原样**交给 `--assist` —— 它走 Cortex 匹配流程,做供应商叫法到标准名的翻译、制成品到材质的还原、物料类别到工艺方向的映射,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。不要在本地先"整理"一遍名称再去搜,那会丢掉原始信息。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等的 GWP 与 LCIA | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

一张采购清单通常横跨多个库。**受限行如实标注,不要用免费库的值悄悄顶上去** —— 混了口径又没标注的清单,核查时会被整批质疑。

## 硬规则

1. **每个因子都来自本次会话的工具调用。** 一行都不能凭记忆填。
2. **每一行都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。报送要逐行追溯。
3. **产地会实质改变结果。** 供应商所在地已知时就用对应地域的数据集,不要一律用全球平均。只能用代理时明确标注代理关系。
4. **单位要对齐。** 采购量单位(件、套、米、吨)与数据集参考单位(kg、m³、kWh、tkm)不一致时先换算,换算系数的来源要写出来;是假设值就标为假设。
5. **口径不一致不合计。** 系统模型不同的数据不能相加,先核对参考单位、系统模型与方法。
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

`lookup`(含 GWP100)可以用 API key(`QUERYING_LCA_DATASETS_API_KEY`),数值按该 key 自己的权益与调用额度返回;**`lci`、`lcia`、`methods` 不接受 API key,只认 `login` 的凭据**。注册用户都能读免费库的数值;商业库数值还要账号已由海科开通 Environmental Data CLI 的商业数据访问,且只限账号已有的数据包权益,否则返回 `restricted`。

凭据由 CLI 自己保存 —— **绝不硬编码进为用户生成的文件,不在输出里回显,不从别的客户端借 token**。

## 工具

| 需求 | 命令 |
|---|---|
| 采购行 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

**批量 lookup**:几百行时按批传 key(每批最多 200 个),不要逐行调。`--assist` 每次要数十秒 —— 行数多时先告诉用户预计耗时,不要并发轰接口。

行数极多时的务实做法:先按物料类别去重(同一种钢材出现 50 次只需查一次),再把因子回填到每一行。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 逐行记录,报送时要写 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 的行单列出来复核,不要混进合计 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 该行标注受限并说明原因 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

范围三的产出是一张要交给核查方的表:

- **逐行**:采购项 → 匹配到的数据集(名称 + 参考流 + 地域)→ 用量 + 单位 → 因子 → 小计 → 数据来源(库 + 版本 + 系统模型)
- **按类别汇总**:采购商品与服务、上游运输、外购能源、废弃物处理等分开
- **单列**:匹配存疑的行(`--assist` 的 `fit: low`,或你判定不吻合)、代理数据行、受限未取到值的行、用假设换算系数的行
- **数据质量说明**:哪些行来自数据库直取、哪些来自代理、哪些是估算

不要只给一个总数。核查方要看的是每一行怎么来的。

## 语气与术语

面向企业碳管理与 LCA 从业者写,用 GHG Protocol 与 ISO 14064/14040 的标准术语。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定报送义务。** 本技能负责取数与追溯,范围边界划定、类别取舍、报送口径由用户的核查机构或碳管理负责人确认。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 某行怎么都搜不到 | 描述里没有可识别的材质或工艺信息 | 加 `--assist` 再试;仍不行就把原话给用户问清楚,不要自己猜一个顶上 |
| 行数太多耗时长 | `--assist` 每行数十秒 | 先按类别去重再查,能用默认检索的行用默认检索;告知预计耗时 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 该行标注受限并说明原因 |
| 合计比同行高一个数量级 | 多半是单位错配 | 逐行核对参考单位与用量单位 |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
