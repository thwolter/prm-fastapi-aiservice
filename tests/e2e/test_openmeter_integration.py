import pytest
from openmeter import Client

from core.config import settings


@pytest.mark.integration
def test_openmeter_healthcheck():
    api_key = settings.OPENMETER_API_KEY
    if not api_key:
        pytest.skip("OPENMETER_API_KEY not provided")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    client = Client(endpoint=settings.OPENMETER_API_URL, headers=headers)
    try:
        client.list_meters()
    except Exception as exc:
        pytest.fail(f"OpenMeter request failed: {exc}")
