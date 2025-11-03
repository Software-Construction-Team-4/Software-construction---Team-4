import requests
import pytest

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = "replace_with_real_admin_token"  # you need a valid session token

@pytest.mark.parametrize("username", ["testtest", "otheruser"])
def test_billing_endpoint(username):
    headers = {"Authorization": ADMIN_TOKEN}

    if username == "testtest":
        # Normal endpoint: /billing
        url = f"{BASE_URL}/billing"
    else:
        # Admin lookup: /billing/<username>
        url = f"{BASE_URL}/billing/{username}"

    response = requests.get(url, headers=headers)

    # ✅ Check the endpoint responds correctly
    assert response.status_code == 200, f"Unexpected status {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list of sessions"

    if username == "otheruser":
        # Optional: check all sessions belong to 'otheruser'
        # (but note: your current response doesn’t include 'user')
        for s in data:
            assert "session" in s
            assert "parking" in s
