"""
Global test configuration and fixtures.

This file configures pytest and imports all fixture modules to make them available to all tests.
"""

import pytest

pytest_plugins = [
    'tests.fixtures.environment',  # Renamed from env.py for clarity
    'tests.fixtures.auth',
    'tests.fixtures.test_clients',  # Renamed from client.py for clarity
    'tests.fixtures.service_handler',
    'tests.fixtures.local_openmeter',
]


@pytest.fixture(autouse=True)
def auto_openmeter_environment(request):
    if request.node.get_closest_marker('openmeter'):
        request.getfixturevalue('local_openmeter_environment')
    yield
