# 排错指南 — dsh-travel-recon

> 错误信息统一为 `<一句人话>（E_XXX）｜下一步：<动作>`。完整报错与堆栈只写日志，不打印内部路径。

## 1. 金额列读不懂

- **症状**：导入后提示「金额“abc”读不懂（E_TRAVEL_CSV_INVALID）｜下一步：把金额改成 1234.56 这样的纯数字，最多两位小数」。
- **原因**：行程 / 发票 / 卡流水的 `amount` 列出现空值、字母、三位以上小数，或把负数写成了括号。
- **动作**：把该列改成 `1234.56` 这样的纯数字后重跑。

## 2. CSV 缺少必需列

- **症状**：导入后提示「CSV 缺少 trip_id 列（E_TRAVEL_CSV_INVALID）｜下一步：按 README 的列名补齐第一行表头后重跑」。
- **原因**：三个 CSV 的表头与文档不一致，或有中文列名、空格拼写差异。
- **动作**：按 README 的表头补齐：行程 `trip_id,employee,origin,destination,date,amount`，发票 `invoice_id,trip_id,amount`，卡流水 `txn_id,trip_id,amount`。

## 3. 行程行缺少 trip_id

- **症状**：提示「行程行缺少 trip_id（E_TRAVEL_CSV_INVALID）｜下一步：给每一行填上唯一 trip_id（如 TRIP-1001）后重跑」。
- **原因**：`trips.csv` 有空白行，或 `trip_id` 列写成了 `tripId` / 中文「行程号」。
- **动作**：确认表头是 `trip_id`，并给每一行填上唯一编号（如 `TRIP-1001`）后重新导入。

## 安装或激活失败

- DSH 需满足 `>=0.2.1-rc.3 <0.4.0`，Node 需满足 `>=24.9 <25`。
- 用临时 `DSH_HOME` 排除旧配置干扰：

```sh
export DSH_HOME="$(mktemp -d)"
dsh plugin --profile <profile> add dsh-travel-recon
dsh --profile <profile> --dump-config | grep dsh-travel-recon
```

## 自己复现

```sh
pnpm build
node samples/quickstart/run.mjs          # 合成样例，应输出 quickstart ok
node --test test/*.test.mjs              # 全绿
```

## 报告问题

请附版本号、最小合成输入和完整工具调用；**不要上传客户数据**。
<https://github.com/PerryLink/dsh-travel-recon/issues>
