# Documentation revision and verification / 文档重构验收记录

## Scope and baseline

- Public source baseline: `d60bbb4074199b71f5c2a272680c235f9a13e974`, cloned from `Yessyye/CommerceLens`.
- Local review branch: `docs/architecture-and-evaluation`.
- A separate clone preserves the original project and the earlier release candidate's uncommitted work.
- Changes are limited to README, documentation and genuine screenshots. No source, requirements, SQL, evaluation algorithm, vendor code or historical result has been changed.
- No commit, push, repository setting update or GitHub Release has been performed in this revision.

## What changed and why

| File | Change |
|---|---|
| README.md | English business-first overview, real demo, five-layer Mermaid, contributions, stack roles, constrained workflow, scores, offline-first start, limits |
| README.zh-CN.md | Matching Chinese entry point with identical cases, architectural facts and evaluation boundaries |
| architecture.md | Five responsibility layers, control/data/evidence/evaluation arrows, exact two-node graph, post-graph Docker and separate evaluation |
| technical_design.md | Twelve source-backed sections covering routing, state, model choices, governance, MCP, SQL, metrics, evidence, Docker, reports and runtime limits |
| evaluation.md | Exact predicates, historical artifacts, commands, mock fault limits, 4/5→5/5 caveat and Oracle independence boundary |
| project_structure.md | Concise actual tree and entry points; removes nonexistent dotfiles from the old inventory |
| assets/*.jpg | Seven direct screenshots of the current running UI; no generated visuals or code changes |
| documentation_validation.json | Machine-readable observations from this revision's offline checks |
| documentation_review.md | Review scope, verification, remaining gaps and suggested About text |

The existing implementation_map.md and all historical audit records are retained as appendices. Audit documents describe their earlier release-candidate context; they are not evidence that every file survived the later GitHub web upload.

## Source verification anchors

| Conclusion | Verified source |
|---|---|
| Only plan and execute are LangGraph nodes | scripts/phase2_planner.py::build_workflow |
| Diagnostic paths come from Python, with singleton candidate sets | phase2_planner.py::diagnostic_tasks/plan |
| Model selects a bounded task and reason; normal report is generated | phase2_planner.py::run/choose/complete |
| Main query path calls only the SQL MCP tool | scripts/analyst_adapter.py::McpAnalystAdapter.execute |
| SQL is parsed and restricted before read-only DuckDB | scripts/phase1_mcp.py::execute_readonly_sql |
| Contribution math uses Decimal and is shared in review | scripts/sales_drivers.py::decompose; scripts/docker_review.py::verify |
| Container review follows graph completion | phase2_planner.py::run/review_evidence |
| Diagnostic Markdown is always deterministic | phase2_planner.py::run; scripts/diagnostic_report.py::render_report |
| CSV aggregation is a different implementation | commercelens_eval/baseline.py::oracle |
| Normal Agent checks paths, numbers and ID presence | commercelens_eval/agent_eval.py::score_trace |
| Eleven checks use mocked faults and changed report fields | commercelens_eval/diagnostic_faults.py::main |

## Actual runtime checks: 2026-11-20

[Machine-readable observations](documentation_validation.json) record this checkout using the existing Python 3.11.9 interpreter with Streamlit 1.67.0 on Windows build 26200. Python's platform string reports Windows-10; this string alone is not a reliable marketing-name identification.

- Streamlit AppTest switched A, B and C without exceptions.
- Business summary, three report/evidence/evaluation tabs, query IDs, SQL blocks, result tables and stored score cards were inspected.
- SQL blocks: A=3, B=3, C=1. Visible merchandise changes: −266,357.20; −152,469.04; +13,434.31 BRL.
- Actual Streamlit server at localhost:8523 returned HTTP 200 for `/` and `/_stcore/health`.
- Browser interaction independently switched all three cases, opened evidence and evaluation, and captured screenshots. No warning/error entries were observed in the browser console at the earlier inspection.
- No DeepSeek calls, Docker start/pull, raw CSV or DuckDB were involved.
- This used an existing environment. The separate [fresh-install record](fresh_replay_validation.json) remains historical; no new clean-environment installation is claimed.
- No full live benchmark suites were rerun.

The temporary validation script initially looked for an HTML-rendered heading in AppTest's title collection; that locator was corrected to the actual offline button before the successful run. Project code was not changed to make a check pass.

## Screenshot provenance

| Asset | Actual view |
|---|---|
| demo_home.jpg | Chinese question entry |
| demo_overview.jpg | Case A business summary |
| demo_diagnostic.jpg | Case A contribution and category/seller drill-down |
| demo_sql.jpg | Case A expanded SQL evidence |
| demo_evidence_eval.jpg | Saved SQL, Agent and policy score display |
| demo_case_b.jpg | Case B average-value-led decline |
| demo_case_c.jpg | Case C growth, with decline drill-down stopped |

All captures come from the unmodified baseline UI on localhost:8523. Light theme was selected in the page menu. JPEG is the browser's returned format. Seller IDs belong to the already-shipped public derived fixtures; screenshots contain no private keys or local configuration values. A displayed Docker-passed badge is historical metadata, not a container run performed by this revision.

## Checks and remaining issues

The companion local QA output records Markdown link/image-target checks, Git whitespace checks and unchanged-source checks. Mermaid diagrams were reviewed for structure and syntax, but no GitHub-hosted renderer validation was performed. External links have not all been re-requested; local target existence is the link check's scope.

1. The uploaded baseline lacks `.gitignore`, `.env.example` and `.streamlit/config.toml`. Docs explain inline configuration and Light theme. Adding runtime/configuration files is outside this task.
2. User-facing questions are regex-limited; diagnostic branches are rule-selected. Neither arbitrary autonomous analytics nor multi-Agent coordination is implemented.
3. Query ID presence is not semantic entailment. Shared decomposition is not an independently implemented formula check. Small fixed suites do not prove broad generalization or production reliability.
4. Source CSVs and database are absent by design. Full live installation, current API credentials and Docker runtime remain unverified in this revision.
5. Historical release manifests list their original candidate, not this new documentation set. Regenerate a release manifest only during an explicitly approved packaging pass.

## Suggested GitHub About (not applied)

**Description:** An auditable e-commerce analytics Agent demo: controlled LangGraph workflows, MCP read-only SQL, execution evidence and independent evaluation. Offline Streamlit replay included.

**Topics:** `python`, `langgraph`, `streamlit`, `mcp`, `duckdb`, `sqlglot`, `ecommerce-analytics`, `agent-evaluation`, `llm-agent`.

These settings are suggestions only. Local review is complete before any publication approval.

## Approved packaging follow-up

The user subsequently requested a complete upload resource package. Only the separate upload directory restores the three omitted configuration files from the audited candidate; README instructions were adjusted accordingly. The source review clone remains unchanged. Packaging validation is recorded in [packaging_validation.json](packaging_validation.json). No remote action was performed.
