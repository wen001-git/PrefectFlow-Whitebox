"""Whitebox tooling: snapshot freezing, diff harness, lineage builder, doc generators.

Modules added incrementally during Phase 1:
    freeze_snapshot.py -- pull Redshift tables to local Parquet
    diff_report.py     -- compare candidate XLSX against gold JSON
    build_lineage.py   -- sqlglot-driven column lineage + Mermaid DAG
    autodoc.py         -- render MkDocs pages from YAML registry
"""
