# Third-party notices

## DeepAnalyze

Repository https://github.com/ruc-datalab/DeepAnalyze

Pinned commit afc697a11675c59683b9f6596c3ab3b3d661182a.

MIT License, Copyright (c) 2025 RUC-DataLab. The unmodified license is preserved at vendor/DeepAnalyze/LICENSE.

The candidate copies these unmodified upstream files at their original relative locations:

- demo/chat_v2/backend_app/settings.py
- demo/chat_v2/backend_app/services/docker_executor.py
- demo/chat_v2/backend_app/services/workspace.py
- demo/chat_v2/backend_app/services/sample_catalog.py
- demo/chat_v2/backend_app/services/__init__.py

scripts/docker_review.py::verify dynamically loads the executor using an isolated package alias. Its dependencies use settings and workspace helpers. sample_catalog is needed for workspace imports; no upstream demo dataset is shipped. The complete DeepAnalyze web application and General analysis loop are outside this candidate.

## Python dependencies

Runtime dependencies are installed from requirements files. No Python environment or package wheel is bundled. docs/dependency_licenses.json records installed distribution versions, metadata notices and license-file names from the audit environment. Metadata is an inventory, not a complete legal interpretation of every transitive dependency.

Key licenses include Streamlit/OpenAI Apache-2.0, pandas BSD-3-Clause, and LangGraph/MCP/SQLGlot/Pydantic MIT. Consult each installed distribution for its complete notices.

## Data and interface references

Olist attribution and data terms are in DATA_LICENSE.md.

Wren AI and Vanna informed the conversational entry design. No Wren AI or Vanna source or image is bundled.

- https://github.com/Canner/WrenAI/tree/legacy/v1
- https://github.com/vanna-ai/vanna

No model weights, original Kaggle archive, third-party screenshot or generated concept artwork is included.

## Principal dependency licenses

requirements-demo.txt includes the pinned environment lock and replay requirements. The lock mixes direct and transitive dependencies. requirements-replay.txt explicitly declares Streamlit. The following principal imports/runtime packages were checked against the installed distribution metadata.

| Package | Audited version | License metadata |
|---|---|---|
| streamlit | 1.67.0 | Apache-2.0 |
| altair | 6.3.0 | BSD-3-Clause |
| pandas | 3.1.1 | BSD-3-Clause |
| langgraph | 1.2.20 | MIT |
| mcp | 2.3.0 | MIT |
| sqlglot | 30.30.0 | MIT |
| duckdb | 2.0.0 | MIT |
| openai | 3.48.0 | Apache-2.0 |
| pyyaml | 6.0.3 | MIT |
| anyio | 4.16.0 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| fastapi | 0.162.2 | MIT |
| pydantic | 2.14.3 | MIT |

All original distribution notices remain applicable. The root MIT license does not relicense Python dependencies or vendor source. This inventory is not exhaustive legal clearance of every transitive package.
