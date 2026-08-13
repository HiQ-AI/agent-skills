---
name: lca
description: '做生命周期评价(LCA)时取真实的清单数据与全套影响评价指标。不只是碳:除 GWP 外还可取酸化(AP)、富营养化(EP)、臭氧消耗(ODP)、水耗(WDP)、资源消耗(ADP)等 LCIA 指标,覆盖 18 个生命周期清单数据库与 24000+ 已发布 EPD。用于完整 LCA 研究、多指标环境评价、生态设计权衡分析、工序级热点识别、行业分布定位。当任务涉及生命周期评价、LCA 研究、清单分析、影响评价、多指标评价、环境热点、ISO 14040/14044 时使用。触发词:LCA、生命周期评价、生命周期评估、清单分析、LCI、影响评价、LCIA、酸化、富营养化、环境影响、ISO 14040。'
slug: lca
displayName: 生命周期评价(LCA)数据与多指标影响评价
version: 1.1.1
summary: 做 LCA 取清单数据与全套 LCIA 指标:GWP 之外还有酸化、富营养化、臭氧消耗、水耗、资源消耗,以及工序级热点与行业分布。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [LCA, 生命周期评价, LCI, LCIA, 影响评价, 酸化, 富营养化, 碳足迹, 排放因子, ISO 14040]
---

# LCA 生命周期评价数据与多指标影响评价

碳只是一个影响类别。一份只报 GWP 的 LCA 不是 LCA —— 换材料常常是把碳降下去、把水耗或资源消耗顶上来,不看其他指标就看不见这种转移。

本技能负责 LCA 的数据侧:清单数据获取、多指标影响评价取值、工序级热点、行业分布定位。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

可访问:

- **18 个生命周期清单数据库**,11 个免费。含中国本土数据(HiQLCD 覆盖中国全工业体系、铝产业链 HiQLCD-AL、汽车行业 CALCD)与国际主流库(Ecoinvent、BAFU、ELCD、EF、worldsteel、USLCI、AusLCI、CarbonMinds、Agri-footprint)。
- **24000+ 已发布 EPD**(EPDItaly、ECO Platform、EPD Norge)。
- 口径遵循 ISO 14040/14044 与 GB/T 24040/24044,系统模型覆盖截止法、后果法、APOS、EN 15804。

**检索与候选排序在服务端完成**,返回带 `fit` 匹配质量与 `summary` 说明,转述即可,不要另编一套。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 全部 18 库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI、NEEDS、ozLCI、bioenergiedat、recycledplastics | 任一有效凭据 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

**LCIA 覆盖各库差别很大** —— 有的库指标数以百计,有的只有 GWP,少数只有 LCI 层没有 LCIA 层。做多指标评价前先看目录层给出的指标覆盖,别在只有 GWP 的库上找酸化。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 GWP、LCIA 值或分布。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **一次一个指标。** `indicators` 按指标查询,`--source` 必须与队列实际所在库一致 —— 特征化方法跨库不通用。
4. **口径不一致不做对比。** 系统模型、功能单位、系统边界不同的数据不可比,先读 `comparability_note`。
5. **多指标结论要并列呈现,不要合成单一分数。** 加权成一个总分需要价值判断,那是用户和委托方的事,不是取数环节该替他做的。
6. **受限不是错误**,给 `purchase_url`,不静默替代。

## 接入

**没有凭据时,第一句话就给扫码登录 —— 不要让用户去控制台建 API key。**

扫码是「跑一条命令 + 浏览器点一下」,无需注册;建 API key 要登录控制台、找入口、
复制粘贴、设环境变量,门槛高出一个量级。把后者摆在第一步会直接劝退用户。

```bash
python3 scripts/cortex.py login      # ← 缺凭据时默认走这条
```

命令会打印一个授权链接。**把链接原样给用户,让他点「授权访问」**,然后继续原来的任务 ——
凭据落在 `~/.hiq/credentials.json`(权限 600),之后所有命令直接可用,可见数据范围与
该账号一致(**包含他已开通的商业数据库**)。

只在这三种情况下才提 API key:用户自己说要用 key、运行在 CI / 服务端无浏览器环境、
或扫码登录失败。

```bash
export HIQ_API_KEY=sk_xxx            # 服务端 / CI 用;同时存在时优先于扫码凭据
```

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_indicators` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 材料 / 工艺 → 数据集 key | *(无,走 REST)* | `search "<原话>" [--sources X]` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| **非 GWP 的 LCIA 指标**(AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| 队列分布 / 百分位定位 | `aggregate_datasets` | `aggregate --source X [--target N]` |
| **工序级热点** | `process_hotspot` | `hotspot <key> [--indicator GWP100]` |
| 已发布 EPD 检索与同类分布 | `epd_search` / `epd_peer_benchmark` | `epd` / `epd-benchmark` |

`process_hotspot` 支持指定指标 —— 找热点时不要只看 GWP,同一个产品在不同指标下的热点工序可能完全不同。

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库权益 | 给 `purchase_url`,替代要说明 |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `entitlement` | 聚合为空是权益问题 | 不要换谓词重试 |
| `indicators` 返回空 | 该库可能没有 LCIA 层,或 `--source` 不对 | 先确认库的指标覆盖 |

## 输出形态

多指标结果并列成表,一列一个指标,并注明各自的特征化方法来源与所在库。指标之间出现权衡(碳降了、水耗升了)时明确指出来 —— 这正是做多指标评价的意义,不要只挑对结论有利的指标报。

## 什么时候该问用户

**先查、再对比、最后才问。** 有可检索的对象就先检索,在同一轮里给结果。

用户说「不确定该用哪个」是**决策支持信号**:给候选、在同一口径下并列、说明差异来自哪个维度、在证据支持时给带条件的推荐。

只有当需要敲定一个数据集、且剩余歧义会实质改变结果时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 从业者写,用 ISO 14040/14044、ILCD、GB/T 24040 的标准术语。单元过程 unit process · 基本流 elementary flow · 中间流 intermediate flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `indicators` 返回空 | `--source` 必须等于队列所在库,或该库没有 LCIA 层 | 传正确的 `--source`;先看目录层的指标覆盖 |
| `restricted: true` | 无该库数据包权益 | 给 `purchase_url`;**绝不静默替换** |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| 队列跨多个数量级 | 功能单位混杂 | 收窄谓词,先读 `comparability_note` |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| 检索耗时 30 秒 | 正常 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
