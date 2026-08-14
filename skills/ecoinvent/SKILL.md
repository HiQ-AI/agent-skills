---
name: ecoinvent
description: '在 ecoinvent 中检索并读取真实的生命周期清单数据。ecoinvent 是全球覆盖最广的 LCI 数据库,同一材料在不同系统模型(cut-off、APOS、consequential、EN 15804)、不同地域、不同参考流下结果可差数倍,本技能负责把检索、口径核对与基准交代做对。当任务涉及 ecoinvent 数据集查询、系统模型选择、活动名称与参考流核对、地域代理、GWP 与 LCIA 指标取数时使用。触发词:ecoinvent、cut-off、截止法、APOS、consequential、后果法、系统模型、system model、LCI 数据集、生命周期清单、排放因子、GWP、kg CO2e。'
slug: ecoinvent
displayName: ecoinvent 数据集查询与系统模型核对
version: 1.0.2
summary: 在 ecoinvent 中检索数据集并读懂口径:系统模型、地域、参考流、版本一并交代,候选之间的差异由服务端标注。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [ecoinvent, LCA, 系统模型, cut-off, APOS, consequential, 排放因子, 生命周期评价, LCI, GWP]
---

# ecoinvent 数据集查询与系统模型核对

在 ecoinvent 里查一个材料,难点不是「找不到」,而是**找到十几条都叫这个名字的数据集** —— 不同生产路线、不同地域、不同系统模型、不同参考流。选错口径不会报错,只会安静地给出一个看起来合理的数。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 ecoinvent 在内的 18 个国际主流数据源与 24000+ 已发布 EPD。

**检索与选型判断在服务端完成。** 把用户的原话直接交给检索接口 —— 术语翻译、路线判别、候选排序与匹配质量评估都在服务端执行,返回的候选已排过序并带 `fit` 标记和 `summary` 说明。不要在本地重新推演该搜什么词,也不要自己另编一套解释覆盖服务端给的说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | ecoinvent 的版本、可用系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 数值层 | GWP、LCIA 值、队列分布与百分位 | **需 ecoinvent 数据包权益** |

**「库里有没有、叫什么、什么口径、该选哪条」免费;「数值是多少」需要权益。**

无权益时 `lookup` 返回 `restricted: true`、聚合返回 `status: "empty"` 且带 `entitlement`,两者都含 `purchase_url`。这时如实说明是 ecoinvent 受限、把链接给用户;若免费库(BAFU、ELCD、EF、worldsteel、USLCI)能回答同一问题,主动提供这条替代路径并**明确说明这是替代、口径不同**。重试无用 —— 受限是授权状态,不是故障。

数据包权益与订阅套餐是两套独立体系,升级套餐不解锁数据库。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 ecoinvent 的值 —— 记忆里的数不知道是哪个版本、哪个系统模型、哪个地域的,等于没有。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。`2.31 kg CO₂e/kg(ecoinvent 3.x,cut-off,RER,steel, low-alloyed, hot rolled)` 可用;单独一个 `2.31` 不可用。版本号以 `lookup` 返回为准,不要凭印象写。
3. **系统模型不同的数据不放进同一次对比。** cut-off、APOS、consequential、EN 15804 回答的是不同问题,相减得到的差值没有物理意义。用户没指定时按 cut-off 走,并在回答里写明。
4. **先读活动名称和参考流再用。** `fit: low` 或检索状态 `partial` 表示相关但不精确 —— 引用前跟用户确认。
5. **地域用代理时必须声明。** 写清用了什么代理什么、哪些差异未修正,不要让代理悄悄变成事实。

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
| 材料名 → 数据集 key | *(无,走 REST)* | `search "<原话>" --sources Ecoinvent` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 队列 GWP 分布 / 百分位定位 | `aggregate_datasets` | `aggregate --source ecoinvent [--target N]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source ecoinvent` |
| 单数据集工序级热点 | `process_hotspot` | `hotspot <key>` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递。它编码了源 + 版本 + 系统模型 —— 版本升级后旧 key 会出现在 `missing_keys` 里,**重新检索,不要手改**。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 服务端给的匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 活动名、参考流、地域 | 引用前必读,这是区分候选的依据 |
| `restricted: true` | 无 ecoinvent 数据包权益 | 给 `purchase_url`,可提供免费库替代并说明 |
| `comparability_note` | 队列可比性说明 | 做对比前必读 |
| `entitlement` | 聚合为空是权益问题,不是谓词问题 | 不要换谓词重试 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

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
| `restricted: true` | 无 ecoinvent 数据包权益 | 给 `purchase_url`;**绝不静默替换数值** |
| 聚合 `status: "empty"` **且带** `entitlement` | 同上 | 不是谓词问题,不要重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | ecoinvent 队列传 `--source ecoinvent` |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索,不要手改 key |
| 队列跨多个数量级 | 功能单位混杂 | 收窄谓词,先读 `comparability_note` |
| 检索耗时 30 秒 | 正常 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
