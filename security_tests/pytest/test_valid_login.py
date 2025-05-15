import requests

URL = "http://localhost:8011/login"

def test_valid_login():
    response = requests.post(URL, json={"username": "a", "password": "a"})
    assert response.status_code == 200
    assert "username" in response.json()
