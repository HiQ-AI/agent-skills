---
name: pcf
description: '做产品碳足迹(PCF)核算时取真实的清单数据。从 BOM 物料清单出发,逐行匹配生命周期清单数据集、取 GWP、合计到产品层,并把每一项的数据库、版本、系统模型、地域、参考流交代清楚。覆盖 18 个 LCI 数据库与 24000+ 已发布 EPD,支持行业分布定位判断结果是否合理。当任务涉及产品碳足迹、PCF 核算、ISO 14067、BOM 碳排、物料清单碳核算、单位产品碳排放、生态设计选材对比时使用。触发词:PCF、产品碳足迹、ISO 14067、BOM、物料清单、碳核算、单位产品碳排、carbon footprint of products、cradle-to-gate。'
slug: pcf
displayName: 产品碳足迹(PCF)核算取数
version: 1.1.0
summary: 从 BOM 出发做产品碳足迹核算:逐行匹配清单数据集、取 GWP、合计到产品层,每一项都可追溯到库、版本、系统模型与地域。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/agent-skills
tags: [PCF, 产品碳足迹, ISO 14067, BOM, 物料清单, 碳核算, LCA, 排放因子, 生命周期评价, GWP]
---

# 产品碳足迹(PCF)核算取数

产品碳足迹的工作量不在加法,在**逐行匹配**:BOM 上写的是「钻头」「废外壳(钢壳,软包)」「框架蒸压加气混凝土砌块外墙 200厚」,清单数据库里只有工艺过程。这一步匹配错了,后面的合计再精确也没有意义。

本技能负责把 BOM 行接到真实数据集上,并保证每一项都可追溯。

## 关于

本技能接入 **HiQ Cortex** —— [海科数据](https://www.hiqlcd.com/)的 LCA 数据智能服务。海科数据是国内 LCA 基础数据与碳足迹服务提供商,自建中国本土生命周期清单数据库,并聚合 18 个国际主流数据源与 24000+ 已发布 EPD,口径遵循 ISO 14040/14044、ISO 14067 与 GB/T 24040/24044。

**BOM 行到数据集的匹配由服务端完成。** 把 BOM 上的原始描述**原样**交给检索接口 —— 工厂俗称到标准名的翻译、制成品到材质的还原、括号里补充说明的拆解、物料类别到工艺方向(生产 / 处理)的映射,都在服务端执行。返回的候选已排序并带 `fit` 匹配质量与 `summary` 说明。

不要在本地先把 BOM 名称「翻译」一遍再去搜 —— 那会丢掉原始信息,反而降低命中率。原话交给它。

## 数据权限

| 层 | 内容 | 要求 |
|---|---|---|
| 目录层 | 各库的版本、系统模型、LCIA 覆盖;数据集名称、参考流、单位、地域 | 有效凭据即可 |
| 免费库数值 | BAFU、ELCD、EF、USLCI、USDA、worldsteel、AusLCI 等的 GWP 与聚合 | 任一有效凭据 |
| 商业库数值 | ecoinvent、HiQLCD、HiQLCD-AL、CALCD(汽车)、CarbonMinds、Agri-footprint | 需对应数据包权益 |

一份 BOM 里通常几种情况混着:部分物料免费库就能覆盖,部分要商业库。**受限项如实标注,不要用免费库的值悄悄顶上去** —— 一份混了口径又没标注的 BOM 核算表,后面没人能复核。

## 硬规则

1. **每个数值都来自本次会话的工具调用。** 一行都不能凭记忆填。
2. **每一行都要交代基准**:数据库 + 版本 + 系统模型 + 地域 + 参考流。BOM 核算表要能逐行追溯。
3. **合计前先确认口径一致。** 系统模型不同的数据不能相加;功能单位不一致要先换算,换算依据要写出来。
4. **单位要对齐。** 数据集的参考单位(kg / m³ / kWh / tkm)与 BOM 的用量单位不一致时,先做单位换算并说明换算系数来源。密度、堆积密度这类换算参数如果是假设值,必须标注为假设。
5. **代理数据单独标注**,不要混进直取行。
6. **受限不是错误**,给 `purchase_url`,不静默替代。

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

宿主支持 MCP 时优先用 MCP —— 若当前会话已有 `lookup_datasets`、`aggregate_datasets` 等工具就直接用;没有则把 `https://x.hiqlcd.com/api/cortex/mcp` 配进宿主的 MCP 配置(header 用 `X-API-Key`,或用扫码登录凭据的 `Authorization: Bearer`),配置方式见 [README](https://github.com/HiQ-AI/agent-skills)。

凭据只从环境变量、宿主配置或 `login` 落盘的那份读取 —— **绝不硬编码进为用户生成的文件,也不在输出里回显**。

## 工具

| 需求 | MCP 工具 | CLI 命令 |
|---|---|---|
| BOM 行 → 数据集 key | *(无,走 REST)* | `hiq-cortex search "<BOM 原话>" [--sources X]` |
| key → GWP + 基准 | `lookup_datasets` | `hiq-cortex lookup-datasets --dataset-keys <key[,key…]>` |
| 结果是否合理(同类分布定位) | `aggregate_datasets` | `hiq-cortex aggregate-datasets --where '{"sources":["X"]}' --target-value <你的合计>` |
| 非 GWP 的 LCIA 指标 | `aggregate_indicators` | `hiq-cortex aggregate-indicators --dataset-keys <keys> --indicator AP --source X` |
| 找减排点(工序级热点) | `process_hotspot` | `hiq-cortex process-hotspot --dataset-key <key>` |
| 同类已发布 EPD 参照 | `epd_search` / `epd_peer_benchmark` | `epd` / `epd-benchmark` |

**批量 lookup**:BOM 有几十行时,一次调用传入全部 key,不要逐行调。

检索是 REST 接口(`POST https://x.hiqlcd.com/api/cortex/search`,SSE 返回,解析 `WorkflowCompleted` 事件的 `content`),**每次 20–40 秒**。BOM 行数多时这是主要耗时 —— 提前告诉用户,不要并发轰接口。

## 怎么读返回

| 字段 | 含义 | 该怎么做 |
|---|---|---|
| `summary` | 服务端对本次检索的说明 | 转述,不要另编一套 |
| `fit: high / medium / low` | 匹配质量 | `low` 的行单独列出来让用户确认,不要混进合计 |
| `name` / `ref_product` / `location` | 数据集名、参考流、地域 | 引用前必读 |
| `restricted: true` | 无该库权益 | 该行标注受限,给 `purchase_url` |
| `comparability_note` | 队列可比性说明 | 合计或对比前必读 |
| `missing_keys` | key 来自旧版本目录 | 重新检索 |

## 输出形态

产品碳足迹的输出是一张可复核的表,不是一个数:

- **逐行**:物料名 → 匹配到的数据集(名称 + 参考流 + 地域)→ 单位用量 → 因子 → 小计 → 数据来源(库 + 版本 + 系统模型)
- **分组小计**:原材料 / 能源 / 运输 / 废弃物,便于看结构
- **单列出来**:`fit: low` 的行、代理数据行、受限未取到值的行
- **合计**:并说明边界(cradle-to-gate 还是 cradle-to-grave)、口径、以及哪些项未纳入

用户只要一个数时也要给基准和边界 —— 一个没有边界说明的产品碳足迹数字不能用。

## 什么时候该问用户

**先查、再对比、最后才问。** BOM 拿到手先跑检索,在同一轮里给出匹配结果和明确的疑问项,不要逐行追问。

必须问的通常只有三类:产地(影响电网与工艺)、材质歧义(BOM 写「塑料件」但没说是 PP 还是 ABS)、边界(算到出厂还是算到报废)。这三类可以一次性问齐,不要挤牙膏。

## 语气与术语

面向 LCA 从业者写,用 ISO 14040/14044、ISO 14067、GB/T 24040 的标准术语。功能单位 · 参考流 · 系统边界 · 单元过程 · 分配 allocation · 截止规则 cut-off criteria。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| BOM 某行怎么都搜不到 | 描述里没有可识别的材质信息 | 把原话给用户,问材质,不要自己猜一个材料顶上 |
| `restricted: true` | 无该库数据包权益 | 该行标注受限,给 `purchase_url` |
| 聚合 `status: "empty"` **且带** `entitlement` | 权益问题 | 不要换谓词重试 |
| 聚合 `status: "empty"` **不带** `entitlement` | 谓词没命中 | 放宽谓词 |
| 合计结果比同行高一个数量级 | 多半是单位错配 | 逐行核对参考单位与用量单位 |
| `missing_keys` 非空 | key 来自旧版本目录 | 重新检索 |
| 检索耗时 30 秒 | 正常 | 等待,不要并发重试 |
| `401 {"code":"INT-007"}` | 用了 Bearer 或 key 无效 | 改用 `X-API-Key` |
| CDN `error 1010` | 默认 User-Agent 被拦 | 内置脚本已设;直接调用时自带常规 User-Agent |
