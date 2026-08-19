import os
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"
os.environ["OPENAI_API_KEY"] = ""
from fastapi.testclient import TestClient
from backend.app.main import app


def pytest_configure(config):
    pass


@pytest.fixture
def client():
    return TestClient(app)
