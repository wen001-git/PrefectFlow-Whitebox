# SQL 白盒化规范

每个 validator 的原始 SQL 从只读的 `PrefectFlow` 源仓库抽出到与 YAML 同目录的 `.sql`：

```
whitebox/validators/<servicer>/<name>.sql
```

## 抽取规则

1. **保持原语义。** 原样拷贝，不重构、不重命名 alias。
2. **每文件一条语句。** 原代码若串多条，拆成多个文件（如 `_setup.sql` / `_main.sql`），YAML 引用主文件。
3. **首行注释标出源码位置。** 始终以 `-- Extracted from: <file>:<line>` 开头。
4. **参数占位符标准化。** 把 f-string / `.format()` 换成标准 SQL 参数（`:param` 或 `?`），参数含义写入 YAML 的 `description_*`。

## 为什么这样设计

`.sql` 文件同时承担三个角色：

- **文档** —— 在 validator 页面上 syntax-highlight 显示。
- **Lineage 输入** —— sqlglot 解析它，自动抽列级 lineage。
- **实现参考** —— 同目录 `.py` 必须在冻结的 Parquet snapshot 上产出等价结果。

`.sql` 与 `.py` 一旦漂移，diff harness 立刻发现。
