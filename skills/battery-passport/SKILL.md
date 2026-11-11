---
name: battery-passport
description: '为电池护照与电池碳足迹取真实的生命周期清单数据。欧盟新电池法要求动力电池与工业电池申报碳足迹并在数字电池护照中披露材料与供应链信息 —— 本技能负责其中的数据获取:正极与负极材料、电解液、隔膜、集流体、电芯组装与外壳的清单数据集匹配与 GWP 取值,以及回收料成分的处理口径,每一项都可追溯到数据库、版本、系统模型与地域。当任务涉及电池护照、电池碳足迹、新电池法、动力电池碳排、正极材料、锂电材料、电芯碳足迹时使用。触发词:电池护照、battery passport、新电池法、EU Battery Regulation、动力电池、电池碳足迹、正极材料、负极材料、电解液、锂电、磷酸铁锂、三元材料。'
slug: battery-passport
displayName: 电池护照与电池碳足迹数据
version: 1.4.0
summary: 为电池护照与电池碳足迹取清单数据:正负极材料、电解液、隔膜、集流体、电芯组装逐项匹配,每项可追溯到库与口径。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [电池护照, battery-passport, 新电池法, 动力电池, 电池碳足迹, LCA, 碳足迹, 排放因子, 锂电, 正极材料]
---

# 电池护照与电池碳足迹数据

电池的碳足迹几乎全在材料端。正极用磷酸铁锂还是三元、镍钴来自哪里、电解液和隔膜怎么算、集流体铜箔铝箔多厚 —— 这些逐项加起来决定结果,而每一项都得落到真实的清单数据集上,并且在申报时说得清来源。

本技能负责这批取数与溯源。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

电池产业链在中国高度集中,材料与电芯的实际生产多在国内 —— **用欧洲数据代表国内产线会系统性失真**,本土清单(HiQLCD 覆盖中国全工业体系、HiQLCD-AL 铝工业数据库、CALCD 中国汽车生命周期数据库)在这个场景尤其重要。化学品与聚合物类材料另有 CarbonMinds 的工艺级数据。

> **关于锂电池专用数据库**:海科数据与中国电子技术标准化研究院等单位联合打造的**中国锂电池碳足迹数据库**(519 条 LCI,覆盖 180 余种物质,贯穿矿产资源、关键材料、电芯、电池包及回收全链条)已发布,但**暂未开放 API 查询** —— 本技能取不到它的数据。需要这批数据请通过 [hiqlcd.com](https://www.hiqlcd.com/databases) 联系。用本技能取数时用的是上面那几个通用与行业库,如实说明即可,不要暗示数据来自锂电池专库。

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。材料名含糊或 BOM 行是内部叫法时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、worldsteel 等 | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

电池材料的高精度数据多在商业库。受限项如实标注并说明原因,**不要用免费库的值悄悄顶上去**。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 电池材料的因子不能凭记忆 —— 这个领域的数据更新快,记忆里的数基本都过时。
2. **每一项都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。申报要追溯。
3. **产地必须落实到电芯与关键材料的实际产地。** 电池是电力密集型产业链,产地换了结果就换了。
4. **回收料成分的处理口径要说明。** 用户报了再生成分比例时,说明当前数据对应的是什么口径,不要自己替他选一种算法。
5. **单位对齐**:材料用量(kg/电芯、g/Wh)与数据集参考单位不一致时先换算,换算依据要写出来。
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
| 材料 / BOM 行 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 找减排点(分阶段贡献) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

**批量 lookup**:一份电池 BOM 几十项,一次调用传全部 key(最多 200 个)。项数多时先按材料去重。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 逐项记录,申报要写 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 单列复核,不要混进合计 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 该项标注受限并说明原因,不替代 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

- **逐项**:材料 / 部件 → 数据集(名称 + 参考流 + 地域)→ 用量 + 单位 → 因子 → 小计 → 来源(库 + 版本 + 系统模型)
- **按部件分组**:正极、负极、电解液、隔膜、集流体、外壳与结构件、电芯组装、Pack
- **单列**:匹配存疑(`--assist` 的 `fit: low`,或你判定不吻合)、代理数据、受限未取到、用假设换算系数的项
- **合计**:说明边界(到电芯出厂还是到 Pack)与未纳入项

## 语气与术语

面向 LCA 与电池行业从业者写,用 ISO 14040/14044、GB/T 24040 的标准术语,材料用标准名(磷酸铁锂 / LFP、三元 / NMC)。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定合规义务。** 电池法的适用范围、申报门槛、护照字段要求、核验方式由用户的合规顾问确认。本技能负责数据与溯源。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 某材料搜不到 | 描述用了内部牌号或缩写 | 用标准化学名或材料类别重试,或加 `--assist`;仍不行就问用户 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 标注受限并说明原因,不替代 |
| 合计与公开数据差一个数量级 | 多半是单位(kg vs g/Wh)或边界不一致 | 逐项核对参考单位与边界 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
