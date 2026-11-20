import asyncio
import sys
from contextlib import asynccontextmanager
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
import json

from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.shared.memory import create_client_server_memory_streams
from phase1_mcp import server


@asynccontextmanager
async def transport(script):
    if "--stdio" in sys.argv:
        async with stdio_client(StdioServerParameters(command=sys.executable, args=[str(script)])) as streams:
            yield streams
        return
    async with create_client_server_memory_streams() as ((read, write), (sr, sw)), anyio.create_task_group() as tasks:
        lowlevel = server._lowlevel_server
        tasks.start_soon(lowlevel.run, sr, sw, lowlevel.create_initialization_options())
        try:
            yield read, write
        finally:
            tasks.cancel_scope.cancel()


async def main():
    script = Path(__file__).with_name("phase1_mcp.py")
    async with transport(script) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=10)
            print("MCP initialized", flush=True)
            queries = {
                "overview": "SELECT COUNT(DISTINCT o.order_id) AS orders, SUM(i.price) AS sales, ROUND(SUM(i.price)/COUNT(DISTINCT o.order_id), 2) AS average_value FROM orders o LEFT JOIN order_items i ON o.order_id=i.order_id",
                "categories": "SELECT p.product_category_name, SUM(i.price) AS sales FROM order_items i LEFT JOIN products p ON i.product_id=p.product_id GROUP BY p.product_category_name ORDER BY sales DESC LIMIT 5",
                "item_grain": "SELECT order_id, order_item_id, COUNT(*) AS n FROM order_items GROUP BY order_id, order_item_id ORDER BY n DESC LIMIT 1",
                "order_fk": "SELECT COUNT(*) AS orphan_items FROM order_items i LEFT JOIN orders o ON i.order_id=o.order_id WHERE o.order_id IS NULL"
            }
            results = {}
            for name, sql in queries.items():
                response = await session.call_tool("execute_readonly_sql", {"sql": sql}, read_timeout_seconds=10)
                assert not response.is_error, response
                results[name] = {"sql": sql, "result": response.model_dump(mode="json")}
            for name in ("get_dataset_profile", "get_schema", "get_metric_definition"):
                response = await session.call_tool(name, read_timeout_seconds=10)
                assert not response.is_error, response
            name = "mcp_stdio_smoke.json" if "--stdio" in sys.argv else "mcp_smoke.json"
            path = script.parents[1] / "artifacts/phase1" / name
            path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print("Four MCP tools passed; four SQL results saved")


if __name__ == "__main__":
    asyncio.run(main())





