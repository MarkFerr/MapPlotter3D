import re
import unicodedata

def normalize_place_name(s: str) -> str | None:
    if s is None:
        return None

    s = str(s).strip()
    if not s:
        return None

    s = unicodedata.normalize("NFKC", s)
    s = s.casefold()

    s = s.replace("’", "'").replace("‘", "'").replace("`", "'")

    s = "".join(
        ch for ch in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(ch)
    )

    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    return s or None