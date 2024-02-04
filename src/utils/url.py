from pydantic import validate_call
import tldextract

@validate_call
def extract_domain(url: str, get_subdomain: bool = True) -> str:
    extracted = tldextract.extract(url)
    domain = extracted.domain + "." + extracted.suffix

    if extracted.subdomain and get_subdomain:
        domain = extracted.subdomain + "." + domain

    return domain