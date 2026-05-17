# G2a 操作员操作手册 — MRC 输入快照冻结

<!-- G2A-A5: OPERATOR-ONLY — G2a 快照导出操作手册。
     需要 VPN 访问权限 + HashiCorp Vault 令牌。Agent 无法自行满足这些前提条件。-->
<!-- LIVING-DOC: 每当工具标志、绑定或导出工作流发生变更时，请更新本文档。-->

> **受众**：任何需要端到端执行 G2a 导出操作的人员（用户 / 同事 / 未来 Copilot 会话）。
>
> **修订历史**
>
> | 日期 | 作者 | 变更 |
> |---|---|---|
> | 2026-05-17 | Copilot CLI agent | v1 — G2a A5 初版。参考来源：`tools/freeze_snapshot.py` v2.2、`_coverage.md`、`_bindings.json`、`docs/mrc/_g2a-redshift-dependencies.zh.md`。|

---

## 1. 目的

G2a（`mrc-snapshot` 待办事项）是一次性导出步骤，将 5 个 MRC 验证器实际读取的每个
Redshift 数据集冻结为本地 Parquet 文件，存储于
`baselines/mrc/2026-04-30/input_snapshots/parquet/`，使 Stage 2 开发能够在
**零实时 Redshift 依赖**的情况下重新运行完整 MRC 验证报告。

**为何是仅限操作员执行？** Agent 可以构建工具和解析 SQL 模板，但无法连接公司内部
Redshift 集群（需要 VPN）或从 HashiCorp Vault 读取凭据（无令牌）。针对 Redshift 的
实际 SQL 执行必须由同时具备 VPN 和 Vault 访问权限的操作员完成。

**谁来关闭 G2a？** 当前用户、拥有 Redshift 访问权限的同事，或任何拥有 VPN + Vault
凭据的未来会话。操作员提交 `_manifest.json` 和 Parquet 文件后，Agent 将继续推进
G2b 和 G3。

---

## 2. 操作前检查清单

执行任何命令前，逐一完成以下所有检查项。

- [ ] **已连接 VPN** — 必须接入公司 VPN；Redshift 集群不对外开放。
- [ ] **Vault 令牌有效** — 可读取 `prefect-secret/db/redshift`：

  ```bash
  vault kv get prefect-secret/db/redshift
  ```

  若已过期，请通过身份提供商重新认证并导出新令牌：

  ```bash
  export VAULT_TOKEN=$(vault login -method=<your-method> -token-only)
  ```

  完整凭据详情请参阅
  [`docs/mrc/_g2a-redshift-dependencies.zh.md`](../docs/mrc/_g2a-redshift-dependencies.zh.md)
  §§ 2–3。

- [ ] **Python 环境** — 必须安装以下软件包：

  ```bash
  pip install redshift-connector pandas pyarrow hvac
  ```

  验证安装：

  ```python
  import redshift_connector, pandas, pyarrow, hvac
  print("all imports OK")
  ```

- [ ] **已克隆仓库且为最新状态** — 在 `main` 分支上进行最近一次拉取：

  ```bash
  git checkout main && git pull origin main
  ```

- [ ] **已填写 `.env`** — 将 `.env.example` 复制为 `.env` 并填入实际值
      （**切勿提交 `.env`**）：

  ```bash
  cp .env.example .env
  # 编辑 .env — 设置 VAULT_ADDR、VAULT_TOKEN，并核实锚点日期
  ```

  完整模板请参见项目根目录下的 `.env.example`。

---

## 3. 第 1 步 — 生成导出计划

在项目根目录执行：

```bash
python tools/freeze_snapshot.py plan \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --resolve
```

### 输出内容说明

| 输出 | 位置 | 描述 |
|---|---|---|
| 模板 SQL（全部 21 条） | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/template/*.sql` | 保留 `{placeholder}` 的原始 SQL；包含所有服务商，不仅限于 MRC |
| 已解析 SQL（仅 MRC，可直接运行） | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/resolved/*.sql` | 占位符已替换为锚点绑定值；8 个 MRC 模板产生 9 个文件（含一个扇出） |
| 计划索引 | `baselines/mrc/2026-04-30/input_snapshots/_plan_index.json` | 所有 SQL 命中的机器可读清单；供 `verify` 子命令使用 |
| 覆盖率报告 | `baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md` | 人类可读表格；导出前请先审查 |
| 绑定快照 | `baselines/mrc/2026-04-30/input_snapshots/_bindings.json` | `--resolve` 使用的锚点绑定；提交至 git |

> **进入第 2 步之前**，请打开 `_coverage.md`，确认摘要行显示
> **"MRC-relevant SQL strings: 8"**，且 5 个 chapter-1.2 模板均显示 ✅。

---

## 4. 第 2 步 — 审查已解析的 SQL

**打开 `_export_queries/resolved/` 中的每个文件**，在运行之前先阅读。共有 9 个已解析
文件：

```
mrc__get_port_funding_data_<sha>.sql
mrc__get_port_month_data_<sha>.sql       （两个变体 — 一个含 service 过滤）
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-04-01.sql
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-05-01.sql
mrc__mrc_adv_validation_<sha>.sql
mrc__mrc_general_check_<sha>.sql
mrc__mrc_service_fee_check_<sha>.sql
mrc__mrc_summary_check_<sha>.sql
```

### 绑定核验清单

| 绑定项 | 期望值 | 含义 |
|---|---|---|
| `fctrdt`（当月） | `2026-05-01` | 因子日期 = 汇款月份第 1 天 |
| `fctrdt_1m` / 上月 `fctrdt` | `2026-04-01` | 上月因子日期 |
| `service` | `'MRC'` | SQL 中的服务商名称过滤 |
| `remit_date` | `2026-04-30` | 锚点汇款日期 |

- 确认当期查询中出现 `WHERE fctrdt = '2026-05-01'`。
- 确认先期查询中出现 `WHERE fctrdt = '2026-04-01'`。
- 在预期位置确认 `WHERE service = 'MRC'`（大小写不敏感）。
- 确认任何已解析文件中均无残留的 `{expr}` 花括号占位符。

### 扇出合理性检查

`_mrc_adv_info_sql` 必须恰好有 **2** 个已解析变体：

```
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-05-01.sql   ← 当前周期
mrc__mrc_adv_info_sql_<sha>__fctrdt=2026-04-01.sql   ← 上一周期（MoM 对比）
```

这是正确的：验证器调用此函数两次（每个 fctrdt 各一次），并通过 pandas 左连接合并结果
以计算月度环比 advance info 差值。底层表的详细信息请参阅
`docs/mrc/_g2a-redshift-dependencies.zh.md` § 4。

---

## 5. 第 3 步 — 逐数据集运行导出

> **请勿在本仓库中创建 `tools/g2a_export_helper.py`** — 凭据不得进入仓库，且该脚本
> 仅在操作员的本地环境中运行。使用以下代码片段作为可粘贴的起点。

### 可直接粘贴的导出代码片段

将以下内容另存为 `~/g2a_export_helper.py`（仓库外部），并在完成操作前检查清单后，
在您的虚拟环境中运行。

```python
"""
g2a_export_helper.py — G2a MRC 输入快照导出工具。
在仓库外部运行；从仓库路径读取 _plan_index.json。
依赖：redshift_connector, pandas, pyarrow, hvac, python-dotenv（可选）。
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import hvac
import pandas as pd
import redshift_connector

# ── 配置 ──────────────────────────────────────────────────────────────────────
REPO_ROOT       = Path("/path/to/PrefectFlow-Whitebox")  # ← 请修改
SERVICER        = "mrc"
REMIT_DATE      = "2026-04-30"
SNAPSHOT_DIR    = REPO_ROOT / "baselines" / SERVICER / REMIT_DATE / "input_snapshots"
PARQUET_DIR     = SNAPSHOT_DIR / "parquet"
PLAN_INDEX      = SNAPSHOT_DIR / "_plan_index.json"
MANIFEST_PATH   = SNAPSHOT_DIR / "_manifest.json"
RESOLVED_DIR    = SNAPSHOT_DIR / "_export_queries" / "resolved"

VAULT_ADDR      = os.environ["VAULT_ADDR"]
VAULT_TOKEN     = os.environ["VAULT_TOKEN"]
VAULT_RS_PATH   = os.environ.get("VAULT_REDSHIFT_PATH", "prefect-secret/db/redshift")

# ── 从 Vault 获取凭据 ──────────────────────────────────────────────────────────
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)
secret = client.secrets.kv.read_secret_version(path=VAULT_RS_PATH)["data"]["data"]
RS_HOST     = secret["hostname"]
RS_PORT     = int(secret.get("port", 5439))
RS_DATABASE = secret["database"]
RS_USER     = secret["username"]
RS_PASSWORD = secret["password"]

# ── 辅助函数 ─────────────────────────────────────────────────────────────────
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_canonical_rows(df: pd.DataFrame) -> str:
    """对排序后的 (行, 列, 值) 元组进行稳定哈希计算。"""
    h = hashlib.sha256()
    for row in df.sort_values(by=list(df.columns)).itertuples(index=False):
        h.update(str(tuple(row)).encode("utf-8"))
    return h.hexdigest()


# ── 加载计划索引 ─────────────────────────────────────────────────────────────
plan_data = json.loads(PLAN_INDEX.read_text(encoding="utf-8"))
entries = [e for e in plan_data["entries"] if e.get("mrc_relevant")]
PARQUET_DIR.mkdir(parents=True, exist_ok=True)

manifest: list[dict] = []

# ── 连接 Redshift ────────────────────────────────────────────────────────────
conn = redshift_connector.connect(
    host=RS_HOST,
    port=RS_PORT,
    database=RS_DATABASE,
    user=RS_USER,
    password=RS_PASSWORD,
)
conn.autocommit = True

# ── 导出循环 ─────────────────────────────────────────────────────────────────
for entry in entries:
    resolved_paths = entry.get("resolved_paths", [])
    targets = resolved_paths if resolved_paths else []

    for resolved_rel in targets:
        sql_path = REPO_ROOT / resolved_rel
        if not sql_path.exists():
            raise FileNotFoundError(f"已解析 SQL 未找到：{sql_path}")

        sql_text = sql_path.read_text(encoding="utf-8")
        sql_body = "\n".join(
            line for line in sql_text.splitlines()
            if not line.strip().startswith("--")
        ).strip()

        logical_name = sql_path.stem
        parquet_path = PARQUET_DIR / f"{logical_name}.parquet"

        print(f"[EXPORT] {logical_name} ... ", end="", flush=True)
        try:
            cursor = conn.cursor()
            cursor.execute(sql_body)
            df = cursor.fetch_dataframe()
            df.to_parquet(parquet_path, index=False, engine="pyarrow")
            cursor.close()

            file_sha = sha256_file(parquet_path)
            row_sha  = sha256_canonical_rows(df)
            col_list = [
                {"name": c, "dtype": str(df[c].dtype)}
                for c in df.columns
            ]
            print(f"{len(df)} 行，{len(df.columns)} 列 ✅")

            manifest.append({
                "logical_name":           logical_name,
                "source":                 {"type": "redshift",
                                           "schema": "",   # ← 从 SQL 填写
                                           "table": ""},   # ← 从 SQL 填写
                "export_sql_path":        str(resolved_rel),
                "filter":                 entry.get("filter_hints", {}),
                "exported_at":            datetime.now(tz=timezone.utc).isoformat(),
                "exporter":               RS_USER,
                "format":                 "parquet",
                "path":                   str(parquet_path.relative_to(SNAPSHOT_DIR)),
                "row_count":              len(df),
                "column_count":           len(df.columns),
                "columns":                col_list,
                "sha256_file":            file_sha,
                "sha256_canonical_rows":  row_sha,
                "redshift_session":       {
                    "user":     RS_USER,
                    "cluster":  RS_HOST,
                    "query_id": None,
                },
            })

        except Exception as exc:
            print("失败 ❌")
            print(f"  错误：{exc}")
            print(f"  SQL 路径：{sql_path}")
            print("  → 请修复 SQL 或绑定，然后重新运行。切勿静默跳过。")
            raise  # 硬停止 — 绝对不能静默跳过失败的导出

conn.close()

# ── 写入清单 ─────────────────────────────────────────────────────────────────
MANIFEST_PATH.write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False, default=str),
    encoding="utf-8",
)
print(f"\n[完成] {len(manifest)} 条记录已写入 {MANIFEST_PATH}")
```

### 错误处理约定

| 场景 | 必须执行的操作 |
|---|---|
| SQL 执行抛出异常 | 打印完整错误、打印 SQL 路径，**raise**（硬停止）。绝不静默跳过。|
| 已解析 SQL 文件未找到 | 抛出 `FileNotFoundError`。重新运行 `plan --resolve`。|
| Parquet 写入失败（磁盘满、权限） | 修复环境问题后重新导出受影响的数据集。|
| 行数为 0 | 需排查：绑定是否错误？日期是否正确？`verify` 步骤（C2）将拒绝 `row_count <= 0`。|

---

## 6. 第 4 步 — 填写 `_manifest.json`

第 3 步的导出代码片段会逐步写入清单。每个条目必须符合 `tools/freeze_snapshot.py`
中的 `MANIFEST_ENTRY_TEMPLATE`（约第 208 行）：

```python
MANIFEST_ENTRY_TEMPLATE = {
    "logical_name":          "",          # 已解析 SQL 文件名（不含扩展名）
    "source":                {            # Redshift 数据源信息
        "type":   "redshift",
        "schema": "",                     # 例如 "mrc" 或 "port"
        "table":  "",                     # 主要查询的表名
    },
    "export_sql_path":       "",          # 已解析 .sql 文件的相对路径
    "filter":                {},          # 使用的占位符绑定（来自 filter_hints）
    "exported_at":           None,        # ISO-8601 UTC 时间戳
    "exporter":              None,        # 执行查询的 Redshift 用户名
    "format":                "parquet",   # 始终为 "parquet"
    "path":                  "",          # .parquet 文件路径（相对于快照目录）
    "row_count":             None,        # int > 0
    "column_count":          None,        # int > 0（必须 == len(columns)）
    "columns":               [],          # [{"name": "col", "dtype": "int64"}, ...]
    "sha256_file":           None,        # .parquet 文件字节的 sha256 十六进制值
    "sha256_canonical_rows": None,        # 排序后 (行, 列, 值) 元组的 sha256 值
    "redshift_session":      {
        "user":     None,
        "cluster":  None,
        "query_id": None,
    },
}
```

### 实例示例 — `mrc_summary_check`

```json
{
  "logical_name":          "mrc__mrc_summary_check_e943649b57cd",
  "source":                {"type": "redshift", "schema": "mrc",
                            "table": "portmrcremitloanlevelrecap"},
  "export_sql_path":       "_export_queries/resolved/mrc__mrc_summary_check_e943649b57cd.sql",
  "filter":                {"mrc_db.fctrdt": "2026-05-01"},
  "exported_at":           "2026-05-18T09:42:00Z",
  "exporter":              "your-redshift-username",
  "format":                "parquet",
  "path":                  "parquet/mrc__mrc_summary_check_e943649b57cd.parquet",
  "row_count":             1,
  "column_count":          5,
  "columns": [
    {"name": "tot_uupb",       "dtype": "float64"},
    {"name": "tot_remit_amt",  "dtype": "float64"},
    {"name": "tot_curtailment","dtype": "float64"},
    {"name": "tot_svcfee",     "dtype": "float64"},
    {"name": "tot_int",        "dtype": "float64"}
  ],
  "sha256_file":           "a1b2c3d4...e5f6（64 位十六进制字符）",
  "sha256_canonical_rows": "9f8e7d6c...5b4a（64 位十六进制字符）",
  "redshift_session":      {"user": "your-redshift-username",
                            "cluster": "<cluster-id>.redshift.amazonaws.com",
                            "query_id": null}
}
```

> **提示**：导出代码片段会逐步写入条目——若某个查询在中途失败，已导出的条目在
> 部分写入的清单中是安全的。修复失败的 SQL 后，删除该数据集的部分条目，仅重新运行
> 受影响的查询即可。

---

## 7. 第 5 步 — 验证

```bash
python tools/freeze_snapshot.py verify \
    --servicer mrc \
    --remit-date 2026-04-30 \
    --strict \
    --verbose \
    --json
```

### 退出码说明

| 退出码 | 含义 | 操作 |
|---|---|---|
| `0` | 所有检查通过（核心 C1–C6 + 严格 C7–C8） | 继续执行第 6 步 |
| `1` | 一个或多个**核心**检查（C1–C6）失败 | 读取 `_verify_report.json`；修复并重新导出 |
| `2` | 核心通过，但**仅严格**检查（C7–C8）失败 | 读取 `_verify_report.json`；决定是否在交接前修复 |

### 检查项摘要

| 检查项 | 验证内容 |
|---|---|
| C1 — 覆盖率对等 | 每个预期数据集均在清单中；无孤立条目 |
| C2 — 模式完整性 | 所有必填字段存在，row_count > 0，sha256 格式有效 |
| C3 — 文件 + 校验和 | Parquet 文件在磁盘上存在；sha256 与清单值匹配 |
| C4 — SQL 哈希绑定 | 可选字段 `sql_sha256` 与已解析 SQL 文件匹配（如已提供） |
| C5 — 模式合理性 | `column_count` == `len(columns)`；无重复列名；无空 dtype |
| C6 — 扇出一致性 | `_mrc_adv_info_sql` 恰好有 2 个清单条目（每个 fctrdt 一个） |
| C7 — 绑定文档 [严格] | `_bindings.json` 存在且内容一致 |
| C8 — 存储策略 [严格] | Parquet 文件在预期路径；`.gitignore` 策略得到遵守 |

### 若验证失败

1. 使用 `--json` 运行以获取 `_verify_report.json`。
2. 打开报告，阅读每个失败检查项下的 `"details"` 数组。
3. 按照第 10 节"故障排查"中的说明进行修复。
4. 重新运行验证，直至退出码为 `0`（或若您接受严格差异则为 `2`）。

---

## 8. 第 6 步 — 交接给 Agent

### 提交产物

```bash
git add baselines/mrc/2026-04-30/input_snapshots/_manifest.json
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/template/
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/resolved/
git add baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md
git add baselines/mrc/2026-04-30/input_snapshots/_verify_report.json
git commit -m "g2a(export): MRC 2026-04-30 输入快照 — <N> 个数据集

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
git push origin main
```

> **关于 `_plan_index.json` 的说明**：此文件通常已在 A1/A3 工具步骤中提交。
> 若您重新运行了 `plan --resolve`，请一并重新提交。

### Parquet 文件 — Git LFS / 带外存储

根据 `.gitignore`，`baselines/**/input_snapshots/parquet/` 下的 Parquet 文件
**不直接提交至 git**。提交前，请与团队确认适用的存储方案：

- **Git LFS**（默认计划）：`git lfs track "baselines/**/*.parquet"` 然后
  `git add .gitattributes`，再正常添加 Parquet 文件。
- **带外共享存储**（例如 S3、SharePoint）：将 Parquet 文件上传至商定位置，并在
  每个清单条目的 `"path"` 字段中记录 URL。

### 通知 Agent

推送后，更新 `plan.md` 或发布会话消息：

> "G2a 已关闭；全部 9 个 Parquet 文件已导出并通过验证。
>  请 Agent 继续推进 G2b。"

Agent 随后将驱动 `mrc-source-baseline` + `mrc-gold`（G2b）。

---

## 9. 凭据禁止提交检查清单

每次 `git add` / `git commit` 之前，请确认：

- [ ] 暂存文件中无 Vault 令牌。
- [ ] 提交中无真实 Redshift 主机名 — 使用 `<cluster-id-redacted>` 作为替代，或
      若符合组织安全策略，仅在 `redshift_session.cluster` 字段中保留主机名。
- [ ] `.env` 已在 `.gitignore` 中（已确认 — 项目 `.gitignore` 中有此项）。
- [ ] 导出辅助脚本（`~/g2a_export_helper.py`）位于**仓库外部**，且未被暂存。
- [ ] `_manifest.json` 仅在 `redshift_session` 中包含 Redshift **用户名**和
      集群主机名，而非密码。

### 可选：pre-commit 钩子

将以下内容添加至 `.git/hooks/pre-commit`，以捕获意外的令牌泄露：

```bash
#!/bin/sh
if git diff --cached --name-only | xargs grep -l "VAULT_TOKEN\|hvs\.\|password" 2>/dev/null; then
    echo "错误：暂存文件中检测到可能的密钥。正在中止提交。"
    exit 1
fi
```

---

## 10. 故障排查

### Vault 令牌已过期

```
Error authenticating: 403 Forbidden
```

重新认证并导出新令牌：

```bash
vault login -method=<your-method>
export VAULT_TOKEN=$(vault print token)
```

### SQL 占位符未解析

若已解析文件中仍含有 `{expr}` 花括号：

1. 检查 `baselines/mrc/2026-04-30/input_snapshots/_bindings.json` — 该占位符
   键是否列于 `"bindings"` 下？
2. 重新运行 `python tools/freeze_snapshot.py plan --servicer mrc --remit-date 2026-04-30 --resolve`。
3. 若该占位符确实未知，请在重新运行前将其添加至 `_bindings.json`（或传入自定义的
   `--bindings` 文件）。

### 验证失败 C3 — 校验和不匹配

```
C3-file-existence-checksum: sha256_file mismatch (expected a1b2c3d4…, got 9f8e7d6c…)
```

Parquet 文件在写入清单后被修改（例如重新导出但未更新清单）。修复方式：重新导出
受影响的数据集，使 Parquet 文件与清单条目保持一致。

### 验证失败 C6 — 扇出不一致

```
C6-fanout-consistency: _mrc_adv_info_sql has 1 manifest entry (expected 2)
```

`_mrc_adv_info_sql` 查询必须**导出两次** — 分别使用 `fctrdt=2026-05-01` 和
`fctrdt=2026-04-01`。两个变体均须以不同 `logical_name` 出现在 `_manifest.json`
中。请导出缺失的变体并将其条目添加至清单。

### 验证失败 C1 — 孤立清单条目

```
C1-coverage-parity: Orphan in manifest (1): some_unexpected_name
```

清单中存在不对应任何预期数据集（不在 `_plan_index.json` 的 MRC 相关列表中）的条目。
请从清单中删除孤立条目，或若覆盖率扫描已更新以包含新模板，则重新运行
`plan --resolve`。

### 验证失败 C2 — `row_count <= 0`

查询返回 0 行。可能原因：
- `fctrdt` 绑定错误 — 请根据 Redshift 数据核实日期。
- `service` 过滤器错误 — 请确认 `'MRC'` 的大小写是否正确。
- 该周期的表数据为空 — 请与数据团队确认。

---

## 11. 参考资料

- **A6 Redshift 依赖目录**（表名、模式名、凭据路径）：
  [`docs/mrc/_g2a-redshift-dependencies.zh.md`](../docs/mrc/_g2a-redshift-dependencies.zh.md)
- **SQL 覆盖率报告**：`baselines/mrc/2026-04-30/input_snapshots/_export_queries/_coverage.md`
- **决策日志**（G2 重新定义、A1–A6 条目）：
  `decisions.md` — 搜索 `"G2a"` 或 `"G2 redefinition"`
- **计划 § 4.2**（G2a 绑定规范）：
  `C:\Users\jli\.copilot\session-state\4cd52a8e-d034-4def-84a0-04057dd64872\plan.md`
  § 4.2 "G2a — frozen input snapshot specification (binding)"
