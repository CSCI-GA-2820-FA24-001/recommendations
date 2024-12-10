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

This service implements a REST API that allows you to Create, Read, Update,
and Delete Recommendations
"""

from datetime import datetime
from flask import request, current_app as app  # Group Flask imports together
from flask_restx import Resource, fields, reqparse, Api
from service.models import RecommendationModel
from service.common import status  # HTTP Status Codes


######################################################################
# Models
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Recommendations Demo RESTful Service",
    description="Recommendations API",
    default="recommendations",
    default_label="Recommendations Operations",
    doc="/apidocs",
    prefix="/api",
)

create_model = api.model(
    "Recommendation",
    {
        "user_id": fields.Integer(required=True, description="The User ID"),
        "product_id": fields.Integer(required=True, description="The Product ID"),
        "score": fields.Float(required=True, description="The Recommendation score"),
        "timestamp": fields.DateTime(
            default=datetime.utcnow(), description="The Recommendation timestamp"
        ),
        "num_likes": fields.Integer(default=0, description="Number of likes"),
    },
)

recommendation_model = api.inherit(
    "RecommendationModel",
    create_model,
    {"id": fields.Integer(readOnly=True, description="The unique Recommendation ID")},
)

# Query string arguments
recommendation_args = reqparse.RequestParser()
recommendation_args.add_argument(
    "user_id", type=int, location="args", required=False, help="Filter by User ID"
)
recommendation_args.add_argument(
    "product_id", type=int, location="args", required=False, help="Filter by Product ID"
)
recommendation_args.add_argument(
    "min_score", type=float, location="args", required=False, help="Minimum score"
)
recommendation_args.add_argument(
    "max_score", type=float, location="args", required=False, help="Maximum score"
)
recommendation_args.add_argument(
    "from_date", type=str, location="args", required=False, help="Filter by from_date"
)
recommendation_args.add_argument(
    "to_date", type=str, location="args", required=False, help="Filter by to_date"
)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


@api.route("/recommendations/<recommendation_id>")
@api.param("recommendation_id", "The Recommendation identifier")
class RecommendationResource(Resource):
    """Handles individual recommendation operations"""

    @api.doc("get_recommendation")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def get(self, recommendation_id):
        """Retrieve a Recommendation by its ID"""
        app.logger.info(f"Retrieving recommendation with id {recommendation_id}")
        if not recommendation_id.isdigit():  # Check if ID is valid
            api.abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid ID format: {recommendation_id}",
            )
        recommendation = RecommendationModel.find(int(recommendation_id))
        if not recommendation:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                "404 Not Found",
            )
        return recommendation.serialize(), status.HTTP_200_OK

    @api.doc("update_recommendation")
    @api.expect(create_model)
    @api.response(404, "Recommendation not found")
    @api.response(400, "Invalid data")
    @api.marshal_with(recommendation_model)
    def put(self, recommendation_id):
        """Update a Recommendation by its ID"""
        app.logger.info(f"Updating recommendation with id {recommendation_id}")

        # Validate the ID format if the recommendation exists
        if not recommendation_id.isdigit():
            api.abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid ID format: {recommendation_id}",
            )

        recommendation = RecommendationModel.find(recommendation_id)

        # If the recommendation doesn't exist, return a 404 error
        if not recommendation:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                "404 Not Found",
            )

        data = api.payload
        recommendation.deserialize(data)
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK

    @api.doc("delete_recommendation")
    @api.response(204, "Recommendation deleted")
    @api.response(404, "Recommendation not found")
    @api.response(400, "Invalid ID format")
    def delete(self, recommendation_id):
        """Delete a Recommendation by its ID"""
        app.logger.info(
            f"Request to delete Recommendation with id [{recommendation_id}]"
        )

        # Validate the ID format
        if not recommendation_id.isdigit():
            app.logger.error(f"Invalid ID format: [{recommendation_id}]")
            return {
                "error": f"Invalid ID format: {recommendation_id}"
            }, status.HTTP_400_BAD_REQUEST

        # Convert to integer and find the recommendation
        recommendation = RecommendationModel.find(int(recommendation_id))
        if not recommendation:
            return "404 Not Found", status.HTTP_404_NOT_FOUND

        # Delete the recommendation
        recommendation.delete()
        app.logger.info(
            f"Recommendation with id [{recommendation_id}] has been deleted."
        )
        return "", status.HTTP_204_NO_CONTENT


@api.route("/recommendations")
class RecommendationCollection(Resource):
    """Handles collection-level recommendation operations"""

    @api.doc("list_recommendations")
    @api.expect(recommendation_args, validate=True)
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """List or filter recommendations"""
        app.logger.info("Listing recommendations with filters")

        try:
            # Parse query parameters
            # args = recommendation_args.parse_args()
            args = recommendation_args.parse_args()
            user_id = args.get("user_id")
            product_id = args.get("product_id")
            min_score = args.get("min_score")
            max_score = args.get("max_score")
            min_likes = request.args.get("min_likes", type=int)
            max_likes = request.args.get("max_likes", type=int)
            # from_date = request.args.get("from_date")
            # to_date = request.args.get("to_date")

            # # Validate date formats
            # if from_date:
            #     app.logger.debug(
            #         f"Validating from_date: {from_date}"
            #     )  # Debug: Log the from_date value
            #     try:

            #         from_date = datetime.strptime(from_date, "%Y-%m-%d")
            #         app.logger.debug(
            #             f"Validated from_date successfully: {from_date}"
            #         )  # Debug: Log the parsed date
            #     except ValueError:
            #         app.logger.error("Invalid from_date format: [%s]", from_date)
            #         return {
            #             "error": "Invalid from_date format. Use YYYY-MM-DD."
            #         }, status.HTTP_400_BAD_REQUEST

            # if to_date:
            #     try:
            #         to_date = datetime.strptime(to_date, "%Y-%m-%d")
            #     except ValueError:
            #         app.logger.error("Invalid to_date format: [%s]", to_date)
            #         return {
            #             "error": "Invalid to_date format. Use YYYY-MM-DD."
            #         }, status.HTTP_400_BAD_REQUEST

            # Start with base query
            query = RecommendationModel.query

            # Apply filters
            if user_id:
                query = query.filter(RecommendationModel.user_id == user_id)
            if product_id:
                query = query.filter(RecommendationModel.product_id == product_id)
            if min_score is not None:
                query = query.filter(RecommendationModel.score >= min_score)
            if max_score is not None:
                query = query.filter(RecommendationModel.score <= max_score)
            if min_likes is not None:
                query = query.filter(RecommendationModel.num_likes >= min_likes)
            if max_likes is not None:
                query = query.filter(RecommendationModel.num_likes <= max_likes)
            # if from_date:
            #     query = query.filter(RecommendationModel.timestamp >= from_date)
            # if to_date:
            #     query = query.filter(RecommendationModel.timestamp <= to_date)

            # Execute query
            recommendations = query.all()
            results = [rec.serialize() for rec in recommendations]

            app.logger.info("Returning %d recommendations", len(results))
            return results, status.HTTP_200_OK

        except ValueError as e:
            app.logger.error(f"Error while filtering recommendations: {e}")
            return {"error": "Invalid query parameters"}, status.HTTP_400_BAD_REQUEST

    @api.doc("create_recommendation")
    @api.expect(create_model)
    @api.response(400, "Invalid data")
    @api.marshal_with(recommendation_model, code=201)
    def post(self):
        """Create a new Recommendation"""
        app.logger.info("Creating a new recommendation")
        data = api.payload
        recommendation = RecommendationModel()
        recommendation.deserialize(data)
        recommendation.create()
        location_url = api.url_for(
            RecommendationResource, recommendation_id=recommendation.id, _external=True
        )
        return (
            recommendation.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


@api.route("/recommendations/<recommendation_id>/likes")
@api.param("recommendation_id", "The Recommendation identifier")
class RecommendationLikesResource(Resource):
    """Handles operations related to likes"""

    @api.doc("get_recommendation_likes")
    @api.response(404, "Recommendation not found")
    @api.response(200, "Retrieved Successfully")
    def get(self, recommendation_id):
        """Get the number of likes for a Recommendation"""
        app.logger.info(f"Getting likes for recommendation id {recommendation_id}")
        if not recommendation_id.isdigit():
            api.abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid ID format: {recommendation_id}",
            )
        recommendation = RecommendationModel.find(int(recommendation_id))
        if not recommendation:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                "404 Not Found",
            )
        return {
            "id": recommendation_id,
            "likes": recommendation.num_likes,
        }, status.HTTP_200_OK

    @api.doc("increment_recommendation_likes")
    @api.response(404, "Recommendation not found")
    @api.marshal_with(recommendation_model)
    def post(self, recommendation_id):
        """Increment likes for a Recommendation"""
        app.logger.info(f"Incrementing likes for recommendation id {recommendation_id}")
        if not recommendation_id.isdigit():
            api.abort(
                status.HTTP_400_BAD_REQUEST,
                f"Invalid ID format: {recommendation_id}",
            )
        recommendation = RecommendationModel.find(int(recommendation_id))
        if not recommendation:
            api.abort(
                status.HTTP_404_NOT_FOUND,
                "404 Not Found",
            )
        recommendation.num_likes += 1
        recommendation.update()
        return recommendation.serialize(), status.HTTP_200_OK


@api.route("/recommendations/filter")
class RecommendationFilterResource(Resource):
    """Handles filtering recommendations"""

    @api.doc("find_recommendations_by_filters")
    @api.expect(recommendation_args, validate=True)
    @api.response(400, "Invalid query parameters")
    @api.marshal_list_with(recommendation_model)
    def get(self):
        """
        Find Recommendations by Filters
        This endpoint will return recommendations based on query parameters such as user_id,
        product_id, score range, and minimum number of likes.
        """
        app.logger.info("Request to filter Recommendations")

        # Extract query parameters
        filters = {
            "user_id": request.args.get("user_id", type=int),
            "product_id": request.args.get("product_id", type=int),
            "score": request.args.get("score", type=float),
            "min_score": request.args.get("min_score", type=float),
            "max_score": request.args.get("max_score", type=float),
            "min_likes": request.args.get("min_likes", type=int),
        }

        # Remove None values to avoid filtering with empty parameters
        filters = {key: value for key, value in filters.items() if value is not None}

        # Validate query parameters
        errors = []
        if filters.get("min_score", 0) < 0:
            errors.append("min_score must be non-negative.")
        if filters.get("max_score", 0) < 0:
            errors.append("max_score must be non-negative.")

        if errors:
            app.logger.error(f"Invalid query parameters: {errors}")
            return {"errors": errors}, status.HTTP_400_BAD_REQUEST

        try:
            # Call the `find_by_filters` method in the model
            recommendations = RecommendationModel.find_by_filters(filters)

            # Serialize the results
            results = [recommendation.serialize() for recommendation in recommendations]
            app.logger.info("Returning %d filtered recommendations", len(results))

            return results, status.HTTP_200_OK

        except ValueError as e:
            app.logger.error(f"Error while filtering recommendations: {e}")
            return {"error": "Invalid query parameters"}, status.HTTP_400_BAD_REQUEST
