"""
Models for recommendations

All of the models are stored in this module
"""

import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for data validation errors when deserializing"""


class RecommendationModel(db.Model):
    """
    Class that represents a Recommendation
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    num_likes = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Recommendation user_id={self.user_id}, product_id={self.product_id}, score={self.score}>"

    def create(self):
        """
        Creates a Recommendation in the database
        """
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()  # Set default timestamp if not provided

        logger.info(
            "Creating recommendation for user_id=%s, product_id=%s",
            self.user_id,
            self.product_id,
        )
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating recommendation: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Recommendation in the database
        """
        logger.info(
            "Updating recommendation for user_id=%s, product_id=%s",
            self.user_id,
            self.product_id,
        )
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating recommendation: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info(
            "Deleting recommendation for user_id=%s, product_id=%s",
            self.user_id,
            self.product_id,
        )
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting recommendation: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "score": self.score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "num_likes": self.num_likes,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the recommendation data
        """
        try:
            self.user_id = data["user_id"]
            self.product_id = data["product_id"]
            self.score = data["score"]
            self.timestamp = data["timestamp"]
            self.num_likes = data.get("num_likes", 0)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return db.session.get(cls, by_id)

    @classmethod
    def find_by_user(cls, user_id):
        """Returns all Recommendations for a specific user"""
        logger.info("Processing lookup for user_id %s ...", user_id)
        return cls.query.filter(cls.user_id == user_id).all()

    @classmethod
    def find_by_product(cls, product_id):
        """Returns all Recommendations for a specific product"""
        logger.info("Processing lookup for product_id %s ...", product_id)
        return cls.query.filter(cls.product_id == product_id).all()

    @classmethod
    def find_by_filters(cls, filters=None):
        """
        Filters recommendations based on query parameters provided in a dictionary

        Args:
            filters (dict): A dictionary of filter parameters
        """
        filters = filters or {}
        query = cls.query

        if "user_id" in filters:
            query = query.filter(cls.user_id == filters["user_id"])
        if "product_id" in filters:
            query = query.filter(cls.product_id == filters["product_id"])
        if "score" in filters:
            query = query.filter(cls.score == filters["score"])  # Filter by exact score
        if "min_score" in filters:
            query = query.filter(cls.score >= filters["min_score"])
        if "max_score" in filters:
            query = query.filter(cls.score <= filters["max_score"])
        if "min_likes" in filters:
            query = query.filter(cls.num_likes >= filters["min_likes"])

        return query.all()
