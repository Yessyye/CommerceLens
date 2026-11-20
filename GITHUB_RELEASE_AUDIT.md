# GitHub release candidate audit

Audit date 2026-11-20. Final status **READY WITH WARNINGS**. Candidate offline checks completed successfully. Live API/Docker execution, full live-environment installation and current screenshots remain pending. A newly installed replay-only environment is evaluated separately in this revision.

## Scope, consent and source identity

The owner selected MIT for CommerceLens code and approved publication of the selected Olist-derived fixtures with separate data notices. The candidate was assembled under dist/CommerceLens-release-candidate to stay within the existing writable workspace. Source files were copied to their original relative paths. No business code, model, database or evaluation logic was changed.

docs/source_identity.json lists files copied byte-for-byte from the source workspace and pins the upstream executor commit. The manifest records final file hashes. No original data or source file was deleted or moved.

## Structure and architecture

See docs/project_structure.md and docs/implementation_map.md. Entrypoints are scripts/demo_app.py::main, scripts/phase2_planner.py::run/build_workflow, scripts/phase1_mcp.py::server.run and commercelens_eval module mains.

Normal mode permits model task choice from the eligible catalog. Diagnostic mode exposes at most one candidate per planning round, with Python determining branches. The diagnosis report always uses render_report. CSV aggregation is independently implemented, while contribution decomposition reuses decompose and the SQL monthly row. The page uses trusted upstream container execution modules. OpenJudge, a Grader Adapter and multi-Agent collaboration were not found.

## Security

The phase-one bounded source scan found private paths in local configuration pointers, stage-zero scripts and logs. Those files were excluded. Candidate text scanning found no matched key prefixes, private user paths or unreviewed binary assets in the assembled set. Exact scan details are summarized in docs/candidate_security_results.json after finalization.

The candidate uses explicit source and artifact allowlists. Environment files, private configuration pointers, original datasets, local databases, complete logs, installers, caches, virtual environments and model weights are excluded. The genuine .env.example contains only keys actually consumed by the planner.

The candidate .gitignore was checked using an isolated temporary Git directory outside the candidate. Credential/database/model/local-IDE test paths were ignored and required source/fixture/notice paths were included. The candidate contains no .git directory.

Pattern scanning is not a guarantee that every possible secret format can be identified. No full binary archive or package-history scan is claimed.

## Git history

The source root is not a Git repository. CommerceLens tracked files and historical commits therefore could not be audited. No existing history is transferred. Before importing any other repository history, independently scan that history.

The separate local DeepAnalyze checkout was clean at afc697a11675c59683b9f6596c3ab3b3d661182a. Only the required runtime modules and original MIT LICENSE were copied. Upstream .git history was excluded.

## Source, dependency and data licenses

The root MIT license was added following the owner's explicit choice, with the publicly confirmed GitHub attribution Yessyye. The root LICENSE explicitly limits its scope to project-owned source and documentation. Copied vendor source and Olist-derived fixtures retain their separate notices.

DeepAnalyze's original MIT copyright notice is retained. THIRD_PARTY_NOTICES.md identifies the commit and exact copied modules. No MetaGPT source is shipped.

docs/dependency_licenses.json records metadata from 83 installed packages, with zero default dependency-version conflicts in that environment. Metadata for every transitive license has not been given a complete legal interpretation. No installed environment or package wheel is redistributed.

The official Kaggle search result checked in this audit identifies Olist's dataset license as CC BY-NC-SA 4.0, consistent with existing local metadata. DATA_LICENSE.md attributes Olist, describes transformations and assigns the shipped derived fixtures separate noncommercial/share-alike terms. Source-code MIT terms do not override the data terms.

Source https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

## Dependency and reproduction limits

Python 3.11.9 is the test interpreter. Existing dependency pins are retained. The replay path installs requirements-replay.txt. Live analysis uses requirements-demo.txt, raw CSV preparation, credentials and Docker.

The initial candidate audit used the existing interpreter. In this final revision, after explicit network authorization, a new Python 3.11.9 virtual environment was created and replay dependencies were installed from official PyPI. Fresh replay results are recorded in docs/fresh_replay_validation.json. Full live-environment installation and non-Windows support remain unverified. The full lock contains platform-specific dependencies.

build_phase1_data.main builds a new local snapshot or reuses an existing database. It does not incrementally merge updates. The shipped query_results.json is retained because phase2_planner.run reads its query definitions.

## Included files

Core scripts and evaluation modules, current Streamlit theme, empty example configuration, dependency pins, selected derived fixtures, minimal upstream executor modules, code/data/third-party notices and implementation documentation are included. RELEASE_MANIFEST.md provides the actual final file list and hashes.

## Exclusions

Excluded groups are raw Olist files, DuckDB, local configuration, source Git histories, environment/cache directories, Windows setup tools, full logs, unrelated vendor code, source PDFs/DOCX/images with unverified provenance and previous release archives.

No real API credentials were copied. No key was rotated. No GitHub repository, commit or push was created.

## Test results and evidence

Historical fixtures report Golden SQL 10/10, Agent 5/5, Docker Agent 5/5, SQL policy 5/5 and fault/report checks 11/11. These remain historical results.

Newly executed candidate checks all passed. Golden SQL scored 10/10, SQL policy 5/5 and fault/report checks 11/11. Both regular and Docker stored-trace replay scored 5/5. Offline replay switched all three cases. Detailed results are recorded in docs/candidate_test_results.json. The verification script parses candidate Python, loads the offline page with no raw data or key, switches among three cases, stages local CSVs temporarily, builds DuckDB, runs deterministic suites and rescores saved traces. It also imports the minimal upstream executor without starting Docker. Tests that rewrite fixtures are followed by restoration of the original historical fixture bytes.

This final revision downloaded and installed only the replay requirements from official PyPI under explicit owner authorization. No live model request, Docker execution or pull, or paid service was used. New screenshots are pending and are labeled accordingly in README. Test scratch files and raw CSVs must be removed before packaging.

## README completeness

README includes project purpose, real mode boundaries, architecture, stack, execution governance, workflow, offline quick start, live configuration, data preparation, evaluation commands, historical scores, limitations, roadmap and license acknowledgements.

Screenshots are explicitly pending. Their absence is a presentation warning, not fabricated evidence.

## Remaining warnings and publication advice

- Fresh replay installation is validated separately. Full live installation and non-Windows portability remain unverified.
- No source-root Git history exists to audit.
- Full transitive-license legal review is outside the metadata inventory.
- Screenshot assets are pending.
- API/Docker live reproduction requires manual setup and may incur costs.
- The public copyright attribution is Yessyye, as confirmed by the owner through the GitHub profile supplied for this purpose.

Upload the reviewed candidate directory contents when ready. Keep DATA_LICENSE.md and the upstream LICENSE. Preserve the distinction between historical scores and this audit's new offline checks. The previous dist/CommerceLens-GitHub.zip is an older delivery and is outside this release candidate.

## Final documentation revision

The owner supplied https://github.com/Yessyye/ as the public copyright attribution and authorized official-PyPI replay installation. The prior derived-fixture publication approval is documented in DATA_LICENSE.md with its limited scope. docs/derived_data_inventory.md inventories every shipped artifact JSON, including seller IDs, questions, model decision reasons, answers, SQL and operational identifiers. No full HTTP/API request-response log or customer/order detail result column was observed. Seller IDs remain linkable to the original dataset and are explicitly disclosed. The source MIT license does not grant commercial data rights.

Principal runtime dependency licenses and versions have been added to THIRD_PARTY_NOTICES.md. The original DeepAnalyze notice, pinned commit and unmodified copied-file list remain in place. Core code and evaluation algorithms are unchanged.

## New fresh-environment result

Fresh replay validation passed on Windows 10, Python 3.11.9, Streamlit 1.67.0. A newly created environment installed requirements-replay.txt from official PyPI. All three cases, SQL evidence and evaluation widgets passed Streamlit AppTest. A real Streamlit process returned health ok and homepage HTTP 200. No DeepSeek, Docker or raw data was used.

This new check validates replay installation only. Historical Golden SQL and Agent evaluation results were not rerun in the fresh replay environment, which has no DuckDB or API client installed. No new browser visual validation or screenshots are claimed.

## Public Git staging revision

Input ZIP checksum and CRC verified before changes. Operational container/image/session/host JSON fields were redacted without changing core code or evaluation algorithms. Fixture sanitization is documented in docs/source_identity.json. release/ is ignored so archives are not committed. Repository initialization is local only; public creation and push require a separate explicit approval. The local gh executable is absent; the GitHub connector identifies Yessyye. The target lookup returned 404 and accessible owner repository list was empty. Remote availability must be rechecked before creation.

## Published repository inspection and bilingual documentation

The public Yessyye/CommerceLens repository was read through the GitHub connector. Its main file tree contains 83 blobs. All 83 match the reviewed local candidate bytes or LF-normalized bytes. README is at repository root and the tree has no raw CSV, DuckDB, environment, cache or distribution archive paths. This is a content comparison, not a new runtime test of a clone.

The upload omitted .gitignore, .env.example and .streamlit/config.toml. Their absence affects ignore protection, live configuration instructions and intended theme. The bilingual update package restores them without altering core code.

README.zh-CN.md now provides Chinese onboarding, workflow, architecture, actual autonomy boundaries, evaluation and licensing. README.md links to the Chinese document. The recommended delivery is one repository with two README languages. No second remote repository or remote documentation change was made during this revision.
