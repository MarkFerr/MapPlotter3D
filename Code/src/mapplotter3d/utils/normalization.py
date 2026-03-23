import logging
import pandas as pd

logger = logging.getLogger(__name__)


def get_normalization(gdf) -> int:
    xmin, ymin, xmax, ymax = gdf.total_bounds
    map_width = xmax - xmin
    map_height = ymax - ymin
    avg = (map_width + map_height)/2
    max_plot_height = round(avg/8)
    logger.info("Max Height found: %i", max_plot_height)
    return max_plot_height


def normalize_df(df, max_value):
    logger.info("Normalizing Data")
    normal_df = df.copy()
    numeric = normal_df.select_dtypes(include="number")
    normal_df[numeric.columns] = (
        (numeric - numeric.min()) /
        (numeric.max() - numeric.min())
    ) * max_value

    return normal_df