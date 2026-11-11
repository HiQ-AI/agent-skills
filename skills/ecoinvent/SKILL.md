---
name: ecoinvent
description: '在 ecoinvent 中检索并读取真实的生命周期清单数据。ecoinvent 是全球覆盖最广的 LCI 数据库,同一材料在不同系统模型(cut-off、APOS、consequential、EN 15804)、不同地域、不同参考流下结果可差数倍,本技能负责把检索、口径核对与基准交代做对。当任务涉及 ecoinvent 数据集查询、系统模型选择、活动名称与参考流核对、地域代理、GWP 与 LCIA 指标取数时使用。触发词:ecoinvent、cut-off、截止法、APOS、consequential、后果法、系统模型、system model、LCI 数据集、生命周期清单、排放因子、GWP、kg CO2e。'
slug: ecoinvent
displayName: ecoinvent 数据集查询与系统模型核对
version: 1.3.0
summary: 在 ecoinvent 中检索数据集并读懂口径:系统模型、地域、参考流、版本一并交代,并可取 LCIA 结果、累计清单与过程贡献。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [ecoinvent, LCA, 系统模型, cut-off, APOS, consequential, 排放因子, 生命周期评价, LCI, GWP]
---

# ecoinvent 数据集查询与系统模型核对

在 ecoinvent 里查一个材料,难点不是「找不到」,而是**找到十几条都叫这个名字的数据集** —— 不同生产路线、不同地域、不同系统模型、不同参考流。选错口径不会报错,只会安静地给出一个看起来合理的数。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 ecoinvent 在内的 18 个国际主流数据源与 24000+ 已发布 EPD。

**默认检索是按名称的词法检索,约一秒返回,不替你判断需求。** 检索词里写活动 / 产品的标准名,库、系统模型、地域用参数限定;每条候选的参考流、地域、边界由你对照需求判定。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | ecoinvent 的版本、可用系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 登录即可 |
| 数值层 | GWP、LCIA 值 | **需 ecoinvent 数据包权益** |

**「库里有没有、叫什么、什么口径、该选哪条」免费;「数值是多少」需要权益。**

无权益时 `lookup` / `lcia` 返回 `restricted: true` 及原因(`reason`)。这时如实说明是 ecoinvent 受限及原因;若免费库(BAFU、ELCD、EF、worldsteel、USLCI)能回答同一问题,主动提供这条替代路径并**明确说明这是替代、口径不同**。重试无用 —— 受限是授权状态,不是故障。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 ecoinvent 的值 —— 记忆里的数不知道是哪个版本、哪个系统模型、哪个地域的,等于没有。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。`2.31 kg CO₂e/kg(ecoinvent 3.x,cut-off,RER,steel, low-alloyed, hot rolled)` 可用;单独一个 `2.31` 不可用。版本号以 `lookup` 返回为准,不要凭印象写。
3. **系统模型不同的数据不放进同一次对比。** cut-off、APOS、consequential、EN 15804 回答的是不同问题,相减得到的差值没有物理意义。用户没指定时按 cut-off 走,并在回答里写明。
4. **先读活动名称和参考流再用。** 名称相近不等于合用 —— 参考流、地域、边界对不上的候选,引用前跟用户确认。
5. **地域用代理时必须声明。** 写清用了什么代理什么、哪些差异未修正,不要让代理悄悄变成事实。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `webUrl` 的,每条结果都一并给出,别等用户追问。
- **不要把 `datasetRef` / `epd_key` / `activityUuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`activityUuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 ecoinvent。** 每次 `search` 都要带 `--sources ecoinvent`,`methods` 也查 `ecoinvent` —— 用户来装这个技能就是冲着这个库来的,混进别的库的候选只会让他
更难挑。用户明确要求跨库比较时,告诉他主技能 `hiq-cortex-lca` 更合适。

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
| 材料名 → 候选数据集 | `environmental-data search '<检索词>' --sources 'ecoinvent' --json` |
| key → 详情、GWP100、链接 | `environmental-data lookup '<key1,key2,…>' --json`(一次 1–200 个) |
| 非 GWP 的 LCIA 指标 | `environmental-data methods <库代码>` 查 methodId → `environmental-data lcia '<key[,key…]>' --method '<methodId>' --json` |
| 单数据集过程贡献(分阶段) | `environmental-data lcia '<key>' --contributions --method '<methodId>' --json` |
| 累计清单(基本流) | `environmental-data lci '<key>' [--type output --category air] --json` |

`--model` 取 `cut_off` / `consequential` / `apos` / `en15804`,是系统模型过滤,不是 LCIA 方法。

默认检索直连数据服务,约一秒返回,是按名称的词法检索:检索词里写产品 / 工艺名(中英文名都写更好),库、系统模型、地域用 `--sources` / `--model` / `--location` 限定。它不判断需求 —— 每条候选是否合用,由你对照需求判定。

`--sources` 用小写库代码,多个用 `|` 连在**一个**参数里(如 `'hiqlcd|hiqlcd-al'`);指定版本写 `库代码:版本`,版本号用 `environmental-data sources --json` 返回的完整写法。methodId 不要猜:先 `methods <库代码>`,或看 `lcia` 返回的 `methodIdsWithData`。

`datasetRef` 是不透明句柄,原样传递,绝不自行拼接或修改。默认输出是预览(每个数组最多 10 行,省略描述类字段,`coverage.omitted` 标出省略了什么),需要全部内容加 `--full`。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `datasetRef` | 数据集句柄 | `lookup` / `lci` / `lcia` 时原样传,**不展示给用户** |
| `name` / `referenceProduct` / `location` | 名称、参考流(名称 / 单位 / 数量)、地域 | 引用前必读,这是区分候选的依据 |
| `source.code` / `source.version` / `systemModel.code` | 库 / 版本 / 系统模型 | 这就是要交代的基准,直接取,别自己拼 |
| `searchEvidence` | 默认检索的词法得分 | 不是匹配质量,候选是否合用自己判定 |
| `headlineGwp` | `lookup` 给的 GWP100:`value` / `unit` / `method` | 数值连同方法一起引用 |
| `restricted: true` + `reason` | 有数据,但本账号读不到 | 说明是 ecoinvent 受限及原因,可提供免费库替代并说明 |
| `webUrl` | 数据集详情页 | **每条结果都带上**,别等用户要;没有就如实说没有,不要自己拼 |
| `data.coverage.missingKeys` | 请求的 key 没有返回 | 重新检索,不要手改 key |

## 什么时候该问用户

**先查、再对比、最后才问。** 有可检索的对象就先检索,在同一轮里给结果。

用户说「不确定该用哪个」是**决策支持信号,不是提问信号**:给候选、在同一口径下并列、说明差异来自哪个维度、在证据支持时给带条件的推荐。

只有当需要最终敲定一个数据集、且剩余歧义会实质改变结果时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 从业者写,用 ISO 14040/14044 与 ILCD 的标准术语。单元过程 unit process · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 特征化因子 characterization factor · 截止法 cut-off · 后果法 consequential。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 本账号读不到该库数值(看 `reason`:商业库要账号已开通 CLI 商业数据访问且有该库数据包) | 如实说明;**绝不静默替换数值** |
| `lcia` 没有数据 | methodId 不对,或该库没有 LCIA 层 | `methods ecoinvent` 查 methodId,看 `methodIdsWithData` |
| `missingKeys` 非空 | key 不在当前目录(多为旧版本) | 重新检索,不要手改 key |
| 指定版本被拒 | 版本号要写全(`3.13.0`,不是 `3.13`) | 用 `sources --json` 返回的版本号 |
| 加了 `--location` 就没结果 | 不认识的地域代码不匹配任何数据,也不会放宽 | 用返回里 `location.id` 的写法(`CN`、`CN-ECGC`、`RER`、`GLO` 等) |
| `command not found` | 没装 CLI | 按「接入」安装固定版本 |
| 认证错误 / `doctor` exit 2 | 本机没有凭据,或凭据被拒 | `environmental-data login --json`,用户授权后继续原任务 |
| 设了 `QUERYING_LCA_DATASETS_API_KEY` 时 `lci` / `lcia` / `methods` 被拒 | 这三个命令不接受 API key(`lookup` 可以) | 用 `login` 的凭据跑这三个命令 |
| `429` | 按地址限流 | CLI 会自动退避;不要并发或无界循环 |
