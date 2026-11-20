# Technical design

[Architecture](architecture.md) · [Evaluation](evaluation.md) · [Source-level appendix](implementation_map.md)

Code references use paths relative to this repository. This design describes the implementation at the documented main baseline. It separates task choice, execution constraints, business calculations and evidence.

## 1. Business question routing

`scripts/business_questions.py::interpret_question` applies Unicode normalization, removes selected whitespace/punctuation and uses full regex matches. It returns a `BusinessQuestion(kind, prompt, comparison)` for all-time overview, top categories or two-month comparison.

The prompt sent onward is a fixed English instruction for the recognized family. At least one comparison month needs a year. The explicit dates are converted to `Comparison`; `Comparison.validate` rejects equal months and months outside the allowed range. The range excludes first/last partial months based on dataset boundaries, without checking completeness of every interior month.

Unsupported wording or additional filters raise a user-facing ValueError. Cross-year expressions should specify both years. No conversation state resolves pronouns or follow-up periods.

## 2. Agent State and task catalogs

`scripts/phase2_planner.py::State` carries question, scenario, periods, next_task, evidence, execution_error, drivers, decisions and status. Initial execution supplies the basic fields, with drivers/errors added when needed. answer, usage, report_validation, docker_review and data_purchase_end are attached outside the graph.

`CATALOG` has overview, top_categories, jul_aug_change and category_contributions. `DEPENDENCIES` requires a completed month-difference task before category contributions. The task name jul_aug_change is historical naming; its SQL can compare validated explicit months.

`DIAGNOSTIC_TASKS` additionally supplies monthly_drivers, category_order_declines, seller_sales_declines and seller_order_declines. These task IDs select project-written SQL builders.

## 3. LangGraph Plan–Execute

`build_workflow` compiles exactly two nodes.

| Node | Input/state operation | Output |
|---|---|---|
| plan | Derives completed tasks and eligible choices, calls choose, validates task/reason | next_task, updated decisions and status |
| execute | Invokes adapter, appends evidence, runs decompose for monthly_drivers | Evidence/drivers or execution_failed |

Edges are START→plan, plan→execute/END, execute→plan/END. Each planning decision permits two validity attempts in total. Execution failure ends the graph. No checkpointer, persistent graph resume or multi-Agent coordination is configured.

`run.complete` calls `AsyncOpenAI.chat.completions.create` against the allowed DeepSeek endpoint. It requests up to 1,000 output tokens, a client timeout of 45 seconds and no client-level retries. The endpoint/model are read from configuration. `choose` asks for JSON task/reason and supplies the allowed IDs, existing evidence and feedback.

## 4. Normal versus diagnostic planning

In normal mode, the model chooses among eligible registered tasks. A category-contribution task is eligible only after a negative month difference. Once any evidence exists, finish becomes an allowed decision.

In diagnosis mode, `diagnostic_tasks` returns an empty list or one task. First it requires monthly_drivers. If total merchandise change is nonnegative, Python stops. Otherwise it compares signed order-volume and average-value contributions, selects the corresponding category breakdown, then selects sellers within the leading non-null category. Python ends the sequence after those results or when no suitable category exists.

The LLM still returns a task and reason in diagnostic planning, but receives a singleton allowed set. Branch selection and stopping are determined by Python. Model choice among alternatives is exercised more directly by the normal-mode evaluation suite.

## 5. Harness-style execution governance

This project implements a collection of execution checks in its own functions. The term Harness describes their role around the Agent.

| Mechanism | Actual location | Enforcement |
|---|---|---|
| Task catalog | `phase2_planner.CATALOG/DIAGNOSTIC_TASKS` | Defines supported task IDs |
| Dependency validation | `build_workflow.plan` | Filters by DEPENDENCIES, completed IDs and observed decline |
| Planning validation | `plan` | Requires allowed task and nonempty reason |
| Execution budget | `plan`, MAX_TASKS=4 | Stops after four executed evidence tasks |
| Invalid-choice correction | `plan` | Two decision attempts, then invalid_plan |
| Tool retry | `analyst_adapter.McpAnalystAdapter.execute` | One retry for supported timeout/connection errors |
| SQL AST validation | `phase1_mcp.execute_readonly_sql` | SELECT, AST-node, table and JOIN constraints |
| Read-only execution | Same tool | read_only=True, external access disabled |
| Result validation | `McpAnalystAdapter.execute` | Checks query ID, columns, row widths and nonnegative elapsed time |
| Evidence recording | Adapter and `phase2_planner.run` | SQL, ID, rows, attempts, timing and decisions |
| Failure handling | execute node / review_evidence / run | Typed execution/review errors and status when caught |

The four-task budget counts executed tasks. Model correction and report calls are additional requests. Errors returned by tools, nonretryable MCP errors and malformed evidence are handled differently from retryable transport failures. General unexpected exceptions may escape.

## 6. MCP tool integration

`scripts/phase1_mcp.py` registers four tools on MCPServer.

| Tool | Parameters | Returned structure |
|---|---|---|
| get_dataset_profile | dataset_id, default olist | Cached PROFILE with table counts, columns and purchase range |
| get_schema | Optional exact table_filter | Mapping of matching tables to profile information |
| get_metric_definition | Optional list metric_ids | YAML metric definitions |
| execute_readonly_sql | sql and limit=100 | columns, rows, query_id and elapsed_seconds |

`run` starts the server with `StdioServerParameters`, `stdio_client` and `ClientSession`. MCP initialization waits up to 45 seconds. `McpAnalystAdapter` invokes only execute_readonly_sql, with a 20-second read timeout. Registered metadata tools are available, but the main planner does not use them for autonomous schema discovery.

## 7. SQL safety and DuckDB

`execute_readonly_sql` uses `sqlglot.parse(..., read="duckdb")`. It accepts one Select and traverses the AST using an explicit node whitelist. Tables must be known local tables without catalog/schema qualifiers, and joins require ON.

The SQL string is limited to 10,000 characters. The returned row limit is 1–500. A wrapper SELECT adds a parameterized LIMIT. This limits output size while the aggregate may still scan the full table.

Every call opens DuckDB with read_only=True, external access disabled, threads=2 and memory_limit=512MB. A `Timer(15, conn.interrupt)` interrupts query execution. Connection startup and overall process duration are outside that timer's full guarantee.

`build_phase1_data.main` reads nine CSVs into a new snapshot or reuses an existing database. `run` retrieves overview/ranking query definitions from shipped query_results.json and comparison queries from `Comparison`.

## 8. E-commerce metrics and diagnostic rules

`Comparison.monthly_query` counts distinct order IDs from orders LEFT JOIN order_items and sums merchandise prices. The population includes all recorded order states, and merchandise excludes freight. Category/seller breakdown counts distinct orders in its own group. Group counts may overlap.

`sales_drivers.decompose` takes baseline/target order counts and merchandise values. Let n be orders and a be merchandise per order.

```text
volume contribution = (n1 - n0) × (a0 + a1) / 2
average-value contribution = (s1 - s0) - volume contribution
```

The volume contribution rounds to cents using ROUND_HALF_UP. The residual average contribution keeps the displayed sum balanced. This explains the arithmetic composition of a difference. Investigating causes such as inventory, traffic or promotion requires additional observations.

## 9. Evidence recording

`analyst_adapter.QueryEvidence` includes task, sql, query_id, columns, rows, elapsed_seconds and attempts. `run` serializes the result to artifacts/phase2/planner_UUID.json. decisions stores selected task/reason pairs. usage stores model token statistics.

The diagnostic report cites all evidence query IDs, and the UI expands each SQL/result. Query IDs are UUIDs rather than content hashes. Trace writing happens at the end of run, so failures that escape before it may leave no complete trace. The JSON write is not atomic.

## 10. Docker review and CSV Oracle

After `ainvoke` returns, `run` optionally calls `review_evidence` through asyncio.to_thread. It starts docker_review.py with a 100-second timeout. `verify` creates a unique temporary workspace, copies three CSVs plus oracle/decompose code, and invokes the vendored DeepAnalyze `execute_python_in_docker`.

The image is python:3.11-slim with network=none explicitly set and inspected. Upstream defaults supply a read-only root filesystem, writable workspace, non-root user and CPU/memory/PID restrictions. Those default settings can be overridden through environment variables. Python execution receives a 25-second deadline, excluding preparation.

`baseline.oracle` independently aggregates CSV with dictionaries, sets and Decimal. `review_evidence` compares rows and records matched flags linked to query IDs. `cells_match` uses Decimal-normalized equality for native numbers and ordinary equality for other values.

The container computes drivers by reusing the same decompose function on the SQL-produced monthly row passed in driver_row. Independent CSV aggregation checks that row separately. Shared decomposition cannot detect every error in the common formula implementation.

DeepAnalyze reuse is limited to its pinned container executor and import dependencies. The General model-generated-code loop is not part of the current page path.

## 11. Report generation

In diagnosis mode, `report_facts` extracts verified amounts, periods, direction, unit and query IDs. The model is asked to copy those fields into JSON. `validate_facts` rejects missing/changed fields and unsupported extra fields. Whether this succeeds or fails, `render_report` generates the final Markdown from expected facts.

Normal mode calls the model to write Chinese prose with evidence IDs. Its full prose is not subjected to the diagnosis fact schema. The UI's `show_business_summary` builds its own deterministic summary from saved values. Old traces lacking data_purchase_end use a fixed Olist archive date fallback.

## 12. Runtime boundaries and reproduction notes

`demo_app.run_business_question` uses a Python subprocess with a 300-second parent timeout and Docker enabled. Advanced mode invokes asyncio.run directly and lets the user select Docker review. Historical replay reads JSON and displays stored review flags.

This checkout's online baseline omits .env.example, .gitignore and .streamlit/config.toml. Documentation retains a copyable inline .env template and describes Light theme selection rather than changing runtime files in this documentation task.

Remaining work includes incremental data ingestion, task queues, idempotency, cancellation cleanup, authentication, tenant isolation, persistent graph recovery, generalized question routing and sentence-level semantic evaluation. The current flow has no implementation of OpenJudge, general Grader Adapter, vector retrieval or enterprise semantic layer.

Packaging follow-up: the upload package restores the three missing configuration files from the audited candidate. The baseline absence above remains a historical observation; the packaged runtime source is unchanged.
