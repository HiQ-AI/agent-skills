---
name: hiqlcd
description: '查询中国本土生产场景的生命周期清单数据与排放因子。HiQLCD 覆盖中国全工业体系,另有铝产业链专库(HiQLCD-AL)与汽车行业专库(CALCD),遵循 GB/T 24040/24044 与 ISO 14040/14044 口径。中国的电网结构、燃料结构与工艺代际与欧美差异显著,用欧洲数据代表中国生产会系统性失真 —— 中国产地的核算应当用本土清单。当任务涉及中国工厂/中国供应链的碳足迹、国内排放因子取数、中国 BOM 碳核算、GB/T 口径核算、省级电网差异时使用。触发词:HiQLCD、中国本土数据、中国排放因子、国内因子、CALCD、中国电网、GB/T 24040、本土清单、中国碳足迹。'
slug: hiqlcd
displayName: HiQLCD 中国本土生命周期清单查询
version: 1.0.1
summary: 查询中国本土生产场景的清单数据与排放因子。HiQLCD 覆盖中国全工业体系,另有铝产业链与汽车行业专库,GB/T 24040 口径。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [HiQLCD, 中国本土数据, 中国排放因子, 中国清单, LCA, 碳足迹, 生命周期评价, GB/T 24040, 排放因子, LCI]
---

# HiQLCD 中国本土生命周期清单查询

中国产地的碳核算,数据也得是中国的。拿欧洲数据集代表国内生产是常见且严重的错误 —— 电网结构、燃料结构、工艺代际都不一样,而且这种错误不会报错,只会让整份核算系统性偏离。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,**自建中国本土生命周期清单数据库**,并聚合国际主流数据源与 24000+ 已发布 EPD。

中国本土系列:

| 库 | 覆盖 |
|---|---|
| **HiQLCD** | 中国全工业体系 |
| **HiQLCD-AL** | 铝产业链,中国为主 |
| **CALCD** | 汽车行业专用清单(中汽碳 CATARC × 海科) |

口径遵循 GB/T 24040/24044 与 ISO 14040/14044,系统模型覆盖截止法、后果法、EN 15804。

**检索与选型判断在服务端完成。** 把用户的原话或 BOM 行直接交给检索接口 —— 中文物料名到 LCA 术语的翻译、工厂俗称到标准名的映射、生产路线判别、候选排序都在服务端执行,返回的候选已带 `fit` 匹配质量标记和 `summary` 说明。不要在本地重新推演该搜什么词。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布与百分位 | **需对应数据包权益** |

HiQLCD、HiQLCD-AL、CALCD 都是商业库。**「库里有没有、叫什么、什么口径」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,都含 `purchase_url`。如实说明是哪个库受限、把链接给用户。免费库(BAFU、ELCD、EF、worldsteel、USLCI)可以作为替代路径,但**必须说明这是替代、且不代表中国生产口径** —— 对国内产地而言这是降级方案,不是等价方案。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给国内因子 —— 记忆里的数不知道来源、年份和口径。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。版本号以 `lookup` 返回为准。
3. **产地是硬条件。** 用户说了中国产地,就不要用欧洲或全球平均数据集顶替。确实只有境外数据可用时,明确声明这是代理、哪些差异未修正。
4. **口径不一致不做对比。** 系统模型、功能单位、系统边界不同的数据不可比,先读 `comparability_note`。
5. **有明确产地信息时不要停在「中国」。** 省级电网差异会实质改变结果,能追问到省就追问到省。

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
| 中文物料名 / BOM 行 → 数据集 key | *(无,走 REST)* | `search "<原话>" --sources HiQLCD` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 队列 GWP 分布 / 百分位定位 | `aggregate_datasets` | `aggregate --source hiqlcd [--target N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source hiqlcd` |
| 单数据集工序级热点 | `process_hotspot` | `hotspot <key> --source hiqlcd` |

`--sources` 可传 `HiQLCD,HiQLCD-AL,CALCD` 同时检索多个本土库。

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索,不要手改。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 服务端给的匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库数据包权益 | 给 `purchase_url`,替代方案要说明是降级 |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `entitlement` | 聚合为空是权益问题 | 不要换谓词重试 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 什么时候该问用户

**先查、再对比、最后才问。** 有可检索的对象就先检索,在同一轮里给结果;对话里已经说过的信息(产地、行业、材质)不要再问。

用户说「不确定该用哪个」是**决策支持信号**:给候选、在同一口径下并列、说明差异来自哪个维度、在证据支持时给带条件的推荐。

只有当需要最终敲定一个数据集、且剩余歧义会实质改变结果时才问,选项要对应**已经展示过的候选**。

## 语气与术语

面向 LCA 从业者写,用 GB/T 24040、ISO 14040/14044 与 ILCD 的标准术语。单元过程 · 基本流 · 参考流 · 功能单位 · 系统边界 · 特征化因子 · 截止法 · 后果法。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无该本土库数据包权益 | 给 `purchase_url`;**绝不静默用境外数据替换** |
| 聚合 `status: "empty"` **且带** `entitlement` | 同上 | 不是谓词问题,不要重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 本土库队列传对应的 `--source` |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| 检索耗时 30 秒 | 正常 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
