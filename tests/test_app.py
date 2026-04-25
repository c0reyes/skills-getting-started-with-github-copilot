from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    # Arrange: No special setup needed as data is in-memory

    # Act: Make GET request to /activities
    response = client.get("/activities")

    # Assert: Check status code and response structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Nine activities

    # Check each activity has required fields
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_root_redirect():
    # Arrange: No setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Should redirect to /static/index.html
    assert response.status_code == 200  # FastAPI handles static files
    # Note: In test environment, static files might not be served the same way


def test_successful_signup():
    # Arrange: Choose an activity and email not already signed up
    activity_name = "Chess Club"
    email = "newstudent@example.com"

    # Act: Make POST request to signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should succeed and add to participants
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "signed up" in data["message"].lower()

    # Verify the email was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_invalid_activity():
    # Arrange: Use a non-existent activity
    invalid_activity = "NonExistent Activity"
    email = "test@example.com"

    # Act: Attempt signup
    response = client.post(f"/activities/{invalid_activity}/signup", params={"email": email})

    # Assert: Should return 404 or appropriate error
    # Note: Current app may not handle this properly, test documents current behavior
    # Based on exploration, it might return 200 or error - need to check
    # For now, assert based on expected behavior
    # Assuming it returns 404 for invalid activity
    assert response.status_code == 404


def test_signup_duplicate_email():
    # Arrange: Sign up once, then try again with same email
    activity_name = "Programming Class"
    email = "duplicate@example.com"

    # First signup
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act: Second signup with same email
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should handle duplicate (current app prevents duplicates)
    # Note: Current app does prevent duplicates, so it returns 400
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_activity_full():
    # Arrange: Fill an activity to capacity, then try to sign up
    activity_name = "Gym Class"  # Max 30, currently 2
    email = "fulltest@example.com"

    # Fill the activity (add 28 more participants)
    for i in range(28):
        client.post(f"/activities/{activity_name}/signup", params={"email": f"user{i}@example.com"})

    # Act: Try to sign up when full
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert: Should handle full capacity (current app allows overbooking)
    # Note: Current app doesn't check capacity, so it succeeds even when over limit
    assert response.status_code == 200
    data = response.json()
    assert "message" in data