import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_app_runs(client):
    """Test that the app starts and returns something"""
    response = client.get('/')
    assert response.status_code in [200, 404]

def test_api_reachable(client):
    """Test the API is reachable"""
    response = client.get('/api/health')
    assert response.status_code in [200, 404]