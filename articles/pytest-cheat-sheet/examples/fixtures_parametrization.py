import pytest


@pytest.fixture(params=["settings.Setup1", "settings.Setup2"])
def app(request):
    instance = create_flask_app(request.param)
    with instance.app_context():
        yield instance