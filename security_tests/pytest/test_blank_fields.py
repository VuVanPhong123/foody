import requests

URL = "http://localhost:8011/login"

def test_username_empty():
    response = requests.post(URL, json={"username": "", "password": "abc123"})
    assert response.status_code != 200

def test_password_empty():
    response = requests.post(URL, json={"username": "user1", "password": ""})
    assert response.status_code != 200

def test_both_empty():
    response = requests.post(URL, json={"username": "", "password": ""})
    assert response.status_code != 200

