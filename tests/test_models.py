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
from wsgi import app
from service.models import RecommendationModel, DataValidationError, db
from .factories import RecommendationFactory

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
        from datetime import datetime
        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.now()
        )
        
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.user_id, 123)
        self.assertEqual(recommendation.product_id, 456)
        self.assertEqual(recommendation.score, 4.5)
        self.assertIsNotNone(recommendation.timestamp)
    
    def test_serialize_a_recommendation(self):
        """It should serialize a recommendation into a dictionary"""
        from datetime import datetime
        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.now()
        )
        serial_recommendation = recommendation.serialize()
        
        self.assertEqual(serial_recommendation["user_id"], 123)
        self.assertEqual(serial_recommendation["product_id"], 456)
        self.assertEqual(serial_recommendation["score"], 4.5)
        self.assertIsNotNone(serial_recommendation["timestamp"])
        self.assertEqual(serial_recommendation["id"], None)  # Since it hasn't been saved to DB yet
    
    def test_update_a_recommendation(self):
        """It should update a recommendation in the database"""
        from datetime import datetime
        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.now()
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
        from datetime import datetime
        recommendation = RecommendationModel(
            user_id=123,
            product_id=456,
            score=4.5,
            timestamp=datetime.now()
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
            "timestamp": "2024-10-14T12:00:00Z"
        }
        recommendation = RecommendationModel()
        recommendation.deserialize(data)

        self.assertEqual(recommendation.user_id, 123)
        self.assertEqual(recommendation.product_id, 456)
        self.assertEqual(recommendation.score, 4.5)
        self.assertIsNotNone(recommendation.timestamp)
