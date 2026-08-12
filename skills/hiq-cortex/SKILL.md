---
name: hiq-cortex
description: '查询真实的 LCA 排放因子与碳足迹数据,覆盖 18 个生命周期清单数据库(Ecoinvent、BAFU、USLCI、ELCD、EF、worldsteel、AusLCI、HiQLCD 等)和 24000+ 已发布 EPD。当任务需要真实排放因子而不是凭记忆给数时使用:物料 GWP 查询、产品碳足迹、BOM 碳核算、行业对标与百分位定位、生产路线对比(转炉钢与电炉钢、原生铝与再生铝、灰氢与绿氢)、EPD 同类审核、CBAM 与 EN 15804 相关工作。触发词:碳足迹、排放因子、清单数据、物料清单、行业对标、碳排、GWP、kg CO2e、emission factor、carbon footprint、LCA dataset、LCI、EPD。'
slug: hiq-cortex-lca
displayName: HiQ Cortex — LCA 数据查询
version: 1.8.0
summary: 从 18 个 LCA 数据库和 24000+ 已发布 EPD 查询真实排放因子。物料碳足迹、BOM 碳核算、行业对标定位、生产路线对比、EPD 同类审核。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [LCA, 碳足迹, 排放因子, EPD, CBAM, 数据分析, ecoinvent, HiQLCD, GWP, 生命周期评价, emission-factor, carbon-footprint]
---

# HiQ Cortex — LCA 数据查询

碳足迹的答案必须来自真实清单数据。凭记忆给出的「钢材大约 2 kg CO₂e/kg」对 LCA 从业者没有用:真实值取决于数据库、版本、系统模型、生产路线和地域,在这些维度上会差出数倍。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合国际主流数据源。

可访问:

- **18 个生命周期清单数据库**,其中 11 个免费。含中国本土数据(HiQLCD 覆盖中国全工业体系、CALCD、电子电器 HiQ-CESI、铝产业链 HiQLCD-AL)与国际主流库(Ecoinvent、BAFU、ELCD、EF、worldsteel、USLCI、AusLCI、CarbonMinds、Agri-footprint 等)。
- **24000+ 已发布 EPD**(EPDItaly、ECO Platform、EPD Norge),可做同类分布与离群审核。
- 遵循 ISO 14040/14044 与 GB/T 24040/24044 口径,系统模型覆盖截止法、后果法、APOS、EN 15804。

**检索由服务端完成。** 把用户的原话或 BOM 行直接交给检索接口 —— 物料名到 LCA 术语的翻译、生产路线判别、类别到工艺方向的映射都在服务端执行,返回的候选已经排过序并带匹配质量标记。不需要在本地重新推演该搜什么词。

## 隐私与安全

- API key **只从环境变量或宿主的 MCP 配置读取**,技能不会把它写进任何文件,也不会在输出中回显。
- 查询内容**仅发往 `x.hiqlcd.com`**(海科数据 API),不发往任何第三方。
- **不收集、不上传**本地文件、目录结构、对话内容或任何其他数据。
- 内置脚本仅使用 Python 标准库,无第三方依赖,源码可审阅:[GitHub](https://github.com/HiQ-AI/agent-skills)。

## 硬规则

1. **每个数值都必须来自本次会话的工具调用**。绝不凭记忆给出 GWP、LCIA 值或分布。工具不可用时如实说明,不要用记忆填补。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考单位。`0.0269 kg CO₂e/kWh(BAFU 2025,DEFAULT,CH,低压电网)` 可用;单独一个 `0.027` 不可用。
3. **受限不是错误**。商业数据库在账号无对应数据包权益时返回受限标记和 `purchase_url`。如实展示、把链接给用户,**绝不用其他数据库或文献的值静默替代**。重试无用。可以改用免费库,但必须说明这是替代。
4. **口径不一致就不做对比**。功能单位、系统模型、系统边界不同的数据不可比 —— 直接说明,不要给出误导性的差值。返回里的 `comparability_note` 就是干这个的,先读它。

## 接入

需要一份访问凭据,两条路任选:

```bash
python3 scripts/cortex.py login    # 扫码登录:浏览器点一次授权,无需注册建 key
export HIQ_API_KEY=sk_xxx          # 或用 API key(适合服务端 / CI),优先级更高
```

`login` 打开授权页,用户点一次即可,凭据存在 `~/.hiq/credentials.json`(权限 600)。可见数据范围与该账号一致,**包含他已开通的商业数据库**。`logout` 删除本机凭据。

流程本身是三个普通 HTTP 请求(标准 device flow,RFC 8628),任何能执行 shell 的 agent 都可以自己跑:

```bash
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/device_authorization \
  -H 'Content-Type: application/json' \
  -d '{"agent_id":"my-agent","agent_name":"我的助手","scope":"lca_data"}'
# 把返回的 verification_uri_complete 给用户 → 他点授权
curl -sX POST https://x.hiqlcd.com/api/cortex/oauth/token \
  -H 'Content-Type: application/json' -d '{"device_code":"..."}'   # 428 = 还没授权,继续轮询
```

宿主支持 MCP 时优先用 MCP。若当前会话已有 `lookup_datasets`、`aggregate_datasets`、`epd_search` 这些工具就直接用;没有则把下面这段配进宿主的 MCP 配置文件(WorkBuddy `~/.workbuddy/mcp.json`、Claude Code `~/.claude.json`、Cursor `~/.cursor/mcp.json`),配置后通常需重启宿主:

```json
{
  "mcpServers": {
    "cortex": {
      "type": "http",
      "url": "https://x.hiqlcd.com/api/cortex/mcp",
      "headers": { "X-API-Key": "sk_xxx" }
    }
  }
}
```

扫码登录拿到的凭据也可用,把那一行换成 `"Authorization": "Bearer <凭据>"`,二选一。

**绝不把凭据硬编码进为用户生成的文件。**

## 工具

| 需求 | MCP 工具 | 脚本命令 |
|---|---|---|
| 材料名 / BOM 行 → 数据集 key | *(无,见下)* | `search "<原话>" [--sources X]` |
| key → GWP、基准、链接 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 队列 → GWP 分布、百分位定位 | `aggregate_datasets` | `aggregate --source X [--target N]` |
| 队列 → 非 GWP 的 LCIA 指标(AP/EP/ODP/WDP/ADP) | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| 单个数据集 → 工序级热点 | `process_hotspot` | `hotspot <key>` |
| 已发布 EPD 检索 | `epd_search` | `epd "<关键词>" [--unit m3]` |
| EPD 同类分布、离群判定 | `epd_peer_benchmark` | `epd-benchmark "<品类>" --unit m3` |

脚本命令加 `--json` 输出原始 payload。

检索没有对应的 MCP 工具 —— 它是一个 REST 接口,脚本已封装。直接调用:

```bash
curl -sN -X POST https://x.hiqlcd.com/api/cortex/search \
  -H "X-API-Key: sk_xxx" -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=304 不锈钢&sources=BAFU,Ecoinvent"
```

返回是 SSE —— 解析 `WorkflowCompleted` 事件,再对其 `content` 字段做 JSON 解码。**耗时 20–40 秒**(服务端要检索并逐条校验),属正常,不是卡死,不要并发重试。

`dataset_key` 是不透明句柄,原样传递,绝不自行拼接或修改。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `status: found` / `partial` / `not_found` | `partial` = 有结果但部分受限 | 照常展示,受限项按硬规则 3 处理 |
| `summary` | 服务端对本次检索的说明 | 转述给用户,不要自己另编一套解释 |
| `fit: high / medium / low` | 服务端给出的匹配质量 | `low` 的候选引用前先跟用户确认 |
| `name` / `ref_product` / `location` | 数据集名称、参考流、地域 | 引用前先读 —— 「冷轧退火卷」和「中厚板」是不同产品 |
| `restricted: true` | 无该库数据包权益 | 给 `purchase_url`,可提供免费库替代并说明 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索,不要手改 key |
| `comparability_note` | 队列可比性说明 | 做对比前必读 |
| `entitlement` | 聚合为空是因为权益,不是谓词 | 不要换谓词重试 |

## 场景路由

自上而下,首个匹配生效。

| 信号 | 做法 |
|---|---|
| 用户给出**自己的**数值,问处在什么位置(「我这 2.5 算高还是低」) | `aggregate` 加队列谓词 + `--target` → 百分位定位 |
| 有材料或 BOM 要匹配数据集 | `search` → 批量 `lookup` |
| 要比两条生产路线(转炉钢与电炉钢、原生铝与再生铝) | 按路线分别 `search` 再分别聚合,在同一功能单位下对比 |
| 「这个 EPD 数值合理吗」 | `epd-benchmark` 并指定 `--unit`,跨单位比较没有意义 |
| 多指标评价(酸化、富营养化等) | `indicators`,一次一个指标;`--source` 必须与队列所在库一致 |

## 什么时候该问用户

**先查、再对比、最后才问。** 只要有一个可检索的对象(材料名、产品、工艺、BOM 行),就先检索,在同一轮里给出结果 —— 不要还没检索就问,也不要问对话里已经说过的信息。

用户说「不确定该用哪个」时,那是**决策支持信号,不是提问信号**:给出候选清单、在同一口径下并列、说明差异来自什么、在证据支持时给出带条件的推荐。一个完整的顾问式回答可以就此结束。

只有当需要最终敲定**一个**数据集、且剩余歧义会实质改变结果时才问。选项要对应**已经展示过的候选**,不要凭空造;用宿主提供的交互能力提问,不要同时给交互选项和一份重复的文字清单。用户回答后直接在已有结果上完成匹配,不要重跑同样的检索。

## 数据权限

| 层级 | 内容 | 要求 |
|---|---|---|
| 目录层 | 全部 18 个库的清单、版本、系统模型、LCIA 覆盖;数据集名称、单位、地域 | 无需权益 |
| 免费库数值 | BAFU、USLCI、ELCD、EF、AusLCI、NEEDS、ozLCI、worldsteel、USDA、bioenergiedat、recycledplastics 的 GWP 与聚合统计 | 任一有效 key |
| 商业库数值 | Ecoinvent、HiQLCD、HiQLCD-AL、CarbonMinds、Agri-footprint、CALCD、HiQ-CESI 的 GWP 与聚合统计 | 需对应数据包权益 |

数据包权益与订阅套餐是**两套独立体系**,升级套餐不会解锁数据库。无权益时告诉用户是哪个库受限、把 `purchase_url` 给他;若免费库能回答同一问题,主动提供这条路径并说明这是替代。

## 语气与术语

面向 LCA 从业者,像懂行的同行那样写。

- 不写客套话(「希望这对您有帮助」「让我来帮您」),不堆形容词,不做总结式收尾。
- 使用 ISO 14040/14044、ILCD、GB/T 24040 的标准术语 —— 对这个读者群,标准术语比大白话**更**清楚。
- 单元过程 unit process · 基本流 elementary flow · 参考流 reference flow · 功能单位 functional unit · 系统边界 system boundary · 影响类别 impact category · 特征化因子 characterization factor · 截止法 cut-off · 后果法 consequential。
- 不要自造中文术语。拿不准标准叫法时直接用 ISO/GB 原词。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `401 {"code":"INT-007"}` | 用了 Bearer,或 key 无效 | 改用 `X-API-Key` |
| CDN 返回 `error 1010` | HTTP 客户端默认 User-Agent 被拦截 | 内置脚本已设;直接调用时自行带一个常规 `User-Agent` |
| 检索耗时 30 秒 | 正常,服务端要检索并校验 | 等待,不要并发重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词确实没命中 | 放宽谓词 |
| `indicators` 返回空 | `source` 必须等于队列实际所在库(`method_id` 跨库不通用) | 传入正确的 `--source` |
| 队列数值跨越多个数量级 | 功能单位混杂,不是真实离散 | 收窄谓词;先读 `comparability_note` |
| 轮询授权返回 `428` | 用户还没点授权 | 正常状态,按返回的 `interval` 继续轮询 |
| 授权后仍查不到商业库 | 该账号本就没有那个数据包权益 | 扫码登录只换凭据,不改变权益;按受限提示给开通链接 |
