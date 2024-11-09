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
        self.assertEqual(
            new_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertAlmostEqual(
            new_recommendation["score"], test_recommendation.score, places=2
        )

    def test_create_recommendation_with_invalid_content_type(self):
        """It should not Create a new Recommendation with invalid Content-Type"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(
            BASE_URL, data=test_recommendation.serialize()
        )  # Missing "json=" parameter
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

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

        # Send the PUT request to update the recommendation
        response = self.client.put(
            f"{BASE_URL}/{recommendation_id}", json=updated_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Retrieve the updated recommendation and verify the change
        response = self.client.get(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_data = response.get_json()
        self.assertEqual(updated_data["score"], 4.9)

    def test_update_recommendation_not_found(self):
        """It should return 404 when trying to Update a non-existent Recommendation"""
        test_recommendation = RecommendationFactory()
        updated_data = test_recommendation.serialize()
        updated_data["score"] = 4.9  # Update some field

        # Try to update a recommendation that doesn't exist (ID 9999)
        response = self.client.put(f"{BASE_URL}/9999", json=updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST DELETE A RECOMMENDATION
    # ----------------------------------------------------------
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        # First, create a new recommendation
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the recommendation from the response
        new_recommendation = response.get_json()
        recommendation_id = new_recommendation["id"]

        # Now, delete the recommendation by ID
        response = self.client.delete(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to retrieve the deleted recommendation, expecting a 404
        response = self.client.get(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recommendation_invalid_id_format(self):
        """It should return 400 Bad Request when the ID format is invalid"""
        response = self.client.delete("/recommendations/invalid-id")  # Non-integer ID
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ID format", response.get_json()["error"])

    def test_delete_recommendation_not_found(self):
        """It should return 404 Not Found when the recommendation does not exist"""
        response = self.client.delete("/recommendations/99999")  # Non-existent ID
        self.assertEqual(response.status_code, 404)
        self.assertIn("Recommendation not found", response.get_json()["error"])

    # ----------------------------------------------------------
    # TEST RETRIEVE A RECOMMENDATION
    # ----------------------------------------------------------
    def test_get_recommendation(self):
        """It should Retrieve a Recommendation by ID"""
        # First, create a new recommendation
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Retrieve the recommendation from the response
        new_recommendation = response.get_json()
        recommendation_id = new_recommendation["id"]

        # Now, retrieve the recommendation by ID
        response = self.client.get(f"{BASE_URL}/{recommendation_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the response data
        retrieved_recommendation = response.get_json()
        self.assertEqual(
            retrieved_recommendation["user_id"], test_recommendation.user_id
        )
        self.assertEqual(
            retrieved_recommendation["product_id"], test_recommendation.product_id
        )
        self.assertAlmostEqual(
            retrieved_recommendation["score"], test_recommendation.score, places=2
        )

    def test_get_recommendation_not_found(self):
        """It should return 404 Not Found when the recommendation doesn't exist"""
        # Try to retrieve a non-existent recommendation
        response = self.client.get(
            f"{BASE_URL}/9999"
        )  # 9999 is an arbitrary non-existent ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recommendation_with_missing_data(self):
        """It should not Create a new Recommendation with missing data"""
        incomplete_data = {"user_id": 123}  # Missing product_id, score, timestamp
        response = self.client.post(BASE_URL, json=incomplete_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_recommendation_with_invalid_id(self):
        """It should handle Delete request with invalid ID format"""
        # Pass a string instead of an integer for the recommendation ID
        response = self.client.delete(f"{BASE_URL}/invalid-id")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is missing"""
        response = self.client.post(
            "/recommendations", data="{}"
        )  # Missing Content-Type
        self.assertEqual(response.status_code, 415)
        self.assertIn("Content-Type must be", response.get_json()["message"])

    def test_create_recommendation_invalid_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is incorrect"""
        headers = {"Content-Type": "text/plain"}  # Incorrect Content-Type
        response = self.client.post("/recommendations", data="{}", headers=headers)
        self.assertEqual(response.status_code, 415)
        self.assertIn(
            "Content-Type must be application/json", response.get_json()["message"]
        )

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

    def test_query_by_product_id(self):
        """It should Query Recommendations by a source product id"""
        recommendations = self._create_recommendations(5)
        test_id = int(recommendations[0].product_id)
        name_count = len([rec for rec in recommendations if rec.product_id == test_id])
        response = self.client.get(BASE_URL, query_string=f"product_id={test_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        for rec in data:
            self.assertEqual(rec["product_id"], test_id)

    def test_query_by_user_id(self):
        """It should Query Recommendations by a source user id"""
        recommendations = self._create_recommendations(5)
        test_id = int(recommendations[0].user_id)
        name_count = len([rec for rec in recommendations if rec.user_id == test_id])
        response = self.client.get(BASE_URL, query_string=f"user_id={test_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        for rec in data:
            self.assertEqual(rec["user_id"], test_id)

    def test_query_by_user_and_product_id(self):
        """It should query recommendations by both user_id and product_id"""
        recommendations = self._create_recommendations(10)
        test_user_id = int(recommendations[0].user_id)
        test_product_id = int(recommendations[0].product_id)

        expected_recommendations = [
            rec
            for rec in recommendations
            if rec.user_id == test_user_id and rec.product_id == test_product_id
        ]
        expected_count = len(expected_recommendations)

        response = self.client.get(
            BASE_URL,
            query_string=f"user_id={test_user_id}&product_id={test_product_id}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), expected_count)

        for rec in data:
            self.assertEqual(rec["user_id"], test_user_id)
            self.assertEqual(rec["product_id"], test_product_id)
