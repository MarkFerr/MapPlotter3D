import logging
import pandas as pd

logger = logging.getLogger(__name__)


def get_normalization(gdf) -> int:
    #TODO optimize this. use only shapes of areas that will be plotted & consider edgecases (e.g. only one area/object plotted)
    xmin, ymin, xmax, ymax = gdf.total_bounds
    map_width = xmax - xmin
    map_height = ymax - ymin
    avg = (map_width + map_height)/2
    max_plot_height = round(avg/8)
    logger.info("Max Height found: %i", max_plot_height)
    return max_plot_height


def normalize_df(df, max_value):
    logger.info("Normalizing Data to be between 0 and %f", max_value)
    normal_df = df.copy()
    numeric = normal_df.select_dtypes(include="number")
    normal_df[numeric.columns] = (
        (numeric - numeric.min()) /
        (numeric.max() - numeric.min())
    ) * max_value

    return normal_df