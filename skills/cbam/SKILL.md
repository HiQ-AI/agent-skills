---
name: cbam
description: '为 CBAM(欧盟碳边境调节机制)申报取真实的生命周期清单数据。CBAM 覆盖钢铁、铝、水泥、化肥、电力、氢六个品类,申报要求逐项交代内含排放的数据来源与口径,不能凭经验值填报。本技能负责按品类检索对应的清单数据集、取 GWP 与基准,并把数据库、版本、系统模型、地域、参考流一并交代清楚,供申报文件追溯。当任务涉及 CBAM 申报、碳边境、碳关税、内含排放数据准备、出口欧盟的产品碳数据、钢铁铝水泥化肥电力氢的排放因子时使用。触发词:CBAM、碳边境调节机制、碳关税、内含排放、embedded emissions、出口欧盟、申报、钢铁、铝、水泥、化肥、氢。'
slug: cbam
displayName: 碳边境调节机制 CBAM 申报数据准备
version: 1.4.0
summary: 为 CBAM 申报取真实清单数据:按品类检索数据集、取 GWP 与基准,每个数值都可追溯到库、版本、系统模型与地域。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CBAM, 碳关税, 碳边境, 内含排放, LCA, 碳足迹, 排放因子, 钢铁, 铝, 生命周期评价]
---

# CBAM 碳边境调节机制数据准备

CBAM 申报的核心不是算得快,是**每个数字都得说得清来源**。申报文件要经得起追溯:这个值来自哪个数据库、哪个版本、什么系统模型、什么地域、参考流是什么。凭经验值或文献均值填报,在核查环节站不住。

本技能负责把取数这一步做扎实 —— 检索、取值、交代基准。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

对 CBAM 的六个品类,数据可及性差别很大:

| 品类 | 可用来源 |
|---|---|
| 钢铁 | worldsteel(免费)、中国本土清单、ecoinvent |
| 铝 | HiQLCD-AL 铝产业链专库、ecoinvent |
| 水泥 | 各国清单库 + 已发布 EPD |
| 化肥 | Agri-footprint、各国清单库 |
| 电力 | 按地域取,免费库覆盖较好 |
| 氢 | 按制取路线区分,清单库 + EPD |

**默认检索是按名称的词法检索,候选是否合用由你判定。** 检索词里写标准名(中英文都写更好),库、地域用参数限定。产品描述或 BOM 行含糊时,原样交给 `--assist` —— 它走 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 匹配证据与 `summary` 说明,但要数十秒。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 免费库数值 | worldsteel、BAFU、ELCD、EF、USLCI、USDA 等的 GWP 与 LCIA | 任一登录账号 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

**钢铁与电力用免费库就能拿到数值**;铝、化肥、水泥的高精度数据多在商业库。无权益时返回 `restricted: true` 及原因,如实告诉用户是哪个库受限。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 申报数据不能凭记忆 —— 记忆里的数没有来源、年份和口径,填进申报文件就是风险。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。申报要追溯,这不是可选项。
3. **产地必须落实。** CBAM 关心的是实际生产地的排放,不是全球平均。产地明确时不要用 GLO 或欧洲平均顶替;只能用代理时明确声明代理关系与未修正的差异。
4. **口径不一致不做对比,也不做合计。** 系统模型或系统边界不同的数据不能相加,先核对参考单位、系统模型与方法。
5. **受限不是错误。** 无权益时如实展示受限的库与原因,**绝不用其他库或文献的值静默替代** —— 那会让整份申报的可追溯性归零。

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
| 产品 / 物料 → 候选数据集 | `environmental-data search '<检索词>' [--sources '<库代码>'] --json` |
| 原话含糊,要服务端理解需求再匹配 | 同上加 `--assist`(数十秒) |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 找减排点(分阶段贡献) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 同类已发布 EPD 参照 | `epd-data search '<品类描述>' --json` → `epd-data lookup '<epd_key>' --json` |

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。`--assist` 把原话交给 Cortex 匹配流程,解释条件并校验候选,返回带 `fit` 与 `summary`,但要数十秒,且不能与 `--location` / `--limit` / `--cursor` / `--collapse` 同用。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读,申报文件里要写 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `fit` / `summary`(仅 `--assist`) | 服务端的匹配证据与说明 | `low` 不要直接填进申报,先确认 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明受限及原因,不静默替代 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 输出形态

CBAM 场景的输出通常要进申报表格或说明文件,所以:

- **逐项列出**,一行一个物料 / 工序,每行带数值 + 单位 + 数据库 + 版本 + 系统模型 + 地域 + 参考流。
- **代理数据单独标注**,不要混在实测或数据库直取的行里。
- **受限项如实留空并注明原因**,不要用估值填坑。
- 用户要合计时,先确认各项口径一致再合计;不一致就说明并拒绝直接相加。

## 语气与术语

面向 LCA 与合规从业者写,用 ISO 14040/14044、GB/T 24040 的标准术语。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要对法规义务下判断。** 本技能负责取数与口径,申报义务、缺省值适用条件、核查要求这些应由用户的合规顾问确认 —— 需要时明确说明这一点,不要替用户拍板。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;可用免费库替代但要说明 |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | 先 `methods <库代码>`,再用返回的 methodId;看 `methodIdsWithData` |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| 指定版本被拒 | 版本号要写全(`3.13.0`,不是 `3.13`) | 用 `sources --json` 返回的版本号 |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
