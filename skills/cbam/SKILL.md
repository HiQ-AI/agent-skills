---
name: cbam
description: '为 CBAM(欧盟碳边境调节机制)申报取真实的生命周期清单数据。CBAM 覆盖钢铁、铝、水泥、化肥、电力、氢六个品类,申报要求逐项交代内含排放的数据来源与口径,不能凭经验值填报。本技能负责按品类检索对应的清单数据集、取 GWP 与基准、做同类分布定位,并把数据库、版本、系统模型、地域、参考流一并交代清楚,供申报文件追溯。当任务涉及 CBAM 申报、碳边境、碳关税、内含排放数据准备、出口欧盟的产品碳数据、钢铁铝水泥化肥电力氢的排放因子时使用。触发词:CBAM、碳边境调节机制、碳关税、内含排放、embedded emissions、出口欧盟、申报、钢铁、铝、水泥、化肥、氢。'
slug: cbam
displayName: 碳边境调节机制 CBAM 申报数据准备
version: 1.1.1
summary: 为 CBAM 申报取真实清单数据:按品类检索数据集、取 GWP 与基准、做同类分布定位,每个数值都可追溯到库、版本、系统模型与地域。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [CBAM, 碳关税, 碳边境, 内含排放, LCA, 碳足迹, 排放因子, 钢铁, 铝, 生命周期评价]
---

# CBAM 碳边境调节机制数据准备

CBAM 申报的核心不是算得快,是**每个数字都得说得清来源**。申报文件要经得起追溯:这个值来自哪个数据库、哪个版本、什么系统模型、什么地域、参考流是什么。凭经验值或文献均值填报,在核查环节站不住。

本技能负责把取数这一步做扎实 —— 检索、取值、交代基准、同类定位。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD。

对 CBAM 的六个品类,数据可及性差别很大:

| 品类 | 可用来源 |
|---|---|
| 钢铁 | worldsteel(免费)、中国本土清单、ecoinvent |
| 铝 | HiQLCD-AL 铝产业链专库、ecoinvent |
| 水泥 | 各国清单库 + 已发布 EPD |
| 化肥 | Agri-footprint、各国清单库 |
| 电力 | 按地域取,免费库覆盖较好 |
| 氢 | 按制取路线区分,清单库 + EPD |

**检索与选型判断在服务端完成。** 把产品描述或 BOM 行原话交给检索接口 —— 术语翻译、路线判别、候选排序都在服务端执行,返回带 `fit` 匹配质量和 `summary` 说明。

## 数据权限 —— 先说清楚

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 免费库数值 | worldsteel、BAFU、ELCD、EF、USLCI、USDA 等的 GWP 与聚合 | 任一有效凭据 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

**钢铁与电力用免费库就能拿到数值**;铝、化肥、水泥的高精度数据多在商业库。无权益时返回 `restricted: true` + `purchase_url`,如实告诉用户是哪个库受限。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 申报数据不能凭记忆 —— 记忆里的数没有来源、年份和口径,填进申报文件就是风险。
2. **每个数值都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。申报要追溯,这不是可选项。
3. **产地必须落实。** CBAM 关心的是实际生产地的排放,不是全球平均。产地明确时不要用 GLO 或欧洲平均顶替;只能用代理时明确声明代理关系与未修正的差异。
4. **口径不一致不做对比,也不做合计。** 系统模型或系统边界不同的数据不能相加,先读 `comparability_note`。
5. **受限不是错误。** 无权益时如实展示并给开通链接,**绝不用其他库或文献的值静默替代** —— 那会让整份申报的可追溯性归零。

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
| 产品 / 物料 → 数据集 key | *(无,走 REST)* | `search "<原话>" [--sources X]` |
| key → GWP + 基准 | `lookup_datasets` | `lookup <key> [<key> ...]` |
| 同品类分布、自有数值定位 | `aggregate_datasets` | `aggregate --source X --target <你的值>` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `indicators <keys> --indicator AP --source X` |
| 工序级热点(找减排点) | `process_hotspot` | `hotspot <key>` |
| 同类已发布 EPD | `epd_search` / `epd_peer_benchmark` | `epd` / `epd-benchmark` |

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`)。**耗时 20–40 秒属正常**,不要并发重试。

`dataset_key` 是不透明句柄,原样传递;版本升级后旧 key 进 `missing_keys`,重新检索。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 不要直接填进申报,先确认 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读,申报文件里要写 |
| `restricted: true` | 无该库权益 | 给 `purchase_url`,不静默替代 |
| `comparability_note` | 队列可比性说明 | 对比或合计前必读 |
| `entitlement` | 聚合为空是权益问题 | 不要换谓词重试 |

## 输出形态

CBAM 场景的输出通常要进申报表格或说明文件,所以:

- **逐项列出**,一行一个物料 / 工序,每行带数值 + 单位 + 数据库 + 版本 + 系统模型 + 地域 + 参考流。
- **代理数据单独标注**,不要混在实测或数据库直取的行里。
- **受限项如实留空并注明原因**,不要用估值填坑。
- 用户要合计时,先确认各项口径一致再合计;不一致就说明并拒绝直接相加。

## 语气与术语

面向 LCA 与合规从业者写,用 ISO 14040/14044、GB/T 24040 的标准术语。不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

**不要对法规义务下判断。** 本技能负责取数与口径,申报义务、缺省值适用条件、核查要求这些应由用户的合规顾问确认 —— 需要时明确说明这一点,不要替用户拍板。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| `restricted: true` | 无该库数据包权益 | 给 `purchase_url`;可用免费库替代但要说明 |
| 聚合 `status: "empty"` **且带** `entitlement` | 同上 | 不是谓词问题,不要重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| `indicators` 返回空 | `--source` 必须等于队列所在库 | 传入正确的 `--source` |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| 检索耗时 30 秒 | 正常 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
