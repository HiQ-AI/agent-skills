---
name: en15804
description: '按 EN 15804 口径处理建材的环境产品声明(EPD)与清单数据。检索 24000+ 已发布 EPD(EPDItaly、ECO Platform、EPD Norge),按声明单位与模块取指标,做同类分布与离群判定;并可取 EN 15804 系统模型下的生命周期清单数据集。用于建材 EPD 编制与第三方审核、建筑 LCA 取数、绿色建筑评价、同类产品对标。当任务涉及 EN 15804、建材 EPD、A1-A3 等模块、声明单位、EPD 审核、建筑材料碳足迹时使用。触发词:EN 15804、EPD、环境产品声明、建材、A1-A3、模块、declared unit、声明单位、EPDItaly、ECO Platform、建筑碳排。'
slug: en15804
displayName: 建材 EPD 与 EN 15804 模块化指标
version: 1.2.0
summary: 按 EN 15804 口径检索已发布 EPD 与清单数据:按声明单位和模块取指标、做同类分布与离群判定,用于 EPD 编制、审核与建筑 LCA。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [EN 15804, EPD, 环境产品声明, 建材, 建筑碳排, LCA, 碳足迹, 生命周期评价, A1-A3, 排放因子]
---

# EN 15804 建材 EPD 与模块化指标

建材的环境数据是**按模块组织**的:A1-A3、A4-A5、B、C、D 各自代表不同的生命周期阶段,声明单位可能是 m³、m²、kg 或一个功能单元。拿 A1-A3 的值跟别人的 A1-C4 比、拿 m³ 的分布判断 kg 的数值,得到的结论没有意义。

本技能负责在正确的模块和声明单位下取数与对标。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

本技能可访问:

- **24000+ 已发布 EPD**,来自 EPDItaly、ECO Platform、EPD Norge。可按品类、声明单位、地域检索,并做同类分布(min / p25 / median / p75 / max)与离群 fences 判定。
- **EN 15804 系统模型下的清单数据集**,来自 ecoinvent、HiQLCD 等库(数值需对应数据包权益)。

**检索与匹配在服务端完成**,返回带 `summary` 说明与匹配质量标记,转述即可,不要另编一套解释。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| **已发布 EPD 检索与同类分布** | 24000+ 条 EPD 的注册号、声明单位、地域、有效期、指标值、分布与离群 fences | **有效凭据即可,无需数据包** |
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位 | 有效凭据即可 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

EPD 部分是完整可用的 —— 编制、审核、对标这些工作不需要额外权益。

## 硬规则

1. **声明单位必须指定。** 做同类分布时不给 `--unit`,拿到的是把 m³、m²、kg 混在一起的分布,没有意义。
2. **模块必须对齐。** 只在同一模块组合之间比较。引用别人的 EPD 数值时先确认对方报的是哪几个模块。
3. **D 模块不并入合计。** 边界外的收益与负担单列,把它加进 A-C 总量是建材 LCA 里最常见的错误之一。
4. **每个数值都要交代来源**:EPD 注册号 + 声明单位 + 模块 + 有效期,或数据集的库 + 版本 + 系统模型 + 地域。
5. **样本量小的分布只能作量级参考。** 返回里的 `comparability_note` 会说明 cohort 是否充分,先读它再下结论。
6. **每个数值都来自本次会话的工具调用**,不凭记忆给 EPD 值或分布。

**另外两条通用的**:

- **给了数值就给链接。** 返回里带 `link` 的,每条结果都一并给出,别等用户追问。
- **不要把 `dataset_key` / `dataset_uuid` 贴给用户看。** 那是给工具用的不透明句柄,
  对人没有意义 —— 展示的是名称、参考流、地域、库+版本+系统模型、数值、链接。
  另注:`dataset_uuid` **不是** `hiq-editor` 里的「背景数据唯一 ID」,别拿去填 `background`。

## 接入

**没有凭据时,第一句话就给扫码登录 —— 不要让用户去控制台建 API key。**

扫码是「跑一条命令 + 浏览器点一下」,无需注册;建 API key 要登录控制台、找入口、
复制粘贴、设环境变量,门槛高出一个量级。把后者摆在第一步会直接劝退用户。

```bash
npx @hiq-ai/hiq-cortex-cli login      # ← 缺凭据时默认走这条
```

命令会打印一个授权链接。**把链接原样给用户,让他点「授权访问」**,然后继续原来的任务 ——
凭据落在 `~/.hiq/credentials.json`(权限 600),之后所有命令直接可用,可见数据范围与
该账号一致(**包含他已开通的商业数据库**)。

只在这三种情况下才提 API key:用户自己说要用 key、运行在 CI / 服务端无浏览器环境、
或扫码登录失败。

```bash
export HIQ_API_KEY=sk_xxx            # 服务端 / CI 用;同时存在时优先于扫码凭据
```

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `epd_search`、`epd_peer_benchmark`、`lookup_datasets` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 找某品类的已发布 EPD | `epd_search` | `epd "<品类>" [--unit m3] [--geo IT] [--limit N]` |
| 同类分布、离群判定 | `epd_peer_benchmark` | `epd-benchmark "<品类>" --unit m3 [--indicators GWP-total] [--modules A1-A3]` |
| 建材原料 → 清单数据集 | *(无,走 REST)* | `search "<原话>"` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |

`epd_peer_benchmark` 的统计单位是**一个 EPD 注册号**,同一注册号下的多个变体只算一票 —— 分布不会被多变体声明灌水。审自己那份 EPD 时,用 `exclude_registration` 把被审的注册号从 cohort 里剔除,否则它会把分布往自己身上拉。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `registration_number` | EPD 注册号 | 引用时必须带上,这是可追溯的锚点 |
| `declared_unit` | 声明单位 | 对比前先确认一致 |
| `valid_until` | 有效期 | 过期 EPD 不能作为现行依据,要提示用户 |
| `n` / `min` / `p25` / `median` / `p75` / `max` | 同类分布 | n 太小只作量级参考 |
| 离群 fences(1.5× / 3× IQR) | 离群判定边界 | 超出 3× 的先怀疑口径而不是先怀疑产品 |
| `comparability_note` | cohort 是否充分、有哪些干扰 | **下结论前必读** |
| `summary` | 服务端说明 | 转述,不要另编 |

## 审 EPD 时的输出形态

- 先给**被审值 + 声明单位 + 模块 + 注册号**,把口径钉死。
- 再给**同类分布**(n、四分位、fences),并说明 cohort 怎么圈的、有没有剔除被审对象。
- 判定**是否离群**,并区分「数值离群」与「口径不同导致看起来离群」—— 后者更常见,先排除它。
- 结论要可复核:任何一句判断后面都跟着它依据的数与来源。

## 语气与术语

面向建材 LCA 与 EPD 从业者写,用 EN 15804、ISO 14025、ISO 14040/14044 的标准术语。声明单位 declared unit · 功能单位 functional unit · 模块 module · 产品阶段 A1-A3 · 边界外收益与负担 module D。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定合规性。** 本技能负责取数与对标,PCR 适用范围、验证要求、注册流程这些由用户的验证机构确认。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 分布跨多个数量级 | 声明单位混杂 | 指定 `--unit` 重跑 |
| `n` 很小 | 该品类已发布 EPD 少 | 如实说明只能作量级参考,不要强行下结论 |
| 找不到某品类 EPD | 品类词太窄或太宽 | 换品类词重试,或改用清单数据集路径 |
| `restricted: true`(清单数据集) | 无该库数据包权益 | 给 `purchase_url`;EPD 部分不受影响 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| 检索耗时 30 秒 | 清单检索正常耗时 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
