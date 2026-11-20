# Repository guide / 项目目录

[English README](../README.md) · [中文 README](../README.zh-CN.md) · [Source-level implementation map](implementation_map.md)

This is the actual public baseline, excluding .git, environments, caches and external datasets. Generated databases and original CSVs are not shipped. The tree groups repetitive historical traces instead of listing every UUID.

```text
CommerceLens/
├── README.md / README.zh-CN.md       English / Chinese entry points
├── LICENSE / DATA_LICENSE.md        Separate code and derived-data terms
├── THIRD_PARTY_NOTICES.md            Vendor and dependency notices
├── requirements-replay.txt          Minimal offline UI requirements
├── requirements-demo.txt            Full demo requirements
├── requirements-phase0.lock         Earlier dependency lock snapshot
├── scripts/
│   ├── start_demo.ps1               Offline-first Streamlit launcher
│   ├── demo_app.py / demo_theme.css UI, replay, charts and stored scores
│   ├── business_questions.py        Supported Chinese intent routing
│   ├── analysis_periods.py          Validated month pairs and SQL builders
│   ├── phase2_planner.py            State, plan/execute graph, model calls
│   ├── analyst_adapter.py           MCP boundary and QueryEvidence
│   ├── phase1_mcp.py                Four tools, SQL policy, DuckDB execution
│   ├── phase1_metrics.yaml          Metric definitions
│   ├── build_phase1_data.py         Local CSV-to-DuckDB preparation
│   ├── sales_drivers.py             Decimal contribution calculation
│   ├── diagnostic_report.py         Fact schema and deterministic report
│   ├── docker_review.py             Graph-external container verification
│   └── check_*.py / check_*.ps1      Existing smoke/readiness utilities
├── commercelens_eval/
│   ├── baseline.py                  Python CSV Oracle
│   ├── golden_sql.py                Ten aggregate-reference checks
│   ├── agent_eval.py                Five normal-mode path/result checks
│   ├── diagnostic_eval.py           Diagnosis and fixed-SQL pilot
│   ├── diagnostic_faults.py         Mock faults and report-field checks
│   ├── sql_policy.py                Rejection and database hash checks
│   └── question_routing.py / regression.py
├── artifacts/
│   ├── phase1/query_results.json    Query definitions and saved aggregates
│   ├── phase2/planner_*.json        Selected historical execution traces
│   └── phase3/*.json                Historical evaluation and pilot results
├── data/README.md                   Source data acquisition instructions
├── docs/
│   ├── architecture.md             Five layers and exact runtime flow
│   ├── technical_design.md         Function-level mechanisms and boundaries
│   ├── evaluation.md               Scoring, commands and experimental limits
│   ├── implementation_map.md        Existing detailed source appendix
│   ├── documentation_review.md     This revision and validation record
│   ├── documentation_validation.json Current offline replay observations
│   ├── assets/*.jpg                Real current-runtime screenshots
│   └── *.json / *.md               Preserved release audit evidence
└── vendor/DeepAnalyze/              Pinned executor, dependencies and LICENSE
```

## Entry points

| Purpose | Entry point |
|---|---|
| UI | `scripts/demo_app.py::main` |
| Chinese business question | `scripts/business_questions.py::interpret_question`, then UI `run_business_question` |
| LangGraph | `scripts/phase2_planner.py::build_workflow`, called by `run` |
| MCP server | `scripts/phase1_mcp.py`, server.run over stdio |
| Independent CSV reference | `commercelens_eval/baseline.py::oracle` |
| Evaluation | Module entry points in `commercelens_eval`; see [commands](evaluation.md) |

The current public baseline omits `.gitignore`, `.env.example` and `.streamlit/config.toml`. The previous directory document listed them despite their absence. This revision corrects the inventory and documents the theme/configuration workaround without adding runtime files.

## Packaging follow-up

The 2026-11-20 upload package restores `.gitignore`, `.env.example` and `.streamlit/config.toml` from the previously audited release candidate. The absence described above refers to the public source baseline. No core business code changed. See [packaging validation](packaging_validation.json).
