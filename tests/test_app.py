import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_activity(monkeypatch):
    activity = {"participants": ["student@mergington.edu"]}
    monkeypatch.setitem(activities, "Test Activity", activity)
    return activity


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert response.json()[expected_activity]["description"]
    assert response.json()[expected_activity]["participants"]


def test_signup_adds_participant(client, test_activity):
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Test%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Test Activity"
    }
    assert email in test_activity["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_bad_request_for_existing_participant(client, test_activity):
    # Arrange
    email = "student@mergington.edu"
    original_participants = test_activity["participants"].copy()

    # Act
    response = client.post(
        "/activities/Test%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }
    assert test_activity["participants"] == original_participants


def test_unregister_removes_participant(client, test_activity):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Test%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert test_activity["participants"] == []
    assert response.json() == {
        "message": f"Unregistered {email} from Test Activity"
    }


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_participant(
    client, test_activity
):
    # Arrange
    email = "missingstudent@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Test%20Activity/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
