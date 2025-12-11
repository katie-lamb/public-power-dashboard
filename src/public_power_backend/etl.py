"""The ETL module to coordinate creating the data warehouse and output tables."""

import logging
from collections.abc import Callable

import pandas as pd

import public_power_backend
from public_power_backend.constants import OUTPUT_DIR

logger = logging.getLogger(__name__)


def etl_pudl_tables() -> dict[str, pd.DataFrame]:
    """Pull tables from PUDL S3 storage."""
    pudl_raw_dfs = public_power_backend.extract.pudl_data.extract()
    pudl_transformed_dfs = public_power_backend.transform.pudl_data.transform(
        pudl_raw_dfs
    )
    return pudl_transformed_dfs


def run_etl(funcs: dict[str, Callable], schema_name: str):
    """Execute etl functions and save outputs to parquet."""
    transformed_dfs = {}
    for dataset, etl_func in funcs.items():
        logger.info(f"Processing: {dataset}")
        transformed_dfs.update(etl_func())

    # Create parquet files
    parquet_dir = OUTPUT_DIR / schema_name
    parquet_dir.mkdir(exist_ok=True, parents=True)

    # TODO: rework this to use pyarrow and schemas from metadata
    for table, df in transformed_dfs.items():
        output_table_name = table + ".parquet"
        df.to_parquet(parquet_dir / output_table_name)

    # schema = dbcp.helpers.get_pyarrow_schema_from_metadata(
    #    table.name, schema_name
    # )
    # pa_table = pa.Table.from_pandas(df, schema=schema)
    # pq.write_table(pa_table, parquet_dir / f"{table.name}.parquet")

    logger.info("Sucessfully finished ETL.")


def etl():
    """Run public power backend ETL."""
    # Run public ETL functions
    etl_funcs = {
        "pudl_tables": etl_pudl_tables,
    }
    run_etl(etl_funcs, "data_warehouse")

    logger.info("Sucessfully finished ETL.")


if __name__ == "__main__":
    # debugging entry point
    etl()
    print("Successfully finished ETL.")
