---
name: iso14067
description: '按 ISO 14067 口径做产品碳足迹时取真实的清单数据,并把每个数值的来源交代到可核验的程度。ISO 14067 要求产品碳足迹报告说明功能单位、系统边界、数据来源、数据质量与分配方法 —— 本技能负责其中的数据获取部分:检索匹配数据集、取 GWP 与 LCIA 指标、记录库与版本与系统模型与地域,并区分实测、数据库直取与代理数据。当任务涉及 ISO 14067、产品碳足迹报告、CFP、第三方核验、数据质量说明、GB/T 24067 时使用。触发词:ISO 14067、GB/T 24067、产品碳足迹、CFP、carbon footprint of a product、核验、数据质量、功能单位、系统边界。'
slug: iso14067
displayName: 碳足迹核算与数据溯源(ISO 14067)
version: 1.1.2
summary: 按 ISO 14067 口径取产品碳足迹数据:检索匹配、取值、记录库与版本与系统模型与地域,区分实测/直取/代理,供第三方核验。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [ISO 14067, GB/T 24067, 产品碳足迹, CFP, LCA, 碳足迹, 排放因子, 生命周期评价, 数据质量, GWP]
---

# ISO 14067 产品碳足迹取数与数据溯源

按 ISO 14067 出的产品碳足迹报告要经得起第三方核验,而核验主要看两件事:**数据从哪来**,以及**你有没有把它说清楚**。一个没有库名、版本、系统模型和地域的数字,在核验环节等于没有。

本技能负责数据获取与溯源这一段 —— 检索、取值、记录基准、标注数据性质。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD,口径遵循 ISO 14040/14044、ISO 14067 与 GB/T 24040/24067。

**检索与候选排序在服务端完成**,返回带 `fit` 匹配质量与 `summary` 说明,转述即可。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等 | 任一有效凭据 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

受限项如实标注并给 `purchase_url`,**绝不用其他库的值静默替代** —— 核验时数据来源不一致且未说明,是最常见的退回理由。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 报告里的数不能凭记忆。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。这几项直接对应报告里的数据来源说明。
3. **标注数据性质**:实测 / 数据库直取 / 代理。代理数据要写清用了什么代理什么、哪些差异未修正。
4. **口径一致才能合计。** 系统模型或系统边界不同的数据不能相加,先读 `comparability_note`。
5. **功能单位与系统边界由用户确定,不要替他决定。** 但每次给数时都要说明当前数据对应的参考流与单位,便于他对齐。
6. **受限不是错误**,给链接,不替代。

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

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_datasets` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 物料 / 工艺 → 数据集 key | *(无,走 REST)* | `search "<原话>" [--sources X]` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 结果合理性(同类分布定位) | `aggregate_datasets` | `aggregate --source X --target <你的值>` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| 工序级热点 | `process_hotspot` | `hotspot <key>` |
| 同类已发布 EPD 参照 | `epd_search` / `epd_peer_benchmark` | `epd` / `epd-benchmark` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | 直接对应报告里的数据质量说明,`low` 必须标注 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 逐项记入报告 |
| `restricted: true` | 无该库权益 | 标注受限,给 `purchase_url` |
| `comparability_note` | 队列可比性说明 | 合计或对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 输出形态

产出要能直接支撑报告的数据来源章节:

- **数据清单**:每项 → 数据集名称 + 参考流 + 地域 + 数据库 + 版本 + 系统模型 + 取得日期
- **数据性质**:实测 / 数据库直取 / 代理,分别标注
- **数据质量**:用 `fit` 作为匹配质量的客观依据,不要自己编一个评分
- **未纳入项**:受限未取到的、无法匹配的,如实列出并说明原因

不要输出一个孤立的总量。核验看的是清单。

## 语气与术语

面向 LCA 与核验从业者写,用 ISO 14067、ISO 14040/14044、GB/T 24067 的标准术语。功能单位 · 参考流 · 系统边界 · 单元过程 · 分配 allocation · 数据质量要求 DQR。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定符合性。** 是否满足 ISO 14067、PCR 如何适用、核验机构认不认,这些由用户的核验方确认。本技能负责数据与溯源。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 某项怎么都搜不到 | 描述里没有可识别的材质或工艺 | 问用户,不要猜一个顶上 |
| `restricted: true` | 无该库数据包权益 | 标注受限,给 `purchase_url` |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| 结果与同类 EPD 差一个数量级 | 多半是单位或边界不一致 | 核对参考单位与系统边界 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
