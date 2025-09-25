import re
from urllib.parse import urlparse, unquote

_DOI_RX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)


def sanitise_doi(value: str) -> str:
    s = value.strip()
    if s.lower().startswith(("http://", "https://")):
        u = urlparse(s)
        host = u.netloc.lower()
        if host not in {"doi.org", "dx.doi.org"}:
            raise ValueError("not a DOI URL")
        s = unquote(u.path.lstrip("/"))
    else:
        s = re.sub(r"(?i)^doi:\s*", "", s)
    if not _DOI_RX.fullmatch(s):
        raise ValueError("invalid DOI")
    return f"https://doi.org/{s.lower()}"
