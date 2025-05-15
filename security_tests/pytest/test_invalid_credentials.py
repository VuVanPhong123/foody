import requests

URL = "http://localhost:8011/login"

def test_wrong_username():
    response = requests.post(URL, json={"username": "not_exist", "password": "abc"})
    assert response.status_code == 401

def test_wrong_password():
    response = requests.post(URL, json={"username": "a", "password": "wrongpw"})
    assert response.status_code == 401
