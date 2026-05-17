# Selene — 待分析占位 / Pending analysis placeholder (zh)

> **状态**：⏳ pending-deferred（v9.1 placeholder）
> **Purpose**：占位文档。Selene 的 Validation Report 生成逻辑**尚未**分析。
> 本文件保证 mkdocs 站点导航和 servicers-registry 中存在 Selene 的位置，
> 避免遗忘；待分析完成后，本文件会被 toc/rawdata/dataflow/sheets/fields/rules
> 章节集合替换。
>
> **Intended audience**：未来接手 Selene 分析的 session agent + 用户。
>
> **Revision history**
>
> | Date | Author | Change |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — 创建占位（v9.1 placeholder-everywhere 规则）。 |

---

## 概要 / Summary

- **预计 sheet 数 / Estimated sheets**: 5 (assumed)
- **已知源码文件 / Known source files** (in `flow/remit_validation/`):
  selene_db.py, selene_validation.py
- **当前状态**：未分析。

---

## 待回答的开放问题 / Open questions

1. Selene 共有多少个 @task validator？分别叫什么名字？
2. 各 validator 写入哪几张 sheet？sheet 名是什么？
3. 每张 sheet 的列结构、header_row、高亮规则？（参考 `util/gen_remit_validation_report.py`）
4. SQL 模板复用 `servicer_validation_with_portdaily.py` 哪几个？（与 carrington/shellpoint/mrc 是否共用）
5. Selene 在 `port.portmonth` 中的 `servicer` 字段值是什么？
6. 是否有 Selene-specific schema（如 `selene.*`）作为 unified 层？
7. 已知缺陷或边界情况？

---

## 假设 / Assumptions（待验证）

- 沿用 carrington/shellpoint/mrc 的 4 维度组织（overview / 每 sheet / 每字段 / 数据流分支）。
- 沿用 v8 文档约定（doc-header、zh/en 对齐、源码引用 `file.py:LINE`、内嵌 mermaid + caption + 步骤说明）。
- 沿用 v9.1 mermaid 节点 ID 前缀约定（`SH1["SH1 · ..."]`）。

---

## 分析完成后的下一步 / Follow-up when analyzed

1. 创建 `docs/selene/toc.{zh,en}.md`、`rawdata.{zh,en}.md`、`dataflow.{zh,en}.md`、`sheets.{zh,en}.md`、`fields.{zh,en}.md`、`rules.{zh,en}.md`，参考 MRC 章节的模板结构。
2. 更新 `mkdocs.yml` 导航：把 Selene 从 "Pending servicers" 移到正式章节区。
3. 在 `tools/stage_doc_checks.py` 的 PAIRS 列表中添加 Selene 的所有新文档对。
4. 更新 `docs/_status/servicers-registry.{zh,en}.md` + `plan.md` 状态矩阵：⏳ → ✅。
5. 在 `test_reports/` 写测试报告。
6. SQL todo（`stage1-selene` 或新拆分的 `stage1-selene-*`）状态从 `pending-deferred` → `done`。

详见 plan.md `Placeholder reservation policy` 节、AGENTS.md § 6.5–6.8。

---

## 备注 / Notes

Sheet count assumed 5; verify validator count and sheet column definitions in util/gen_remit_validation_report.py.
