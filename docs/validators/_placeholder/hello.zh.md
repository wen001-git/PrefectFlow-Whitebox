# 占位：Hello validator

**ID**：`_placeholder/hello` &nbsp;&nbsp; **Servicer**：`_placeholder` &nbsp;&nbsp; **源码出处**：`whitebox/validators/_placeholder/hello.py:1`

仅用于 Phase 1 文档基础设施自检的合成 validator（registry、lineage、
autodoc、harness），不是真业务 validator。Phase 3 清理时删除。

## 业务规则

对 placeholder_input 表每一行，拷贝 loan_id 并计算 principal_x2 = principal * 2。
!!! info "业务影响"
    若失效，占位 sheet 显示错误的翻倍值；无业务影响。

## 产出 sheets

- [placeholder_hello](../../sheets/placeholder_hello.md) —— 自检 sheet —— 占位贷款的本金翻倍结果。

## 源数据表

- `public.placeholder_input`

## SQL

```sql
-- Extracted from: whitebox/validators/_placeholder/hello.py:1
-- Placeholder validator SQL — selftest only.
SELECT
    loan_id        AS loan_id,
    principal * 2  AS principal_x2
FROM public.placeholder_input

```

**标签**：`selftest`, `placeholder`