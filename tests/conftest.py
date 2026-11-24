import pytest

import Live


@pytest.fixture(autouse=True)
def fresh_live():
    Live.reset()
    yield
    Live.reset()


@pytest.fixture
def app():
    return Live.Application.get_application()


@pytest.fixture
def song(app):
    return app.get_document()
