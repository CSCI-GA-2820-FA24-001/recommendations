######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Recommendation Steps

Steps file for recommendations.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from wsgi import app
from service.models import db, RecommendationModel

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following recommendations")
def step_impl(context):
    """Delete all Recommendations and load new ones"""
    with app.app_context():
        # Delete all existing recommendations
        db.session.query(RecommendationModel).delete()
        db.session.commit()
        # Load new recommendations from the table
        for row in context.table:
            recommendation = RecommendationModel()
            recommendation.user_id = int(row["user_id"])
            recommendation.product_id = int(row["product_id"])
            recommendation.score = float(row["score"])
            recommendation.timestamp = row.get("timestamp", None)
            db.session.add(recommendation)
        db.session.commit()
