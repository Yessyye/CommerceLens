# Technical design and boundaries

BusinessQuestion routing uses regex patterns for overview, category ranking and explicit two-month comparison. The resulting English prompt is fixed for each supported intent. Month values must pass Comparison.validate.

Ordinary planning uses a catalog of four registered tasks and a dependency for category contributions. Diagnostic planning uses diagnostic_tasks, which returns zero or one eligible task. Python selects the decline branch by comparing signed contribution values. Task IDs, dependencies and the four-task budget are checked in plan.

McpAnalystAdapter executes registered SQL and records evidence. MCP tools expose profile, schema, metrics and read-only SQL, but the main adapter invokes only the SQL tool.

SQL tool limits include permitted AST nodes, local table checks, one SELECT, 500 returned rows maximum, read-only DuckDB, external access disabled and a query-interrupt timer. These controls do not provide user authentication or row-level permissions.

Docker review uses the independent baseline.oracle implementation for CSV aggregation. Contributions reuse sales_drivers.decompose with the SQL-produced monthly row. Diagnostic Markdown always comes from diagnostic_report.render_report. Ordinary reports are model-written and carry query IDs.

No queue, cancellation API, persistent graph checkpoint, incremental data ingestion, OpenJudge or multi-Agent execution is implemented.
