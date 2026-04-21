"""
Tests for the High School Management System API

This module contains comprehensive tests for all FastAPI endpoints,
including both happy path and error case scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original data
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Swimming Club": {
            "description": "Swimming training and water sports",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Studio": {
            "description": "Express creativity through painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater arts and performance training",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Learn public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    yield
    
    # Reset activities to original state after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 9 activities are returned
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Swimming Club" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Club" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that each activity has the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        # Check a specific activity has all required fields
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_list_is_array(self, client, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test successful signup adds participant to activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns proper success message"""
        email = "test@mergington.edu"
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for Programming Class"
    
    def test_signup_fails_when_activity_not_found(self, client, reset_activities):
        """Test signup returns 404 when activity doesn't exist"""
        response = client.post(
            "/activities/NonexistentClub/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_fails_when_student_already_registered(self, client, reset_activities):
        """Test signup returns 400 when student already registered"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_increments_participant_count(self, client, reset_activities):
        """Test that signup increases participant count"""
        initial_count = len(activities["Gym Class"]["participants"])
        
        client.post(
            "/activities/Gym Class/signup",
            params={"email": "newcomer@mergington.edu"}
        )
        
        final_count = len(activities["Gym Class"]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_with_multiple_students(self, client, reset_activities):
        """Test multiple different students can signup for same activity"""
        activity_name = "Basketball Team"
        
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "student1@mergington.edu"}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "student2@mergington.edu"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities[activity_name]["participants"]) == 2
        assert "student1@mergington.edu" in activities[activity_name]["participants"]
        assert "student2@mergington.edu" in activities[activity_name]["participants"]


class TestUnregisterForActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test successful unregister removes participant from activity"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Verify participant is registered before unregister
        assert email in activities[activity_name]["participants"]
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns proper success message"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity_name}"
    
    def test_unregister_fails_when_activity_not_found(self, client, reset_activities):
        """Test unregister returns 404 when activity doesn't exist"""
        response = client.delete(
            "/activities/NonexistentClub/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_fails_when_student_not_registered(self, client, reset_activities):
        """Test unregister returns 400 when student not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_decrements_participant_count(self, client, reset_activities):
        """Test that unregister decreases participant count"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        final_count = len(activities[activity_name]["participants"])
        assert final_count == initial_count - 1


class TestIntegrationFlows:
    """Integration tests for multiple operations"""
    
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test signup followed by unregister"""
        activity_name = "Art Studio"
        email = "test@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple signups and unregisters on same activity"""
        activity_name = "Swimming Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        assert len(activities[activity_name]["participants"]) == 3
        
        # Unregister first student
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": emails[0]}
        )
        assert response.status_code == 200
        
        # Verify count is correct
        assert len(activities[activity_name]["participants"]) == 2
        assert emails[0] not in activities[activity_name]["participants"]
        assert emails[1] in activities[activity_name]["participants"]
        assert emails[2] in activities[activity_name]["participants"]
    
    def test_signup_after_unregister(self, client, reset_activities):
        """Test student can re-signup after unregistering"""
        activity_name = "Drama Club"
        email = "actor@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert email in activities[activity_name]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert email not in activities[activity_name]["participants"]
        
        # Sign up again - should succeed
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
