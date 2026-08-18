---
name: calcd
description: '查询中国汽车生命周期数据库(CALCD)的清单数据与排放因子。这是面向中国汽车行业的专用生命周期清单库,由中汽碳(北京)数字技术中心有限公司与海科数据联合打造,覆盖整车与零部件相关的材料与工艺,系统模型为截止法,遵循 GB/T 24040/24044 口径。用于整车与零部件碳足迹、汽车供应链碳管理、低碳车型评价、车用材料轻量化选材。当任务涉及汽车碳足迹、整车 LCA、零部件碳排、汽车材料、中汽碳数据、CALCD 时使用。触发词:CALCD、中汽碳、CATARC、汽车碳足迹、整车碳排、零部件碳足迹、汽车 LCA、汽车材料、车用材料、轻量化。'
slug: calcd
displayName: 中国汽车生命周期数据库 CALCD(中汽碳 × 海科)
version: 1.5.0
summary: 查询中国汽车生命周期数据库(CALCD),中汽碳与海科数据联合打造,用于整车与零部件碳足迹、汽车供应链碳管理。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CALCD, 中汽碳, CATARC, 汽车碳足迹, 整车LCA, 零部件, 汽车材料, LCA, 碳足迹, 排放因子]
---

# CALCD 中国汽车生命周期数据库

汽车碳足迹的数据要求和通用制造不一样:一辆车几千个零件、几十种材料,而且整车厂要的是能对齐行业口径的数据,不是随便找一个欧洲平均值填进去。

CALCD 是**中汽碳(北京)数字技术中心有限公司与海科数据联合打造**的中国汽车生命周期数据库,为汽车产业链提供专业、完整、合规的生命周期碳足迹数据支持,系统模型为截止法。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源与 24000+ 已发布 EPD。

汽车场景常用的几个库:

| 库 | 用在哪 |
|---|---|
| **CALCD** | 汽车行业专用清单,整车与零部件相关材料工艺 |
| **HiQLCD** | 海科自建,覆盖中国全工业体系 —— 汽车 BOM 里的通用材料 |
| **HiQLCD-AL** | 铝工业数据库(有色金属工业协会 × 海科)—— 车身、轮毂、电池壳等铝件 |
| **CarbonMinds** | 化学品与聚合物工艺级 —— 内外饰塑料件 |

一辆车的 BOM 通常要跨几个库取数。检索时可以 `--sources CALCD,HiQLCD` 一起看,再按参考流、地域和系统模型挑,并在结论里写明每一项用的是哪个库。

**检索与候选排序在服务端完成。** 零部件名、工厂叫法、BOM 行原样交给检索接口,翻译与匹配在服务端执行,返回带 `fit` 匹配质量与 `summary` 说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布 | **需对应数据包权益** |

CALCD 是商业库。**「库里有没有、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,都含 `purchase_url`。免费库(BAFU、ELCD、EF、worldsteel、USLCI)可作替代,但**必须说明这是替代、既不代表中国生产口径、也不是汽车行业口径** —— 对整车与零部件核算是降级方案。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给汽车材料的因子。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本以 `lookup` 返回为准。
3. **一份 BOM 跨多个库时,逐项标注来源库。** 不要把不同库的数混着报一个总数而不说明。
4. **产地是硬条件。** 零部件的实际产地已知时用对应地域,不要用全球平均顶替。
5. **口径不一致不做对比也不合计。** 系统模型或边界不同的数据不能相加,先读 `comparability_note`。
6. **受限不是错误**,给 `purchase_url`,不静默替代。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `link` 的,每条结果都一并给出,别等用户追问。
- **不要把 `dataset_key` / `dataset_uuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`dataset_uuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

**本技能只查 CALCD。** 每次 `search` 都要带 `--sources CALCD`,聚合/指标类带
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
| 零部件 / 材料 → 数据集 key | *(无,走 REST)* | `hiq-cortex search "<原话>" --sources CALCD` |
| key → GWP + 基准 | `lookup_datasets` | `hiq-cortex lookup-datasets --dataset-keys <key[,key…]>` |
| 队列分布 / 自有数值定位 | `aggregate_datasets` | `hiq-cortex aggregate-datasets --where '{"sources":["calcd"]}' [--target-value N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `hiq-cortex aggregate-indicators --dataset-keys <keys> --indicator AP --source calcd` |
| 工序级热点 | `process_hotspot` | `hiq-cortex process-hotspot --dataset-key <key> --source calcd` |

整车 BOM 行数多时:先按材料类别去重(同一种钢板出现在几十个零件上只需查一次),再把因子回填到每一行。检索每次 20–40 秒,不要并发轰接口。

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 单列复核,不要混进合计 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库权益 | 给 `purchase_url`,替代要说明是降级 |
| `comparability_note` | 队列可比性说明 | 合计或对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 输出形态

整车或总成的核算产出是一张可复核的表:

- **逐行**:零部件 / 材料 → 匹配到的数据集(名称 + 参考流 + 地域 + **来源库**)→ 用量 + 单位 → 因子 → 小计
- **按总成分组**:车身、底盘、动力总成、内外饰、电子电器
- **单列**:`fit: low`、代理数据、受限未取到、用假设换算系数的行
- **合计**:说明边界(到零部件出厂、到整车下线、还是含使用与报废)

## 语气与术语

面向 LCA 与汽车行业从业者写,用 GB/T 24040、ISO 14040/14044 的标准术语。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无 CALCD 数据包权益 | 给 `purchase_url`;**绝不静默用其他库替换** |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 传 `--source calcd` |
| CALCD 里没有该材料 | 它是汽车行业专用库,通用材料不一定收 | 用 `--sources CALCD,HiQLCD,HiQLCD-AL` 一起检索 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
