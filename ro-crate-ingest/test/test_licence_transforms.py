import pytest
from ro_crate_ingest.licences import to_url, to_code


@pytest.mark.parametrize(
    "input_code, output_url",
    [
        ("CC0", "https://creativecommons.org/public-domain/cc0/"),
        ("CC_BY_4.0", "https://creativecommons.org/licenses/by/4.0/"),
        ("CC_BY-SA_2.5", "https://creativecommons.org/licenses/by-sa/2.5/"),
        ("CC_BY-SA_2.1_JP", "https://creativecommons.org/licenses/by-sa/2.1/jp/"),
        ("CC_BY-NC_3.0", "https://creativecommons.org/licenses/by-nc/3.0/"),
        ("CC_BY-NC-SA_1.0", "https://creativecommons.org/licenses/by-nc-sa/1.0/"),
        ("CC_BY-NC-ND_4.0", "https://creativecommons.org/licenses/by-nc-nd/4.0/"),
    ],
)
def test_to_url(input_code, output_url):
    assert to_url(input_code) == output_url


@pytest.mark.parametrize(
    "input_code, output_url",
    [
        ("https://creativecommons.org/public-domain/cc0/", "CC0"),
        ("https://creativecommons.org/licenses/by/4.0/", "CC_BY_4.0"),
        ("https://creativecommons.org/licenses/by-sa/2.5/", "CC_BY-SA_2.5"),
        ("https://creativecommons.org/licenses/by-sa/2.5", "CC_BY-SA_2.5"),
        ("https://creativecommons.org/licenses/by-sa/2.1/jp/", "CC_BY-SA_2.1_JP"),
        ("https://creativecommons.org/licenses/by-nc/3.0/", "CC_BY-NC_3.0"),
        ("https://creativecommons.org/licenses/by-nc-sa/1.0/", "CC_BY-NC-SA_1.0"),
        ("https://creativecommons.org/licenses/by-nc-nd/4.0/", "CC_BY-NC-ND_4.0"),
    ],
)
def test_to_code(input_code, output_url):
    assert to_code(input_code) == output_url
