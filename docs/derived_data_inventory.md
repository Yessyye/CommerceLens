# Shipped JSON data inventory

Inspected every shipped artifacts JSON file on 2026-11-20. This inventory records categories, not identifier values.

| File | Actual data categories | Customer/order detail columns |
|---|---|---|
| artifacts/phase1/query_results.json | aggregate result rows; SQL/schema/period filters | None observed |
| artifacts/phase2/planner_0bae01c8d97e481fad990a5ace79cc9f.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_0e9104dbfdb046ecae6172273ea25bfe.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_1db99daf59ed4cdab7a7169627baa66b.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_213a42097d2e4fdfbce177f6874213a2.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_29aacd7933574c2b87234d08465a3938.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_2b936e75a12a43149c1e4783393c54b6.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_2e00f670a79941c29ab6e903ff155521.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_42952277a5b84566941527b51627d4e6.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_5118329795904bb199277a94d7bf9dfb.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_5dd3ef11531341d1bf6b9764f11fbacf.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_5efc6da699ed450a961cc6b69d698311.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_7193e332077049e0be6b11175b0ec735.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_828c29afcf564eeca3c475c9dd5871d2.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_9390a70cdbb44314a828541de78981d5.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_98bc24e5e9ba47a5832de4944ea247b5.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_99277b0309204334bda77f6f99f55583.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_b15b435f72ab4f5a99bf390c2da480c0.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_b3d7b583c8df4fd783b9e75da035efd8.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase2/planner_bb1a3a183ff541b4a3c0f865cd6a6c73.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_d10ed626126f45dd8f5330475909f225.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_df5ee6359026444bb170f7cc32d97f8e.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage; review state; some traces have container/image identifiers | None observed |
| artifacts/phase2/planner_f1a60a38ef44406dac2d81bfa440b20b.json | aggregate result rows; SQL/schema/period filters; task question; selected tasks and model reasons; final rendered or model-written answer; token usage | None observed |
| artifacts/phase3/agent_eval.json | evaluation scores/paths/check flags | None observed |
| artifacts/phase3/agent_eval_docker.json | review state; some traces have container/image identifiers | None observed |
| artifacts/phase3/agent_eval_initial.json | evaluation scores/paths/check flags | None observed |
| artifacts/phase3/bi_comparison_pilot.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters | None observed |
| artifacts/phase3/diagnostic_eval.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters | None observed |
| artifacts/phase3/diagnostic_fault_checks.json | evaluation scores/paths/check flags | None observed |
| artifacts/phase3/golden_sql_results.json | aggregate result rows; pseudonymous seller IDs; SQL/schema/period filters; task question | None observed |
| artifacts/phase3/sql_policy_validation.json | aggregate result rows | None observed |

## Public disclosure risks

Seller IDs are pseudonymous identifiers that can link rankings back to the original Olist dataset. They are retained in seller drill-down and top-seller fixtures. Query IDs are generated trace identifiers and must not be mistaken for seller IDs. SQL exposes table names, metric definitions and month/category filters.

Trace fields include the standardized task question, planning task/reason pairs, token counts and final report. They do not contain full HTTP/API request-response logs or the complete chat messages. Some final answers are model outputs, while diagnosis answers are deterministically rendered. Original report-fact proposals and full raw model completion objects are not stored in these traces.

Review records include container/image identifiers. These are operational metadata that can correlate runs. The candidate excludes Docker inspect dumps, full host logs, private configuration and original CSV records.

No customer ID, customer unique ID, individual order ID, address, email, phone or review-text result column was observed. SQL may reference order_id/customer joins for aggregation without returning those source identifiers. This inspection does not assert that arbitrary future user questions or traces are safe to publish.

## Owner authorization

The owner explicitly chose MIT and approved retaining derived demonstration data with separate attribution and CC BY-NC-SA 4.0 notices in the release-audit question reply. That approval covers this reviewed fixture set. It does not establish ownership of Olist data or approve automatic publication of future traces.

The later final-revision request did not rescind that approval. After inspection, this candidate explicitly discloses seller IDs and operational identifiers. Dataset rights and commercial restrictions remain separate from owner approval.

## Public-release operational metadata redaction

Before Git initialization, container_id/image_id and any session/host identifier fields in the shipped JSON were replaced with redacted-for-public-release. Query IDs, seller IDs, SQL, numeric results and review flags remain. Earlier descriptions of container identifiers refer to the pre-publication fixture audit. No actual container/image identifier is intended in this public fixture set.
