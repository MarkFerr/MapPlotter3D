
import requests
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def download_geojson_temp(geojson_url: str) -> Path:
    """
    Download a GeoJSON to a temporary file and return the path.
    Caller is responsible for deleting it.
    """
    logger.info("Starting download of %s", geojson_url)
    response = requests.get(geojson_url, timeout=120, stream=True)
    response.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".geojson")
    tmp_path = Path(tmp.name)

    try:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                tmp.write(chunk)
    finally:
        tmp.close()
    logger.info("\tDownload complete")
    return tmp_path