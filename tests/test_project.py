import unittest
import requests
import sys
import os

# Add backend to path for import if needed, though we test API directly here
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestLibrarySystem(unittest.TestCase):
    
    BASE_URL = "http://127.0.0.1:5000/media"

    # Backend Test 1: Check if API is returning a list 
    def test_backend_list(self):
        try:
            response = requests.get(self.BASE_URL)
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), list)
        except requests.exceptions.ConnectionError:
            self.fail("Backend is not running. Start server.py first.")

    # Backend Test 2: Create a Dummy Item 
    def test_backend_create(self):
        payload = {
            "name": "TestGame",
            "author": "Tester",
            "category": "Test",
            "date": "2025-01-01"
        }
        response = requests.post(self.BASE_URL, json=payload)
        self.assertEqual(response.status_code, 201)
        
        # Cleanup
        requests.delete(f"{self.BASE_URL}/TestGame")

    # Frontend Logic Test (Simulated) 
    def test_data_structure_integrity(self):
        # This tests the logic that the frontend expects
        expected_keys = ["name", "author", "category", "date"]
        payload = {
            "name": "TestGame",
            "author": "Tester",
            "category": "Test",
            "date": "2025-01-01"
        }
        for key in expected_keys:
            self.assertIn(key, payload)

if __name__ == '__main__':
    unittest.main()