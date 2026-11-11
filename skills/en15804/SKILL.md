---
name: en15804
description: '按 EN 15804 口径处理建材的环境产品声明(EPD)与清单数据。检索 24000+ 已发布 EPD(EPDItaly、ECO Platform、EPD Norge),按声明单位与模块取指标、并列对比;并可取 EN 15804 系统模型下的生命周期清单数据集。用于建材 EPD 编制与第三方审核、建筑 LCA 取数、绿色建筑评价、同类产品对标。当任务涉及 EN 15804、建材 EPD、A1-A3 等模块、声明单位、EPD 审核、建筑材料碳足迹时使用。触发词:EN 15804、EPD、环境产品声明、建材、A1-A3、模块、declared unit、声明单位、EPDItaly、ECO Platform、建筑碳排。'
slug: en15804
displayName: 建材 EPD 与 EN 15804 模块化指标
version: 1.4.0
summary: 按 EN 15804 口径检索已发布 EPD 与清单数据:按声明单位和模块取指标、并列对比,用于 EPD 编制、审核与建筑 LCA。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [EN 15804, EPD, 环境产品声明, 建材, 建筑碳排, LCA, 碳足迹, 生命周期评价, A1-A3, 排放因子]
---

# EN 15804 建材 EPD 与模块化指标

建材的环境数据是**按模块组织**的:A1-A3、A4-A5、B、C、D 各自代表不同的生命周期阶段,声明单位可能是 m³、m²、kg 或一个功能单元。拿 A1-A3 的值跟别人的 A1-C4 比、拿 m³ 的数值判断 kg 的数值,得到的结论没有意义。

本技能负责在正确的模块和声明单位下取数与对标。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

本技能可访问:

- **24000+ 已发布 EPD**,来自 EPDItaly、ECO Platform、EPD Norge。按品类、声明单位、地域描述检索,取详情后在同一声明单位与模块下并列对比。
- **EN 15804 系统模型下的清单数据集**,来自 ecoinvent、HiQLCD 等库(数值需对应数据包权益)。

**检索不替你判断口径。** 声明单位、模块、有效期要按返回字段逐条核对,不能因为检索命中就当作合用。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| **已发布 EPD 检索** | 24000+ 条 EPD 的检索摘要 | **公开,无需登录** |
| **EPD 详情** | 注册号、声明单位、有效期、模块与指标值 | **登录即可,无需数据包** |
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位 | 登录即可 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

EPD 部分是完整可用的 —— 编制、审核、对标这些工作不需要额外权益。

## 硬规则

1. **声明单位必须一致。** 对比几份 EPD 前先确认声明单位相同;把 m³、m²、kg 混在一起比没有意义。
2. **模块必须对齐。** 只在同一模块组合之间比较。引用别人的 EPD 数值时先确认对方报的是哪几个模块。
3. **D 模块不并入合计。** 边界外的收益与负担单列,把它加进 A-C 总量是建材 LCA 里最常见的错误之一。
4. **每个数值都要交代来源**:EPD 注册号 + 声明单位 + 模块 + 有效期,或数据集的库 + 版本 + 系统模型 + 地域。
5. **几份 EPD 的对比只是这几份的对比。** 写明样本是哪几份、剔除了哪些;不要把检索到的样本说成品类或行业分布。
6. **每个数值都来自本次会话的工具调用**,不凭记忆给 EPD 值。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带链接(清单数据集为 `webUrl`)的,每条结果都一并给出,别等用户追问。
- **不要把 `epd_key` / `datasetRef` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
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
| 找某品类的已发布 EPD | `epd-data search '<品类、声明单位、地域、模块要求>' [--publishers 'eco,epditaly,epdnorge'] [--limit 20] --json` |
| EPD 详情(声明单位、模块、有效期、指标) | `epd-data lookup '<epd_key1,epd_key2>' --json`(需登录) |
| 建材原料 → 清单数据集 | `environmental-data search '<检索词>' --model en15804 --json` |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json` |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |

EPD 检索没有声明单位、地域、模块的过滤参数 —— 这些要求写进检索原话,再逐条按返回字段核对。`--publishers` 只接受 `eco`、`epditaly`、`epdnorge`(逗号分隔);翻页用返回的 `--cursor` 原样续查,其余参数不变。EPD 不接受 `--sources` / `--model`。

**没有同类分布或离群判定的命令。** 要对标,只能把检索到、且声明单位与模块一致的几份 EPD 并列给出,写明样本是哪几份、剔除了哪些、为什么 —— 这是几份 EPD 的对比,不是品类分布,不要算四分位、fences 或百分位冒充行业统计。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `epd_key` | EPD 句柄 | `epd-data lookup` 时原样传,**不展示给用户** |
| `source.pt_source` | 发布平台(eco / epditaly / epdnorge) | 引用时写明 |
| 注册号、产品、声明单位、有效期、模块 / 方法、链接 | 按返回里实际有的字段读;检索摘要不一定都带,缺了就 `lookup` | 注册号是可追溯的锚点;声明单位不一致不比;过期 EPD 不能作为现行依据,要提示用户 |
| 指标值 | 按模块报的结果 | 只引用返回里实际有的数,连同模块与声明单位 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不能据此说该 EPD 不存在 |
| `datasetRef` / `headlineGwp` / `restricted` + `reason` / `webUrl` | 清单数据集侧的句柄、GWP100、受限状态、详情页 | 同其他查询技能:受限如实说明,链接每条都给 |

EPD 摘要不等于完整声明的审核;要下结论先 `lookup` 看详情。

## 审 EPD 时的输出形态

- 先给**被审值 + 声明单位 + 模块 + 注册号**,把口径钉死。
- 再并列给出**声明单位与模块一致的已发布 EPD**,说明这几份是怎么选的、剔除了被审对象和哪些口径不符的;样本少就明说只作量级参考。
- 数值差异大时,先排除「口径不同导致看起来偏离」(声明单位、模块、PCR、地域),再讨论数值本身 —— 前者更常见。不给四分位、fences 或百分位。
- 结论要可复核:任何一句判断后面都跟着它依据的数与来源。

## 语气与术语

面向建材 LCA 与 EPD 从业者写,用 EN 15804、ISO 14025、ISO 14040/14044 的标准术语。声明单位 declared unit · 功能单位 functional unit · 模块 module · 产品阶段 A1-A3 · 边界外收益与负担 module D。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定合规性。** 本技能负责取数与并列对比,PCR 适用范围、验证要求、注册流程这些由用户的验证机构确认。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 几份 EPD 数值差多个数量级 | 声明单位或模块不一致 | 按声明单位与模块分组后再比 |
| 声明单位与模块一致的 EPD 很少 | 该品类已发布 EPD 少 | 如实说明只能作量级参考,不要强行下结论 |
| 找不到某品类 EPD | 品类词太窄或太宽 | 换品类词(中英文)重试,或改用清单数据集路径 |
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;EPD 部分不受影响 |
| `epd-data` 报 `--sources` / `--model` 不支持 | EPD 只认 `--publishers` / `--limit` / `--cursor` | 去掉这两个参数 |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `epd-data login --json` 或 `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 仍读不到数值 | API key 读不了数值 | unset 后改用 `login` |
