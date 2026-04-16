import pytest
from starlette.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """TestClient for pytest-bdd."""
    return TestClient(app)
