---
name: pef
description: '按欧盟产品环境足迹(PEF / OEF)口径取清单数据与多指标结果。PEF 要求用 Environmental Footprint 参考包的数据与特征化方法,并报告一整套环境影响类别而不只是碳。本技能负责数据获取:用 EF 参考包及其他清单库检索匹配数据集、取 GWP 与酸化富营养化等 LCIA 指标、做同类分布定位,并把库、版本、系统模型、地域逐项交代清楚。当任务涉及 PEF、OEF、产品环境足迹、EF 参考包、欧盟环境足迹、PEFCR、多指标环境评价时使用。触发词:PEF、OEF、产品环境足迹、Environmental Footprint、EF 3.1、PEFCR、欧盟环境足迹、多指标评价、LCIA。'
slug: pef
displayName: 产品环境足迹 PEF 数据与多指标评价
version: 1.3.0
summary: 按 PEF/OEF 口径取数:EF 参考包数据集、GWP 与多项 LCIA 指标、同类分布定位,库与口径逐项交代。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [PEF, OEF, 产品环境足迹, Environmental Footprint, EF, LCIA, 多指标评价, LCA, 碳足迹, 排放因子]
---

# PEF 欧盟产品环境足迹数据与指标

PEF 和一般的碳足迹不是一回事:它要求一整套环境影响类别一起报,而且对用哪套数据、哪套特征化方法有明确要求。只报一个 GWP 交不了差。

本技能负责 PEF 的数据侧 —— 用 EF 参考包及其他清单库取数,并把多指标结果一并拿全。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

**EF(Environmental Footprint)参考包免费开放**,任一有效凭据即可取数值 —— 这是 PEF 语境下的基准数据源。需要更细的工艺级数据时可再看 ecoinvent、CarbonMinds 等商业库,国内生产场景可看本土清单。

**检索与候选排序在服务端完成。** 把物料或工艺的原话交给检索接口,翻译与匹配在服务端执行,返回带 `fit` 匹配质量与 `summary` 说明。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| **EF 参考包数值** | GWP 与聚合统计 | **任一有效凭据,无需数据包** |
| 其他免费库 | BAFU、ELCD、USLCI、USDA、worldsteel、AusLCI 等 | 任一有效凭据 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 不凭记忆给 LCIA 值。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。
3. **多指标一起报,不要只挑碳。** PEF 的意义就在于看见指标之间的权衡 —— 碳降了水耗升了这种情况必须指出来。
4. **一次一个指标查询。** `indicators` 的 `--source` 必须与队列实际所在库一致,特征化方法跨库不通用。
5. **不要把多指标加权成单一分数。** 加权涉及价值判断,由用户和 PEFCR 决定,不是取数环节该替他做的。
6. **口径不一致不做对比。** 先读 `comparability_note`。
7. **受限不是错误**,给 `purchase_url`,不静默替代。

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

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_indicators` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | CLI 命令 |
|---|---|---|
| 物料 / 工艺 → 数据集 key | *(无,走 REST)* | `hiq-cortex search "<原话>" --sources EF` |
| key → GWP + 基准 | `lookup_datasets` | `hiq-cortex lookup-datasets --dataset-keys <key[,key…]>` |
| **多项 LCIA 指标** | `aggregate_indicators` | `hiq-cortex aggregate-indicators --dataset-keys <keys> --indicator AP --source ef` |
| 队列分布 / 百分位定位 | `aggregate_datasets` | `hiq-cortex aggregate-datasets --where '{"sources":["ef"]}' [--target-value N]` |
| 工序级热点 | `process_hotspot` | `hiq-cortex process-hotspot --dataset-key <key>` |
| 已发布 EPD 参照 | `epd_search` / `epd_peer_benchmark` | `epd` / `epd-benchmark` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 引用前先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库权益 | 给 `purchase_url` |
| `comparability_note` | 队列可比性说明 | 对比前必读 |
| `indicators` 返回空 | 该库可能没有 LCIA 层,或 `--source` 不对 | 先确认库的指标覆盖 |

## 输出形态

多指标结果排成表:一列一个影响类别,注明各自的特征化方法来源与所在库。指标之间出现权衡时明确写出来,并说明是哪个环节造成的(可用 `process_hotspot` 定位)。

不要用一个"综合环境得分"代替这张表。

## 语气与术语

面向 LCA 从业者写,用 PEF 方法学、ISO 14040/14044、ILCD 的标准术语。影响类别 impact category · 类别指标 category indicator · 特征化因子 characterization factor · 参考流 reference flow · 功能单位 functional unit。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要替用户判定 PEFCR 适用性与符合性。** 用哪份 PEFCR、是否满足要求、由谁验证,由用户和验证方确定。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `indicators` 返回空 | `--source` 必须等于队列所在库,或该库没有 LCIA 层 | 传正确的 `--source`;先看指标覆盖 |
| EF 库里找不到某物料 | EF 参考包覆盖有限 | 换其他库检索,并说明这不是 EF 数据 |
| `restricted: true` | 用了商业库且无权益 | 给 `purchase_url`;EF 部分不受影响 |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| 队列跨多个数量级 | 功能单位混杂 | 收窄谓词,先读 `comparability_note` |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
