import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def read_xml(path: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_xml(path, **kwargs)

    if len(df.columns) < 2:
        logger.info("Not enough XML columns found. Trying fallback reshape")
        df = pd.read_xml(path, xpath="//record/field")

        if {"name", "field"}.issubset(df.columns):
            df = (
                df.rename(columns={"name": "field", "field": "value"})
                .assign(record=lambda x: x.index // x["field"].nunique())
                .pivot(index="record", columns="field", values="value")
                .reset_index(drop=True)
            )
        else:
            raise ValueError("Could not normalize XML structure into tabular form.")

    return df


def read_csv_flexible(path: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(path)
    read_kwargs = dict(kwargs)

    has_header = read_kwargs.pop("has_header", True)

    if "delimiter" in read_kwargs and "sep" not in read_kwargs:
        read_kwargs["sep"] = read_kwargs.pop("delimiter")

    if "header" not in read_kwargs:
        read_kwargs["header"] = 0 if has_header else None

    df = pd.read_csv(path, **read_kwargs)

    if not has_header:
        df.columns = [f"col_{i}" for i in range(df.shape[1])]

    return df


READERS = {
    ".csv": read_csv_flexible,
    ".pickle": pd.read_pickle,
    ".xml": read_xml,
}


def read_file(file: str | Path, **kwargs) -> pd.DataFrame:
    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file}")

    suffix = path.suffix.lower()
    logger.info("Detected suffix '%s'", suffix)

    if suffix not in READERS:
        raise ValueError(f"Unsupported format for data chooser: {suffix}")

    df = READERS[suffix](path, **kwargs)

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Reader returned unsupported type: {type(df).__name__}")

    return df


def get_dataframe_preview(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    return df.head(n).copy()


def get_column_info(df: pd.DataFrame) -> list[dict]:
    numeric_cols = set(df.select_dtypes(include="number").columns)
    info = []

    for col in df.columns:
        series = df[col]
        info.append(
            {
                "name": str(col),
                "dtype": str(series.dtype),
                "numeric": col in numeric_cols,
                "nulls": int(series.isna().sum()),
            }
        )

    return info


def infer_default_columns(df: pd.DataFrame) -> dict[str, str | None]:
    lower_map = {str(c).lower(): str(c) for c in df.columns}

    def find(names: list[str]) -> str | None:
        for name in names:
            if name in lower_map:
                return lower_map[name]
        return None

    numeric_cols = [str(c) for c in df.select_dtypes(include="number").columns]
    non_numeric_cols = [str(c) for c in df.columns if str(c) not in numeric_cols]

    x = find(["x", "lon", "longitude", "easting"])
    y = find(["y", "lat", "latitude", "northing"])
    z = find(["z", "elev", "elevation", "height", "depth"])
    value = find(["value", "scalar", "intensity"])

    label = find(["label", "name", "id"])
    if label is None and non_numeric_cols:
        label = non_numeric_cols[0]

    if x is None and len(numeric_cols) >= 1:
        x = numeric_cols[0]
    if y is None and len(numeric_cols) >= 2:
        y = numeric_cols[1]
    if z is None and len(numeric_cols) >= 3:
        z = numeric_cols[2]

    return {
        "x": x,
        "y": y,
        "z": z,
        "value": value,
        "label": label,
    }