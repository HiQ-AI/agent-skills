---
name: pcf
description: '做产品碳足迹(PCF)核算时取真实的清单数据。从 BOM 物料清单出发,逐行匹配生命周期清单数据集、取 GWP、合计到产品层,并把每一项的数据库、版本、系统模型、地域、参考流交代清楚。覆盖 18 个 LCI 数据库与 24000+ 已发布 EPD。当任务涉及产品碳足迹、PCF 核算、ISO 14067、BOM 碳排、物料清单碳核算、单位产品碳排放、生态设计选材对比时使用。触发词:PCF、产品碳足迹、ISO 14067、BOM、物料清单、碳核算、单位产品碳排、carbon footprint of products、cradle-to-gate。'
slug: pcf
displayName: 产品碳足迹(PCF)核算取数
version: 1.3.0
summary: 从 BOM 出发做产品碳足迹核算:逐行匹配清单数据集、取 GWP、合计到产品层,每一项都可追溯到库、版本、系统模型与地域。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [PCF, 产品碳足迹, ISO 14067, BOM, 物料清单, 碳核算, LCA, 排放因子, 生命周期评价, GWP]
---

# 产品碳足迹(PCF)核算取数

产品碳足迹的工作量不在加法,在**逐行匹配**:BOM 上写的是「钻头」「废外壳(钢壳,软包)」「框架蒸压加气混凝土砌块外墙 200厚」,清单数据库里只有工艺过程。这一步匹配错了,后面的合计再精确也没有意义。

本技能负责把 BOM 行接到真实数据集上,并保证每一项都可追溯。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD,口径遵循 ISO 14040/14044、ISO 14067 与 GB/T 24040/24044。

**BOM 行含糊时交给 `--assist` 匹配。** 默认检索是按名称的词法检索,约一秒返回,适合已经知道标准名的行;BOM 上的原始描述(工厂俗称、制成品、括号里的补充说明)**原样**交给 `--assist` —— 它走 Cortex 匹配流程,做俗称到标准名的翻译、制成品到材质的还原、物料类别到工艺方向(生产 / 处理)的映射,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

不要在本地先把 BOM 名称「翻译」一遍再去搜 —— 那会丢掉原始信息,反而降低命中率。原话交给它。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等的 GWP 与 LCIA | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

一份 BOM 里通常几种情况混着:部分物料免费库就能覆盖,部分要商业库。**受限项如实标注,不要用免费库的值悄悄顶上去** —— 一份混了口径又没标注的 BOM 核算表,后面没人能复核。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 一行都不能凭记忆填。
2. **每一行都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。BOM 核算表要能逐行追溯。
3. **合计前先确认口径一致。** 系统模型不同的数据不能相加;功能单位不一致要先换算,换算依据要写出来。
4. **单位要对齐。** 数据集的参考单位(kg / m³ / kWh / tkm)与 BOM 的用量单位不一致时,先做单位换算并说明换算系数来源。密度、堆积密度这类换算参数如果是假设值,必须标注为假设。
5. **代理数据单独标注**,不要混进直取行。
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
| BOM 行 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 找减排点(分阶段贡献) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

**批量 lookup**:BOM 有几十行时,一次调用传入全部 key(最多 200 个),不要逐行调。BOM 原话含糊时用 `--assist`,它较慢 —— 行数多时提前告诉用户,不要并发轰接口。

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
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 的行单独列出来让用户确认,不要混进合计 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 该行标注受限并说明原因 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

产品碳足迹的输出是一张可复核的表,不是一个数:

- **逐行**:物料名 → 匹配到的数据集(名称 + 参考流 + 地域)→ 单位用量 → 因子 → 小计 → 数据来源(库 + 版本 + 系统模型)
- **分组小计**:原材料 / 能源 / 运输 / 废弃物,便于看结构
- **单列出来**:匹配存疑的行(`--assist` 的 `fit: low`,或你判定不吻合)、代理数据行、受限未取到值的行
- **合计**:并说明边界(cradle-to-gate 还是 cradle-to-grave)、口径、以及哪些项未纳入

用户只要一个数时也要给基准和边界 —— 一个没有边界说明的产品碳足迹数字不能用。

## 什么时候该问用户

**先查、再对比、最后才问。** BOM 拿到手先跑检索,在同一轮里给出匹配结果和明确的疑问项,不要逐行追问。

必须问的通常只有三类:产地(影响电网与工艺)、材质歧义(BOM 写「塑料件」但没说是 PP 还是 ABS)、边界(算到出厂还是算到报废)。这三类可以一次性问齐,不要挤牙膏。

## 语气与术语

面向 LCA 从业者写,用 ISO 14040/14044、ISO 14067、GB/T 24040 的标准术语。功能单位 · 参考流 · 系统边界 · 单元过程 · 分配 allocation · 截止规则 cut-off criteria。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| BOM 某行怎么都搜不到 | 描述里没有可识别的材质信息 | 加 `--assist` 再试;仍不行就把原话给用户,问材质,不要自己猜一个材料顶上 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 该行标注受限并说明原因 |
| 合计结果比同行高一个数量级 | 多半是单位错配 | 逐行核对参考单位与用量单位 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
