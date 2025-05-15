import requests

URL = "http://localhost:8011/login"
INJECTION = "' OR '1'='1"

def test_sql_injection_username():
    response = requests.post(URL, json={"username": INJECTION, "password": "abc"})
    assert response.status_code != 200

def test_sql_injection_password():
    response = requests.post(URL, json={"username": "a", "password": INJECTION})
    assert response.status_code != 200
