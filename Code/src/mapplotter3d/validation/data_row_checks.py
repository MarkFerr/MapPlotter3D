import logging

from mapplotter3d.utils.text_normalization import normalize_place_name


logger = logging.getLogger(__name__)


def check_missing_row_names(df, gdf):
    #todo check if both directions needed!
    missing_names = missing_row_names(df, gdf)
    if missing_names:
        logger.warning("No Shapenames found for: %s", list(missing_names)[:20])
    else:
        logger.info("Data matches")


def missing_row_names(df, gdf):
    a = gdf["shapeName"].map(normalize_place_name)
    b = df["municipality"].map(normalize_place_name)

    a_set = set(a.dropna().unique())
    b_set = set(b.dropna().unique())

    return b_set - a_set

