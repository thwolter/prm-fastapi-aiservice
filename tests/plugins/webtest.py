import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--webtest', action='store_true', default=False, help='run tests marked as webtest'
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption('--webtest'):
        return
    skip_webtest = pytest.mark.skip(reason='need --webtest option to run')
    for item in items:
        if 'webtest' in item.keywords:
            item.add_marker(skip_webtest)
