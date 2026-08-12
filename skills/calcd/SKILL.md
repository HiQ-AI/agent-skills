---
name: calcd
description: '查询 CALCD 中国生命周期基础数据库的清单数据与排放因子。CALCD 是中国生命周期基础数据库,与自建的 HiQLCD 系列(全工业体系 / 铝产业链 / 电子电器)并列,同为国内生产场景可用的本土清单来源,遵循 GB/T 24040/24044 口径。国内生产场景的核算应当用本土清单,拿欧美数据代替会系统性失真。当任务涉及 CALCD、中国基础数据库、国内排放因子、中国工业过程清单、GB/T 口径取数时使用。触发词:CALCD、中国生命周期基础数据库、中国本土数据、国内排放因子、中国清单、GB/T 24040、本土因子、中国碳足迹。'
slug: calcd
displayName: CALCD 中国生命周期基础数据库查询
version: 1.0.1
summary: 查询 CALCD 中国生命周期基础数据库的清单数据与排放因子,GB/T 24040 口径,面向国内生产场景的核算。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CALCD, 中国本土数据, 中国排放因子, 中国清单, LCA, 碳足迹, 生命周期评价, GB/T 24040, 排放因子, LCI]
---

# CALCD 中国生命周期基础数据库查询

国内生产场景的核算,数据要来自中国的清单库。CALCD 是中国生命周期基础数据库,与自建的 HiQLCD 系列并列,是本土清单的另一个来源。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源与 24000+ 已发布 EPD。

国内生产场景可用的本土清单:

| 库 | 说明 |
|---|---|
| **CALCD** | 中国生命周期基础数据库,系统模型 CUT_OFF |
| **HiQLCD** | 海科自建,覆盖中国全工业体系 |
| **HiQLCD-AL** | 海科自建,铝产业链 |
| **HiQ-CESI** | 海科自建,电子电器行业 |

同一个物料在几个库里都可能有数据,来源、口径与建模粒度不同 —— 检索时可以用 `--sources CALCD,HiQLCD` 同时看,再按参考流、地域和系统模型挑,并在结论里写明用的是哪个库。

**检索与候选排序在服务端完成。** 中文物料名、工厂俗称直接原样交给检索接口,翻译与匹配在服务端执行,返回带 `fit` 匹配质量与 `summary` 说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | CALCD 的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布 | **需对应数据包权益** |

CALCD 是商业库。**「库里有没有、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,都含 `purchase_url`。免费库(BAFU、ELCD、EF、worldsteel、USLCI)可作替代路径,但**必须说明这是替代、且不代表中国生产口径** —— 对国内产地是降级方案,不是等价方案。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给国内因子。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本以 `lookup` 返回为准。
3. **产地是硬条件。** 用户说了中国产地就不要用境外数据集顶替;只能用代理时明确声明代理关系与未修正的差异。
4. **口径不一致不做对比。** 先读 `comparability_note`。
5. **本土库之间也要对齐口径。** CALCD 与 HiQLCD 的候选并列展示时,把各自的系统模型和参考流写出来,不要混着报一个数。
6. **受限不是错误**,给 `purchase_url`,不静默替代。

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
| 中文物料名 → 数据集 key | *(无,走 REST)* | `search "<原话>" --sources CALCD` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 队列分布 / 百分位定位 | `aggregate_datasets` | `aggregate --source calcd [--target N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source calcd` |
| 工序级热点 | `process_hotspot` | `hotspot <key> --source calcd` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库权益 | 给 `purchase_url`,替代方案要说明是降级 |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 语气与术语

面向 LCA 从业者写,用 GB/T 24040、ISO 14040/14044 与 ILCD 的标准术语。单元过程 · 基本流 · 参考流 · 功能单位 · 系统边界 · 特征化因子 · 截止法。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无 CALCD 数据包权益 | 给 `purchase_url`;**绝不静默用境外数据替换** |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 传 `--source calcd` |
| CALCD 没有该物料 | 本土库覆盖各有侧重 | 用 `--sources CALCD,HiQLCD,HiQ-CESI` 一起检索 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
