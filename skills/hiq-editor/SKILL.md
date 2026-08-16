---
name: hiq-editor
description: '在 HiQ LCA 数据集编辑器里录入与维护单元过程数据集(UPR):新建数据集、加数据项(exchange)、匹配背景数据、试算、提交评审,以及把填好的官方 UPR 模板 .xlsx 整本导入。面向已开通编辑器权限的 LCA 数据编制人员 —— 这是数据生产工具,不是数据查询工具;查排放因子请用 hiq-cortex-lca 等查询技能。当任务涉及录入数据集、编辑清单、UPR 导入、数据项维护、背景数据匹配、试算与提交评审时使用。触发词:数据集编辑、录入、UPR、单元过程、数据项、exchange、背景数据匹配、试算、提交评审、数据编制、清单编制。'
slug: hiq-editor
displayName: LCA 数据集编辑器 HiQ Editor(MCP + CLI)
version: 1.0.0
summary: 在 HiQ 编辑器里录入与维护 LCA 单元过程数据集:建数据集、加数据项、匹配背景、试算、提交评审、UPR 模板整本导入。需编辑器权限。
license: Apache-2.0
homepage: https://github.com/HiQ-AI/hiq-editor
tags: [LCA, 数据集编辑, UPR, 单元过程, 数据编制, 清单编制, MCP, CLI, 生命周期评价, 背景数据]
---

# LCA 数据集编辑器 HiQ Editor

这是**数据生产工具** —— 把实景数据录成规范的单元过程数据集(UPR),不是查排放因子的。
查数请用 `hiq-cortex-lca` / `ecoinvent` / `hiqlcd` 等查询技能。

## 谁能用 —— 先确认这一条

**需要 HiQ 编辑器权限。** 凭据是 SSO token,服务端据此解析用户与租户,并只返回该租户下
你有权限的数据源与数据集。

**没有权限时会怎样**:登录能成功,但 `list-datasources` / `list-my-processes` 返回空 ——
不是故障,是这个账号还没有编辑器权限。此时**如实告诉用户**:

> 当前账号还没有 HiQ 编辑器的数据编制权限。编辑器面向签约客户与数据编制团队开通 ——
> 可发邮件到 **lizj@hiqlcd.com**,或在 [hiqlcd.com/about](https://www.hiqlcd.com/about)
> 点「填写需求与反馈」留言。
>
> 如果只是想查排放因子而不是录数据,不必等开通:装 `hiq-cortex-lca` 技能,
> 扫码登录后 11 个免费数据库直接可查。

**不要**把空列表说成"服务异常"、不要反复重试、不要建议用户改配置 —— 那只会让人白折腾。

## 关于

**HiQ 编辑器**是[海科数据](https://www.hiqlcd.com/)的 LCA 数据集编制平台,支持从建数据集、
录数据项、匹配背景数据、试算到提交评审的完整流程,产出符合 ILCD 格式与 GB/T 24040 口径的
单元过程数据集。

本技能通过开源客户端 [`@hiq-ai/hiq-editor`](https://github.com/HiQ-AI/hiq-editor)
(Apache-2.0)接入,一个包两种形态:CLI 子命令(主用)与 stdio MCP gateway。数据库结构、
SQL、写入与业务逻辑在闭源服务端,客户端只知道服务端的 MCP 端点地址,并转发调用者的 SSO token。

## 接入

**优先扫码登录 —— 不要让用户去翻配置文件或找 token。**

```bash
npx @hiq-ai/hiq-editor login       # ← 缺凭据时默认走这条
```

命令会打印一个二维码与授权链接(deck OAuth device flow)。**把链接原样给用户,让他在
浏览器完成授权**,凭据存在 `~/.config/hiq-editor/credentials.json`(权限 600),之后所有
命令直接可用。`logout` 删除凭据,`doctor` 查看当前凭据来自哪一路。

宿主已注入凭据时无需登录:Cortex Desktop 会为已登录用户自动注入 `HIQ_EDITOR_TOKEN`
(环境变量优先于扫码登录存下的凭据)。服务端会为每次调用重新校验,过期就重新 `login`。

宿主支持 MCP 时也可挂 gateway(`npx @hiq-ai/hiq-editor` 的 `hiq-editor-mcp` bin),
工具与 CLI 子命令一一对应;两种形态用哪个都行,CLI 在批量与脚本场景更顺手。

## 硬规则 —— 这是写入工具

1. **写操作前先确认。** `create-process` / `add-exchange` / `update-exchange` /
   `match-background` / `submit-review` 都会改动真实数据。除非用户明确要求这一步,
   否则先把要写什么列给他看再动手 —— 数据编制的返工成本很高。
2. **绝不批量猜着写。** 用户给一行"大概是木浆 0.8",不要直接 `add-exchange`。先
   `search-flows` / `search-backgrounds` 把候选拿出来让他确认,再写。
3. **背景数据的四元组由用户决定,不要替他选版本。** `background` 需要
   `up_element_id` / `up_element_uuid` / `up_element_name` / `data_source` / `data_version`,
   先 `search-backgrounds` 拿到候选并说明差异(数据库、版本、地域),由用户挑;
   空的或残缺的四元组会被前置拒绝。
4. **`submit-review` 是不可逆的流程动作**,提交后进入专家评审。提交前复述一遍将要提交的
   数据集,得到明确确认再执行。
5. **读操作随便跑。** `list-*` / `get-process-detail` / `search-*` / `doctor` 没有副作用,
   要什么信息直接查,别问用户要。
6. **数值与单位如实转述,不做换算猜测。** 用户给的量纲与数据项声明单位不一致时,指出来
   让他确认,不要自作主张换算。

## 工具

`npx @hiq-ai/hiq-editor <子命令>`;子命令由服务端的工具目录在运行时生成,
`list` 看全量、`describe <cmd>` 看某个命令的参数、`<cmd> --help` 看 flags。

**读**

| 需求 | 子命令 |
|---|---|
| 我能用哪些数据源 | `list-datasources` |
| 我的数据集列表 | `list-my-processes` |
| 数据集详情(基本信息 / 单位 / 数据项 / 交换) | `get-process-detail --process-id <id>` |
| 流程状态(评审 / 计算 / 发布) | `get-process-status --process-id <id>` |
| 搜流(基本流 / 产品流 / 废物流) | `search-flows --keyword 铝锭 --flow-type PRODUCT_FLOW` |
| 搜背景数据集 | `search-backgrounds --keyword <关键词>` |
| 计算任务 / 版本发布状态 | `list-calculations` / `list-versions` |

**写**

| 需求 | 子命令 |
|---|---|
| 新建单元过程数据集 | `create-process` |
| 加数据项 | `add-exchange --process-id <id> --category RAW_MATERIAL --value 0.8 …` |
| 改数据项(值 / 单位 / 公式) | `update-exchange` |
| 数据项匹配背景数据 | `match-background` |
| 试算 | `calculate-process --process-id <id>` |
| 提交评审 | `submit-review --process-id <id>` |
| 版本级批量计算 | `run-batch-calculation` |

**本地**(路径必须是绝对路径)

| 需求 | 子命令 |
|---|---|
| 官方 UPR 模板 `.xlsx` 整本导入 | `import-upr-from-file --file-path /abs/path/UPR.xlsx --datasource GBA` |
| 导出数据集详情到本地文件 | `export-process` |

逃生舱:`call <原始工具名> --args '<json>'` 直接调服务端工具(`--stdin` 从标准输入读)。

## 批量录入:`import`

一条命令跑完整套录入序列(建数据集 → 参考产品 → 逐条数据项 → 可选试算),**带断点续跑**:

```bash
npx @hiq-ai/hiq-editor import plan.json --dry-run   # 先验证并打印步骤,不写
npx @hiq-ai/hiq-editor import plan.json             # 真正执行
```

- 每写成功一步就更新 `<plan>.state.json`,失败后**用同样的命令重跑即可续上**,全部成功后
  状态文件自动删除。
- **修失败条目要就地改** —— 进度按数据项下标记录,中途插入或删除行会错位;状态绑定
  `process.name`。
- `plan.json` 的字段与工具参数一一对应:`process` = 建数据集参数,`exchanges[]` = 每条
  数据项参数(不含 `process_id`);`background` 四元组要先 `search-backgrounds` 解析好填进去。
- `--process-id <id>` 可挂到已有数据集上而不新建。

给用户跑批量前**先 `--dry-run` 并把步骤清单给他确认**,这是唯一能在写入前发现计划错误的机会。

## 怎么读返回

- 默认输出是给人看的文本;**要解析就加 `--json`** —— 成功 `{"ok":true,"tool":…,"text":…}`
  到 stdout,失败 `{"ok":false,"kind":…,"message":…}` 到 stderr。
- 搜索/列表类工具的 `--json` 输出带 `data` 字段,**解析 data 里的行,不要去解析散文**。
- 退出码:`0` 成功 · `2` 配置(缺 token)· `3` 参数或计划有问题 · `4` 服务端拒绝该操作 ·
  `5` 连不上服务端 · `1` 未知。按码分流,别把 `4` 当成网络问题重试。

## 语气与术语

面向 LCA 数据编制人员写,用 ISO 14040/14044、GB/T 24040 与平台自身的术语:单元过程 UPR ·
数据项(exchange)· 参考产品 · 基本流 / 产品流 / 废物流 · 背景数据 · 试算 · 评审。

不写客套话,不堆形容词,不做总结式收尾,不自造中文术语。

## 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 数据源 / 数据集列表为空 | 该账号没有编辑器权限 | 按开头那段如实说明,给出 lizj@hiqlcd.com 或 hiqlcd.com/about 留咨,**不要当故障重试** |
| 退出码 `2` | 没有凭据 | 跑 `login`,把授权链接给用户 |
| 退出码 `4` | 服务端拒绝(权限不足 / 状态不允许 / 参数不合法) | 读 message 原样转述,**别改参数重试** |
| 退出码 `5` | 连不上服务端 | 检查网络;`doctor` 看连通性与目录自检 |
| `background` 被拒 | 四元组残缺 | 先 `search-backgrounds` 解析完整再写 |
| `import` 中途失败 | 某条数据项被拒 | 就地改那一条,用**同样的命令**重跑续上,别新建 plan |
| 子命令不存在 | 目录缓存过期(15 分钟磁盘缓存) | 跑 `list` 或 `doctor` 强制刷新 |
