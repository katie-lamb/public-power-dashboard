"""Transform module for PUDL data."""

import pandas as pd

from public_power_backend.constants import (
    OWNER_FILL_INS,
    SUB_TO_PARENT_CIK_MAPPING,
    ULTIMATE_OWNER_COMPANY_UTILITY_ID_EIA_LIST,
    UTILITY_ID_EIA_TO_DROP,
    UTILITY_ID_EIA_TO_KEEP,
)


def _transform_eia_utilities(raw_eia_utils_df: pd.DataFrame) -> pd.DataFrame:
    """Transform EIA utilities to create an IOUs table.

    Filter for IOUs using owner entity_type. Restrict to utility
    name and ID columns.
    """
    ious = raw_eia_utils_df[raw_eia_utils_df.entity_type == "I"]
    ious = ious[
        ["utility_id_eia", "utility_name_eia", "utility_id_pudl", "state"]
    ].drop_duplicates()
    ious = ious[~ious["utility_id_eia"].isin(UTILITY_ID_EIA_TO_DROP)]
    assert len(ious[~ious["utility_id_eia"].isin(UTILITY_ID_EIA_TO_KEEP)]) == 0, (
        "The following utility_id_eia have not been seen before "
        "and are not in UTILITY_ID_EIA_TO_DROP or UTILITY_ID_EIA_TO_KEEP: "
        f"{ious[~ious['utility_id_eia'].isin(UTILITY_ID_EIA_TO_KEEP)]['utility_id_eia'].unique()}"
    )
    # TODO: move this into extract and clean this up
    ferc_utils_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/core_pudl__assn_ferc1_pudl_utilities.parquet",
        dtype_backend="pyarrow",
    )
    # not ideal, look into why there are duplicates
    ferc_utils_df = ferc_utils_df.drop_duplicates(subset="utility_id_pudl")[
        ["utility_id_pudl", "utility_id_ferc1"]
    ]
    ious = ious.merge(ferc_utils_df, how="left", on="utility_id_pudl", validate="1:1")
    sec_utils_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/stable/core_sec10k__assn_sec10k_filers_and_eia_utilities.parquet",
        dtype_backend="pyarrow",
    )
    sec_utils_df = sec_utils_df.drop_duplicates(subset="utility_id_eia")
    ious = ious.merge(sec_utils_df, how="left", on="utility_id_eia", validate="1:1")
    sec_parents_df = pd.read_parquet(
        "s3://pudl.catalyst.coop/nightly/out_sec10k__parents_and_subsidiaries.parquet",
        dtype_backend="pyarrow",
    )
    clean_parents_df = (
        sec_parents_df[
            [
                "subsidiary_company_central_index_key",
                "parent_company_name",
                "parent_company_central_index_key",
            ]
        ]
        .drop_duplicates()
        .dropna(subset="subsidiary_company_central_index_key")
    )
    # If a subsidiary lists itself as the parent then there's
    # either another row with a higher parent company or the parent
    # CIK should be null if it has no owner company.
    clean_parents_df = clean_parents_df[
        ~(
            clean_parents_df.subsidiary_company_central_index_key
            == clean_parents_df.parent_company_central_index_key
        )
    ]
    ious = ious.merge(
        clean_parents_df,
        how="left",
        left_on="central_index_key",
        right_on="subsidiary_company_central_index_key",
    )
    ious = ious.merge(
        SUB_TO_PARENT_CIK_MAPPING, on="subsidiary_company_central_index_key", how="left"
    )
    # In the SEC data there are often many parent CIKs listed
    # for one subsidiary because there is a hierarchy of parents.
    # We've manually compiled a mapping of these subsidiaries to
    # their ultimate (highest) parent company. Apply these overrides.
    overriden_parents = ious[
        (ious.preferred_parent_cik == ious.parent_company_central_index_key)
    ]
    correct_parents = ious[(ious.preferred_parent_cik.isna())]
    # TODO: fix this and put the assert back in
    """
    assert len(overriden_parents) + len(correct_parents) == len(ious), (
        "There are subsidiaries manually mapped to a parent where "
        "the relationship never appears as a row in the SEC parents to subs table."
    )
    """
    ious = pd.concat([overriden_parents, correct_parents])
    # TODO: take this out
    ious = ious.drop_duplicates(subset="utility_id_eia")
    ious = ious.rename(
        columns={
            "parent_company_name": "owner_company_name",
            "parent_company_central_index_key": "owner_company_central_index_key",
        }
    )
    # conduct manual overrides
    ultimate_owner_mask = ious.utility_id_eia.isin(
        ULTIMATE_OWNER_COMPANY_UTILITY_ID_EIA_LIST
    )
    ious.loc[ultimate_owner_mask, "owner_company_name"] = ious[ultimate_owner_mask][
        "utility_name_eia"
    ]
    ious.loc[ultimate_owner_mask, "owner_company_central_index_key"] = ious[
        ultimate_owner_mask
    ]["central_index_key"]
    ious = ious.merge(OWNER_FILL_INS, how="left", on="utility_id_eia")
    ious["owner_company_name"] = ious["owner_company_name_fillin"].fillna(
        ious["owner_company_name"]
    )
    ious["owner_company_central_index_key"] = ious[
        "owner_company_central_index_key_fillin"
    ].fillna(ious["owner_company_central_index_key"])
    ious["central_index_key"] = ious["central_index_key"].astype(str)
    ious["owner_company_central_index_key"] = ious[
        "owner_company_central_index_key"
    ].astype(str)
    assert ious.utility_id_eia.is_unique, (
        "utility_id_eia is not unique in EIA IOUs table."
    )
    return ious[
        [
            "utility_name_eia",
            "utility_id_eia",
            "utility_id_ferc1",
            "utility_id_pudl",
            "central_index_key",
            "state",
            "owner_company_name",
            "owner_company_central_index_key",
        ]
    ]


def _transform_eia861_rtos(raw_eia_rto_df: pd.DataFrame) -> pd.DataFrame:
    """Transform EIA 861 RTOs."""
    rto_df = raw_eia_rto_df.copy()
    rto_df["rtos_of_operation"] = rto_df["rtos_of_operation"].astype("string")
    combined_rtos = (
        rto_df.groupby("utility_id_eia")["rtos_of_operation"].agg(list).reset_index()
    )
    rto_df = rto_df.drop(columns="rtos_of_operation")
    rto_df = rto_df.drop_duplicates()
    assert rto_df["utility_id_eia"].is_unique, (
        "utility_id_eia is not unique in EIA RTOs table."
    )
    rto_df = rto_df.merge(
        combined_rtos, how="left", on="utility_id_eia", validate="1:1"
    )

    return rto_df


def transform(raw_pudl_tables: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Transform PUDL tables.

    Args:
        raw_pudl_tables: The raw PUDL tables.

    Returns:
        The transformed PUDL tables.
    """
    table_transform_functions = {
        "pudl_utilities": _transform_eia_utilities,
        "pudl_rtos": _transform_eia861_rtos,
    }

    transformed_dfs = {}
    for pudl_table_name, raw_pudl_table in raw_pudl_tables.items():
        transformed_dfs[pudl_table_name] = table_transform_functions[pudl_table_name](
            raw_pudl_table
        )

    return transformed_dfs
