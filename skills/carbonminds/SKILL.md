---
name: carbonminds
description: '查询化学品与塑料的工艺级生命周期清单数据。CarbonMinds 覆盖化学品与高分子材料,建模细度到工艺路线层级,适合区分同一聚合物的不同合成路线、原料来源(石油基 / 生物基 / 再生)与地域。用于塑料件与化工产品的碳足迹、材料替代评估、生态设计选材、包装碳排。当任务涉及化学品排放因子、塑料碳足迹、聚合物 LCI、树脂、单体、生物基塑料、再生塑料时使用。触发词:CarbonMinds、化学品、塑料、聚合物、树脂、单体、PP、PE、PET、PVC、ABS、PA、生物基塑料、再生塑料、化工碳足迹。'
slug: carbonminds
displayName: 化学品与塑料 LCA 数据 —— CarbonMinds 工艺级清单
version: 1.1.0
summary: 查询化学品与高分子材料的工艺级清单数据,区分合成路线、原料来源与地域,用于塑料件与化工产品碳足迹。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CarbonMinds, 化学品, 塑料, 聚合物, 树脂, LCA, 碳足迹, 排放因子, 生命周期评价, LCI]
---

# CarbonMinds 化学品与塑料工艺级清单

塑料的碳足迹不是一个数。同一种 PP,石油基与生物基不同,不同合成路线不同,不同产地的能源结构也不同 —— 拿一个"通用 PP"的值套所有场景,在材料替代评估里会直接得出相反结论。

CarbonMinds 的价值就在这里:它把化学品与高分子建模到工艺路线层级,能把这些区分做出来。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 CarbonMinds 在内的 18 个国际主流数据源与 24000+ 已发布 EPD。

**检索与候选排序在服务端完成。** 把材料名或牌号原样交给检索接口 —— 商品名到化学名的映射、路线判别、候选排序都在服务端执行,返回带 `fit` 匹配质量与 `summary` 说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | CarbonMinds 的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布 | **需 CarbonMinds 数据包权益** |

CarbonMinds 是商业库。**「库里有没有这条工艺、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,都含 `purchase_url`。如实说明并给链接;免费库(BAFU、ELCD、EF)也有常见聚合物的数据,可作替代路径,但**必须说明这是替代,且工艺细度不同** —— 免费库通常只有材料级平均值,做不了路线区分。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给聚合物的 GWP。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本以 `lookup` 返回为准。
3. **路线不同的数据分别报,不要平均。** 用户问某种塑料时,如果候选里有多条不同工艺路线,把它们并列展示并说明区别来自哪个维度,不要自己挑一条或取中间值。
4. **先读数据集名称和参考流。** 单体与聚合物、粒料与制品、不同牌号在库里是不同条目。
5. **受限不是错误**,给 `purchase_url`,不静默替代。

## 接入

```bash
python3 scripts/cortex.py login    # 扫码登录:浏览器点一次授权,无需注册建 key
export HIQ_API_KEY=sk_xxx          # 或用 API key(适合服务端 / CI),优先级更高
```

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_datasets` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 材料名 / 牌号 → 数据集 key | *(无,走 REST)* | `search "<原话>" --sources CarbonMinds` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 同品类分布 / 数值定位 | `aggregate_datasets` | `aggregate --source carbonminds [--target N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source carbonminds` |
| 工序级热点 | `process_hotspot` | `hotspot <key> --source carbonminds` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 —— 单体与聚合物是不同条目 |
| `restricted: true` | 无 CarbonMinds 权益 | 给 `purchase_url`,替代方案要说明细度差异 |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 什么时候该问用户

**先查、再对比、最后才问。** 材料名拿到就先检索,把候选和它们的区别一次给出来。

材料替代评估("换成再生料能减多少")属于**决策支持**:并列展示各路线的候选与数值,说明差异来自哪个维度,在证据支持时给带条件的推荐 —— 不要上来就问用户要哪条路线。

只有当需要敲定一条数据集、且剩余歧义会实质改变结论时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 与材料工程从业者写,用 ISO 14040/14044 与 ILCD 的标准术语。单元过程 · 参考流 · 功能单位 · 系统边界 · 截止法 cut-off。化学品用标准名(聚丙烯 / polypropylene),牌号只在用户给出时沿用。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无 CarbonMinds 数据包权益 | 给 `purchase_url`;免费库可替代但要说明细度不同 |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 传 `--source carbonminds` |
| 候选里全是单体 | 检索词落在原料层 | 用聚合物名或制品描述重新检索 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
