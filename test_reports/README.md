# Tests Reports Index / 测试报告索引

> 每完成一个阶段的工作（`stage1-*` 章节、`stage2-*` 交付物），就在本目录新增一份测试报告。
> 报告命名：`<todo-id>_YYYY-MM-DD.md`。规则详见 `AGENTS.md` § 6.5。
>
> One test report is added here every time a stage todo (`stage1-*` chapter or
> `stage2-*` deliverable) completes. Filename: `<todo-id>_YYYY-MM-DD.md`. See
> `AGENTS.md` § 6.5 for the rule.

## 报告索引（时间倒序）/ Reports (newest first)

| 日期 / Date | Stage todo-id | 报告 / Report | 结论 / Verdict |
|---|---|---|---|
| 2026-05-17 | stage2-mrc-srs (B2 SRS bilingual) | [stage2-mrc-srs_2026-05-17.md](stage2-mrc-srs_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-rules | [stage1-mrc-rules_2026-05-17.md](stage1-mrc-rules_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-fields | [stage1-mrc-fields_2026-05-17.md](stage1-mrc-fields_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-sheets | [stage1-mrc-sheets_2026-05-17.md](stage1-mrc-sheets_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-dataflow (v2 refine — §6.10 diagram+text rule) | [stage1-mrc-dataflow-v2-refine_2026-05-17.md](stage1-mrc-dataflow-v2-refine_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-dataflow | [stage1-mrc-dataflow_2026-05-17.md](stage1-mrc-dataflow_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-rawdata | [stage1-mrc-rawdata_2026-05-17.md](stage1-mrc-rawdata_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-mrc-toc | [stage1-mrc-toc_2026-05-17.md](stage1-mrc-toc_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | cleanup-a-plan-convention-refresh (A) | — (inline; see decisions.md + progress.md) | ✅ PASS |
| 2026-05-17 | cleanup-c6-registry-servicer-status (B) | [cleanup-c6_2026-05-17.md](cleanup-c6_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-pending-registry | [stage1-pending-registry_2026-05-17.md](stage1-pending-registry_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-shellpoint | [stage1-shellpoint_2026-05-17.md](stage1-shellpoint_2026-05-17.md) | ✅ PASS |
| 2026-05-17 | stage1-carrington | [stage1-carrington_2026-05-17.md](stage1-carrington_2026-05-17.md) | ✅ PASS |
| 2026-05-16 | stage1-overall-flow (v1.1 diagrams expansion) | [stage1-overall-flow-v1.1-diagrams_2026-05-16.md](stage1-overall-flow-v1.1-diagrams_2026-05-16.md) | ✅ PASS |
| 2026-05-16 | stage1-overall-flow | [stage1-overall-flow_2026-05-16.md](stage1-overall-flow_2026-05-16.md) | ✅ PASS |
| 2026-05-16 | stage1-toc | [stage1-toc_2026-05-16.md](stage1-toc_2026-05-16.md) | ✅ PASS |

## 报告模板字段 / Required sections

1. Stage / todo-id / 日期 / 触发人 (agent vs user)
2. 范围（本阶段新增 / 修改的文件清单）
3. 每条检查的：命令、退出码、PASS/FAIL、关键输出节选
4. 失败项分级：P0 / P1 / P2
5. 结论：是否允许进入下一阶段
6. 下一阶段 todo-id + 已通知用户
