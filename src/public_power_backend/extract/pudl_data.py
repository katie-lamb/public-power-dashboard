"""Module to extract EIA and FERC data from PUDL."""

import pandas as pd

from public_power_backend.constants import PUDL_DATA_YEAR


def _extract_pudl_eia_utilities():
    # TODO: use the entity table instead (core_pudl__assn_eia_pudl_utilities)
    eia_utils = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/out_eia__yearly_utilities.parquet",
        dtype_backend="pyarrow",
    )

    # filter utilities where report_year >= PUDL_DATA_YEAR and < PUDL_DATA_YEAR+1
    eia_utils = eia_utils[
        (eia_utils.report_date.dt.year >= PUDL_DATA_YEAR)
        & (eia_utils.report_date.dt.year < PUDL_DATA_YEAR + 1)
    ]
    return eia_utils


def _extract_pudl_rtos():
    util_rtos = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/core_eia861__yearly_utility_data_rto.parquet",
        dtype_backend="pyarrow",
    )
    util_rtos = util_rtos[
        (util_rtos.report_date.dt.year >= PUDL_DATA_YEAR)
        & (util_rtos.report_date.dt.year < PUDL_DATA_YEAR + 1)
    ]
    return util_rtos


def _extract_pudl_ferc1_utilities():
    ferc_utils_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/core_pudl__assn_ferc1_pudl_utilities.parquet",
        dtype_backend="pyarrow",
    )
    return ferc_utils_df


def _extract_sec_filers_to_eia_utilities():
    sec_utils_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/core_sec10k__assn_sec10k_filers_and_eia_utilities.parquet",
        dtype_backend="pyarrow",
    )
    return sec_utils_df


def _extract_sec_ownership():
    sec_parents_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/nightly/out_sec10k__parents_and_subsidiaries.parquet",
        dtype_backend="pyarrow",
    )
    return sec_parents_df


def extract() -> dict[str, pd.DataFrame]:
    """Pull PUDL tables from AWS cloud storage.

    Returns:
        A dictionary of pandas DataFrames where the keys are the PUDL table names.
    """
    raw_pudl_tables = {}
    # dictionary of PUDL table names to names used in DGM data warehouse
    tables = {
        "pudl_eia_utilities": _extract_pudl_eia_utilities,
        "pudl_rtos": _extract_pudl_rtos,
        "pudl_ferc1_utilities": _extract_pudl_ferc1_utilities,
        "pudl_sec_utils": _extract_sec_filers_to_eia_utilities,
        "pudl_sec_ownership": _extract_sec_ownership,
    }
    for table_name, extract_func in tables.items():
        raw_pudl_tables[table_name] = extract_func()
    return raw_pudl_tables
