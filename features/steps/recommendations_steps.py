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
Recommendation Steps

Steps file for recommendations.feature
"""
import requests
from behave import given
from compare import expect


@given("the following recommendations")
def step_impl(context):
    """Delete all Recommendations and load new ones"""
    # List all of the recommendations and delete them one by one
    rest_endpoint = f"{context.base_url}/recommendations"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for recommendation in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{recommendation['id']}")
        expect(context.resp.status_code).to_equal(204)

    # load the database with new recommendations
    for row in context.table:
        recommendation = {
            "user_id": int(row["user_id"]),
            "product_id": int(row["product_id"]),
            "score": float(row["score"]),
            "timestamp": row["timestamp"],
            "num_likes": int(row["num_likes"]),
        }
        context.resp = requests.post(rest_endpoint, json=recommendation)
        expect(context.resp.status_code).to_equal(201)
