# Evaluation

Historical results and newly executed candidate checks are reported separately in GITHUB_RELEASE_AUDIT.md.

From the candidate root, with the nine CSVs and built database available:

```powershell
.venv/Scripts/python.exe -m commercelens_eval.question_routing
.venv/Scripts/python.exe -m commercelens_eval.baseline
.venv/Scripts/python.exe -m commercelens_eval.golden_sql
.venv/Scripts/python.exe -m commercelens_eval.sql_policy
.venv/Scripts/python.exe -m commercelens_eval.diagnostic_faults
.venv/Scripts/python.exe -m commercelens_eval.agent_eval --replay
.venv/Scripts/python.exe -m commercelens_eval.agent_eval --replay --docker-review
```

These commands do not request model APIs or start a Docker review. Docker replay scores stored container evidence against the CSV expectations.

Golden SQL directly invokes the tool function for ten fixed questions. Agent evaluation requires exact task order, nonempty numeric evidence and every query ID appearing in the answer. Docker mode additionally requires matching review IDs. Numeric comparison uses Decimal-normalized exact equality.

The eleven fault/report checks inject mock errors and mutate structured fields. They cover timeout recovery/exhaustion, invalid planning, empty evidence, Docker failure classification, five incorrect fact fields and one extra unsupported field.

The diagnostic comparison suites require a correct task path, matching CSV values, report IDs, balanced contributions and successful Docker review. They are live commands and require explicit API/Docker setup:

```powershell
.venv/Scripts/python.exe -m commercelens_eval.diagnostic_eval --pilot
```

This command may incur API costs. It was not executed in the release audit.

Citation-string presence does not establish sentence-level entailment. The fixed suites do not establish general accuracy or measured human productivity gains. OpenJudge and a general semantic grader are absent.
