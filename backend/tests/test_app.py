import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_app_runs(client):
    """Test that the app starts and returns something"""
    response = client.get('/')
    assert response.status_code in [200, 404]


def test_health_check(client):
    """Test the API is reachable"""
    response = client.get('/api/health')
    assert response.status_code == 200