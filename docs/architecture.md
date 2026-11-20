# Runtime architecture

The current graph is defined by scripts/phase2_planner.py::build_workflow. START enters plan. plan routes to execute or END. execute routes to plan unless execution_failed, which ends the graph.

The page has two live execution paths. Business question submission launches the existing planner CLI in a subprocess with Docker review enabled. Advanced analysis calls run directly through asyncio and has a Docker checkbox. Historical views only read existing traces.

run creates a DeepSeek client, stdio MCP session and McpAnalystAdapter. Tool queries use SQLGlot and read-only DuckDB. Optional review happens after graph execution, followed by report handling and JSON persistence.

The detailed call graph and symbol map are in [implementation_map.md](implementation_map.md).
