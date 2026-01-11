from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Make a shallow copy of participants to restore after each test
    original = {k: v["participants"][: ] for k, v in activities.items()}
    yield
    for k, parts in original.items():
        activities[k]["participants"] = parts[:]


def test_get_activities():
    client = TestClient(app)
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Basketball Team" in data


def test_signup_and_duplicate_prevention():
    client = TestClient(app)
    email = "testuser@example.com"
    activity = "Basketball Team"

    # Signup should succeed
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should return 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400


def test_remove_participant():
    client = TestClient(app)
    activity = "Tennis Club"
    email = "james@mergington.edu"

    # Ensure participant exists
    assert email in activities[activity]["participants"]

    # Delete participant
    r = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r.status_code == 200
    assert email not in activities[activity]["participants"]

    # Deleting again should return 404
    r2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r2.status_code == 404
