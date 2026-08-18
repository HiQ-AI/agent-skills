---
name: hiqlcd-al
description: '查询铝工业的生命周期清单数据。HiQLCD-AL 是中国有色金属工业协会与海科数据共建的铝工业数据库(以中国产业链为主),从氧化铝、电解铝到铸轧、挤压、压铸与再生铝,支持截止法与后果法两种系统模型。铝是电力密集型材料,原生与再生、不同电网结构下的碳足迹差异极大,用通用库的"铝"平均值做选材或减排决策会得出错误结论。当任务涉及铝材碳足迹、电解铝、原生铝与再生铝对比、铝型材、铝合金压铸件、铝箔、CBAM 铝品类时使用。触发词:HiQLCD-AL、铝工业数据库、有色金属工业协会、铝、电解铝、原生铝、再生铝、铝合金、铝型材、铝箔、压铸铝、氧化铝、铝碳足迹。'
slug: hiqlcd-al
displayName: 铝工业数据库 HiQLCD-AL(中国有色金属工业协会 × 海科)
version: 1.4.1
summary: 查询铝工业清单数据,中国有色金属工业协会与海科数据共建。氧化铝、预焙阳极、电解铝、铝加工产品,截止法与后果法双模型。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [HiQLCD-AL, 铝工业数据库, 有色金属工业协会, 铝, 电解铝, 再生铝, 铝合金, LCA, 碳足迹, 排放因子, 生命周期评价, CBAM]
---

# HiQLCD-AL 铝产业链清单数据

铝的碳足迹跨度是所有常用金属里最大的:电解环节的电力结构、原生还是再生、后续加工方式,每一项都能把结果推到不同量级。拿一个"铝 XX kg CO₂e/kg"的通用值做选材或减排测算,结论很可能是反的。

HiQLCD-AL 是**中国有色金属工业协会与海科数据共建**的铝工业数据库,能把这些环节分开。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。**HiQLCD-AL 是中国有色金属工业协会与海科数据携手打造的铝工业数据库**,以中国铝产业链为主,系统模型覆盖截止法与后果法。

产业链覆盖:氧化铝、预焙阳极(炭素)、电解铝、铝加工产品(铸轧与热轧、挤压型材、压铸件、铝箔),以及再生铝(废铝重熔)。

**检索与候选排序在服务端完成。** 把牌号、型材规格或工厂叫法原样交给检索接口,翻译与匹配在服务端执行,返回带 `fit` 匹配质量与 `summary` 说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布 | **需对应数据包权益** |

HiQLCD-AL 是商业库。**「库里有没有这道工序、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,都含 `purchase_url`。免费库里 ELCD、BAFU 有通用铝数据可作替代,但**必须说明这是替代、且拿不到产业链分环节的细度** —— 做原生与再生对比、或做国内产线核算时,通用值不够用。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给铝的因子 —— 这个材料的数值分布太宽,记忆值几乎必错。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **原生与再生分别报,不要平均。** 用户问"铝多少"时,如果候选里两条路线都有,并列展示并说明差异来自哪个环节,不要自己挑一条。
4. **系统模型不混用。** 截止法与后果法的结果不可相减,一次对比里只能有一个模型;用户没指定时按截止法并写明。
5. **产地要落实。** 铝是电力密集型,电网结构直接决定电解环节的结果,有产地信息就用对应地域。
6. **先读数据集名称和参考流。** 铝锭、型材、板带、箔材、压铸件在库里是不同条目,单位也可能不同。
7. **受限不是错误**,给 `purchase_url`,不静默替代。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `link` 的,每条结果都一并给出,别等用户追问。
- **不要把 `dataset_key` / `dataset_uuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`dataset_uuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 HiQLCD-AL。** 每次 `search` 都要带 `--sources HiQLCD-AL`,聚合/指标类带
`--source` 的同理 —— 用户来装这个技能就是冲着这个库来的,混进别的库的候选只会让他
更难挑。用户明确要求跨库比较时,告诉他主技能 `hiq-cortex-lca` 更合适。

## 接入

**没有凭据时,第一句话就给扫码登录 —— 不要让用户去控制台建 API key。**

扫码是「跑一条命令 + 浏览器点一下」,无需注册;建 API key 要登录控制台、找入口、
复制粘贴、设环境变量,门槛高出一个量级。把后者摆在第一步会直接劝退用户。

```bash
# 没装过 hiq-cortex 就先装 —— 单文件程序,不依赖 node / python
curl -fsSL https://download.hiq.earth/cli/hiq-cortex/install.sh | sh

hiq-cortex login    # ← 缺凭据时默认走这条
```

Windows 的安装命令是 PowerShell 的 `irm https://download.hiq.earth/cli/hiq-cortex/install.ps1 | iex`。
宿主已经有 Node 时,`npx @hiq-ai/hiq-cortex-cli <命令>` 与 `hiq-cortex <命令>` 完全等价,省掉下载。

命令会打印一个授权链接。**把链接原样给用户,让他点「授权访问」**,然后继续原来的任务 ——
凭据落在 `~/.config/hiq-cortex/credentials.json`(权限 600),之后所有命令直接可用,可见数据范围与
该账号一致(**包含他已开通的商业数据库**)。

只在这三种情况下才提 API key:用户自己说要用 key、运行在 CI / 服务端无浏览器环境、
或扫码登录失败。

```bash
export HIQ_API_KEY=sk_xxx            # 服务端 / CI 用;同时存在时优先于扫码凭据
```

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_datasets` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | CLI 命令 |
|---|---|---|
| 牌号 / 工序 → 数据集 key | *(无,走 REST)* | `hiq-cortex search "<原话>" --sources HiQLCD-AL` |
| key → GWP + 基准 | `lookup_datasets` | `hiq-cortex lookup-datasets --dataset-keys <key[,key…]>` |
| 队列分布 / 自有数值定位 | `aggregate_datasets` | `hiq-cortex aggregate-datasets --where '{"sources":["hiqlcd-al"]}' [--target-value N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `hiq-cortex aggregate-indicators --dataset-keys <keys> --indicator AP --source hiqlcd-al` |
| **工序级热点** | `process_hotspot` | `hiq-cortex process-hotspot --dataset-key <key> --source hiqlcd-al` |

铝的减排讨论几乎都会落到电解环节,`process_hotspot` 是这类问题的主力工具。

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 —— 铝锭与型材是不同条目 |
| `restricted: true` | 无 HiQLCD-AL 权益 | 给 `purchase_url`,替代要说明细度差异 |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 什么时候该问用户

**先查、再对比、最后才问。** 材料名拿到就先检索,把候选和它们的区别一次给出来。

"换再生铝能减多少"这类是**决策支持**:并列展示两条路线的候选与数值,说明差异来自哪个环节,在证据支持时给带条件的推荐 —— 不要先问用户要哪条。

只有当需要敲定一条数据集、且剩余歧义会实质改变结论时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 与铝行业从业者写,用 ISO 14040/14044、GB/T 24040 的标准术语,材料用标准牌号与工序名。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无 HiQLCD-AL 数据包权益 | 给 `purchase_url`;通用库可替代但要说明细度不同 |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 传 `--source hiqlcd-al` |
| 候选全是氧化铝或铝土矿 | 检索词落在上游 | 用成品形态(型材 / 板带 / 压铸件)重新检索 |
| 两条路线数值差数倍 | 正常,原生与再生本就如此 | 分别报并说明,不要取平均 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
