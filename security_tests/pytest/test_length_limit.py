import requests

URL = "http://localhost:8011/login"
LONG_STRING = "A" * 10000

def test_long_username():
    response = requests.post(URL, json={"username": LONG_STRING, "password": "abc"})
    assert response.status_code != 200

def test_long_password():
    response = requests.post(URL, json={"username": "user", "password": LONG_STRING})
    assert response.status_code != 200
