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
Test cases for Recommendation Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from datetime import datetime
from wsgi import app
from service.models import RecommendationModel, DataValidationError, db

# from .factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  R E C O M M E N D A T I O N   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendationModel(TestCase):
    """Test Cases for RecommendationModel"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(RecommendationModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_recommendation(self):
        """It should Create a recommendation and assert that it exists"""

        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.utcnow(),
            num_likes=0,
        )

        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.user_id, 123)
        self.assertEqual(recommendation.product_id, 456)
        self.assertEqual(recommendation.score, 4.5)
        self.assertIsNotNone(recommendation.timestamp)

    def test_serialize_a_recommendation(self):
        """It should serialize a recommendation into a dictionary"""

        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.utcnow(),
            num_likes=10,
        )
        serial_recommendation = recommendation.serialize()

        self.assertEqual(serial_recommendation["user_id"], 123)
        self.assertEqual(serial_recommendation["product_id"], 456)
        self.assertEqual(serial_recommendation["score"], 4.5)
        self.assertIsNotNone(serial_recommendation["timestamp"])
        self.assertEqual(
            serial_recommendation["id"], None
        )  # Since it hasn't been saved to DB yet
        self.assertEqual(recommendation.num_likes, 10)

    def test_update_a_recommendation(self):
        """It should update a recommendation in the database"""

        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.utcnow(),
            num_likes=0,
        )
        recommendation.create()

        # Update the score and product_id
        recommendation.score = 4.9
        recommendation.product_id = 789
        recommendation.update()

        # Fetch the updated recommendation
        updated_recommendation = RecommendationModel.find(recommendation.id)

        self.assertEqual(updated_recommendation.product_id, 789)
        self.assertEqual(updated_recommendation.score, 4.9)

    def test_delete_a_recommendation(self):
        """It should delete a recommendation from the database"""

        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.utcnow(),
            num_likes=0,
        )
        recommendation.create()

        # Delete the recommendation
        recommendation.delete()

        # Try to retrieve the deleted recommendation
        deleted_recommendation = RecommendationModel.find(recommendation.id)

        self.assertIsNone(deleted_recommendation)

    def test_deserialize_a_recommendation(self):
        """It should deserialize a recommendation from a dictionary"""
        data = {
            "user_id": 123,
            "product_id": 456,
            "score": 4.5,
            "timestamp": "2024-10-14T12:00:00Z",
            "num_likes": 10,
        }
        recommendation = RecommendationModel()
        recommendation.deserialize(data)

        self.assertEqual(recommendation.user_id, 123)
        self.assertEqual(recommendation.product_id, 456)
        self.assertEqual(recommendation.score, 4.5)
        self.assertIsNotNone(recommendation.timestamp)
        self.assertEqual(recommendation.num_likes, 10)

    def test_deserialize_missing_data(self):
        """It should raise DataValidationError when deserializing with missing fields"""
        incomplete_data = {
            "user_id": 123,
            # "product_id" and "score" are missing
        }
        recommendation = RecommendationModel()
        with self.assertRaises(DataValidationError):
            recommendation.deserialize(incomplete_data)

    def test_deserialize_empty_data(self):
        """It should raise DataValidationError when deserializing empty data"""
        recommendation = RecommendationModel()
        with self.assertRaises(DataValidationError):
            recommendation.deserialize({})

    def test_deserialize_with_invalid_type(self):
        """It should raise DataValidationError when the input data is not a dictionary"""
        recommendation = RecommendationModel()

        # Test with a non-dictionary type (string in this case)
        with self.assertRaises(DataValidationError) as context:
            recommendation.deserialize("This is not a dictionary")  # Passing a string

        self.assertIn(
            "Invalid Recommendation: body of request contained bad or no data",
            str(context.exception),
        )

        # Test with None (another invalid type)
        with self.assertRaises(DataValidationError) as context:
            recommendation.deserialize(None)  # Passing None

        self.assertIn(
            "Invalid Recommendation: body of request contained bad or no data",
            str(context.exception),
        )

    @patch("service.models.db.session.commit", side_effect=Exception("Database error"))
    @patch("service.models.db.session.rollback")
    def test_create_recommendation_with_db_error(
        self, mock_db_rollback, mock_db_commit
    ):
        """It should rollback when the database throws an error during create"""
        recommendation = RecommendationModel(user_id=123, product_id=456, score=4.5)
        with self.assertRaises(DataValidationError):
            recommendation.create()
        self.assertTrue(mock_db_commit.called)
        self.assertTrue(mock_db_rollback.called)

    @patch(
        "service.models.db.session.commit",
        side_effect=[None, Exception("Database error")],
    )
    @patch("service.models.db.session.rollback")
    def test_update_recommendation_with_db_error(
        self, mock_db_rollback, mock_db_commit
    ):
        """It should rollback when the database throws an error during update"""
        # Allow create to work without error
        recommendation = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation.create()  # Successfully create the recommendation

        # Update recommendation and trigger error
        recommendation.score = 4.9
        with self.assertRaises(DataValidationError):
            recommendation.update()

        self.assertTrue(mock_db_commit.called)
        self.assertTrue(mock_db_rollback.called)

    @patch(
        "service.models.db.session.commit",
        side_effect=[None, Exception("Database error")],
    )
    @patch("service.models.db.session.rollback")
    def test_delete_recommendation_with_db_error(
        self, mock_db_rollback, mock_db_commit
    ):
        """It should rollback when the database throws an error during delete"""
        # Allow create to work without error
        recommendation = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation.create()  # Successfully create the recommendation

        # Raise error during delete
        with self.assertRaises(DataValidationError):
            recommendation.delete()

        self.assertTrue(mock_db_commit.called)
        self.assertTrue(mock_db_rollback.called)

    # def test_delete_recommendation_with_invalid_id(self):
    #     """It should raise DataValidationError for invalid ID format"""
    #     invalid_id = "invalid-id"  # Pass a string as an invalid ID

    #     # We simulate an invalid ID by trying to delete a non-integer value.
    #     # The model find method will raise a ValueError for invalid ID type if validation is added.
    #     with self.assertRaises(ValueError):
    #         recommendation = RecommendationModel.find(invalid_id)
    #         if recommendation:
    #             recommendation.delete()

    # def test_delete_recommendation_with_invalid_id_format(self):
    #     """It should handle Delete request with invalid ID format"""
    #     # This assumes `self.client` exists in the service route tests
    #     response = self.client.delete("/recommendations/invalid-id")
    #     self.assertEqual(response.status_code, 400)

    def test_update_with_invalid_data(self):
        """It should raise DataValidationError when trying to update with invalid data"""
        recommendation = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation.create()

        # Set to invalid data
        recommendation.user_id = None  # Set invalid data

        # Use no_autoflush to prevent automatic flushing of invalid data
        with db.session.no_autoflush:
            with self.assertRaises(DataValidationError):
                recommendation.update()

    def test_find_by_user(self):
        """It should return recommendations for a given user"""
        recommendation1 = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation2 = RecommendationModel(user_id=123, product_id=789, score=4.0)
        recommendation1.create()
        recommendation2.create()

        recommendations = RecommendationModel.find_by_user(123)
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0].user_id, 123)
        self.assertEqual(recommendations[1].user_id, 123)

    def test_find_by_user_no_recommendations(self):
        """It should return an empty list when no recommendations exist for a user"""
        recommendations = RecommendationModel.find_by_user(999)  # Non-existent user_id
        self.assertEqual(len(recommendations), 0)

    def test_find_by_product_no_recommendations(self):
        """It should return an empty list when no recommendations exist for a product"""
        recommendations = RecommendationModel.find_by_product(
            999
        )  # Non-existent product_id
        self.assertEqual(len(recommendations), 0)

    def test_find_by_product(self):
        """It should return recommendations for a given product"""
        recommendation1 = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation2 = RecommendationModel(user_id=124, product_id=456, score=4.0)
        recommendation1.create()
        recommendation2.create()

        recommendations = RecommendationModel.find_by_product(456)
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0].product_id, 456)
        self.assertEqual(recommendations[1].product_id, 456)

    def test_get_all_recommendations(self):
        """It should return all recommendations from the database"""
        # Create a few recommendations
        recommendation1 = RecommendationModel(user_id=123, product_id=456, score=4.5)
        recommendation2 = RecommendationModel(user_id=124, product_id=789, score=3.8)
        recommendation1.create()
        recommendation2.create()

        # Call the `all()` method
        recommendations = RecommendationModel.all()

        # Check that both recommendations are returned
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0].user_id, 123)
        self.assertEqual(recommendations[1].user_id, 124)


class TestRecommendationFilter(TestCase):
    """Test Cases for RecommendationModel"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(RecommendationModel).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_find_by_filters_user_id(self):
        """It should return recommendations filtered by user_id"""
        recommendation1 = RecommendationModel(
            user_id=123, product_id=456, score=4.5, num_likes=5
        )
        recommendation2 = RecommendationModel(
            user_id=123, product_id=789, score=4.0, num_likes=3
        )
        recommendation3 = RecommendationModel(
            user_id=124, product_id=456, score=3.5, num_likes=2
        )
        recommendation1.create()
        recommendation2.create()
        recommendation3.create()

        # Find by user_id
        recommendations = RecommendationModel.find_by_filters(user_id=123)
        self.assertEqual(len(recommendations), 2)
        for rec in recommendations:
            self.assertEqual(rec.user_id, 123)

    def test_find_by_filters_product_id(self):
        """It should return recommendations filtered by product_id"""
        recommendation1 = RecommendationModel(
            user_id=123, product_id=456, score=4.5, num_likes=5
        )
        recommendation2 = RecommendationModel(
            user_id=124, product_id=456, score=4.0, num_likes=3
        )
        recommendation3 = RecommendationModel(
            user_id=123, product_id=789, score=3.5, num_likes=2
        )
        recommendation1.create()
        recommendation2.create()
        recommendation3.create()

        # Find by product_id
        recommendations = RecommendationModel.find_by_filters(product_id=456)
        self.assertEqual(len(recommendations), 2)
        for rec in recommendations:
            self.assertEqual(rec.product_id, 456)

    def test_find_by_filters_score(self):
        """It should return recommendations filtered by score"""
        recommendation1 = RecommendationModel(
            user_id=123, product_id=456, score=4.5, num_likes=5
        )
        recommendation2 = RecommendationModel(
            user_id=124, product_id=456, score=4.0, num_likes=3
        )
        recommendation3 = RecommendationModel(
            user_id=123, product_id=789, score=4.5, num_likes=2
        )
        recommendation1.create()
        recommendation2.create()
        recommendation3.create()

        # Find by score
        recommendations = RecommendationModel.find_by_filters(score=4.5)
        self.assertEqual(len(recommendations), 2)
        for rec in recommendations:
            self.assertEqual(rec.score, 4.5)

    def test_find_by_filters_combined(self):
        """It should return recommendations matching multiple filters"""
        recommendation1 = RecommendationModel(
            user_id=123, product_id=456, score=4.5, num_likes=5
        )
        recommendation2 = RecommendationModel(
            user_id=124, product_id=456, score=4.0, num_likes=3
        )
        recommendation3 = RecommendationModel(
            user_id=123, product_id=789, score=3.5, num_likes=2
        )
        recommendation1.create()
        recommendation2.create()
        recommendation3.create()

        # Find by user_id and product_id
        recommendations = RecommendationModel.find_by_filters(
            user_id=123, product_id=456
        )
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].user_id, 123)
        self.assertEqual(recommendations[0].product_id, 456)
