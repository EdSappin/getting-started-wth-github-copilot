"""
Tests for the Mergington High School Activities API
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Test suite for activities endpoints"""

    def test_get_activities(self):
        """Test that we can fetch all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Basketball" in data
        assert "Tennis" in data

    def test_activity_structure(self):
        """Test that activity data has required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball"]
        
        assert "leader" in activity
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_signup_for_activity(self):
        """Test signing up for an activity"""
        response = client.post(
            "/activities/Tennis/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicate_student(self):
        """Test that duplicate signup fails"""
        # First signup should succeed
        client.post(
            "/activities/Tennis/signup?email=duplicate@mergington.edu"
        )
        # Second signup should fail
        response = client.post(
            "/activities/Tennis/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test that signup for nonexistent activity fails"""
        response = client.post(
            "/activities/NonexistentClub/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_participant(self):
        """Test unregistering a participant"""
        # First signup
        client.post(
            "/activities/Chess Club/signup?email=unregtest@mergington.edu"
        )
        # Then unregister
        response = client.post(
            "/activities/Chess Club/unregister?email=unregtest@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]

    def test_unregister_nonexistent_participant(self):
        """Test that unregistering nonexistent participant fails"""
        response = client.post(
            "/activities/Drama Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity(self):
        """Test that unregistering from nonexistent activity fails"""
        response = client.post(
            "/activities/FakeClub/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_root_redirect(self):
        """Test that root redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
