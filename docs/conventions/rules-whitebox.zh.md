# 业务规则白盒化规范

业务规则在 YAML 里分**两层**：validator 级 + column 级。**全部双语**。

## 两个层级

### Validator 级（写在 `whitebox/validators/<servicer>/<name>.yaml`）

| 字段 | 必填 | 含义 |
|---|---|---|
| `rule_en` / `rule_zh` | 是 | 本 validator 做什么，用业务语言，1-3 句。 |
| `rule_business_impact_en` / `_zh` | 可选 | 出错时影响哪个业务决策/流程。 |

### Column 级（写在 `sheets/<sheet>.yaml` 的 `columns.<col>` 下）

| 字段 | 必填 | 含义 |
|---|---|---|
| `rule_en` / `rule_zh` | 是 | 这列**具体**怎么来的，用业务语言。 |
| `business_impact_en` / `_zh` | 可选 | 这列出错的后果。 |

## 写作风格

- **读者 = 业务分析师**。少用术语（`JOIN`、`CTE`），说"匹配"、"合并"。
- **先讲 "做什么"，再讲 "怎么做"**。
- **双语保真**。中英文要说同一件事，不许漂移。用户用中文写时**中文照搬原文**，再翻成英文。
- **一规则一意**。多分支独立成行。

## 链接到 known deltas

规则若与原 `PrefectFlow` 行为**有意不同**，把差异记到 `docs/known-deltas.md`，并在规则里引用：

```yaml
rule_zh: |
  活跃贷款的月度本金还款总额。
  （已知差异：KD-007 —— 原系统误把已撤销的贷款也算进去了。）
```
