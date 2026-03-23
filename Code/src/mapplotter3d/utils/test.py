import argparse
import json
import sys
from pathlib import Path

import requests


GEObOUNDARIES_ADM0_ALL_URL = "https://www.geoboundaries.org/api/current/gbOpen/ALL/ADM0/"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def normalize_country_name(item: dict) -> str | None:
    """
    geoBoundaries API commonly returns fields like:
      - boundaryName
      - boundaryISO
    but we allow a couple of fallbacks just in case.
    """
    for key in ("boundaryName", "country", "name"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def fetch_world_countries() -> list[str]:
    resp = requests.get(GEObOUNDARIES_ADM0_ALL_URL, timeout=60)
    resp.raise_for_status()
    payload = resp.json()

    if not isinstance(payload, list):
        raise ValueError(
            f"Expected a list from geoBoundaries API, got {type(payload).__name__}"
        )

    countries = []
    seen = set()

    for item in payload:
        if not isinstance(item, dict):
            continue

        name = normalize_country_name(item)
        if not name:
            continue

        if name not in seen:
            seen.add(name)
            countries.append(name)

    countries.sort()
    return countries


def remove_single_shape_entries(data: list[dict]) -> list[dict]:
    filtered = []

    for entry in data:
        shape_names = entry.get("shapeNames")

        # Keep entries that do not have shapeNames as a list
        # or have more than one shape name.
        if not isinstance(shape_names, list) or len(shape_names) > 1:
            filtered.append(entry)

    return filtered


def build_world_entry(countries: list[str]) -> dict:
    count = len(countries)

    return {
        "id": "WORLD-ADM0-GEOBOUNDARIES",
        "country": "World",
        "iso3": "WLD",
        "level": "ADM0",
        "finest_type_found": "ADM0",
        "year": "current",
        "canonical": "World",
        "source": "geoBoundaries API",
        "license": "Varies by country dataset",
        "licenseDetail": (
            "Synthetic entry created from geoBoundaries ADM0 country list. "
            "shapeNames contains all country names returned by the API."
        ),
        "licenseSource": "https://www.geoboundaries.org/api.html",
        "sourceDataUpdateDate": "",
        "buildDate": "",
        "continent": "World",
        "unsdgRegion": "World",
        "unsdgSubregion": "World",
        "worldBankIncomeGroup": "",
        "admUnitCount": str(count),
        "meanVertices": "",
        "minVertices": "",
        "maxVertices": "",
        "minPerimeterLengthKM": "",
        "meanPerimeterLengthKM": "",
        "maxPerimeterLengthKM": "",
        "meanAreaSqKM": "",
        "minAreaSqKM": "",
        "maxAreaSqKM": "",
        "staticDownloadLink": "",
        "geojsonUrl": "",
        "topojsonUrl": "",
        "previewImage": "",
        "simplifiedGeojsonUrl": "",
        "adress": "",
        "shapeNames": countries,
    }


def upsert_world_entry(data: list[dict], world_entry: dict) -> list[dict]:
    """
    Remove any existing synthetic World entry with the same id/country+iso3,
    then append the new one.
    """
    cleaned = []
    for entry in data:
        if entry.get("id") == world_entry["id"]:
            continue
        if entry.get("country") == "World" and entry.get("iso3") == "WLD":
            continue
        cleaned.append(entry)

    cleaned.append(world_entry)
    return cleaned


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Remove entries with only one shapeName and append a World entry "
            "built from geoBoundaries ADM0 country names."
        )
    )
    parser.add_argument("--input", help="Path to input JSON file", default="C:\\Users\\Mark\\VisualStudioProjects\\MapPlotter3D\\MapPlotter3D\\Code\\src\\mapplotter3d\\geo_info\\geo_layers copy.json")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output JSON file (default: overwrite input)",
        default=None,
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    data = load_json(input_path)
    if not isinstance(data, list):
        print("Input JSON must be a top-level array.", file=sys.stderr)
        sys.exit(1)

    filtered = remove_single_shape_entries(data)
    countries = fetch_world_countries()
    world_entry = build_world_entry(countries)
    result = upsert_world_entry(filtered, world_entry)

    save_json(output_path, result)

    removed_count = len(data) - len(filtered)
    print(f"Removed {removed_count} entries with exactly one shape name.")
    print(f"Added/updated World entry with {len(countries)} countries.")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()