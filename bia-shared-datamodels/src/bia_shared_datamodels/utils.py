import re
from urllib.parse import urlparse, unquote

_DOI_RX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)


def sanitise_doi(value: str) -> str:
    sanitised_value = value.strip()
    if sanitised_value.lower().startswith(("http://", "https://")):
        pared_url = urlparse(sanitised_value)
        host = pared_url.netloc.lower()
        if host not in {"doi.org", "dx.doi.org"}:
            raise ValueError("not a DOI URL")
        sanitised_value = unquote(pared_url.path.lstrip("/"))
    else:
        sanitised_value = re.sub(r"(?i)^doi:\s*", "", sanitised_value)
    if not _DOI_RX.fullmatch(sanitised_value):
        raise ValueError("invalid DOI")
    return f"https://doi.org/{sanitised_value.lower()}"
