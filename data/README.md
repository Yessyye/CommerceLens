# Prepare local Olist data

Download the original archive from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), accepting the source's access and license requirements yourself. Unzip the following files into data/raw/olist/.

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

From the candidate root with full dependencies installed, execute:

```powershell
.venv/Scripts/python.exe scripts/build_phase1_data.py
```

scripts/build_phase1_data.py::main creates artifacts/phase1/olist.duckdb if absent and writes data_profile.json. If a database already exists it is reused. This is a snapshot builder. To analyze another snapshot, prepare it in a separate project copy.

The shipped query_results.json includes query definitions needed by phase2_planner.run. Keep that file for the current entry point.

Source data are excluded from Git and the release archive. Attribution and data terms are in DATA_LICENSE.md.
