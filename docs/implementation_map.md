# CommerceLens 代码级实现地图

核对日期为 2026-11-19。用途是开发者学习与技术面试。本文依据当前源码和已保存 JSON 产物编写。此次只读源码与产物，未执行模型请求、Docker 作业、测试或数据构建。命令均供后续复现，文中的通过数表示历史产物记录。

项目根目录为 `<project-root>`。下文所有相对路径均相对这个根目录。文中符号名可以直接在对应源码搜索。配置只说明读取机制，不展示密钥或本机私有配置内容。

## 1. 项目目录、入口与职责

排除原始数据、虚拟环境、缓存、安装器和 Git 内部文件后的核心结构如下。artifacts 只列逻辑产物。

```text
CommerceLens/
├── scripts/
│   ├── start_demo.ps1
│   ├── demo_app.py
│   ├── demo_theme.css
│   ├── business_questions.py
│   ├── analysis_periods.py
│   ├── build_phase1_data.py
│   ├── phase2_planner.py
│   ├── analyst_adapter.py
│   ├── phase1_mcp.py
│   ├── phase1_metrics.yaml
│   ├── sales_drivers.py
│   ├── diagnostic_report.py
│   ├── docker_review.py
│   ├── check_release_readiness.ps1
│   ├── check_phase1_mcp.py
│   ├── check_phase1_model_mcp.py
│   ├── check_phase1_numbers.py
│   ├── check_phase2_routing.py
│   ├── check_upstream_protocol.py
│   └── phase0_isolated_analysis.py
├── commercelens_eval/
│   ├── baseline.py
│   ├── golden_sql.py
│   ├── agent_eval.py
│   ├── diagnostic_eval.py
│   ├── diagnostic_faults.py
│   ├── sql_policy.py
│   ├── question_routing.py
│   └── regression.py
├── vendor/DeepAnalyze/demo/
│   ├── chat_v2/backend_app/settings.py
│   ├── chat_v2/backend_app/services/docker_executor.py
│   ├── chat_v2/backend_app/services/workspace.py
│   └── deepanalyze_general/deepanalyze_general.py
├── artifacts/
│   ├── phase0/  历史阶段零验收
│   ├── phase1/  DuckDB、数据概况、预存查询与结果
│   ├── phase2/  planner_*.json 分析轨迹
│   └── phase3/  独立评测结果
├── .streamlit/config.toml
├── requirements-demo.txt
├── requirements-replay.txt
├── requirements-phase0.lock
└── reports/  说明文档，本文不据此认定实现
```

| 核心文件与符号 | 职责和入口 |
|---|---|
| `scripts/start_demo.ps1` | 启动 `python -m streamlit run scripts/demo_app.py`，监听 127.0.0.1，默认端口 8501 |
| `scripts/demo_app.py::main` | Streamlit 页面入口，分发业务问数、历史报告、评测与对照、高级分析 |
| `demo_app.py::show_questions/run_business_question` | 表单提交、规则路由、以子进程运行分析脚本，读取 stdout 最后一行中的轨迹路径。子进程等待上限 300 秒 |
| `demo_app.py::show_question_result/show_business_summary/show_trace` | 展示摘要、贡献图、报告、SQL、复核与评测。摘要由 Python 计算与拼接 |
| `demo_app.py::show_pilot/show_evaluation` | 读取历史试点和评分文件，不在页面中重新运行评测 |
| `scripts/business_questions.py::BusinessQuestion/interpret_question` | 正则全匹配三类中文问题，转换成固定英文任务提示及可选 Comparison |
| `scripts/analysis_periods.py::Comparison` | 月份范围验证、月份差额、两期指标和品类/卖家 SQL 模板 |
| `scripts/build_phase1_data.py::main` | 检查九个 CSV，首次构建 DuckDB 和概况。已有数据库时复用现有库并重新生成概况，未实现增量合并或自动刷新 |
| `scripts/phase2_planner.py::run/build_workflow` | LangGraph 与模型分析主入口。CLI 的 `__main__` 调用 `asyncio.run(run(...))` |
| `scripts/analyst_adapter.py::McpAnalystAdapter/review_evidence` | 查询调用边界、重试、证据校验、启动 Docker 复核子进程 |
| `scripts/phase1_mcp.py` 的 `server` 与 `__main__` | 注册四个 MCP 工具，`server.run()` 启动服务 |
| `scripts/sales_drivers.py::decompose` | Decimal 两因素贡献拆解 |
| `scripts/diagnostic_report.py::report_facts/validate_facts/render_report` | 构造可信事实、校验模型字段、确定性生成诊断 Markdown |
| `scripts/docker_review.py::verify` | 准备临时复核数据和脚本，调用 DeepAnalyze Docker 执行器 |
| `commercelens_eval/*.py` | 评测入口分别是模块内 main 或 unittest 主入口，细目见第 6 节 |
| `scripts/check_release_readiness.ps1` | 顺序运行路由、CSV、SQL、安全、故障、Agent 回放及 Docker 轨迹回放。可选 IncludeMcp 检查 stdio |

业务问数和高级分析入口不同。`show_questions` 走独立 Python 子进程，默认带 `--docker-review`。高级分析在 Streamlit 内直接 `asyncio.run(run(...))`，Docker 复核由勾选框控制。历史报告只读已有轨迹。依据为 `demo_app.py::main/show_questions/run_business_question`。

## 2. LangGraph 与模型调用

### 2.1 State、Node、Edge

`scripts/phase2_planner.py::State(TypedDict)` 声明以下字段。

| 字段 | 含义 |
|---|---|
| question、scenario、periods | 标准化问题、场景描述、基准月和目标月 |
| next_task | 下一任务 ID 或 finish |
| evidence | QueryEvidence 列表 |
| execution_error | 错误任务、代码和说明 |
| drivers | 贡献拆解结果 |
| decisions | task 与 reason 组成的决策列表 |
| status | 执行状态 |

TypedDict 字段声明本身不做运行时验证。初始状态未提供 execution_error 和 drivers，后续节点按需增加。answer、usage、report_validation、docker_review、data_purchase_end 是图外在 `run` 中追加的字段。代码没有配置 checkpointer、持久化图恢复或多轮对话记忆。

`build_workflow` 只注册两个节点。

- `plan` 生成 available 和 valid_ids，调用 choose，最多尝试两次有效选择。校验 task 和非空 reason，通过后追加 decisions。
- `execute` 调用 AnalystAdapter.execute，追加 evidence。monthly_drivers 执行后调用 decompose。遇到 AnalystError 或无可比较订单时写 execution_failed。

实际边为 `START → plan`，`plan → execute 或 END`，`execute → plan 或 END`。route 在 next_task 为 finish 时结束。execute 写 execution_failed 时结束。上限 MAX_TASKS=4 是已执行任务数量上限，模型纠正请求和报告请求不包含在这四项内。依据为 `phase2_planner.py::build_workflow`。

一次页面问题的路径为 `main → show_questions → interpret_question → run_business_question → CLI run → build_workflow(...).ainvoke → MCP 查询 → 可选复算 → 报告 → 保存 JSON → 页面读取`。模型和 Docker 复核不作为独立 LangGraph 节点注册。

### 2.2 DeepSeek 请求位置

`phase2_planner.py::run` 内创建 `AsyncOpenAI` 客户端，以兼容接口调用 DeepSeek。内部 `complete(system, payload, structured=False)` 调用 `client.chat.completions.create`。

- 客户端 timeout=45、max_retries=0，请求 max_tokens=1000。结构化请求使用 json_object，并请求关闭 thinking。
- `choose` 通过 complete 获取 JSON task/reason。传入问题、场景、候选任务、既有 evidence 和校验反馈。
- 诊断结束时再请求模型返回与 verified_facts 相同的字段。普通模式则请求中文自然语言答案。
- 模型 usage 追加到 trace.usage。模型 ID 来自配置，不在源码固定。

配置来源依次为 COMMERCE_LLM_CONFIG、项目本地指针文件、项目 .env。端点仅接受 DeepSeek 官方域名的两种指定路径。此处只描述 `run` 的读取逻辑，不展示配置内容。

### 2.3 模型与规则的实际分工

| 行为 | 决定者与代码 |
|---|---|
| 中文意图、月份、对比方向 | `business_questions.py::interpret_question` 正则规则；原始问题转为固定英文 prompt |
| 全量指标和 Top 5 SQL | `run` 从 phase1/query_results.json 取预存 SQL |
| 月份 SQL、维度、品类限制 | `analysis_periods.py::Comparison` 模板和校验 |
| 普通模式选 overview、top_categories、jul_aug_change 或后续 category_contributions | `build_workflow.plan → choose` 的模型选择，受依赖与涨跌条件限制 |
| 普通模式何时 finish | 已有证据后 finish 才加入允许列表，模型可选 |
| 诊断模式下一步 | `diagnostic_tasks` 的确定性规则，最多返回一个任务 |
| 拆解公式、按订单还是金额下钻 | `decompose` 和 `diagnostic_tasks` |
| 诊断卖家筛选品类 | `run.seller_query.build` 取品类结果第一行 |
| 诊断最终 Markdown | `diagnostic_report.render_report`，始终执行 Python 渲染 |
| 普通模式最终文字 | `run.complete` 模型生成，主要靠提示词要求引用与限定解释 |
| 页面经营摘要和下一步提示 | `demo_app.py::show_business_summary` 的固定规则 |

诊断模式所有实际发给模型的规划步骤都只有一个任务可选。初始仅 monthly_drivers。金额不下降时 available 为空，Python 直接结束，不调用模型选择 finish。下跌时比较两个有符号贡献值，volume_contribution 小于 average_contribution 时走订单量分支，否则走金额分支，平局走金额分支。品类完成后，仅在第一行存在且品类非空时给出对应卖家任务。卖家完成后结束。依据为 `diagnostic_tasks` 和 `plan`。

诊断报告模型字段校验通过与否只影响 report_validation，最终都调用 render_report。因此“仅模型校验失败才模板兜底”的描述与当前实现不符。普通模式的自由文本没有同等级的字段校验。依据为 `run` 的 diagnosis 分支与 else 分支。

## 3. MCP、SQLGlot 与 DuckDB

四个真实注册工具都位于 `scripts/phase1_mcp.py`，使用 `@server.tool()`。

| 工具 | 参数 | 返回值 |
|---|---|---|
| get_dataset_profile | dataset_id: str，默认 olist | PROFILE，含源表行数、列结构和 purchase_range。其他 dataset_id 抛 ValueError |
| get_schema | table_filter: str 或 None | 表名到 PROFILE 表信息的字典，表信息含 rows 与 columns。过滤是精确表名匹配，无匹配返回空字典 |
| get_metric_definition | metric_ids: list[str] 或 None | 从 phase1_metrics.yaml 读取的指标定义映射。无参数返回全部，未知键没有专门错误包装 |
| execute_readonly_sql | sql: str，limit: int 默认 100 | columns、rows、query_id、elapsed_seconds |

主 Agent 只调用 execute_readonly_sql。前三个工具已注册，但 `McpAnalystAdapter.execute` 未调用它们做模型自主 schema 发现。主编排使用 `StdioServerParameters + stdio_client + ClientSession` 拉起本地 Python 服务，以标准输入输出通信。初始化等待 45 秒，工具 read_timeout_seconds=20。依据为 `phase2_planner.py::run` 与 `analyst_adapter.py::execute`。

`phase1_mcp.py::execute_readonly_sql` 的执行约束如下。

1. limit 必须在 1–500，SQL 长度不超过 10000。
2. `sqlglot.parse(sql, read="duckdb")` 解析后必须只有一条顶层 Select。
3. 遍历 AST，以 ALLOWED_NODES 白名单逐节点检查。表必须是数据概况中已有表，禁止 catalog/db 前缀和外部表表达式。Join 必须具有 ON。
4. 每次查询新开 `duckdb.connect(..., read_only=True)`，关闭 enable_external_access，设置 threads=2、memory_limit=512MB。
5. 外层包裹 SELECT，再参数化 LIMIT。limit 限制返回行数，聚合扫描仍可能遍历全表。
6. `Timer(15, conn.interrupt)` 在连接建立后启动，finally 中取消并等待定时器。它是查询中断机制，无法证明所有连接建立和进程退出耗时都严格小于 15 秒。
7. 返回行经 JSON 序列化标准化，query_id 用 uuid4().hex 生成，elapsed_seconds 统计连接与执行阶段。

非特定类型 SQL 的完整安全覆盖无法由五个安全用例证明，详见第 6 节。DB 只读约束也不等于用户权限、租户隔离或行级权限。

## 4. DeepAnalyze 与 Docker 复用边界

### 4.1 页面实际复用哪些上游代码

`scripts/docker_review.py::verify` 动态加载本地 vendor 的 `demo/chat_v2/backend_app/services/docker_executor.py`，通过 review_backend 包别名避免启动上游 Web App。其传递依赖包括 `backend_app/settings.py` 和 `services/workspace.py`。

直接调用上游 `execute_python_in_docker`、`_container_name_for_session` 和 `release_session_container`。本次只读 git 核对显示 vendor HEAD 为 `afc697a11675c59683b9f6596c3ab3b3d661182a`，工作树状态无变更输出。提交作者与具体上游补丁来源未做远端核验，标为待核实。

本项目自行编写的复核部分为 `docker_review.verify` 的数据复制、verify.py 构造、inspect 检查及 JSON 返回，以及 `analyst_adapter.review_evidence` 的结果比较、错误映射。业务聚合来自本项目 baseline.oracle。

另有阶段零实验 `scripts/phase0_isolated_analysis.py::main`，加载 `demo/deepanalyze_general/deepanalyze_general.py`，定义继承 DeepAnalyzeVLLM 的 Analyst，把 execute_code 接到 Docker。这个生成代码循环与当前页面主流程分离，不能据此声称页面使用 General 自主编程分析。

### 4.2 一次 Docker 复核

1. `review_evidence` 启动 docker_review.py 子进程，等待上限 100 秒。
2. `verify` 创建独立 TemporaryDirectory 与 UUID session，把 orders、order_items、products 三个 CSV，以及 baseline.py、sales_drivers.py 复制进去。
3. 写 verify.py，调用 oracle 获取参考结果，并输出 JSON。使用 python:3.11-slim，关闭自动构建，网络指定 none，禁止不安全的本地执行。
4. 上游 `ensure_execution_backend_ready` 校验 session 工作目录与容器身份。新容器通过 `docker run -d` 启动，内部 keepalive shell 循环保持存活。
5. `execute_python_in_docker` 使用 `docker exec` 运行 Python 脚本，捕获 stdout 和 stderr。verify.py 用 stdout 打印 JSON，verify 再 json.loads。
6. `verify` 用 docker inspect 取 container_id、image_id，显式核对 NetworkMode==none，在 finally 调 release_session_container，退出临时目录。

stdout/stderr 会被上游拼接。即使 exit code 为零，额外 stderr 文本也可能导致 JSON 解析失败。超时、取消和非零退出会返回上游的标记字符串，随后由项目复核层转成失败。依据为 `docker_executor.execute_python_in_docker`、`docker_review.verify` 和 `review_evidence`。

### 4.3 隔离与限制

| 限制 | 实现和适用范围 |
|---|---|
| 断网 | verify 强制设置 network=none，inspect 再核对 |
| 根文件系统只读 | 上游 settings.docker_read_only 默认 True，ensure_execution_backend_ready 加 --read-only |
| 工作目录 | 每次会话单独挂载到 /workspace，挂载权限 rw。上游 workspace.resolve_workspace_root 与 validate_session_id 校验目录/session |
| 临时目录 | 默认 /tmp 为 256m tmpfs |
| 运行用户 | 默认 1000:1000，非 root |
| 权限 | --cap-drop ALL 与 no-new-privileges |
| CPU、内存、PID | 上游默认 1 CPU、1g、256 PID |
| Python 执行时间 | verify 传 25 秒。上游轮询 communicate，超时终止 docker exec 并停止容器 |
| Docker 命令 | _run_docker_command 默认 60 秒，部分检查使用 20/30 秒。25 秒不包含前面的容器准备时间 |
| 总等待 | review_evidence 子进程上限 100 秒，页面问数子进程上限 300 秒 |

除网络等 verify 明确设置项外，其余为 `settings.py` 的可被环境变量覆盖的默认值。本次没有检查实时容器环境，当前每项实效均需运行态核验。workspace.py 中的上传文件总量/数量检查并未被 verify 的 shutil.copyfile 路径调用，不能声称复核工作区有强制磁盘配额。execute_python_in_docker 本身也未按 settings.execution_output_max_chars 截断输出。外层 subprocess 超时未提供全进程树清理保证，异常终止后的残留回收待核实。

## 5. CSV 参考实现、数值比较与 Evidence

### 5.1 CSV → Python 结果

`commercelens_eval/baseline.py::rows` 使用 csv.DictReader 读表。`oracle` 建立 order_id→下单年月、product_id→品类映射，然后逐条遍历商品明细。

- 金额使用 Decimal(price) 加总，按品类与月份累积。
- 月订单数来自订单映射，包含全部订单状态。品类与卖家订单数用 set(order_id) 去重。
- 月差额以目标月加、基准月减计算。
- 品类下降项过滤负数后排序取前五。卖家只取对应下降品类的首项范围，未分类首项返回空卖家结果。
- 返回 overview、top_categories、jul_aug_change、category_contributions、monthly_drivers、category_order_declines、seller_sales_declines、seller_order_declines。

它不使用 DuckDB 和 SQL，聚合是独立的 Python 实现。其正确性仍依赖相同指标定义与原始数据完整性。若 SQL 和 oracle 共用错误业务定义，相互一致无法发现定义错误。

贡献公式在 `scripts/sales_drivers.py::decompose` 中，输入为两期订单数与商品金额。订单量贡献等于订单差乘两期每单金额均值，按分 ROUND_HALF_UP。另一项用总差额减前者，保证舍入后加总一致。

重要独立性边界为 `docker_review.verify` 将 SQL 的 monthly_drivers 行作为 driver_row 传入容器，容器再次运行复制进去的同一个 decompose 函数。因此聚合确实另写了一套实现，贡献公式只是在同一输入上重执行相同函数。该 drivers_match 不能作为独立公式正确性的证明。容器的 CSV oracle 结果会另外与 monthly_drivers SQL 行比较。

### 5.2 在哪里比较，容差是多少

| 位置 | 比较方法 |
|---|---|
| `analyst_adapter.cells_match` | actual 为原生 int/float 时以 Decimal(str(...)) 做相等比较，其他类型直接 ==。无 epsilon 或相对误差 |
| `analyst_adapter.review_evidence` | 比较行数、每行列数、每个单元格，将 task、query_id、matched 写入 checks |
| `phase2_planner.run` | review.drivers 与 state.drivers 做整个字典相等比较 |
| `baseline.main` | 已存 JSON 的 float 用 Decimal 解析，结果列表精确相等 |
| `golden_sql.main` | SQL 行经 JSON/Decimal 转换后与参考列表精确相等 |
| `agent_eval.score_trace` | JSON 用 parse_float=Decimal，逐任务结果列表精确相等 |
| `diagnostic_eval.matches/main` | 单元格精确比较，另检查两贡献之和等于总差额 |

SQL 通常 ROUND 到两位小数，CSV 金额按 Decimal 加总。这里是规范化后的精确匹配，不能描述为配置了数值容差。同值排名 ties 的顺序也可能影响列表比较，Top 品类 oracle 只按金额排序，未显式设置与 SQL 完全一致的 tie-breaker。

### 5.3 Evidence、Trace、报告落盘

`analyst_adapter.QueryEvidence` 字段为 task、sql、query_id、columns、rows、elapsed_seconds、attempts。McpAnalystAdapter 校验返回结构后补上 task/sql/attempts。

`phase2_planner.run` 写入 `artifacts/phase2/planner_<uuid>.json`。文件包括 evidence、decisions、状态、answer、usage、月份及可选 drivers/report_validation/docker_review。诊断模型字段不合格时保存 rejected_fields，但未保留其完整原始 proposal。查询 ID 是随机标识，不是 SQL 哈希或不可篡改签名。

报告文本保存在 trace.answer。诊断 `render_report` 末尾列出全部查询 ID，普通报告由模型按 prompt 要求引用。页面 `show_trace` 提供 Markdown 与完整 JSON 下载。页面 `show_business_summary` 单独计算摘要，它没有单独持久化回 trace.answer。旧轨迹没有 data_purchase_end 时，页面使用固定 Olist 截止日期作为回退，该日期不是实时刷新水位。

`run` 到末尾才写 JSON。初始化、模型请求等未捕获异常可能直接抛出，无法保证每个失败都有轨迹。写文件没有使用原子替换，进程异常退出时部分写入文件的处理待核实。

## 6. CommerceLens-Eval 的真实评分

以下命令供学习与后续复现，本次没有执行。

| 入口与命令 | 检查对象 | 产物 |
|---|---|---|
| `python -m commercelens_eval.golden_sql` | 直接调用 execute_readonly_sql，十个 SQL 对 CSV 结果 | artifacts/phase3/golden_sql_results.json |
| `python -m commercelens_eval.agent_eval` | 真实模型→LangGraph→MCP→SQL→普通报告的五题 | agent_eval.json |
| `python -m commercelens_eval.agent_eval --docker-review` | 同五题，附加容器结果与 query_id 覆盖检查 | agent_eval_docker.json |
| `python -m commercelens_eval.agent_eval --replay --docker-review` | 用既有 Docker 轨迹与现读 CSV 重评分，不新建容器/调用模型 | agent_eval_docker_replay.json |
| `python -m commercelens_eval.diagnostic_faults` | mock 注入的十一项恢复/字段检查 | diagnostic_fault_checks.json |
| `python -m commercelens_eval.sql_policy` | 五种拒绝及 DB 哈希不变 | sql_policy_validation.json |
| `python -m commercelens_eval.diagnostic_eval` | 三组固定 SQL 与受限诊断工作流对照 | diagnostic_eval.json |
| `python -m commercelens_eval.diagnostic_eval --pilot` | A/B/C 额外月份对照，人工时间为 None | bi_comparison_pilot.json |
| `python -m commercelens_eval.question_routing` | unittest 验证示例、日期方向、拒绝越界问题 | 控制台结果，无专门 JSON |
| `python -m commercelens_eval.baseline` | 已存 phase1 查询结果与 CSV 复算 | baseline_validation.json |
| `python -m commercelens_eval.regression --planner-trace <路径> --growth-trace <路径>` | 旧阶段工具、路由 smoke 和可选模型轨迹评分 | regression_results.json |
| `powershell -File scripts/check_release_readiness.ps1` | 按脚本列出的模块顺序验收，Agent 使用 replay | 上述多份结果 |

10 道黄金题由 `golden_sql.cases` 定义，依次为 overview、top_categories、jul_aug_change、category_contributions、order_status_counts、freight_total、top_seller、payment_total、item_count、product_count。前四条 SQL 取自 phase1/query_results.json，后六条在 cases 中定义。该评测直接调用 Python 工具函数，不覆盖 stdio 传输与模型规划。

5 道 Agent 题由 `agent_eval.CASES` 定义，预期路径分别为 overview，top_categories，jul_aug_change，jul_aug_change→category_contributions，以及反转月份的 jul_aug_change。它们运行 diagnosis=False，与新页面两月诊断的 singleton 任务链不同。

`agent_eval.score_trace` 的 passed 要同时满足路径完全相等、非空 evidence 且数值匹配、每个 query_id 字符串存在 answer。Docker 模式还要求 review.passed，以及 matched 查询 ID 列表与实际证据 ID 列表按顺序一致。它没有对整份报告做逐句语义评分，也未单独要求 state.status=="completed"。finish 决策未纳入 actual_path，因为 actual_path 从 evidence 提取。

十一项 mock 测试由 `diagnostic_faults.main` 定义。

1. 首次 MCP 超时，第二次恢复且 attempts==2。
2. 两次超时后以 mcp_unavailable 结束。
3. 两次无效任务后 planning_failed。
4. 无数据时写 no_comparable_orders 且保留已取证据。
5. mock Docker 子进程非零退出映射为 docker_unavailable。
6. 错误金额字段被 validate_facts 拒绝。
7. 错误涨跌方向被拒绝。
8. 错误币种被拒绝。
9. 错误周期被拒绝。
10. 错误查询 ID 被拒绝。
11. 额外 profit 字段被判 unsupported_fields。

其中“无依据断言”检查实际只测试了一个额外字段，不是对自然语言报告中任意断言的识别。超时、Docker 失败使用 mock，不等于真实服务故障演练。

`sql_policy.main` 测试 CREATE TABLE、未知表、多语句、limit=501、无 ON 的 CROSS JOIN 均抛 ValueError，并用 SHA-256 检查数据库前后相同。positive_control 是一次允许查询。

`diagnostic_eval.main` 另要求 completed、确切诊断路径、数值与引用正确、贡献平衡、固定 SQL 正确以及 Docker passed。固定 SQL 路径提前给定，Agent 耗时含模型和容器，无法直接视为人工 BI 效率对照。replay 的 elapsed_seconds 是重评分用时，不能当作原始推理时延。

### 6.1 历史 4/5 → 5/5 具体证据

本次读取产物确认如下。

| 产物 | 总数 | overview 实际路径 | overview 的数值/引用 |
|---|---|---|---|
| artifacts/phase3/agent_eval_initial.json | 4/5 | overview → jul_aug_change → category_contributions | numeric_match 与 citations 都为 true，passed=false |
| artifacts/phase3/agent_eval.json | 5/5 | overview | numeric_match 与 citations 都为 true，passed=true |
| artifacts/phase3/agent_eval_docker.json | 5/5 | overview | 同上，附 Docker 核验 |

首轮 overview 指向 `artifacts/phase2/planner_42952277a5b84566941527b51627d4e6.json`，后轮指向 `planner_0e9104dbfdb046ecae6172273ea25bfe.json`。当前 `run.choose` 的提示明确默认场景仅作用户要求的周期比较上下文。历史产物证明路径变化。代码修改的精确 diff、是否同模型参数下只改了这一处、是否有多次重复实验，本次无法由当前文件与产物确认，均为待核实。不能把这组结果写成统计显著的提效。

### 6.2 OpenJudge 状态

在当前 `scripts/`、`commercelens_eval/` 和三份依赖文件内检索 OpenJudge、grader、judge，没有找到实现或调用。现有评测为 Python 精确比较、规则断言和 mock。没有代码依据可以认定 OpenJudge 已运行，也未发现统一 Grader Adapter。其他未纳入主链路的外部目录是否另有实验，待核实。

## 7. 能力边界与面试表述

| 代码确认的能力 | 证据与限制 |
|---|---|
| 三类中文入口与参数验证 | interpret_question 正则全匹配，question_routing 有正反例。任意自然语言表达与多轮省略不在当前覆盖内 |
| 普通模式受限模型选任务 | build_workflow + CATALOG + choose，有五题历史模型产物 |
| 诊断分支与卖家下钻 | diagnostic_tasks、Comparison.breakdown_query，有诊断历史轨迹。分支为 Python 规则 |
| 可追溯查询与报告 | QueryEvidence、run 的 JSON、render_report 的 ID 引用。标识可追踪，不提供不可篡改保证 |
| 独立 CSV 聚合 | baseline.oracle 与 golden_sql 对照。贡献函数复用，非独立双实现 |
| 隔离复算 | docker_review.verify 调上游执行器，历史 Docker 评测产物记录 5/5。当前机器运行态未在本次检查 |
| 部分错误纠正与失败标记 | plan 的两次有效选择机会、adapter 的一次重试、diagnostic_faults mock |
| 本地离线回放 | demo_app.main/show_pilot 读取保存轨迹，依赖产物在本地存在 |

以下说法应以实际实现为边界。

- “模型自主决定所有下钻”应说明诊断候选由 diagnostic_tasks 单值规则生成。
- “模型自动生成任意 SQL / Python”在页面主链路无代码支持，SQL 由模板或预存文件提供，容器执行可信 verify.py。
- “模型实时发现数据库语义”在主链路无代码支持，schema/指标工具虽注册，当前 adapter 只调查询工具。
- “诊断报告是模型自由生成并通过语义评审”不符合 run 的 diagnosis 分支，模型只尝试复述事实字段，最终报告始终由 render_report 生成。
- “独立验证了贡献公式”证据不足，容器复用 decompose 且输入来自 SQL。独立的是 CSV 聚合。
- “已做 OpenJudge、RAG、向量检索、多 Agent 协作、图状态断点恢复”在上述主模块无对应实现。
- “实时更新业务库、CDC、任务队列、幂等、租户权限、生产并发与 SLA”在 build_phase1_data、demo_app 和 run 中没有完整实现。
- “找到库存/广告等业务根因”无法由本项目指标拆解证明，render_report 也提示成本和广告数据缺失。
- “准确率 100% / 比人工 BI 提效 / 上线稳定”超出当前固定小样本结果。agent_eval 与 diagnostic_eval 没有人工用时数据，试点 human_review_seconds 明确为 None。

当前目录中保留若干阶段零主机安装与排障脚本，与日常问数运行无调用关联。阶段零模型生成代码实验通过与否、当前发布包与工作区是否逐文件一致、当前服务可用性、所有安全默认值的实时生效情况，本次未运行验证，标为待核实。

## 8. 核心模块调用关系表

| 调用方 | 被调用方 | 输入 → 输出 | 边界 |
|---|---|---|---|
| start_demo.ps1 | demo_app.py::main | 启动参数 → Streamlit 服务 | OS 进程 |
| show_questions | interpret_question | 中文问题/覆盖范围 → BusinessQuestion | Python 规则 |
| run_business_question | phase2_planner.py CLI | 固定 prompt/月份 → 轨迹路径 | 子进程，300 秒 |
| main 高级分析分支 | phase2_planner.run | 预设问题/Comparison → Path | 当前进程 asyncio |
| run | build_workflow | choose/adapter/模式 → 编译图 | LangGraph |
| plan | diagnostic_tasks | 已有结果/drivers → 0 或 1 个任务 | 诊断规则 |
| plan | run.choose → run.complete | 候选/问题/证据 → task/reason | DeepSeek API |
| execute | McpAnalystAdapter.execute | task/依赖 → QueryEvidence | 工具适配层 |
| McpAnalystAdapter.execute | phase1_mcp.execute_readonly_sql | SQL → columns/rows/ID/耗时 | MCP stdio |
| execute_readonly_sql | SQLGlot / DuckDB | SQL AST / 只读查询 → 数据行 | AST 校验与本地库 |
| execute | sales_drivers.decompose | monthly_drivers 首行 → drivers | 确定性计算 |
| run | analyst_adapter.review_evidence | evidence/Comparison → checks | 图外线程调用 |
| review_evidence | docker_review.py::verify | 月份/driver_row → JSON 复核结果 | 子进程，100 秒 |
| verify | 上游 execute_python_in_docker | verify.py/工作目录/session → stdout+stderr | Docker CLI |
| verify.py | baseline.oracle / decompose | CSV / SQL driver_row → 参考结果/贡献 | 容器 Python |
| run | report_facts / validate_facts / render_report | state/模型字段 → 诊断 Markdown | 图外报告处理 |
| run | artifacts/phase2/planner_*.json | 完整结果 → 持久化轨迹 | 本地 JSON |
| show_trace / show_question_result | 保存的 trace | 结果/证据 → 页面和下载内容 | 展示 |
| golden_sql.main | oracle / execute_readonly_sql | CSV/SQL → 精确比较 | 工具层离线评测 |
| agent_eval.main / score_trace | run 或历史轨迹 / oracle | 题目或 JSON → 路径/数值/引用评分 | Agent 评测 |
| diagnostic_eval.main | fixed_sql / run / oracle | 固定月份组 → 对照结果 | 三类诊断对照 |
| diagnostic_faults.main | graph / adapter / validate_facts | mock 故障与错误字段 → 11 项布尔检查 | 故障单元检查 |
