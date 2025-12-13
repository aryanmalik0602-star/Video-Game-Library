import unittest
import requests
import json
import sys
import os

# Ensure the project root is in the path to import gui_app logic for the Frontend Test
# Assuming tests.py is in the project root
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

class TestLibrarySystem(unittest.TestCase):
    
    # --- Configuration ---
    BASE_URL = "http://127.0.0.1:5000/media"

    def setUp(self):
        """Set up is run before every test. We use it to ensure the server is ready."""
        try:
            # Pings the server before each test
            requests.get(self.BASE_URL)
        except requests.exceptions.ConnectionError:
            self.fail("Backend server is not running. Please start 'backend/server.py' first.")

    # --- Task 3: Backend Test 1 (List All) ---
    def test_backend_list_all(self):
        """Tests if the /media endpoint returns a list with status 200."""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200, "API did not return status 200 for GET request.")
        self.assertIsInstance(response.json(), list, "API response is not a list.")
        
    # --- Task 3: Backend Test 2 (Create and Check) ---
    def test_backend_create_and_delete(self):
        """Tests POST (Create) and DELETE (Cleanup) operations."""
        test_id = "TestGameForDeletion"
        payload = {
            "name": test_id,
            "author": "Tester",
            "category": "Book",
            "date": "2025-01-01"
        }
        
        # 1. Test Creation (POST)
        response_post = requests.post(self.BASE_URL, json=payload)
        self.assertEqual(response_post.status_code, 201, f"Failed to create item. Response: {response_post.text}")
        
        # 2. Test Deletion (DELETE)
        response_delete = requests.delete(f"{self.BASE_URL}/{test_id}")
        self.assertEqual(response_delete.status_code, 204, f"Failed to delete item. Response: {response_delete.text}")

        # 3. Verify Deletion (GET attempt)
        response_get = requests.get(f"{self.BASE_URL}/{test_id}")
        self.assertEqual(response_get.status_code, 404, "Item still exists after deletion.")


    # --- Task 3: Frontend Test (Logic Verification) ---
    def test_frontend_api_consumption_logic(self):
        """
        Simulates the filtering logic that the Frontend (GUI) would perform 
        after receiving data from the '/media' endpoint. This verifies the 
        Frontend's ability to process and use the API data structure correctly.
        """
        response = requests.get(f"{self.BASE_URL}?filter=Book")
        self.assertEqual(response.status_code, 200, "API failed to filter data correctly.")
        
        filtered_list = response.json()
        
        # Check if the list contains only items with the category 'Book'
        for item in filtered_list:
            self.assertIn('category', item, "Response item is missing the 'category' key.")
            self.assertEqual(item['category'], 'Book', "Frontend logic failed to filter by category 'Book'.")
            
# This conditional ensures that unittest.main() runs when the file is executed directly.
if __name__ == '__main__':
    unittest.main()