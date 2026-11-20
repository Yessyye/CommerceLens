# CommerceLens-Eval

[Architecture](architecture.md) · [Technical design](technical_design.md)

## Evaluation architecture

Evaluation runs separately from user-request execution. CSV source records feed baseline.oracle. Golden SQL executes tool queries directly; Agent evaluation launches live runs or rescores saved traces. Policy and fault suites inspect distinct failure surfaces.

| Suite | Historical result | Scope |
|---|---:|---|
| Golden SQL | 10/10 | CSV reference equality |
| Agent | 5/5 | Task path, numbers, query IDs |
| Docker Agent | 5/5 | Additional stored review checks |
| SQL Policy | 5/5 | Rejection and unchanged DB hash |
| Fault/report | 11/11 | Mock failures and fact fields |

## Golden SQL

golden_sql.cases defines overview, category ranking, month difference, category declines, order-status counts, freight, top seller, payments, item count and product count. main directly calls execute_readonly_sql and compares Decimal-normalized rows with independent Python references. MCP stdio transport and model planning are outside this suite.

## Agent and Docker Agent

agent_eval.CASES contains five ordinary-mode questions. score_trace requires the exact expected task sequence, nonempty evidence, matching rows and every query ID appearing in answer. Docker mode additionally requires review.passed and the matched ID sequence to equal evidence IDs. It does not perform sentence-level semantic evaluation or separately require status==completed.

Expected paths are overview; top_categories; jul_aug_change; jul_aug_change→category_contributions; and reverse-month jul_aug_change. Diagnosis-mode singleton routing is assessed separately in diagnostic_eval.

## Policy and fault checks

sql_policy.main rejects CREATE TABLE, unknown tables, multiple statements, limit=501 and JOIN without ON. It checks the database SHA-256 before and after requests.

diagnostic_faults.main uses mocks for timeout recovery, two-time timeout exhaustion, invalid planning, empty data and Docker nonzero exit. Five mutated fields test amount, direction, unit, periods and query IDs. One additional profit field tests unsupported_fields. These eleven checks are controlled injections, not production fault drills.

## Independent Oracle and exact equality

baseline.oracle uses csv.DictReader, dictionaries, sets and Decimal. It independently aggregates source CSV. Contribution computation shares sales_drivers.decompose; Docker receives the SQL monthly row as input and separately checks CSV aggregates. cells_match and the evaluators use exact normalized equality, with no epsilon.

## Historical 4/5 to 5/5

agent_eval_initial.json records overview→jul_aug_change→category_contributions for an overview request. Numbers and citations passed, but the path failed. agent_eval.json records overview alone and a 5/5 suite. The current choose prompt restricts default comparison context to explicit comparison requests. The stored files do not prove all other experimental variables were identical or establish a statistically significant improvement.

## Replay versus live evaluation

With full dependencies, raw CSVs and a built database:

```powershell
.venv/Scripts/python.exe -m commercelens_eval.question_routing
.venv/Scripts/python.exe -m commercelens_eval.golden_sql
.venv/Scripts/python.exe -m commercelens_eval.sql_policy
.venv/Scripts/python.exe -m commercelens_eval.diagnostic_faults
.venv/Scripts/python.exe -m commercelens_eval.agent_eval --replay
.venv/Scripts/python.exe -m commercelens_eval.agent_eval --replay --docker-review
```

Replay reads current CSV expectations and saved trace files. Docker replay checks historical review metadata without starting a container. These commands have more prerequisites than the no-data UI replay. Legacy regression.py also needs earlier routing/model smoke artifacts that are not all shipped.

The following commands make live model requests and may incur cost:

```powershell
.venv/Scripts/python.exe -m commercelens_eval.agent_eval
.venv/Scripts/python.exe -m commercelens_eval.agent_eval --docker-review
.venv/Scripts/python.exe -m commercelens_eval.diagnostic_eval --pilot
```

diagnostic_eval requires completed status, exact path, matching rows, report query IDs, additive contribution balance, fixed-SQL correctness and Docker passed. Its fixed SQL baseline receives the expected task path in advance. human_review_seconds remains None. Replay elapsed time measures rescoring, not inference.

## Fresh-environment reproduction

docs/fresh_replay_validation.json records an earlier fresh Windows 10, Python 3.11.9 and Streamlit 1.67.0 install from official PyPI. Three AppTest case switches, SQL/evaluation display and actual HTTP 200 passed without raw data, API or Docker. This is runtime reproducibility evidence, separately from Agent quality scores.

This documentation revision captures actual page screenshots and performs local replay checks. Its current validation record is in documentation_review.md. Historical benchmark JSON files remain unchanged.

## Limits

OpenJudge, a general Grader Adapter and sentence-level entailment scoring are absent. Query-ID string presence checks source references, not whether every sentence follows from them. Small fixed suites do not establish unrestricted generalization, causal explanations, production reliability or measured human time savings.

## Source and historical artifact index

Paths below identify the implementation and the saved output. All commands above run modules from the repository root. This documentation task did not rerun these benchmark suites.

| Check | Implementation | Historical evidence |
|---|---|---|
| 10 SQL references | `commercelens_eval/golden_sql.py::cases/main`, `baseline.py::oracle` | [golden_sql_results.json](../artifacts/phase3/golden_sql_results.json) |
| 5 normal Agent cases | `commercelens_eval/agent_eval.py::CASES/score_trace/main` | [agent_eval.json](../artifacts/phase3/agent_eval.json) |
| 5 stored Docker-reviewed Agent cases | Same module, docker-review flag | [agent_eval_docker.json](../artifacts/phase3/agent_eval_docker.json) |
| Initial 4/5 | Same case family; earlier saved run | [agent_eval_initial.json](../artifacts/phase3/agent_eval_initial.json) |
| 5 SQL policy cases | `commercelens_eval/sql_policy.py::main` | [sql_policy_validation.json](../artifacts/phase3/sql_policy_validation.json) |
| 11 mock fault/report checks | `commercelens_eval/diagnostic_faults.py::main` | [diagnostic_fault_checks.json](../artifacts/phase3/diagnostic_fault_checks.json) |
| Diagnostic cases and A/B/C pilot | `commercelens_eval/diagnostic_eval.py::main` | [diagnostic_eval.json](../artifacts/phase3/diagnostic_eval.json), [bi_comparison_pilot.json](../artifacts/phase3/bi_comparison_pilot.json) |
| Chinese routing assertions | `commercelens_eval/question_routing.py::BusinessQuestionTests` | Source assertions; do not combine with 5/5 Agent score |
| Earlier combined regression | `commercelens_eval/regression.py` | Some prerequisite earlier-phase artifacts are absent in the public package |

The page's 10/10, 5/5 and 5/5 cards show SQL, Docker-reviewed Agent and SQL policy scores. They do not display eleven newly executed fault tests. The 11/11 figure comes from the separate saved fault/report artifact.
