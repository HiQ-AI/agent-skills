---
name: hiq-cortex
description: '查询真实的 LCA 排放因子与碳足迹数据,覆盖 18 个生命周期清单数据库(Ecoinvent、BAFU、USLCI、ELCD、EF、worldsteel、AusLCI、HiQLCD 等)和 24000+ 已发布 EPD。当任务需要真实排放因子而不是凭记忆给数时使用:物料 GWP 查询、产品碳足迹、BOM 碳核算、行业对标与百分位定位、生产路线对比(转炉钢与电炉钢、原生铝与再生铝、灰氢与绿氢)、EPD 同类审核、CBAM 与 EN 15804 相关工作。触发词:碳足迹、排放因子、清单数据、物料清单、行业对标、碳排、GWP、kg CO2e、emission factor、carbon footprint、LCA dataset、LCI、EPD。'
slug: hiq-cortex
displayName: HiQ Cortex — LCA 数据查询
version: 1.6.0
summary: 从 18 个 LCA 数据库和 24000+ 已发布 EPD 查询真实排放因子。物料碳足迹、BOM 碳核算、行业对标定位、生产路线对比、EPD 同类审核。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags:
  - LCA
  - 碳足迹
  - 排放因子
  - 数据分析
  - EPD
  - CBAM
---

# HiQ Cortex — LCA 数据查询

碳足迹的答案必须来自真实清单数据。凭记忆给出的「钢材大约 2 kg CO₂e/kg」对 LCA 从业者没有用:真实值取决于数据库、版本、系统模型、生产路线和地域,在这些维度上会差出数倍。

本技能接入 HiQ Cortex —— 18 个 LCA 数据库(11 个免费、7 个商业)和 24000+ 已发布 EPD。

## 硬规则

1. **每个数值都必须来自本次会话的工具调用**。绝不凭记忆给出 GWP、LCIA 值或分布。工具不可用时如实说明,不要用记忆填补。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考单位。`0.0269 kg CO₂e/kWh(BAFU 2025,DEFAULT,CH,低压电网)` 可用;单独一个 `0.027` 不可用。
3. **受限不是错误**。商业数据库在账号无对应数据包权益时返回受限标记和 `purchase_url`。如实展示、把链接给用户,**绝不用其他数据库或文献的值静默替代**。重试无用。可以改用免费库,但必须说明这是替代。
4. **口径不一致就不做对比**。功能单位、系统模型(截止法 / 后果法 / APOS / EN 15804)、系统边界不同的数据不可比 —— 直接说明,不要给出误导性的差值。

## 接入方式

有两条路。**回答前先确认当前可用的是哪一条**,并在另一条更合适时主动帮用户配置。

### 方式一:MCP(宿主支持时优先)

如果当前会话已有 `lookup_datasets`、`aggregate_datasets`、`epd_search` 这些工具,直接使用,跳到[工具](#工具)一节。

如果没有,可以帮用户配置 —— 把下面内容写入宿主的 MCP 配置文件:

```json
{
  "mcpServers": {
    "cortex": {
      "type": "http",
      "url": "https://x.hiqlcd.com/api/cortex/mcp",
      "headers": {
        "X-API-Key": "sk_xxx"
      }
    }
  }
}
```

| 宿主 | 配置文件 |
|---|---|
| WorkBuddy | `~/.workbuddy/mcp.json`(用户级)或 `<项目>/.workbuddy/mcp.json` |
| Claude Code | `~/.claude.json` 或 `<项目>/.mcp.json` |
| Cursor | `~/.cursor/mcp.json` 或 `<项目>/.cursor/mcp.json` |
| Cline 等 | 该宿主的 MCP 设置文件 |

⚠️ **只支持 `X-API-Key` 这一个 header**。网关会拒绝 `Authorization: Bearer`(返回 `401 {"code":"INT-007"}`)。多数客户端示例默认写 Bearer,务必改掉。配置后宿主通常需要重启才能加载。

### 方式二:内置脚本(任何环境可用,零配置)

宿主不支持 MCP,或用户不愿改配置文件时用这条。仅依赖 Python 标准库,无需 `pip install`:

```bash
export HIQ_API_KEY=sk_xxx
python3 scripts/cortex.py search "304 不锈钢"
```

### 获取 API key

在 [hiqlcd.com](https://www.hiqlcd.com/) 注册账号,在控制台创建 API key。两种方式共用同一把 key。限流 100 次/分钟。

**绝不要把 key 硬编码进为用户生成的文件** —— 只走环境变量或宿主的配置文件。

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 材料名 → 数据集 key | *(无,见下)* | `search "<关键词>" [--sources X]` |
| key → GWP、基准、链接 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 队列 → GWP 分布、百分位定位 | `aggregate_datasets` | `aggregate --source X [--target N]` |
| 队列 → 非 GWP 的 LCIA 指标(AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| 单个数据集 → 工序级热点 | `process_hotspot` | `hotspot <key>` |
| 已发布 EPD 检索 | `epd_search` | `epd "<关键词>" [--unit m3]` |
| EPD 同类分布、离群判定 | `epd_peer_benchmark` | `epd-benchmark "<品类>" --unit m3` |

脚本命令加 `--json` 可输出原始 payload。

**检索没有对应的 MCP 工具** —— 数据集 key 来自一个 REST 接口,脚本已封装。直接调用:

```bash
curl -sN -X POST https://x.hiqlcd.com/api/cortex/search \
  -H "X-API-Key: sk_xxx" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=304 stainless steel&sources=BAFU,Ecoinvent"
```

返回是 SSE —— 解析 `WorkflowCompleted` 事件,再对其 `content` 字段做 JSON 解码。**耗时 20–40 秒**(要检索并校验),属正常,不是卡死,不要并发重试。

key 是不透明句柄,原样传递,绝不自行拼接或修改。

## 核心流程

1. **检索**材料、产品或工艺 → 得到候选 key。路线敏感的材料(铝、钢、氢、塑料)先看 [references/materials.md](references/materials.md) 决定该检索哪几个变体、以及是否需要澄清。
2. **先读候选名称再使用**。LCA 数据集很具体:「冷轧退火卷,304 不锈钢」和「中厚板,304 不锈钢」是不同产品,碳足迹不同。检索状态为 `partial` 表示相关但不精确,引用前必须核对。
3. 需要数值时**批量 lookup**,一次调用传入全部 key。
4. **给出基准**。候选之间差异显著时展示 2–3 条,并说明差异来自什么。
5. 只在请求本身支持时**推荐一条**,并说明所依据的假设。

## 什么时候该问用户

LCA 查询天然有歧义:同一个「304 不锈钢」在库里有十几条,产品形态、生产路线、地域、系统模型都不同。处理歧义的顺序是**先查、再对比、最后才问**,不是上来就问,也不是甩一堆候选让用户自己挑。

**不要问的情况**

- 当前请求、对话历史里已经能推断出来的信息 —— 用户说过「我们在江苏的工厂」,就不要再问地域。
- 还没检索就问。只要已经有一个可检索的对象(材料名、产品、工艺、BOM 行),就先检索,在同一轮里给出结果。
- 用泛泛的快捷回复代替真正的决策(「还需要我做什么吗?」)。

**先给对比,而不是先问**

用户明确表示不确定时(「原铝还是再生铝」「转炉还是电炉」「该用哪个」),这不是提问信号,是**决策支持**信号。正确做法:

1. 给出工具支撑的候选清单;
2. 在同一功能单位、同一系统模型下并列对比;
3. 说明差异来自什么(能源结构、废钢比例、分配方法、边界),以及在什么条件下结论会反转;
4. 在证据支持时给出带条件的推荐(「若为国内电网、含再生成分 30%,选 X」)。

一个完整的顾问式回答可以就此结束,不必再追问。

**确实需要问的情况**

只有当用户需要最终敲定**一个**数据集、而剩余歧义会实质改变结果时才问。此时:

- 选项要对应**已经展示过的候选**,不要凭空造选项;
- 每个选项说清它意味着什么(哪条路线、哪个地域、哪个口径);
- 用宿主提供的交互能力提问(不同宿主的工具名不同,有 `AskUserQuestion` / `AskQuestion` 之类就用,没有就直接在回复里把问题问清楚);
- 不要同时给出交互式选项和一份重复的文字选项清单。

用户回答后,直接在已有检索结果上完成匹配 —— 不要重跑一遍同样的检索。

## 场景路由

先路由,自上而下,首个匹配生效。路由错会浪费整轮 —— 用户问「我这个算高还是低」,给单点查询就答非所问。

| 信号 | 做法 |
|---|---|
| 用户给出**自己的**数值,问处在什么位置(「我这 2.5 算高还是低」「比同行如何」) | `aggregate` 加队列谓词 + `--target` → 百分位定位。方法与可比性闸门见 [references/scenarios.md](references/scenarios.md) |
| 还没有 BOM,想要量级或 A/B 对比(「大概什么量级」) | 按组成拆解 + 每种材料取 p25–p75 区间合成 → 给**区间**,不给虚假精度的单点值。见 [references/scenarios.md](references/scenarios.md) |
| 路线敏感材料(转炉钢与电炉钢、原生铝与再生铝、灰氢与绿氢) | 按路线分别检索、分别聚合,在同一功能单位下对比 —— 见 [references/comparability.md](references/comparability.md) |
| 有材料或 BOM 要匹配数据集 | 检索 → 批量 lookup。材料族、路线区分与产品拆解见 [references/materials.md](references/materials.md) |
| 「这个 EPD 数值合理吗」 | `epd-benchmark` 并指定 `--unit`,跨单位比较没有意义 |
| 多指标评价(酸化、富营养化等) | `indicators`,一次一个指标;`--source` 必须与队列所在库一致 |

## 数据权限

| 层级 | 内容 | 要求 |
|---|---|---|
| 目录层 | 全部 18 个库的清单、版本、系统模型、LCIA 覆盖;数据集名称、单位、地域 | 无需权益 |
| 免费库数值 | BAFU、USLCI、ELCD、EF、AusLCI、NEEDS、ozLCI、worldsteel、USDA、bioenergiedat、recycledplastics 的 GWP 与聚合统计 | 任一有效 key |
| 商业库数值 | Ecoinvent、HiQLCD、HiQLCD-AL、CarbonMinds、Agri-footprint、CALCD、HiQ-CESI 的 GWP 与聚合统计 | 需对应数据包权益 |

无权益时,`lookup` 返回 `restricted: true`,聚合返回 `status: "empty"` 并带 `entitlement` 字段,两者都含 `purchase_url`。告诉用户是哪个库受限、把链接给他;若免费库能回答同一问题,主动提供这条路径。数据包权益与订阅套餐是**两套独立体系**,升级套餐不会解锁数据库。

免费库覆盖面不小:BAFU(瑞士,LCIA 完整,欧洲语境下最好的免费默认选择)、USLCI(美国单元过程)、ELCD / EF(欧洲参考)、worldsteel(全球钢铁)、USDA(农业)。

## 参考资料

| 文件 | 内容 |
|---|---|
| [references/materials.md](references/materials.md) | 材料族:钢/铝/塑料/化学品/能源/运输的生产路线、检索词、典型区间、地域敏感性、单位错配、产品拆解 |
| [references/databases.md](references/databases.md) | 18 个库的版本、系统模型、LCIA 覆盖、选库依据、已知坑 |
| [references/comparability.md](references/comparability.md) | 可比性五维度、聚合结果的读法、生产路线对比、EPD 对比、代理数据纪律 |
| [references/scenarios.md](references/scenarios.md) | 行业对标与轻量估算的完整方法、组成代理 |

## 语气与术语

面向 LCA 从业者,像懂行的同行那样写。

- 不写客套话(「希望这对您有帮助」「让我来帮您」),不堆形容词,不做总结式收尾。
- 使用 ISO 14040/14044、ILCD、GB/T 24040 的标准术语 —— 对这个读者群,标准术语比大白话**更**清楚。
- 单元过程 unit process · 基本流 elementary flow · 中间流 intermediate flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor · 截止法 cut-off · 后果法 consequential。
- 不要自造中文术语。拿不准标准叫法时,直接用 ISO/GB 原词。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `401 {"code":"INT-007"}` | 用了 Bearer,或 key 无效 | 改用 `X-API-Key` |
| CDN 返回 `error 1010` | HTTP 客户端默认 User-Agent 被拦截 | 内置脚本已设;直接调用时自行带一个常规 `User-Agent` |
| 检索耗时 30 秒 | 正常,它要检索并校验 | 等待,不要并发重试 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索获取当前 key |
| `restricted: true` | 无数据包权益 | 给出 `purchase_url`,可提供免费库替代;**绝不静默替换数值** |
| 聚合 `status: "empty"` **且带** `entitlement` | 商业库无权益 | 同上 —— **不是**谓词问题,不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词确实没命中 | 放宽谓词 |
| `indicators` 返回空 | `source` 必须等于队列实际所在库(`method_id` 跨库不通用) | 传入正确的 `--source` |
| 队列数值跨越多个数量级 | 功能单位混杂,不是真实离散 | 收窄谓词;先读 `comparability_note` |
