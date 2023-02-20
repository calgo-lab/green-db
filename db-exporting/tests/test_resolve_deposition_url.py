import pytest
from db_exporting.main import resolve_deposition_url


def test_resolve_deposition_url() -> None:
    try:
        resolve_deposition_url()
    except Exception as e:
        pytest.fail(e)
