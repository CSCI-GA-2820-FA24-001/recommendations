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
from datetime import datetime
from wsgi import app
from service.common import status
from service.models import db, RecommendationModel
from .factories import RecommendationFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/recommendations"


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
            "/api/recommendations", data=test_recommendation.serialize()
        )
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
        response = self.client.delete("/api/recommendations/invalid-id")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid ID format", response.get_json()["error"])

    def test_delete_recommendation_not_found(self):
        """It should return 404 Not Found when the recommendation does not exist"""
        response = self.client.delete("/api/recommendations/99999")
        self.assertEqual(response.status_code, 404)

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

        response = self.client.delete(f"{BASE_URL}/invalid-id")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = response.get_json()
        self.assertIsNotNone(response_data)  # Ensure the response is not empty
        self.assertIn("Invalid ID format", response_data.get("error", ""))

    def test_create_recommendation_no_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is missing"""
        response = self.client.post("/api/recommendations", data="{}")
        self.assertEqual(response.status_code, 415)

    def test_create_recommendation_invalid_content_type(self):
        """It should return 415 Unsupported Media Type when Content-Type is incorrect"""
        headers = {"Content-Type": "text/plain"}  # Incorrect Content-Type
        response = self.client.post("/api/recommendations", data="{}", headers=headers)
        self.assertEqual(response.status_code, 415)

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

    def test_get_recommendation_likes(self):
        """It should get the number of likes for a recommendation"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()["id"]

        # Check likes count (should start with 0)
        response = self.client.get(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["likes"], 0)

    def test_increment_recommendation_likes(self):
        """It should increment the likes for a recommendation"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recommendation_id = response.get_json()["id"]

        # Increment likes
        response = self.client.post(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check likes count (should be 1 after increment)
        response = self.client.get(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["likes"], 1)

    def test_like_recommendation(self):
        """It should increment the likes for a recommendation"""
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_recommendation = response.get_json()
        recommendation_id = new_recommendation["id"]

        # Get initial likes count
        response = self.client.get(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        initial_likes = response.get_json()["likes"]

        # Increment likes
        response = self.client.post(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify likes increased by 1
        response = self.client.get(f"{BASE_URL}/{recommendation_id}/likes")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["likes"], initial_likes + 1)

    def test_like_recommendation_not_found(self):
        """It should return 404 when trying to like a non-existent recommendation"""
        response = self.client.post(f"{BASE_URL}/99999/likes")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_recommendations_by_score(self):
        """It should Query Recommendations by score range"""
        recommendations = self._create_recommendations(10)
        test_score = recommendations[0].score

        response = self.client.get(
            BASE_URL,
            query_string=f"min_score={test_score-0.1}&max_score={test_score+0.1}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()

        # Check that all returned recommendations are within score range
        for rec in data:
            self.assertTrue(test_score - 0.1 <= rec["score"] <= test_score + 0.1)

    def test_query_recommendations_by_likes(self):
        """It should Query Recommendations by number of likes"""
        recommendations = self._create_recommendations(5)
        # Like the first recommendation twice
        rec_id = recommendations[0].id
        self.client.post(f"{BASE_URL}/{rec_id}/likes")
        self.client.post(f"{BASE_URL}/{rec_id}/likes")

        response = self.client.get(BASE_URL, query_string="min_likes=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()

        # Should only return recommendations with 2 or more likes
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]["num_likes"] >= 2)

    def test_query_recommendations_by_date(self):
        """It should Query Recommendations by date range"""
        self._create_recommendations(5)
        today = datetime.now().strftime("%Y-%m-%d")

        response = self.client.get(BASE_URL, query_string=f"from_date={today}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) > 0)

    def test_health(self):
        """It should get the health endpoint"""
        resp = self.client.get("/health")  # Use self.client instead of app
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_find_recommendations_by_filters(self):
        """It should filter recommendations based on query parameters"""
        recommendations = self._create_recommendations(10)

        # Use one of the created recommendations to test filters
        test_user_id = recommendations[0].user_id
        test_product_id = recommendations[0].product_id
        test_min_score = recommendations[0].score - 0.1
        test_max_score = recommendations[0].score + 0.1
        test_min_likes = recommendations[0].num_likes

        # Make a request with all filters
        response = self.client.get(
            f"{BASE_URL}/filter",
            query_string={
                "user_id": test_user_id,
                "product_id": test_product_id,
                "min_score": test_min_score,
                "max_score": test_max_score,
                "min_likes": test_min_likes,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the results match the filters
        data = response.get_json()
        self.assertGreater(len(data), 0)
        for rec in data:
            self.assertEqual(rec["user_id"], test_user_id)
            self.assertEqual(rec["product_id"], test_product_id)
            self.assertGreaterEqual(rec["score"], test_min_score)
            self.assertLessEqual(rec["score"], test_max_score)
            self.assertGreaterEqual(rec["num_likes"], test_min_likes)

    def test_find_recommendations_by_user_id_filter(self):
        """It should filter recommendations by user_id only"""
        recommendations = self._create_recommendations(5)
        test_user_id = recommendations[0].user_id

        response = self.client.get(
            f"{BASE_URL}/filter", query_string={"user_id": test_user_id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate the filtered results
        data = response.get_json()
        self.assertGreater(len(data), 0)
        for rec in data:
            self.assertEqual(rec["user_id"], test_user_id)

    def test_find_recommendations_no_filters(self):
        """It should return all recommendations when no filters are provided"""
        recommendations = self._create_recommendations(5)

        response = self.client.get(f"{BASE_URL}/filter")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure all recommendations are returned
        data = response.get_json()
        self.assertEqual(len(data), len(recommendations))

    def test_find_recommendations_invalid_query(self):
        """It should return an empty list for invalid filters"""

        self._create_recommendations(5)

        # Use filters that won't match any recommendation
        response = self.client.get(
            f"{BASE_URL}/filter",
            query_string={"user_id": 9999, "min_score": 100.0, "max_score": 200.0},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure no recommendations are returned
        data = response.get_json()
        self.assertEqual(len(data), 0)

    def test_find_recommendations_with_invalid_parameters(self):
        """It should return 400 Bad Request for invalid query parameters"""
        response = self.client.get(
            f"{BASE_URL}/filter",
            query_string={"min_score": -5},  # Invalid: min_score should not be negative
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # errors = response.get_json().get("errors", [])
        # print(errors)
        # self.assertIn("min_score must be non-negative.", errors)

    def test_find_recommendations_score_range(self):
        """It should filter recommendations wiscore range"""
        recommendations = self._create_recommendations(10)
        min_score = recommendations[0].score - 0.5
        max_score = recommendations[0].score + 0.5

        response = self.client.get(
            f"{BASE_URL}/filter",
            query_string={"min_score": min_score, "max_score": max_score},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all results are within the score range
        data = response.get_json()
        for rec in data:
            self.assertGreaterEqual(rec["score"], min_score)
            self.assertLessEqual(rec["score"], max_score)

    def test_find_recommendations_min_likes(self):
        """It should filter recommendations with a minimum number of likes"""
        recommendations = self._create_recommendations(5)
        min_likes = max(
            rec.num_likes for rec in recommendations
        )  # Use the highest `num_likes`

        response = self.client.get(
            f"{BASE_URL}/filter", query_string={"min_likes": min_likes}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify all results have `num_likes` >= min_likes
        data = response.get_json()
        self.assertGreater(len(data), 0)
        for rec in data:
            self.assertGreaterEqual(rec["num_likes"], min_likes)

    # Increasing the code coverage
    def test_get_recommendation_invalid_id(self):
        """It should return 400 for invalid ID format in GET"""
        response = self.client.get(f"{BASE_URL}/invalid-id")
        # Verify the status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the error message
        response_data = response.get_json()

        self.assertIn("Invalid ID format", response_data["message"])

    def test_delete_recommendation_invalid_id(self):
        """It should return 400 Bad Request for invalid ID format in DELETE"""
        response = self.client.delete("/api/recommendations/invalid-id")

        # Verify the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the error message
        response_data = response.get_json()
        self.assertIn("Invalid ID format", response_data["error"])

    def test_update_recommendation_invalid_id_format(self):
        """It should return 400 Bad Request for invalid ID format in PUT"""
        # Prepare test data (valid recommendation data)
        test_recommendation = RecommendationFactory()
        updated_data = test_recommendation.serialize()
        updated_data["score"] = 4.9  # Update some field

        # Try to update a recommendation that doesn't exist (ID 'invalid-id')
        response = self.client.put(f"{BASE_URL}/invalid-id", json=updated_data)

        # Verify the response status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the error message
        response_data = response.get_json()
        print(response_data)
        self.assertIn("Invalid ID format", response_data["message"])

    def test_filter_recommendations_by_max_likes(self):
        """It should filter recommendations by maximum number of likes"""
        # Create sample recommendations
        self._create_recommendations(
            5
        )  # Helper function to create test recommendations

        # Set max_likes to filter recommendations
        max_likes = 2
        response = self.client.get(f"/api/recommendations?max_likes={max_likes}")

        # Verify the response status
        self.assertEqual(response.status_code, 200)

        # Verify the filtered recommendations
        recommendations = response.get_json()
        self.assertIsInstance(recommendations, list)
        for recommendation in recommendations:
            self.assertLessEqual(recommendation["num_likes"], max_likes)
