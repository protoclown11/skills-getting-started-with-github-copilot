import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.original_activity = activities.get("Test Activity")
        activities["Test Activity"] = {"participants": ["student@mergington.edu"]}

    def tearDown(self):
        if self.original_activity is None:
            activities.pop("Test Activity", None)
        else:
            activities["Test Activity"] = self.original_activity

    def test_unregister_removes_participant(self):
        response = self.client.delete(
            "/activities/Test%20Activity/signup?email=student%40mergington.edu"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(activities["Test Activity"]["participants"], [])
        self.assertEqual(
            response.json(),
            {"message": "Unregistered student@mergington.edu from Test Activity"},
        )

    def test_unregister_returns_not_found_for_unknown_activity(self):
        response = self.client.delete(
            "/activities/Unknown%20Activity/signup?email=student%40mergington.edu"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Activity not found"})

    def test_unregister_returns_not_found_for_unregistered_participant(self):
        activities["Test Activity"]["participants"] = []
        response = self.client.delete(
            "/activities/Test%20Activity/signup?email=student%40mergington.edu"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"detail": "Student is not signed up for this activity"},
        )
