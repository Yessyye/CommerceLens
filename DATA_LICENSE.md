# Olist data and derived fixtures

Provider — Olist and dataset collaborators.

Dataset — Brazilian E-Commerce Public Dataset by Olist.

Official source — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

The official Kaggle search result checked on 2026-11-20 states **CC BY-NC-SA 4.0**, consistent with the existing local source metadata.

License — https://creativecommons.org/licenses/by-nc-sa/4.0/

The source-code MIT license applies separately. Data-derived JSON rows and report content under artifacts/ are provided for noncommercial demonstration with attribution to Olist and are distributed under CC BY-NC-SA 4.0. Transformations include aggregation, month comparisons, ranking and report rendering. Preserve the attribution and applicable share-alike terms when redistributing adaptations. Commercial permissions for this data require separate consideration.

Raw CSVs, customer records, the generated DuckDB and full logs are excluded from this candidate. Saved fixtures contain aggregate outputs, seller identifiers, SQL and experimental trace metadata. In the release-audit confirmation, the owner explicitly selected retaining the derived demonstration data with separate attribution and data-license notices. This statement records that limited authorization for the reviewed fixtures, not ownership of Olist or a grant of additional data rights.

See [data/README.md](data/README.md) to download the source files and build the local database. Any changes in upstream dataset versions may change expected evaluation outputs.

The per-file inventory and public disclosure risks are recorded in [docs/derived_data_inventory.md](docs/derived_data_inventory.md). Seller IDs can be linked to the source dataset. Some traces contain container/image identifiers, standardized questions, planning reasons and final report text. Full API HTTP request/response logs are excluded.

## Public-release operational metadata redaction

Before Git initialization, container_id/image_id and any session/host identifier fields in the shipped JSON were replaced with redacted-for-public-release. Query IDs, seller IDs, SQL, numeric results and review flags remain. Earlier descriptions of container identifiers refer to the pre-publication fixture audit. No actual container/image identifier is intended in this public fixture set.
