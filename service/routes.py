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
RecommendationModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendations
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import RecommendationModel
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            {
                "service": "Recommendation Service",
                "version": "1.0.0",
                "description": "This service implements a REST API for CRUD recommendations.",
                "status": "Running",
                "endpoints": {
                    "create": "/recommendations (POST)",
                    "retrieve": "/recommendations/<id> (GET)",
                    "update": "/recommendations/<id> (PUT)",
                    "delete": "/recommendations/<id> (DELETE)",
                },
            }
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendation():
    """
    Create a Recommendation
    This endpoint will create a Recommendation based on the data in the body that is posted
    """
    app.logger.info("Request to Create a Recommendation...")
    check_content_type("application/json")

    recommendation = RecommendationModel()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)

    # Save the new Recommendation to the database
    recommendation.create()
    app.logger.info("Recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Recommendation
    location_url = url_for(
        "get_recommendation", recommendation_id=recommendation.id, _external=True
    )
    return (
        jsonify(recommendation.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# RETRIEVE A RECOMMENDATION BY ID
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendation(recommendation_id):
    """
    Retrieve a Recommendation
    This endpoint will return a Recommendation based on its id
    """
    app.logger.info(
        "Request to Retrieve a Recommendation with id [%s]", recommendation_id
    )

    recommendation = RecommendationModel.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id [{recommendation_id}] not found.",
        )

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendation(recommendation_id):
    """
    Update a Recommendation
    This endpoint will update a Recommendation based on the posted data
    """
    app.logger.info(
        "Request to Update a Recommendation with id [%s]", recommendation_id
    )
    check_content_type("application/json")

    recommendation = RecommendationModel.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id [{recommendation_id}] not found.",
        )

    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)
    recommendation.update()

    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<recommendation_id>", methods=["DELETE"])
def delete_recommendation(recommendation_id):
    """
    Delete a Recommendation
    This endpoint will delete a Recommendation based on its id
    """
    app.logger.info(
        "Request to Delete a Recommendation with id [%s]", recommendation_id
    )

    # Check if the recommendation_id is a valid integer
    if not recommendation_id.isdigit():
        app.logger.error("Invalid ID format: [%s]", recommendation_id)
        return {"error": "Invalid ID format"}, status.HTTP_400_BAD_REQUEST

    # Convert the recommendation_id to integer and try to find the recommendation
    recommendation_id = int(recommendation_id)
    recommendation = RecommendationModel.find(recommendation_id)

    if recommendation is None:
        app.logger.error("Recommendation with id [%s] not found", recommendation_id)
        return {"error": "Recommendation not found"}, status.HTTP_404_NOT_FOUND

    # Proceed with the deletion if recommendation is found
    recommendation.delete()
    app.logger.info("Recommendation with id [%s] has been deleted", recommendation_id)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL RECOMMENDATIONS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """
    List all Recommendations
    This endpoint will return all Recommendations or filter them by query parameters
    """
    app.logger.info("Request for recommendation list")

    recommendations = []

    # Parse query parameters
    user_id = request.args.get("user_id")
    product_id = request.args.get("product_id")

    if user_id:
        user_id = int(user_id)
        app.logger.info("Find by user_id: %s", user_id)
        recommendations = RecommendationModel.find_by_user(user_id)
    elif product_id:
        product_id = int(product_id)
        app.logger.info("Find by product_id: %s", product_id)
        recommendations = RecommendationModel.find_by_product(product_id)
    else:
        app.logger.info("Find all")
        recommendations = RecommendationModel.all()

    # Serialize the results
    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# GET NUMBER OF LIKES FOR A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/likes", methods=["GET"])
def get_recommendation_likes(recommendation_id):
    """
    Retrieve the number of likes for a Recommendation
    This endpoint returns the number of likes for a given recommendation by ID
    """
    app.logger.info(
        "Request to get the number of likes for recommendation id [%s]",
        recommendation_id,
    )

    recommendation = RecommendationModel.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id [{recommendation_id}] not found.",
        )

    return (
        jsonify({"id": recommendation_id, "likes": recommendation.num_likes}),
        status.HTTP_200_OK,
    )


######################################################################
# INCREMENT LIKES FOR A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/likes", methods=["POST"])
def increment_recommendation_likes(recommendation_id):
    """
    Increment the number of likes for a Recommendation
    This endpoint increments the number of likes for a given recommendation by ID
    """
    app.logger.info(
        "Request to increment likes for recommendation id [%s]", recommendation_id
    )

    recommendation = RecommendationModel.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id [{recommendation_id}] not found.",
        )

    # Increment the number of likes
    recommendation.num_likes = (
        recommendation.num_likes + 1 if recommendation.num_likes else 1
    )
    recommendation.update()

    return jsonify(recommendation.serialize()), status.HTTP_200_OK
