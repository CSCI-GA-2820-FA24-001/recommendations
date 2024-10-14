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
            user_id=123, product_id=456, score=4.5, timestamp=datetime.now()
        )

        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.user_id, 123)
        self.assertEqual(recommendation.product_id, 456)
        self.assertEqual(recommendation.score, 4.5)
        self.assertIsNotNone(recommendation.timestamp)

    def test_list_all_recommendations(self):
        """It should List all recommendations in the database"""
        recommendations_list = RecommendationModel.all()
        self.assertEqual(recommendations_list, [])
        # Create 5 recommendations
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        # See if we get back 5 recommendations
        recommendations = RecommendationModel.all()
        self.assertEqual(len(recommendations), 5)

    def test_find_by_user(self):
        """It should Find recommendations by user_id"""
        recommendation1 = RecommendationFactory(user_id=101)
        recommendation2 = RecommendationFactory(user_id=102)
        recommendation1.create()
        recommendation2.create()

        # Test finding by user_id
        recommendations = RecommendationModel.find_by_user(101)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].user_id, 101)

    def test_find_by_product(self):
        """It should Find recommendations by product_id"""
        recommendation1 = RecommendationFactory(product_id=201)
        recommendation2 = RecommendationFactory(product_id=202)
        recommendation1.create()
        recommendation2.create()

        # Test finding by product_id
        recommendations = RecommendationModel.find_by_product(201)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_id, 201)
