"""Insert a "Business purpose / 业务用途" subsection at the head of each
MRC sheet chapter in sheets.{zh,en}.md and fields.{zh,en}.md.

The block is unnumbered (`### Business purpose / 业务用途`) so existing
subsection numbering (X.1, X.2 ...) is preserved and no cross-reference
needs updating.

Idempotent: skips if the marker already present in the chapter body.
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "mrc"

MARKER = "BUSINESS-PURPOSE-V1"  # invisible idempotency tag (HTML comment)

# --------------------------------------------------------------------------
# Per-sheet business content. Two registers: SHEETS_* (rendering / report-tab
# angle) and FIELDS_* (per-column / lineage angle). Each value is the full
# subsection body (no `### ...` heading line — heading is added by the
# inserter so EN/ZH heading wording stays consistent).
# --------------------------------------------------------------------------

SHEETS_ZH = {
    "MRC_Summary_check": """
- **业务用途 / Business purpose**：整张 Validation Report 的"封面页"——把当期
  MRC 资产组合的 13 个汇总金额（principal received、interest received、escrow 与
  corporate advance 变化、service fee、other fees、sub-remit / total-remit、期初 /
  期末余额）压成一行，让 ops / treasury / 监管在打开 workbook 的第一眼就能判断
  "这份 remit 是否对得上"。
- **它要回答的业务问题 / Business question it answers**：
    - 本月 servicer 报来的合计数字是否落在我们对这个资产组合的预期范围内？
    - SQL 聚合本身是否跑通（13 个 sum 是否非空、是否合理）？
    - 后续 per-loan 页（General / Advance / ServiceFee）的"宏观背景"是什么？
- **数据口径 / Population**：所有 `servicer='MRC'` 的有效贷款，按 `remit_date` 的
  当月口径汇总，**没有** per-loan 维度——任何一行 = 整个 MRC 投资组合。
- **典型读者 / Audience**：servicing oversight 分析师做"先扫一眼合计"的快速检查；
  treasury 做现金对账时把 `subremit` / `totremit` 与银行入账对一遍。
- **为什么 0 高亮列 / Why no highlights**：本 sheet 只做"投资组合级汇总"，**不**做
  remit-vs-daily 的 per-loan 比对，没有 diff 列就没有高亮——这是设计意图，不是 bug。
- **常见失败场景 / Common failure scenarios**：
    - SQL 聚合丢列 → 某个 sum 为空 / 0（不是高亮触发，而是数字不合理需要人工眼）；
    - 期末余额与下月期初余额对不上（跨月连续性需在外部脚本对账）；
    - `subremit + totremit` 与 servicer wire 入账金额不符（落到 treasury 流程）。
- **风险 / 对账动机 / Risk and reconciliation motivation**：本表是 servicer remit
  与内部账本"宏观一致"的第一道质量门；这一行不对，下面 per-loan 页查得再细也只能
  发现局部异常，无法捕获系统性偏差。
""",

    "MRC_General_Check": """
- **业务用途 / Business purpose**：per-loan 主对账页——把每笔贷款的 6 个核心维度
  （利率、下一付款日、期初余额、期末余额、deferred 本金、deferred 利息、计划 P&I）
  在 servicer remit 与内部 daily 快照之间逐列做差，**任何非零差异**都被涂红，指引
  ops 立刻知道"这笔贷款需要人工核查"。
- **它要回答的业务问题 / Business question it answers**：
    - servicer 报的利率是不是和我们 daily 系统里记录的合同利率一致？（reset bug、
      modification 没同步）
    - 下一付款日是否漂移？（deferment、bankruptcy plan 没同步）
    - 期初 / 期末余额是不是和内部 amortization 一致？（多扣 / 漏扣本金）
    - 计划 P&I（`pandi_schedule_diff`）是否吻合？——这是判断"servicer 是否按计划在收"
      的关键，比 actual P&I 更稳定。
- **数据口径 / Population**：当期 MRC 所有有效贷款 × 7 个差异维度；行数 = 投资
  组合贷款数。
- **典型读者 / Audience**：servicing oversight 分析师、loan accounting、investor
  reporting；任何一行红 → 触发 servicer 工单。
- **高亮规则的业务理由 / Why these 7 columns are highlighted**：
    - `intrate_diff` —— 利率错 = 后续所有 interest 计算都错；
    - `nextduedate_diff` —— 付款日错 = delinquency 状态错；
    - `begbal_diff` / `endbal_diff` —— 余额对不上是 master 风险信号；
    - `deferredprincipal_diff` / `deferredint_diff` —— 反映 modification / forbearance
      执行差异；
    - `pandi_schedule_diff` —— 计划应收差异是"servicer 是否按合同收账"的核心信号。
- **为什么 `pandi_diff_remitvsdaily` 不高亮（gap 1）/ Why actual-P&I diff is NOT
  highlighted**：actual 收款本身就会偏离计划（partial pay / prepay 都合法），高亮
  会噪音爆表；schedule view 才是稳定信号。这是**业务有意决策**，已在 § 6.1 gap 1
  与 1.4 字段定义 (1.4-fields.zh.md) § 5 中显式标注。
- **常见失败场景 / Common failure scenarios**：
    - servicer 系统 reset 重置利率但 daily 未刷 → 7 行同步亮红；
    - bankruptcy plan modification 没回灌 daily → due date + balances 联动亮红；
    - 月末 cut-off 不同（servicer 用 EOM，daily 用 BoM+1）→ 全表偏差 1 天。
- **风险 / 对账动机 / Risk motivation**：本表是 MRC validation 的"心脏"——
  ~ 80% 的实际 ops 工单来自这一页的红色 cell。
""",

    "MRC_Advance_Check": """
- **业务用途 / Business purpose**：per-loan 的 advance 余额对账页——专门跟踪
  servicer 为了让违约贷款保持 current 而垫付的资金（escrow advance、recoverable
  corporate advance、non-recoverable corporate advance、total），并把 remit 报数
  与 daily 快照在 4 个 advance bucket 上逐笔做差。
- **它要回答的业务问题 / Business question it answers**：
    - servicer 当月垫了多少 escrow（taxes & insurance）？daily 系统知道吗？
    - recoverable corp advance（未来可向借款人追回）和 non-recoverable（要从
      investor pool 吃掉）分类是否正确？误分类直接影响损失分摊。
    - 累计 total advance 是否突破合同 cap？是否触发 servicer override / stop-advance？
    - prior daily 与 current daily 的差额（`*_chg_daily`）能不能解释 remit 报的
      `escadv_remit` / `nonrecovadvance_remit`？
- **数据口径 / Population**：当期所有有 advance 活动的贷款（一般是 delinquent、
  REO、bankruptcy 状态）；典型行数远小于 General_Check（绝大多数 performing loan
  没有 advance）。
- **典型读者 / Audience**：advance recovery 团队（追回 recoverable corp adv）、
  treasury（现金影响）、loss-mitigation（non-recov 直接计 loss）。
- **高亮规则的业务理由 / Why these 4 diff columns are highlighted**：每个 advance
  bucket 都对应不同的会计处理 / 损失分摊；分错一桶意味着 P&L 错位，比利率错更敏感。
- **常见失败场景 / Common failure scenarios**：
    - servicer 把 non-recov 报成 recov（少计 loss）；
    - escrow advance 被错记成 corp advance（影响 escrow shortage 计算）；
    - prior daily 漏更新 → `*_chg_daily` 全 0，与 `*_remit` 形成大 diff。
- **命名不对称提示 / Naming asymmetry note (gap 3)**：第 14 列 `recovcorpadv_diff_*`
  与第 10-13 列的 `reccorpadvance_*_daily` 前缀不同（`recov` vs `rec`）——这在 SQL
  侧是有意区分的，详见 § 7.1 gap 3 与 1.4 字段定义 (1.4-fields.zh.md) § 6。
- **风险 / 对账动机 / Risk motivation**：advance 是 servicing 流程中**现金影响最直接、
  会计分类最敏感**的环节；本表是 advance recovery 与 loss reserving 的对账锚点。
""",

    "MRC_ServiceFee_Check": """
- **业务用途 / Business purpose**：per-loan 的 service-fee 对账页——把 servicer 在
  remit 里报的当月服务费（`servicefee_remit_raw`）与我们内部 `port.portmonth` 的
  应付服务费（`servicefee_portmonth`）逐笔做差，**任何非零差异**触发高亮。这是
  MRC validation 唯一一个**revenue side**（我们付钱给 servicer）的对账页。
- **它要回答的业务问题 / Business question it answers**：
    - 我们这个月应该付给 MRC 多少 service fee？实际报多少？差多少？
    - 如果 servicer 多收了（diff < 0），是不是我们 portmonth 算少了，还是 servicer
      用错费率？
    - 如果 servicer 少收了（diff > 0），是漏报，还是某些贷款因为 status 变化不再
      计费？
- **数据口径 / Population**：所有同时存在于 servicer remit 和 `port.portmonth` 的
  贷款；**外连缺失的 loan 会得到 `servicefee_diff = NULL`，NULL 不高亮（已知静默漏报，
  gap 4）**。
- **典型读者 / Audience**：servicer-fee 应付账款组、revenue ops；任何红行 = 在结
  servicer 月度账单前必须解释。
- **设计意图 / Design intent**：本页只有 1 个 diff 列，因为 service fee 只有"对 / 不对"
  一个维度；其它列（`fctrdt`、`loanid`、`mrc_ln`、`dealid`、两个 raw amount）都是
  上下文，给人审计用。
- **常见失败场景 / Common failure scenarios**：
    - 月中费率变更但 servicer 用了旧 rate；
    - portmonth 里 loan 因为 paid-off 不再有行，diff 变 NULL → 不高亮（已知 gap，
      需要外部 NULL-report 兜底）；
    - servicer 把 sub-servicing fee 重复计入。
- **风险 / 对账动机 / Risk motivation**：service fee 是 servicer 直接从 collections
  里扣留的现金，本表是我们对扣留金额的"账单核对"——红行不查，钱就少了。
""",

    "MRC_Adv_Info": """
- **业务用途 / Business purpose**：bucket × description × transaction-code 维度的
  **聚合活动**页，附带月环比 `amt_MoM`——不是 per-loan 对账，而是给 ops 看
  "这个月的 advance / disbursement 活动 mix 是否正常"的趋势页。
- **它要回答的业务问题 / Business question it answers**：
    - 本月各 bucket（advance / recovery / disbursement / fee 等）的总金额分别是
      多少？
    - 与上月相比变动多大？（`amt_MoM = amt / amt_1m - 1`）
    - 是否出现新的 `transaction_code`？（新 code 出现往往是 servicer 系统升级 /
      新业务上线信号）
- **数据口径 / Population**：当期所有 MRC advance / activity 流水按 (bucket,
  description, transaction_code) 聚合；典型行数 = bucket 数 × txn_code 种类，
  远小于贷款数。
- **典型读者 / Audience**：ops investigation、anomaly detection、portfolio
  analytics；用来检测系统性异常，而不是单笔工单。
- **为什么 0 高亮列 / Why no highlights**：本页是**描述性 / 信息性**的，没有"对 vs
  错"的概念——分析人员靠肉眼扫 `amt_MoM` 列发现异动（例如某 bucket MoM > 10×
  就值得查）。
- **关键技术注意 / Technical note for readers (gap 5)**：`amt_MoM` 保留 validator
  侧的 `±inf` / `NaN`（出现于 `amt_1m = 0` 时），且 `data_type_format` **不**给
  float 套 number_format，所以 Excel 里 `inf` 会按 openpyxl 默认方式落入（具体表达
  待 1.6 Baseline XLSX 行为 (1.6-baseline.zh.md) 时验证）。
- **常见失败场景 / Common failure scenarios**：
    - 出现陌生的 `transaction_code` → 业务上往往是 servicer 系统改造未通知；
    - 某 bucket `amt_MoM` 突变（如 +500%）→ 触发 ops 排查；
    - `amt_1m = 0` 导致 `amt_MoM = inf` → 在 Excel 里出现极大数字（需读者知道是
      除零产物）。
- **风险 / 对账动机 / Risk motivation**：本页提供"系统性异常的早期信号"，与前 4 页
  的"逐笔对账"互补——前 4 页查得到的是已经发生的差异，本页查得到的是"模式在
  漂移"。
""",
}

SHEETS_EN = {
    "MRC_Summary_check": """
- **Business purpose**: cover page of the whole Validation Report — collapses
  the 13 portfolio-level monetary totals for the current remit period
  (principal received, interest received, escrow & corporate advance changes,
  service fee, other fees, sub-remit / total-remit, beginning / ending
  balance) into a single row, so ops / treasury / oversight can answer
  "did this remit roughly line up?" at first glance.
- **Business questions answered**:
    - Do this month's servicer-reported totals fall within expectation for
      this MRC portfolio?
    - Did the SQL aggregation itself complete cleanly (all 13 sums non-null
      and plausible)?
    - What is the macro context against which per-loan pages (General,
      Advance, ServiceFee) should be read?
- **Population**: every active loan where `servicer='MRC'`, aggregated at the
  `remit_date` month grain; **no per-loan dimension** — every row in this
  sheet = the entire MRC portfolio.
- **Audience**: servicing-oversight analyst doing a 5-second "totals sniff
  test"; treasury reconciling `subremit` / `totremit` against bank wires.
- **Why 0 highlight columns**: this sheet performs only portfolio-level
  summation; it does NOT perform remit-vs-daily per-loan comparison, so
  there are no diff columns and hence no highlights — by design, not a bug.
- **Common failure scenarios**:
    - SQL aggregation drops a column → some sum is null / 0 (does not trigger
      a highlight; readers have to eyeball "implausible total");
    - Ending balance fails to roll into next month's beginning balance
      (caught by an external cross-month script);
    - `subremit + totremit` ≠ servicer wire — caught downstream by treasury.
- **Risk / reconciliation motivation**: this single row is the first
  quality gate for "is the servicer remit macro-consistent with our books?"
  — if this row is wrong, no amount of per-loan drill-down on the next
  pages can recover the systemic miss.
""",

    "MRC_General_Check": """
- **Business purpose**: the **primary** per-loan reconciliation page —
  compares every loan across 7 core dimensions (interest rate, next-due
  date, beginning balance, ending balance, deferred principal, deferred
  interest, scheduled P&I) between the servicer remit and our internal
  daily snapshot. **Any non-zero difference is highlighted red**, signalling
  ops "this loan needs manual investigation".
- **Business questions answered**:
    - Is the rate reported by the servicer the same as the contract rate in
      our daily system? (catches reset bugs, missed modifications.)
    - Has the next-due date drifted? (deferment / bankruptcy-plan changes
      not propagated.)
    - Do beginning / ending balances reconcile against our amortization?
      (over- or under-applying principal.)
    - Does the **scheduled** P&I (`pandi_schedule_diff`) line up? — a more
      stable signal than actual P&I for "is the servicer collecting per
      contract?".
- **Population**: every active MRC loan in the period × 7 diff dimensions;
  row count = portfolio loan count.
- **Audience**: servicing oversight, loan accounting, investor reporting;
  any red cell → servicer ticket.
- **Why these 7 columns are highlighted (business rationale)**:
    - `intrate_diff` — wrong rate cascades into every downstream interest
      calc;
    - `nextduedate_diff` — wrong due date corrupts delinquency status;
    - `begbal_diff` / `endbal_diff` — balance mismatch is a master risk
      signal;
    - `deferredprincipal_diff` / `deferredint_diff` — reveals execution gaps
      in modification / forbearance;
    - `pandi_schedule_diff` — scheduled-receivable diff is the core "is
      the servicer collecting per contract?" indicator.
- **Why `pandi_diff_remitvsdaily` is NOT highlighted (gap 1)**: actual
  receipts legitimately deviate from schedule (partial pays, prepays), so
  highlighting that column would explode the noise floor; the schedule view
  is the stable signal. This is an **intentional business decision**, also
  flagged at § 6.1 gap 1 and 1.4 Field Definitions (1.4-fields.en.md) § 5.
- **Common failure scenarios**:
    - Servicer system resets a rate but daily wasn't refreshed → 7 rows
      light up simultaneously;
    - Bankruptcy plan modification not back-loaded into daily → due date +
      balances all flag together;
    - Month-end cut-off mismatch (servicer uses EOM, daily uses BoM+1) →
      systematic 1-day offset across all rows.
- **Risk motivation**: this page is the **heart** of MRC validation —
  roughly 80% of real-world ops tickets originate from red cells on this
  tab.
""",

    "MRC_Advance_Check": """
- **Business purpose**: per-loan **advance** balance reconciliation page —
  tracks the money the servicer fronts to keep delinquent loans current
  (escrow advance, recoverable corporate advance, non-recoverable corporate
  advance, total) and diffs each of the 4 advance buckets between remit
  and daily.
- **Business questions answered**:
    - How much escrow (taxes & insurance) did the servicer advance this
      month? Does daily know?
    - Are recoverable corp advances (recoverable from the borrower later)
      vs. non-recoverable (a charge against the investor pool) classified
      correctly? Misclassification flows straight into loss allocation.
    - Has cumulative total advance hit a contractual cap? Should a
      servicer-override / stop-advance be triggered?
    - Does the prior→current daily delta (`*_chg_daily`) explain the
      `escadv_remit` / `nonrecovadvance_remit` reported in remit?
- **Population**: every loan with advance activity in the period (typically
  delinquent, REO, or bankruptcy loans); row count is far smaller than
  General_Check (most performing loans have no advance).
- **Audience**: advance-recovery team (chasing recoverable corp adv),
  treasury (cash impact), loss-mitigation (non-recov is direct loss).
- **Why these 4 diff columns are highlighted (business rationale)**: each
  advance bucket has a distinct accounting / loss-allocation treatment;
  misclassifying one bucket means P&L is mis-stated — more sensitive than
  a rate diff.
- **Common failure scenarios**:
    - Servicer reports non-recov as recov (understating loss);
    - Escrow advance misposted as corp advance (corrupts escrow-shortage
      calc);
    - Prior daily missed an update → `*_chg_daily` all 0, large diff vs
      `*_remit`.
- **Naming asymmetry note (gap 3)**: column 14 `recovcorpadv_diff_*` uses
  a different prefix than columns 10–13 (`reccorpadvance_*_daily`) —
  `recov` vs `rec`. The SQL side distinguishes them intentionally; see
  § 7.1 gap 3 and 1.4 Field Definitions (1.4-fields.en.md) § 6.
- **Risk motivation**: advances are the **single most cash-sensitive and
  most accounting-classification-sensitive** step in MRC servicing; this
  sheet is the reconciliation anchor for advance-recovery and loss-reserve
  workflows.
""",

    "MRC_ServiceFee_Check": """
- **Business purpose**: per-loan **service-fee** reconciliation page —
  compares the servicing fee the servicer reports in remit
  (`servicefee_remit_raw`) against the fee we expect to pay per our
  internal `port.portmonth` (`servicefee_portmonth`); **any non-zero diff
  is highlighted**. This is the **only revenue-side** reconciliation page
  in MRC validation (the only page about money WE owe THEM).
- **Business questions answered**:
    - How much service fee should we pay MRC this month? What did they
      actually report? What is the gap?
    - If servicer reported high (diff < 0), did our portmonth under-calculate,
      or did they apply the wrong fee rate?
    - If servicer reported low (diff > 0), did they miss loans, or did
      status changes legitimately stop fee accrual?
- **Population**: all loans that exist in both servicer remit AND
  `port.portmonth`; **outer-join misses produce `servicefee_diff = NULL`,
  which is NOT highlighted — known silent gap, see gap 4**.
- **Audience**: servicer-fee accounts payable team, revenue ops; any red
  row = must be explained before the monthly servicer invoice is paid.
- **Design intent**: only 1 diff column because service fee is a single
  "right / wrong" dimension; the other columns (`fctrdt`, `loanid`,
  `mrc_ln`, `dealid`, two raw amounts) are context for the auditor.
- **Common failure scenarios**:
    - Mid-month fee-rate change but servicer used the old rate;
    - Loan paid off so missing from `port.portmonth`, diff becomes NULL →
      not highlighted (gap 4, requires an external NULL-report safety net);
    - Servicer double-counts sub-servicing fee.
- **Risk motivation**: service fee is cash the servicer withholds directly
  from collections; this page is our line-item invoice check — if a red
  row isn't investigated, we are short cash.
""",

    "MRC_Adv_Info": """
- **Business purpose**: bucket × description × transaction-code
  **aggregate activity** page with month-over-month — NOT a per-loan
  reconciliation, but an ops-monitoring page that answers "is the mix of
  advance / disbursement activity this month consistent with historical
  pattern?"
- **Business questions answered**:
    - What is the total dollar amount per bucket (advance / recovery /
      disbursement / fee, etc.) this month?
    - How does it compare to last month? (`amt_MoM = amt / amt_1m − 1`.)
    - Are any new `transaction_code` values appearing? (New codes often
      signal a servicer system upgrade or new product activity.)
- **Population**: all MRC advance / activity flows in the period,
  aggregated by `(bucket, description, transaction_code)`; row count =
  number of buckets × number of txn codes, far smaller than the loan
  count.
- **Audience**: ops investigation, anomaly detection, portfolio analytics
  — looking for systemic anomalies, not single-loan tickets.
- **Why 0 highlight columns**: this sheet is **descriptive /
  informational**; there is no "right vs wrong" concept, so analysts
  eyeball the `amt_MoM` column for spikes (e.g. a bucket > 10× MoM is
  worth investigating).
- **Key technical note for readers (gap 5)**: `amt_MoM` preserves the
  validator-side `±inf` / `NaN` (occurring when `amt_1m = 0`), and
  `data_type_format` does NOT apply a number_format to float, so Excel
  lands `inf` per openpyxl default (exact representation to be confirmed
  in 1.6 Baseline XLSX Behavior (1.6-baseline.en.md)).
- **Common failure scenarios**:
    - Unfamiliar `transaction_code` appears → usually a servicer system
      change shipped without notice;
    - Bucket `amt_MoM` jumps (e.g. +500%) → triggers an ops investigation;
    - `amt_1m = 0` produces `amt_MoM = inf` → renders as a giant number
      in Excel (readers must recognize this as a divide-by-zero artifact).
- **Risk motivation**: this page provides **early signals of systemic
  drift**, complementary to the per-loan reconciliation on the previous
  4 sheets — the per-loan pages catch differences that have already
  happened; this page catches **patterns that are shifting**.
""",
}

FIELDS_ZH = {
    "MRC_Summary_check": """
- **业务用途 / Business purpose**：本节给 13 个 portfolio-level money sum 加 1
  个 `asofdate` stamp 提供**逐列血缘**——上游对应 SQL 哪一列、走的哪种聚合、
  在 1.3 Sheet 渲染层 (1.3-sheets.zh.md) § 5 里如何渲染。它的目标读者是想反问
  "这一列到底从哪儿来"的工程师 / auditor / 重写者。
- **它要回答的业务问题 / Business question it answers**：当 Summary 页某个汇总
  数字"看着不对"时，能否在 30 秒内定位到上游 SQL 的具体投影行？能否解释为什么
  这一列是 money 而不是 float？
- **与 1.3-sheets.zh.md 的分工 / Division with 1.3-sheets.zh.md**：1.3-sheets.zh.md § 5 描
  述"页面长什么样、为谁服务"；本节描述"每个数字是哪个 SQL 表达式产生的"——
  reverse-engineering 时优先读本节，业务分析时优先读 1.3-sheets.zh.md。
- **数据口径 / Population**：每列对应 SQL 的一个 `SUM(...)` 投影，作用域
  = 整个 MRC 投资组合的当期。
- **典型读者 / Audience**：Stage 2 重写者（要保持 cell-identity）、数据 audit
  组、上游 SQL 改动的 reviewer。
- **风险 / 对账动机 / Risk motivation**：13 个 money 列承载 reporting 与 treasury
  对账的全部依赖；任一列血缘断裂（SQL 改名 / 投影顺序变化 / round 策略变化）
  都会导致 cell-identity 测试失败。
""",
    "MRC_General_Check": """
- **业务用途 / Business purpose**：本节给 35 列（含 7 个高亮 diff 列）提供
  **逐列血缘 + transform 公式 + 业务含义**——是"为什么这一列在 General sheet
  上"问题的权威答案。
- **它要回答的业务问题 / Business question it answers**：
    - 高亮的 7 个 diff 列各自的计算公式是什么？为什么 `pandi_diff_remitvsdaily`
      存在但不高亮？
    - `intrate_diff` 是百分点差还是相对差？取整到几位？
    - `nextduedate_diff` 为什么声明为 `float` 但其实是天数差？（gap 2）
- **与 1.3-sheets.zh.md 的分工 / Division with 1.3-sheets.zh.md**：1.3-sheets.zh.md § 6 描
  述渲染层（哪列高亮、用什么样式）；本节描述上游来源与变换公式（哪列来自哪个
  CTE、走哪种 join、用什么 transform）——两侧 cross-reference 紧密耦合。
- **数据口径 / Population**：每列对应一笔贷款的一个属性 / 差异；行数 = MRC 投资
  组合贷款数。
- **典型读者 / Audience**：Stage 2 重写者、validator-逻辑 reviewer、加新 diff 列
  时的设计者。
- **风险 / 对账动机 / Risk motivation**：7 个高亮列承载 ~80% 实际 ops 工单的源头；
  本节的 Transform 公式是 ops 工单中"为什么红"的法律依据，**任何 transform
  公式变更**都必须在 decisions.md 留痕。
""",
    "MRC_Advance_Check": """
- **业务用途 / Business purpose**：本节给 27 列（含 4 个高亮 advance-bucket diff
  列）提供**逐列血缘 + 计算公式 + 业务含义**——着重澄清 advance bucket 之间的
  会计含义差异（recov vs non-recov vs escrow vs total）。
- **它要回答的业务问题 / Business question it answers**：
    - 4 个 advance diff 列的计算口径是什么？是 `remit − daily_curr` 还是
      `remit − daily_chg`？
    - 第 14 列 `recovcorpadv_diff_*` 与第 10-13 列的 `reccorpadvance_*` 前缀
      不同到底是什么意思？（gap 3）
    - 哪些列只来自 daily 系统？哪些列只来自 remit？哪些是计算列？
- **与 1.3-sheets.zh.md 的分工 / Division with 1.3-sheets.zh.md**：1.3-sheets.zh.md § 7 解
  释"为什么这 4 列要高亮"（业务理由）；本节解释"这 4 列具体怎么算出来"（公式）。
- **数据口径 / Population**：每列对应一笔有 advance 活动的贷款的一个 advance
  bucket 属性 / 差异。
- **典型读者 / Audience**：advance recovery 团队的工程对接人、会计分类争议
  调解人、bucket 重命名时的影响评估者。
- **风险 / 对账动机 / Risk motivation**：advance bucket 分类直接决定 P&L 与
  loss reserve 计算；本节的 Transform 公式是会计分类争议的客观依据，
  **bucket 公式改动必须经 decisions.md 留痕 + investor 沟通**。
""",
    "MRC_ServiceFee_Check": """
- **业务用途 / Business purpose**：本节给 8 列（仅 1 个高亮 diff 列）提供
  **逐列血缘**——核心是讲清 `servicefee_diff` 的计算公式与 `port.portmonth`
  外连缺失会产生 NULL 的逻辑分支。
- **它要回答的业务问题 / Business question it answers**：
    - `servicefee_diff` = `servicefee_remit_raw − servicefee_portmonth` 还是
      反向？取整规则？
    - portmonth 缺 loan 时 diff = NULL 的具体 SQL 路径在哪？（gap 4 的代码位置）
    - `fctrdt`（SQL 过滤值）与 `asofdate`（remit_date stamp）的关系是什么？
- **与 1.3-sheets.zh.md 的分工 / Division with 1.3-sheets.zh.md**：1.3-sheets.zh.md § 8 解
  释"这页是 revenue-side 唯一的对账页"（业务定位）；本节解释"diff 列是怎么
  算的、NULL 怎么来的"（公式 + 边界）。
- **数据口径 / Population**：每行对应一笔同时存在于 remit 与 portmonth 的贷款；
  外连缺失会出现在 sheet 但 diff = NULL。
- **典型读者 / Audience**：servicer 应付账款组的工程对接人、NULL-report 兜底
  脚本的作者、portmonth 数据质量的 reviewer。
- **风险 / 对账动机 / Risk motivation**：service fee 是 servicer 直接扣留的现金，
  本节的 diff 公式与 NULL 路径是月度应付账款核对的法律依据，**改动需双签**
  （revenue ops + investor reporting）。
""",
    "MRC_Adv_Info": """
- **业务用途 / Business purpose**：本节给 7 列（bucket / description /
  transaction_code / amt / amt_1m / amt_MoM / asofdate）提供**逐列血缘 + 聚合
  公式**——核心是讲清 `amt_MoM` 的除零行为（产生 `±inf`）与 bucket / txn_code
  的来源映射。
- **它要回答的业务问题 / Business question it answers**：
    - `amt_MoM` 的公式（`amt / amt_1m − 1`）在 `amt_1m = 0` 时如何处理？
    - 哪些 (bucket, description, transaction_code) 组合是已知合法集合？新出现
      的组合从哪发现？
    - `amt` 与 `amt_1m` 分别来自哪个 CTE？是同一聚合 key 在不同月份的快照吗？
- **与 1.3-sheets.zh.md 的分工 / Division with 1.3-sheets.zh.md**：1.3-sheets.zh.md § 9 解
  释"这页是趋势页，不做对账"（业务定位 + 高亮策略）；本节解释"每列怎么算"
  （聚合 + 除零）。
- **数据口径 / Population**：按 (bucket, description, transaction_code) 聚合
  的当期活动行；与前 4 页"贷款级"维度不同。
- **典型读者 / Audience**：anomaly detection 的设计者、上游 transaction_code
  字典维护者、`±inf` 渲染问题的排查者。
- **风险 / 对账动机 / Risk motivation**：本节明确 `amt_MoM` 的 `±inf` 来源，
  是下游"为什么 Excel 里出现极大数字"问题的权威答案；改动除零策略需在
  decisions.md 留痕。
""",
}

FIELDS_EN = {
    "MRC_Summary_check": """
- **Business purpose**: this section provides **per-column lineage** for the
  13 portfolio-level money sums plus the `asofdate` stamp — which SQL
  projection produced each column, what aggregation was applied, and how
  the column renders in 1.3 Sheet Rendering Layer (1.3-sheets.en.md) § 5. The
  target reader is the engineer / auditor / rewriter who wants to ask
  "where does this column actually come from?".
- **Business question it answers**: when a summary number "looks wrong",
  can you locate the exact upstream SQL projection line in under 30
  seconds? Can you explain why this column is `money` rather than `float`?
- **Division with 1.3-sheets.en.md**: 1.3-sheets.en.md § 5 describes "what the page
  looks like and who it serves"; this section describes "which SQL
  expression produced each number" — when reverse-engineering, read this
  first; when business-analysing, read sheets first.
- **Population**: each column = one SQL `SUM(...)` projection, scope =
  entire MRC portfolio for the current period.
- **Audience**: Stage 2 rewriters (must preserve cell-identity), data audit
  team, reviewers of upstream SQL changes.
- **Risk motivation**: the 13 money columns carry the full set of reporting
  and treasury-reconciliation dependencies; a lineage break in any column
  (SQL rename, projection reorder, round-strategy change) immediately
  breaks the cell-identity test.
""",
    "MRC_General_Check": """
- **Business purpose**: this section provides **per-column lineage +
  transform formula + business meaning** for all 35 columns (including the
  7 highlighted diff columns) — the authoritative answer to "why is this
  column on the General sheet?".
- **Business questions answered**:
    - What is the calculation formula for each of the 7 highlighted diff
      columns? Why does `pandi_diff_remitvsdaily` exist but stay
      un-highlighted?
    - Is `intrate_diff` a percentage-point delta or a relative delta?
      Rounded to how many decimals?
    - Why is `nextduedate_diff` declared `float` when it's really a
      day-count delta? (gap 2.)
- **Division with 1.3-sheets.en.md**: 1.3-sheets.en.md § 6 describes the rendering
  layer (which columns highlight, what style); this section describes the
  upstream source and transform formula (which CTE each column comes from,
  which join, which transform) — the two sides cross-reference tightly.
- **Population**: each column = one attribute / difference for one loan;
  row count = MRC portfolio loan count.
- **Audience**: Stage 2 rewriters, validator-logic reviewers, designers
  adding a new diff column.
- **Risk motivation**: the 7 highlighted columns are the source of ~80% of
  real-world ops tickets; the transform formulas here are the
  legal-of-record explanation for "why is this red?" in any ticket — **any
  formula change** must be recorded in decisions.md.
""",
    "MRC_Advance_Check": """
- **Business purpose**: this section provides **per-column lineage +
  calculation formula + business meaning** for all 27 columns (including
  the 4 highlighted advance-bucket diff columns) — with special focus on
  clarifying the accounting distinction between advance buckets (recov vs
  non-recov vs escrow vs total).
- **Business questions answered**:
    - What is the calculation grain for the 4 advance diff columns? Is it
      `remit − daily_curr` or `remit − daily_chg`?
    - What does the prefix asymmetry between col 14 `recovcorpadv_diff_*`
      and cols 10–13 `reccorpadvance_*` actually mean? (gap 3.)
    - Which columns come only from daily, which only from remit, and which
      are calculated?
- **Division with 1.3-sheets.en.md**: 1.3-sheets.en.md § 7 explains "why these 4
  columns are highlighted" (business rationale); this section explains
  "how those 4 columns are actually computed" (formula).
- **Population**: each column = one advance-bucket attribute / diff for one
  loan that has advance activity.
- **Audience**: engineering counterpart of the advance-recovery team,
  mediators of accounting-classification disputes, impact assessors for
  bucket renaming.
- **Risk motivation**: advance bucket classification directly drives P&L
  and loss-reserve calc; the transform formulas in this section are the
  objective evidence in accounting-classification disputes — **bucket
  formula changes require a decisions.md entry + investor communication**.
""",
    "MRC_ServiceFee_Check": """
- **Business purpose**: this section provides **per-column lineage** for
  the 8 columns (only 1 highlighted diff column) — the core deliverable is
  making the `servicefee_diff` formula and the `port.portmonth` outer-join
  NULL-producing branch explicit.
- **Business questions answered**:
    - Is `servicefee_diff` = `servicefee_remit_raw − servicefee_portmonth`
      or the reverse? Rounding rule?
    - Where exactly in the SQL is the path that produces `diff = NULL` when
      portmonth is missing the loan? (Code location of gap 4.)
    - What is the relationship between `fctrdt` (SQL filter value) and
      `asofdate` (remit_date stamp)?
- **Division with 1.3-sheets.en.md**: 1.3-sheets.en.md § 8 explains "this is the
  only revenue-side reconciliation page" (business framing); this section
  explains "how the diff column is computed and how NULLs arise" (formula
  + edge cases).
- **Population**: each row = one loan present in both remit and portmonth;
  outer-join misses appear in the sheet with `diff = NULL`.
- **Audience**: engineering counterpart of the servicer-fee A/P team,
  authors of the NULL-report safety-net script, reviewers of portmonth
  data quality.
- **Risk motivation**: service fee is cash the servicer withholds directly;
  the diff formula and NULL path documented here are the legal-of-record
  explanation for the monthly A/P reconciliation — **changes require dual
  sign-off** (revenue ops + investor reporting).
""",
    "MRC_Adv_Info": """
- **Business purpose**: this section provides **per-column lineage +
  aggregation formula** for the 7 columns (bucket / description /
  transaction_code / amt / amt_1m / amt_MoM / asofdate) — the core
  deliverable is making `amt_MoM`'s divide-by-zero behaviour (which
  produces `±inf`) and the (bucket, description, transaction_code) source
  mapping explicit.
- **Business questions answered**:
    - How is `amt_MoM` (`amt / amt_1m − 1`) handled when `amt_1m = 0`?
    - Which `(bucket, description, transaction_code)` tuples are the known
      legal set? How are newly-appearing tuples surfaced?
    - From which CTEs do `amt` and `amt_1m` come? Are they the same
      aggregation key snapshotted in different months?
- **Division with 1.3-sheets.en.md**: 1.3-sheets.en.md § 9 explains "this is a
  trend page, not a reconciliation page" (business framing + highlight
  strategy); this section explains "how each column is computed"
  (aggregation + divide-by-zero).
- **Population**: per-period activity aggregated by (bucket, description,
  transaction_code); a different grain from the per-loan dimension on the
  preceding 4 sheets.
- **Audience**: designers of anomaly-detection logic, maintainers of the
  upstream transaction_code dictionary, debuggers of `±inf` rendering
  issues.
- **Risk motivation**: this section pins down the source of `amt_MoM`'s
  `±inf`, which is the authoritative answer downstream to "why is there
  a giant number in Excel?"; any change to the divide-by-zero strategy
  requires a decisions.md entry.
""",
}

# Map (file, sheet_name) → (heading_label, body) for the inserted block.
HEADINGS = {
    "zh": "业务用途 / Business purpose",
    "en": "Business purpose / 业务用途",
}

# Sheet anchor patterns: in sheets.* the H2 is `## N. \`<name>\``; in fields.*
# it is `## N. \`<name>\` fields`. We use a single anchor regex per file group.

SHEETS_FILE_ANCHOR = re.compile(
    r"^(## \d+\. `(MRC_Summary_check|MRC_General_Check|MRC_Advance_Check|MRC_ServiceFee_Check|MRC_Adv_Info)`)\s*$",
    re.MULTILINE,
)
FIELDS_FILE_ANCHOR = re.compile(
    r"^(## \d+\. `(MRC_Summary_check|MRC_General_Check|MRC_Advance_Check|MRC_ServiceFee_Check|MRC_Adv_Info)` fields)\s*$",
    re.MULTILINE,
)


def insert_into(path: Path, anchor: re.Pattern, content_map: dict, lang: str) -> int:
    text = path.read_text(encoding="utf-8")
    out_parts = []
    cursor = 0
    inserted = 0
    for m in anchor.finditer(text):
        sheet = m.group(2)
        if sheet not in content_map:
            continue
        # Skip if marker already present in the chapter body (idempotency).
        # Chapter body = from this H2 line up to the next H2.
        next_h2 = re.search(r"^## \d+\. ", text[m.end():], re.MULTILINE)
        chapter_end = m.end() + (next_h2.start() if next_h2 else len(text) - m.end())
        chapter_body = text[m.start():chapter_end]
        if MARKER in chapter_body:
            continue
        # Append text up to and including the H2 line + the blank line after it.
        # We insert the new subsection right after the H2 (before the next
        # `### X.1` heading).
        out_parts.append(text[cursor:m.end()])
        out_parts.append("\n\n")
        out_parts.append(f"<!-- {MARKER} -->\n")
        out_parts.append(f"### {HEADINGS[lang]}\n")
        body = content_map[sheet].strip("\n")
        out_parts.append(body)
        out_parts.append("\n")
        cursor = m.end()
        inserted += 1
    out_parts.append(text[cursor:])
    new_text = "".join(out_parts)
    if inserted:
        path.write_text(new_text, encoding="utf-8")
    return inserted


def main():
    targets = [
        (DOCS / "1.3-sheets.zh.md", SHEETS_FILE_ANCHOR, SHEETS_ZH, "zh"),
        (DOCS / "1.3-sheets.en.md", SHEETS_FILE_ANCHOR, SHEETS_EN, "en"),
        (DOCS / "1.4-fields.zh.md", FIELDS_FILE_ANCHOR, FIELDS_ZH, "zh"),
        (DOCS / "1.4-fields.en.md", FIELDS_FILE_ANCHOR, FIELDS_EN, "en"),
    ]
    for path, anchor, cmap, lang in targets:
        n = insert_into(path, anchor, cmap, lang)
        print(f"{path.relative_to(ROOT)}: inserted {n}")


if __name__ == "__main__":
    main()
