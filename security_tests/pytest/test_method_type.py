import requests

URL = "http://localhost:8011/login"

def test_get_method_rejected():
    response = requests.get(URL)
    assert response.status_code == 405
