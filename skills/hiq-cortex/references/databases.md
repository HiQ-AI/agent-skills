# 数据库

以下为 2026-08 快照。版本会变 —— 权威基准是 `lookup` 针对具体数据集返回的值,引用版本号时以返回结果为准,不要抄本表。

## 免费 —— 任一有效 API key 可用

| 代码 | 版本 | 系统模型 | LCIA 指标数 | 适用 |
|---|---|---|---|---|
| `bafu` | 2025 | DEFAULT | 334 | 瑞士国家清单。覆盖面广、LCIA 完整、维护良好。欧洲语境下最好的免费默认选择。 |
| `elcd` | 3.2 | DEFAULT | 294 | 欧洲参考生命周期数据库。材料、能源、运输、生命周期末端。 |
| `uslci` | 1.0 | DEFAULT | 34 | 美国单元过程 —— 燃料、运输、林业、金属。 |
| `usda` | 1.0 | DEFAULT | 63 | 美国农业与食品系统。 |
| `ef` | 3.1.0 | DEFAULT | 14 | Environmental Footprint 参考包(欧盟 PEF/OEF 语境)。 |
| `worldsteel` | 2020 | DEFAULT | 14 | 全球钢铁行业平均数据。钢铁 LCI 的参考来源。 |
| `auslci` | 1.40 | DEFAULT | 1 | 澳大利亚国家清单。仅 GWP。 |
| `needs` | 1.0 | DEFAULT | 1 | 欧洲能源情景。仅 GWP。 |
| `ozlci` | 1.0 | DEFAULT | 1 | 澳新地区数据集。仅 GWP。 |
| `bioenergiedat` | 1.0 | DEFAULT | 1 | 欧洲生物质能源。仅 GWP。 |
| `recycledplastics` | 1.0 | DEFAULT | — | 再生塑料生态档案。无 LCIA 层,仅 LCI。 |

## 商业 —— 需对应数据包权益

| 代码 | 版本 | 系统模型 | LCIA 指标数 | 适用 |
|---|---|---|---|---|
| `ecoinvent` | 3.12.0 | CUT_OFF、APOS、CONSEQUENTIAL_LONG、EN_15804 | 240 | 全球参考数据库。覆盖最广,多数已发表研究使用它。 |
| `hiqlcd` | 1.5.0 | CUT_OFF、CONSEQUENTIAL、EN_15804 | 248 | 中国本土清单。中国生产场景用这个,不要拿欧洲数据代替。 |
| `hiqlcd-al` | 2.0.0 | CUT_OFF、CONSEQUENTIAL | 359 | 铝产业链,中国为主。 |
| `calcd` | 3.0.0 | CUT_OFF | 359 | 中国生命周期基础数据库。 |
| `hiq-cesi` | 1.1.0 | CUT_OFF | 359 | 电子电器行业,中国。 |
| `carbonminds` | 2.0.2 | CUT_OFF | 231 | 化学品与塑料,工艺级细度。 |
| `agrifootprint` | 7.0 | CUT_OFF | — | 农业与食品。无 LCIA 层,仅 LCI。 |

## 怎么选库

**地域对结果的影响比多数人预期的大。** 仅电网结构一项就能让制造类数据集的 GWP 差 2–5 倍。拿欧洲数据集代表中国生产是常见且严重的错误 —— 中国优先 `hiqlcd` / `calcd` / `hiq-cesi`,欧洲用 `bafu` / `elcd` / `ef`,美国用 `uslci` / `usda`。

**系统模型必须与问题匹配。**

- `CUT_OFF` —— 归因法,再生材料不带上游负担。产品碳足迹与 EPD 的默认选择。
- `APOS` —— 替代点分配。Ecoinvent 的另一种归因模型。
- `CONSEQUENTIAL` / `CONSEQUENTIAL_LONG` —— 决策带来的边际影响。与截止法不可互换,同一次对比中绝不能混用。
- `EN_15804` —— 建材,按 EN 15804 模块结构(A1-A3、A4-A5、B、C、D)。
- `DEFAULT` —— 免费库只发布单一模型,按归因法理解。

**LCIA 覆盖差异很大。** 指标数为 1 的库只有 GWP,在这些库上用 `aggregate_indicators` 查 AP/EP/ODP 会返回空 —— 这是数据侧限制,不是工具故障。`agrifootprint` 和 `recycledplastics` 完全没有 LCIA 层(仅 LCI)。

## 已知坑

- **功能单位造成的极值通常是合法的。** 部分数据集以不寻常的功能单位声明,所以整库 GWP 的 min/max 会跨越多个数量级。判断某个值是否离群前,先读参考流和单位。
- **`aggregate_indicators` 的 `source` 必须对。** `method_id` 跨库不通用 —— Ecoinvent 的队列必须用 `source="ecoinvent"` 聚合,否则返回空。
- **版本影响 key。** `dataset_key` 编码了源 + 版本 + 系统模型。数据库版本升级后,旧目录里的 key 会出现在 `missing_keys` 里 —— 重新检索,不要手改 key。
- **检索状态 `partial`。** 表示匹配到相关但不精确的结果。使用前先读数据集 `name`:查「冷轧板」返回「热轧卷」是另一种产品。
