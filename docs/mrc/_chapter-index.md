# MRC 章节索引 / MRC Chapter Index

> **唯一真值 (single source of truth)** —— 所有 `docs/mrc/` 文档以及
> `progress.md` / `plan.md` / `test_reports/stage1-mrc-*.md` 中引用 MRC 章节
> 时，都从此表取标题、文件名、职责。如需新增 / 重命名章节，**只在本文件
> 修改**，然后批量 sed 各处引用。

## 1. 章节索引表 / Chapter index

| # | EN Title | ZH 标题 | 文件名（基名） | 一句话职责 / One-line scope |
|---|---|---|---|---|
| 1.0 | TOC & Scope | 章节地图与范围 | `toc` | MRC 章节入口与契约页：范围、坐标、baseline、章节地图 |
| 1.1 | Raw Data Layer | 原始数据层 | `rawdata` | 8 张上游表的字段、时间锚、unified view 形态 |
| 1.2 | Dataflow Layer | 数据流层 | `dataflow` | 5 个 validator 的端到端执行流水线、SQL 模板、mermaid 总图 |
| 1.3 | Sheet Rendering Layer | Sheet 渲染层 | `sheets` | openpyxl 渲染契约：列声明、类型、高亮、number_format |
| 1.4 | Field Definitions | 字段定义 | `fields` | 每张 sheet 每个输出列的字段级血缘 + 业务含义 + 计算逻辑 |
| 1.5 | Validation Rules | 验证规则 | `rules` | 显式 + 隐式规则目录（highlight / threshold / case-when NULL / coerce） |
| 1.6 | Baseline XLSX Behavior | Baseline XLSX 行为 | `baseline` | `2026-04-30` baseline 截取、`±inf`/`NaN` 实测渲染、Stage 2 cell-identical 真值 |
| 1.7 | User Review Gate | 用户走读评审 | （用户动作 / user action — no file） | Stage 2 开闸点 |

## 2. 引用格式约定 / Citation format conventions

### 2.1 章节级引用（指代整篇）/ Whole-chapter reference

| 旧 (Old) | 新 ZH (New ZH) | 新 EN (New EN) |
|---|---|---|
| `第 1.4 章` / `chapter 1.4` | `1.4 字段定义 (fields.zh.md)` | `1.4 Field Definitions (fields.en.md)` |
| `见 1.5` / `see 1.5` | `见 1.5 验证规则 (rules.zh.md)` | `see 1.5 Validation Rules (rules.en.md)` |
| `defined in 1.3` | `在 1.3 Sheet 渲染层 (sheets.zh.md) 中定义` | `defined in 1.3 Sheet Rendering Layer (sheets.en.md)` |

### 2.2 章节内 section 引用（chapter + § N）

| 旧 (Old) | 新 (New) |
|---|---|
| `chapter 1.3 § 10 gap 3` | `1.3 Sheet Rendering Layer (sheets.{zh,en}.md) § 10 gap 3` |
| `1.5 § 10 政策 5` | `1.5 验证规则 (rules.zh.md) § 10 政策 5` |
| `1.2 § 4` | `1.2 数据流层 (dataflow.zh.md) § 4` |

### 2.3 自指（同文档内）/ Self-reference inside same file

仅写 `§ 4.1` / `第 4.1 节`，**不**带章节名（同文件内无歧义）。

### 2.4 表格 / mermaid 紧凑形式 / Compact form in tables & diagrams

空间受限时允许 `→ 1.4 fields.zh.md § 10 gap 3`（编号 + 文件名，省略
标题）；必须能与本表对照。

### 2.5 语言感知 / Language-aware filename suffix

- 在 `*.zh.md` 中引用 → 用 `.zh.md` 后缀
- 在 `*.en.md` 中引用 → 用 `.en.md` 后缀

### 2.6 H1 补强 / H1 reinforcement

每份文档 H1 同时显性化编号 + 双语名，例如：

- `# 1.4 Field Definitions / 字段定义`
- `# 1.2 Dataflow Layer / 数据流层`

## 3. 各文档头部嵌入用 Index 模板 / Embeddable index snippet

参见同目录 `_chapter-index-snippet.zh.md` 与 `_chapter-index-snippet.en.md`
（在 § 1 表的基础上压缩，去掉 EN/ZH 双标题与文件后缀以减少行宽）。

## 修订历史 / Revision history

| 日期 | 作者 | 变更 |
|---|---|---|
| 2026-05-17 | Copilot CLI agent | v1 — 首版。从 `toc.zh.md § 9` 的章节地图脱出独立成 single-source-of-truth；增加 EN title / 文件名 / 职责四列；加入 § 2 引用格式约定。配合 `decisions.md` § N 决策记录使用。 |
