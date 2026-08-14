# 技能图标

SkillHub 的图标**不能通过 CLI 设置**(`skillhub publish` 的 payload 只有 slug / version /
displayName / summary / description / tags / license / homepage / changelog),只能在
网页后台逐个上传。

## 设计

统一用品牌小蜗牛,靠**颜色**区分技能 —— 列表里图标只有 20–30px,文字会糊,颜色是这个
尺寸下唯一可靠的区分手段;形状保持一致,16 个技能视觉上仍是一家人。

256×256,透明底,内容居中留 14% 边距。

| slug | 色值 | 说明 |
|---|---|---|
| `hiq-cortex-lca` | `#E27E0B` | 主入口 · 品牌橙(不变) |
| `lca` | `#2E7D32` | 绿 |
| `ecoinvent` | — | **用 ecoinvent 官方 logo**(我方为中国独家代理) |
| `hiqlcd` | `#C62828` | 中国红 |
| `hiqlcd-al` | `#546E7A` | 铝灰 |
| `calcd` | `#1565C0` | 汽车蓝 |
| `carbonminds` | `#6A1B9A` | 化学紫 |
| `cbam` | `#D84315` | 橙红 |
| `en15804` | `#795548` | 建材棕 |
| `iso14067` | `#00838F` | 青 |
| `ghg-protocol` | `#37474F` | 深蓝灰 |
| `pef` | `#3949AB` | 靛蓝 |
| `pcf` | `#F9A825` | 金黄 |
| `scope3` | `#AD1457` | 品红 |
| `battery-passport` | `#689F38` | 黄绿 |

## 第三方数据库的 logo

用别家数据库的官方 logo 需要有代理 / 授权关系,否则既越界也会让用户误以为技能是对方
官方出品。已确认可用的:**ecoinvent**(中国独家代理)。CarbonMinds、Agri-footprint
等其余第三方库在确认授权前一律用色板方案。

## 重新生成

```bash
python3 scripts/gen-icons.py      # 改色值后重跑,会覆盖 assets/icons/*.png
```
