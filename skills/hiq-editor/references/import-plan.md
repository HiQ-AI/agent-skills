# `import` 与 `plan.json`

`import` 把整套录入序列(建数据集 → 参考产品 → 逐条数据项 → 可选试算)跑成一条命令,
**带断点续跑**。适合数据项多、需要反复调整的场景。

```bash
npx @hiq-ai/hiq-editor import plan.json --dry-run   # 只验证 + 打印步骤,不写
npx @hiq-ai/hiq-editor import plan.json             # 执行
```

## 结构

字段与工具参数一一对应 —— `process` 就是建数据集的参数,`exchanges[]` 每项就是加数据项的
参数(去掉 `process_id`,由 import 自己串)。所以**字段的准确定义永远以
`describe create-process` / `describe add-exchange` 为准**,本文不复制参数清单。

```jsonc
{
  "process": {
    "name": "漂白硫酸盐木浆生产",
    "datasource": "GBA",
    "middle_flow_id": "…",
    // 其余字段见 describe create-process
  },

  "reference_product": {
    "value": 1,
    "declared_unit_id": "…"
    // flow_id 缺省取 process.middle_flow_id
  },

  "exchanges": [
    {
      "category": "RAW_MATERIAL",
      "value": 0.8,
      "material_name": "木浆",
      "background": {
        "up_element_id":   "…",
        "up_element_uuid": "…",
        "up_element_name": "…",
        "data_source":     "HiQLCD",
        "data_version":    "1.4.0"
      }
    },
    {
      "category": "AIR_EMISSION",
      "value": 0.1,
      "flow_id": "…"          // 基本流直接给 flow_id,不需要 background
    }
  ],

  "calculate": false          // true = 跑完顺带试算
}
```

## 背景四元组要先解析好

`background` 的五个字段**必须完整**,空的或残缺的会在写入前被拒绝。解析是调用方的决定,
不是 import 的职责:

```bash
npx @hiq-ai/hiq-editor search-backgrounds --keyword 木浆 --json
```

从 `data` 里挑,把选中那条的 id / uuid / name / 库 / 版本填进 plan。

**版本要用户定。** 同一个材料在 HiQLCD 1.4.0 与 1.5.0 下是不同的背景数据集,结果会差。
把候选连同库和版本一起给用户看,让他选,不要默认取最新。

## 断点续跑

每写成功一步就更新 `<plan>.state.json`,失败后**用完全相同的命令重跑**即可从断点继续,
全部成功后状态文件自动删除。

```bash
npx @hiq-ai/hiq-editor import plan.json     # 第 12 条失败
# 就地改 plan.json 里第 12 条
npx @hiq-ai/hiq-editor import plan.json     # 同样的命令,从第 12 条继续
```

三条纪律:

1. **就地改,不要增删行。** 进度按数据项**下标**记录,中途插入或删除会让后面全部错位 ——
   已写的被当成没写,或者没写的被跳过。
2. **状态绑定 `process.name`。** 改了名字等于换了一个 plan,进度对不上。
3. **不要为了"重来一遍"手动删 state 文件**,那会把已经写进系统的数据项再写一遍。
   真要重来,先看 `get-process-detail` 确认系统里现在有什么。

## 挂到已有数据集

```bash
npx @hiq-ai/hiq-editor import plan.json --process-id <id>
```

跳过建数据集,把 `exchanges[]` 追加到指定数据集上。plan 里的 `process` 段此时被忽略。

## 先 dry-run

```bash
npx @hiq-ai/hiq-editor import plan.json --dry-run
```

验证 plan 结构、打印将要执行的步骤,**不写任何东西**。这是写入前唯一能发现计划错误的机会 ——
给用户跑批量之前,先把这份步骤清单给他确认。

## 管道用法

```bash
cat plan.json | npx @hiq-ai/hiq-editor import --stdin --state /abs/path/run.state.json
```

`--stdin` 从标准输入读 plan,此时**必须显式给 `--state`**(否则没有地方记录断点)。
