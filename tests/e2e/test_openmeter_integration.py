import os
import pytest
from openmeter import Client

@pytest.mark.integration
@pytest.mark.webtest
def test_openmeter_healthcheck():
    api_key = os.getenv("OPENMETER_API_KEY")
    if not api_key:
        pytest.skip("OPENMETER_API_KEY not provided")
    client = Client(endpoint="https://api.openmeter.de/v1/sandbox/endpoint", headers={"Authorization": f"Bearer {api_key}"})
    try:
        client.list_meters()
    except Exception as exc:
        pytest.fail(f"OpenMeter request failed: {exc}")
