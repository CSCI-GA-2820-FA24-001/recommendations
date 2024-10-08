"""
Models for recommendations

All of the models are stored in this module
"""

import logging
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
    user_id = db.Column(db.Integer, nullable=False)  # ID of the user receiving the recommendation
    product_id = db.Column(db.Integer, nullable=False)  # ID of the recommended product
    score = db.Column(db.Float, nullable=False)  # Score representing recommendation confidence
    timestamp = db.Column(db.DateTime, nullable=False)  # Timestamp when the recommendation was made

    def __repr__(self):
        return f"<Recommendation user_id={self.user_id}, product_id={self.product_id}, score={self.score}>"

    def create(self):
        """
        Creates a Recommendation in the database
        """
        logger.info("Creating recommendation for user_id=%s, product_id=%s", self.user_id, self.product_id)
        self.id = None  # pylint: disable=invalid-name
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
        logger.info("Updating recommendation for user_id=%s, product_id=%s", self.user_id, self.product_id)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating recommendation: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting recommendation for user_id=%s, product_id=%s", self.user_id, self.product_id)
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
            "timestamp": self.timestamp
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
        return cls.query.get(by_id)

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
