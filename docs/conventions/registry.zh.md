# Registry 规范

驱动整个白盒站点的双层 YAML metadata。

## 文件

- `whitebox/validators/<servicer>/<name>.yaml` —— 每个 validator 一份。
- `whitebox/validators/<servicer>/<name>.sql` —— 从原系统抽出的原始 SQL。
- `whitebox/validators/<servicer>/<name>.py` —— 同样逻辑的 Python 重写。
- `sheets/<sheet_name>.yaml` —— 每张报表 sheet 一份，含**列级** metadata。

## 必填字段 —— validator YAML

| 字段 | 说明 |
|---|---|
| `id` | `<servicer>/<name>`，小写 + 下划线，全局唯一。 |
| `servicer` / `name` | 与 `id` 一致。 |
| `title_en` / `title_zh` | 站点显示用短标题。 |
| `related_sheets` | 本 validator 产出的 sheet 名。 |
| `source_tables` | 上游 Redshift 表（`schema.table`）。 |
| `source_citation` | 指向只读原仓库的 `<file>:<line>`。 |
| `rule_en` / `rule_zh` | 业务规则，普通文字，双语。 |
| `sql_file` | `.sql` 文件相对路径（纯 Python 填 `null`）。 |

可选：`description_*`、`rule_business_impact_*`、`tags`。

## 必填字段 —— sheet YAML

| 字段 | 说明 |
|---|---|
| `sheet` | sheet 名，与 gold XLSX 一致。 |
| `business_meaning_*` | 双语一句话简介。 |
| `producing_validators` | 给本 sheet 贡献列的 validator ID。 |
| `columns.<col>.type` | `string`/`integer`/`float`/`decimal`/`date`/`datetime`/`boolean`/`json` 之一。 |
| `columns.<col>.rule_en` / `rule_zh` | **该列**的双语业务规则。 |

可选：`format`、`business_impact_*`、`sample_values`、`related_validator`。

## 自动填充字段（禁止手改）

由 `tools/build_lineage.py`（sqlglot）每次 build 时自动填：

- `columns.<col>.sources` —— 上游 `{table, column, transform}` 列表。
- `columns.<col>.expression` —— 产出该列的 SQL 表达式。

## 校验

跑 `python -m tools.registry` 校验所有 YAML 并打印树。
