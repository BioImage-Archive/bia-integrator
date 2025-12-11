import re
from urllib.parse import urlparse, unquote

_DOI_RX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.I)
_DOI_TEMPLATE = "https://doi.org/{}"


def sanitise_doi(value: str) -> str:
    sanitised_value = unquote(value.strip().lower())

    # If user supplied sanitized value return it
    if _DOI_RX.fullmatch(sanitised_value):
        return _DOI_TEMPLATE.format(sanitised_value)
    
    if sanitised_value.startswith(("http://", "https://")):
        parsed_url = urlparse(sanitised_value)
        host = parsed_url.netloc
        if host not in {"doi.org", "dx.doi.org"}:
            raise ValueError(f"not a DOI URL. host:{host} extracted from {value}")
        sanitised_value = parsed_url.path.lstrip("/")
    else:
        # Allow dx.doi... or doi... .org optional and ':' or '/' before 10.*
        regex = r"(?i)^(?:dx\.doi|doi)(\.org)?[/:]\s*"
        if re.search:
            sanitised_value = re.sub(regex, "", sanitised_value)
        else:
            raise ValueError(f"invalid DOI format: sanitised_value: {sanitised_value} extracted from {value}")  
    if not _DOI_RX.fullmatch(sanitised_value):
        raise ValueError(f"invalid DOI: doi: {sanitised_value} extracted from {value}")
    return _DOI_TEMPLATE.format(sanitised_value)
