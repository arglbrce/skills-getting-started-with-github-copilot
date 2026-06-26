from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def restore_activity_state():
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_and_existing_participants():
    # Arrange
    expected_activity = "Chess Club"
    expected_participant = "michael@mergington.edu"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_activity in data
    assert expected_participant in data[expected_activity]["participants"]


def test_signup_adds_new_participant_to_activity():
    # Arrange
    activity_name = "Gym Class"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_bad_request():
    # Arrange
    activity_name = "Gym Class"
    existing_email = "john@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_unregisters_participant_from_activity():
    # Arrange
    activity_name = "Basketball Club"
    email = "ava@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_delete_unregistered_participant_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@student.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
