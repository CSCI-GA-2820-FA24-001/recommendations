######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test Recommendation API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, RecommendationModel
from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendationService(TestCase):
    """REST API Server Tests for Recommendations"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(RecommendationModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST CREATE RECOMMENDATION
    # ----------------------------------------------------------
    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_recommendation = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_recommendation.serialize())
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["user_id"], test_recommendation.user_id)
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertAlmostEqual(
            new_recommendation["score"], test_recommendation.score, places=2
        )

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_recommendation = response.get_json()
        self.assertEqual(new_recommendation["user_id"], test_recommendation.user_id)
        self.assertEqual(new_recommendation["product_id"], test_recommendation.product_id)
        self.assertAlmostEqual(new_recommendation["score"], test_recommendation.score, places=2)


    # ----------------------------------------------------------
    # TEST UPDATE RECOMMENDATION
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # Create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the recommendation from the response
        created_recommendation = response.get_json()
        recommendation_id = created_recommendation["id"]

        # Update the recommendation
        updated_recommendation = created_recommendation
        updated_recommendation["score"] = 4.9  # Change the score as an example update
        
        # invalid content type
        response = self.client.put(
            f"{BASE_URL}/{recommendation_id}",
            json=updated_recommendation,
            headers={"Content-Type": "text/plain"}  # Incorrect Content-Type
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        
        # Send the PUT request to update the recommendation
        response = self.client.put(
            f"{BASE_URL}/{recommendation_id}",
            json=updated_recommendation,
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Retrieve the updated recommendation and verify the change
        response = self.client.get(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_data = response.get_json()
        self.assertEqual(updated_data["score"], 4.9)


    def test_update_nonexistent_recommendation(self):
        """It should return 404 when trying to update a non-existent recommendation"""
        # Attempt to update a recommendation with an ID that doesn't exist
        non_existent_id = 9999
        updated_data = {
            "user_id": 1,
            "product_id": 1,
            "score": 4.9
        }

        response = self.client.put(
            f"{BASE_URL}/{non_existent_id}",
            json=updated_data,
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    # ----------------------------------------------------------
    # TEST DELETE RECOMMENDATION
    # ----------------------------------------------------------
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        # First, create a recommendation to delete
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the ID of the newly created recommendation
        recommendation_id = response.get_json()["id"]

        # Send a DELETE request to remove the recommendation
        response = self.client.delete(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the recommendation has been deleted
        response = self.client.get(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ############################################################
    # Utility function to bulk Recommendations
    ############################################################
    def _create_recommendations(self, count: int = 1) -> list:
        """Factory method to create pets in bulk"""
        recommendation_list = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendation_list.append(test_recommendation)
        return recommendation_list

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_recommendations_list(self):
        """It should Get a list of recommendations"""
        self._create_recommendations(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)
