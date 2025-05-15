import requests

URL = "http://localhost:8011/login"

def test_error_message_no_traceback():
    response = requests.post(URL, json={"username": "", "password": ""})
    if response.status_code != 200:
        text = str(response.text).lower()
        assert "traceback" not in text
        assert "error" not in text or "username" in text or "password" in text

def test_invalid_type():
    response = requests.post(URL, json={"username": 123, "password": 456})
    assert response.status_code != 200
