# 端到端流程

三条最常走的路。**每条命令的参数都用 `describe <cmd>` 现查** —— 子命令由服务端目录
运行时生成,这里不列参数,免得服务端改了字段而文档还停在旧版。

所有命令前缀 `hiq-editor`,下面省略。

---

## 一、从零录一条 UPR

### 0. 确认能用

```bash
doctor                 # 凭据来源 + 连通性 + 目录自检
list-datasources       # 空 = 该账号没有编辑器权限,别往下走
```

`list-datasources` 返回空就停下来告诉用户去开通,**不要继续尝试建数据集** —— 后面每一步
都会失败,只是把失败推后。

### 1. 建数据集

```bash
create-process --json     # 参数用 describe create-process 查
```

记下返回的 `process_id`,后面每一步都要用。

### 2. 定参考产品

参考产品是这条数据集"产出什么、产出多少"的锚,**必须先于数据项确定**。

### 3. 逐条加数据项

一条数据项的正确顺序是 **先搜、再确认、后写**:

```bash
search-flows --keyword 木浆 --flow-type PRODUCT_FLOW --json   # 找流
search-backgrounds --keyword 木浆 --json                      # 找背景数据集
# ↑ 把候选给用户看,让他确认用哪个库、哪个版本
add-exchange --process-id <id> --category RAW_MATERIAL --value 0.8 \
  --material-name 木浆 --background '<确认后的四元组 JSON>'
```

**背景四元组不能猜**:`up_element_id` / `up_element_uuid` / `up_element_name` /
`data_source` / `data_version` 要么完整,要么被前置拒绝。同一个材料在不同库、不同版本下
是不同的背景数据集,选择权在用户 —— 把差异(库、版本、地域)讲清楚再让他挑。

### 4. 试算

```bash
calculate-process --process-id <id>
get-process-status --process-id <id>    # 看计算任务状态
```

试算不过通常是数据项有问题(单位、背景缺失、值异常)。**读服务端返回的原因,别改参数瞎试**。

### 5. 提交评审

```bash
submit-review --process-id <id>
```

**不可逆**。提交前把这条数据集复述给用户(名称、参考产品、数据项条数、试算结果),
得到明确确认再执行。

---

## 二、给已有数据集补录 / 订正

```bash
list-my-processes --json                      # 找到目标
get-process-detail --process-id <id> --json   # 看现有数据项
```

改一条:

```bash
update-exchange --json      # 参数 describe update-exchange
```

补一条:走上面「三、逐条加数据项」的先搜后写。

订正后**重新试算**再提交 —— 改过值不重算就提交,评审那边看到的还是旧结果。

---

## 三、整本 UPR 模板导入

填好的官方 `.xlsx` 模板一条命令进系统(路径必须绝对):

```bash
import-upr-from-file --file-path /abs/path/UPR.xlsx --datasource GBA
```

这是**单次事务调用** —— 建数据集(或往已有数据集追加工序 sheet)、参考产品一并完成。
适合"表格已经填好、只想搬进系统"的场景。

如果数据不是模板格式,或者需要精细控制每一步,走 `import` + `plan.json`
(见 [import-plan.md](import-plan.md))。

---

## 失败了怎么办

按退出码分流,**别一律当网络问题重试**:

| 码 | 含义 | 处理 |
|---|---|---|
| `2` | 没有凭据 | 跑 `login`,把授权链接给用户 |
| `3` | 参数 / 计划有问题 | 读 message 改参数;`import` 的话先 `--dry-run` |
| `4` | 服务端拒绝 | 权限不足 / 当前状态不允许 / 业务校验没过。**原样转述,别改参数重试** |
| `5` | 连不上服务端 | 网络问题,`doctor` 看连通性 |

`4` 最容易被误判成"参数没写对"而反复重试 —— 它多数时候是**业务上不允许**
(比如已提交评审的数据集不能再改),换参数没用。

---

## 一条纪律

**读操作随便跑,写操作先确认。**

`list-*` / `get-*` / `search-*` / `doctor` 没有副作用,需要什么信息直接查,不要反过来
问用户要。而 `create-process` / `add-exchange` / `update-exchange` / `match-background` /
`submit-review` 都在改真实的生产数据 —— 除非用户明确说了这一步,否则先把"将要写什么"
列出来给他看。

数据编制的返工成本很高,多问一句远比写错一条便宜。
