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
| `ecoinvent` | 白底 | **ecoinvent 官方 wordmark**(我方为中国独家代理);备选见 `_alt/` |
| `hiqlcd` | 白底 | **HiQLCD 官方字样**(自有品牌) |
| `hiqlcd-al` | 白底 | HiQLCD 字样 + 铝灰 `AL` 标记(与 `hiqlcd` 区分) |
| `calcd` | 白底 | **中汽中心 CATARC 符号**(共建方);源图分辨率偏低,大图略糊 |
| `carbonminds` | 白底 | **CarbonMinds 官方 `cm` 符号**(我方为其中国代理) |
| `cbam` | `#D84315` | 橙红 |
| `en15804` | `#795548` | 建材棕 |
| `iso14067` | `#00838F` | 青 |
| `ghg-protocol` | `#37474F` | 深蓝灰 |
| `pef` | `#3949AB` | 靛蓝 |
| `pcf` | `#F9A825` | 金黄 |
| `scope3` | `#AD1457` | 品红 |
| `battery-passport` | `#689F38` | 黄绿 |

## ecoinvent

用官方 wordmark(`Logo-Wordmark.svg`,295×47)转 256×256 方形,文字宽度占 72% ——
卡片常做**圆形裁切**,文字必须落在内切圆安全区内,否则两端会被切掉。

`_alt/` 里放了透明底与深底白字两个备选,按 SkillHub 卡片的实际底色挑。
小尺寸(28px 圆形)下文字必然糊成一条,这是横向 wordmark 的固有限制 ——
接受这一点,换来的是大图与详情页里正确的品牌呈现。

## 第三方数据库的 logo

第三方库的官方 logo **已确认可用** —— 我方是这些库的中国代理 / 合作伙伴。素材大多在
`square-web-next/public/images/database/` 下已有:

| 文件 | 是什么 | 用途 |
|---|---|---|
| `eco.svg` | ecoinvent wordmark | → `ecoinvent.png` |
| `cm.svg` | CarbonMinds(左侧 `cm` 是独立方形符号) | → `carbonminds.png`,只取符号 |
| `logo.svg` | HiQLCD 字样 | → `hiqlcd.png` / `hiqlcd-al.png` |
| `needs.svg` / `exio.svg` | NEEDS / EXIOBASE | 暂未用(无对应技能) |

**优先用方形符号而非 wordmark** —— 卡片图标只有 20–30px 且常做圆形裁切,横向 wordmark
在这个尺寸下必然糊成一条(对比 `carbonminds` 的 `cm` 与 `ecoinvent` 的 wordmark 即可看出)。
有独立符号就用符号。

外部取得的素材放在 `_sources/`:

| 文件 | 来源 | 用途 |
|---|---|---|
| `catarc-symbol.png` | `auto-lcd.cn` 的 `catarclca-logo-left`(白色版,已反色) | → `calcd.png` |
| `agri-footprint-symbol.png` | `carbonx.hiqlcd.com` 的 `agrifootprint-logo`(Mérieux NutriSciences \| Blonk) | 备用,目前无 agri-footprint 技能 |

**尚缺**:有色金属工业协会(HiQLCD-AL 共建方)、中国电子技术标准化研究院(锂电池库共建方)
的标识文件。另外 CATARC 那份源图只有 771×128,裁出的符号 115×96,放大到 256 有锯齿 ——
有 SVG 或更大的 PNG 可以重做。

## 重新生成

```bash
python3 scripts/gen-icons.py      # 改色值后重跑,会覆盖 assets/icons/*.png
```
