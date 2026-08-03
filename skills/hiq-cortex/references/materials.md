# 材料族参考

用于**判断检索方向**和**识别歧义**的领域知识。

本文件**不含任何可引用的数值**,只说明「要区分什么、该怎么检索、什么时候必须澄清」。**所有数值一律来自工具调用** —— 这正是本技能存在的理由:排放因子随数据库、版本、系统模型、路线、地域变化,没有可以背下来的通用值。

文中出现的倍数关系(如「原生铝与再生铝相差 4–10 倍」)用于说明为什么必须区分路线,不能据此推算具体数值。

检索词保留英文,因为数据库里的过程名以英文为主(HiQLCD 为中英双语,中文词命中率往往更高)。

## 钢

| 用户会说 | 行业术语 | 工艺含义 | 检索词  |
|---|---|---|--- |
| 长流程 / 转炉钢 | BF-BOF | 铁矿石 → 高炉 → 转炉 → 粗钢 | `blast furnace, basic oxygen furnace`  |
| 短流程 / 电炉钢 | EAF | 废钢 → 电弧炉 → 粗钢 | `electric arc furnace, steel scrap`  |
| 半长流程 | DRI+EAF | 天然气直接还原 + 电炉 | `direct reduced iron, electric arc furnace`  |
| 绿钢 / 氢冶金 | H-DRI+EAF | 绿氢还原 + 电炉 | `hydrogen-based DRI, green steel`  |
| 热轧卷 / 板 / 型材 | — | 粗钢 → 再加热 → 轧制 | `hot rolling, steel coil/sheet/plate`  |
| 冷轧板 / 带 | — | 热轧 → 酸洗 → 冷轧 | `cold rolling, steel sheet`  |
| 镀锌板(热镀 / 电镀) | — | 冷轧板 → 锌层 | `galvanized steel, zinc coating`  |
| 螺纹钢 / 建筑钢筋 | — | 长流程 → 热轧棒材 | `reinforcing steel, steel rebar`  |
| 不锈钢 | 304 / 316 / 430 | 电炉 + AOD 精炼 | `stainless steel, chromium steel 18/8`  |
| 球团 / 烧结矿 | 炼铁原料 | 造球 / 烧结 | `iron ore pellet / sinter`  |

中国约 90% 钢产量为长流程。用户未指明时按 BF-BOF 处理,并说明这一假设。

## 铝

| 用户会说 | 工艺含义 | 检索词  |
|---|---|--- |
| 原生铝 / 电解铝 | 氧化铝 → 电解 | `primary aluminium, electrolysis`  |
| 再生铝 | 废铝 → 重熔 | `secondary aluminium, scrap`  |
| 铝型材 / 挤压 | 挤压成型 | `aluminium extrusion, profile`  |
| 铝板 / 铝卷 | 轧制 | `aluminium sheet, rolling`  |
| 铝箔 | 极薄轧制(6–200 μm) | `aluminium foil`  |
| 压铸铝 | ADC12 等铸造合金 | `aluminium die casting`  |

原生与再生相差 4–10 倍。用户只说「铝」时**必须澄清**,或至少两条都给出来做对比。

## 塑料

| 用户会说 | 还需区分 | 检索词  |
|---|---|--- |
| PE / 聚乙烯 | HDPE / LDPE / LLDPE | `polyethylene, high/low density`  |
| PP / 聚丙烯 | — | `polypropylene, granulate`  |
| PVC | 硬质(管材)/ 软质(薄膜) | `PVC suspension / PVC emulsion`  |
| PET | 瓶级 / 纤维级 | `PET bottle grade / PET fibre`  |
| ABS | — | `acrylonitrile butadiene styrene`  |
| PC / 聚碳酸酯 | — | `polycarbonate`  |
| PA / 尼龙 | PA6 / PA66 | `polyamide 6 / polyamide 6.6`  |
| 玻纤增强 | 基材树脂 + 玻纤比例 | `glass fibre reinforced` + 基材  |
| 再生塑料 | 具体是哪种树脂 | `recycled` + 具体树脂  |

用户只说「塑料」必须问是哪种树脂;给了具体牌号(PP / ABS 等)直接检索。

## 化学品

| 用户会说 | 歧义点 | 关键区分 |
|---|---|---|
| 烧碱 / NaOH | 与氯气联产,分配方法影响极大 | 离子膜法 / 隔膜法;分配基准 |
| 乙醇 | 石化路线与发酵路线差 2–3 倍 | 合成 / 生物基 |
| 氢气 | 灰氢 / 蓝氢 / 绿氢差 5–10 倍 | 天然气重整 / 电解 |
| 合成氨 | 天然气路线与绿氨差 3–5 倍 | 传统 / 绿氨 |
| 「助剂」「添加剂」 | 可能是任何东西 | 必须问具体化学品名或 CAS 号 |

## 能源

| 用户会说 | 检索词 | 关键变量 |
|---|---|---|
| 电 / 电网电力 | `electricity, grid mix` | **地域** |
| 绿电 | `electricity, wind/solar/hydro` | 具体可再生类型 |
| 蒸汽 | `steam, [压力], from [燃料]` | 压力等级 + 燃料 |
| 天然气(燃烧) | `natural gas, burned in` | 直接燃烧 |
| 天然气(原料) | `natural gas, at plant` | 上游开采 |
| 柴油(燃烧) | `diesel, burned in` | 直接燃烧 |

## 运输

| 用户会说 | 必须区分 | 检索词 |
|---|---|---|
| 运输 / 物流 | 运输方式必须明确 | — 先问 — |
| 海运 | 集装箱 / 散货 | `container ship / bulk carrier` |
| 公路运输 | 车辆吨位 | `lorry, 16-32t / 3.5-7.5t` |
| 铁路 | 电力 / 内燃 | `freight train, electric/diesel` |
| 空运 | 腹舱 / 全货机 | `air freight, long-haul` |

## 地域敏感性

| 敏感度 | 材料 | 处理 |
|---|---|---|
| 极高 | 电力、电解铝 | **必须澄清地域** |
| 高 | 钢、水泥 | 建议澄清 |
| 中 | 玻璃、纸 | 可选 |
| 低 | 通用塑料、基础化学品 | 跳过,用 GLO 即可 |

可供选择的常见地域:中国 CN · 全球平均 GLO · 欧洲 RER · 无偏好

## 常见单位错配

| 用户预期的单位 | 数据库的单位 | 换算需要 |
|---|---|---|
| 每米(管材) | 每 kg | 线密度 kg/m |
| 每平方米(板材) | 每 kg | 面密度 = 厚度 × 密度 |
| 每件 | 每 kg | 单件重量 |
| 每 kWh(电池) | 每 kg | 能量密度 kWh/kg |
| 每 tkm | 每 kg·km | 1 tkm = 1000 kg·km |
| 每升(液体) | 每 kg | 密度 |

按数据库的原生单位(通常是每 kg)检索,再告诉用户需要什么换算系数。

## 产品拆解参考

用户给的是产品名时,先想清楚组成再决定检索什么。

- **排水管** —— PVC 本体 90–95% + 碳酸钙填料 3–5% + 稳定剂 2–3%。Ecoinvent 有完整的 PVC 管材挤出数据集,可直接用。
- **电缆** —— 铜导体 + XLPE/PVC 绝缘 + 钢铠装 + PVC 护套,四种材料分别检索。
- **瓦楞纸箱** —— 面纸 55–65% + 瓦楞芯纸 35–45%。Ecoinvent 有瓦楞纸板的聚合数据集。
- **饲料** —— 玉米约 60% + 豆粕约 25% + 麦麸约 10% + 预混料约 5%。通常没有专用数据集,按组成用原料构建代理。
- **锂电池包** —— 正极(NMC / LFP)+ 石墨负极 + 电解液 + 铜箔铝箔 + 壳体。先确认电芯体系。
- **光伏组件** —— 玻璃 65–70% + 硅片 + EVA + 铝边框。Ecoinvent 有组件级聚合数据集。
- **LED 灯泡** —— 铝散热器 + PC 灯罩 + PCB 驱动 + LED 芯片,按部件分别检索。
- **纯棉 T 恤** —— 棉纤维 85–92% + 涤纶缝纫线 + 染整化学品。湿处理占足迹的 30–50%。

不确定某产品如何拆解时,先查资料确认组成,不要凭空假设。
