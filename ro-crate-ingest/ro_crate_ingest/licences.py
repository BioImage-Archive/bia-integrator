from bia_integrator_api.models import licence_type

def to_url(licence_code: licence_type) -> str:
    if licence_code == "CC0":
        return "https://creativecommons.org/public-domain/cc0/"
    elif licence_code == "CC_BY-SA_2.1_JP":
        return "https://creativecommons.org/licenses/by-sa/2.1/jp/"
    else:
        version = str(licence_code)[-3:]
        code = str(licence_code)[:-4][3:].replace("_","-").lower()
        return f"https://creativecommons.org/licenses/{code}/{version}/"

def to_code(licence_url: str) -> licence_type:
    if licence_url == "https://creativecommons.org/public-domain/cc0/":
        return "CC0"
    elif licence_url == "https://creativecommons.org/licenses/by-sa/2.1/jp/":
        return "CC_BY-SA_2.1_JP"
    else:
        if not licence_url.endswith("/"):
            licence_url += "/"
        
        url_split = licence_url.split('/')
        version = url_split[-2]
        code = url_split[-3].upper()
        return f"CC_{code}_{version}"