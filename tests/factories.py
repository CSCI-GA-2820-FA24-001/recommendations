"""
Test Factory to make fake Recommendation objects for testing
"""
from datetime import datetime
import factory
from factory.fuzzy import FuzzyChoice, FuzzyFloat
from service.models import RecommendationModel

class RecommendationFactory(factory.Factory):
    """Creates fake recommendations for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to the RecommendationModel data model"""
        model = RecommendationModel

    id = factory.Sequence(lambda n: n)  # Sequentially increasing ID
    user_id = factory.Sequence(lambda n: n + 1)  # Simulates unique user IDs
    product_id = factory.Sequence(lambda n: n + 1000)  # Simulates unique product IDs
    score = FuzzyFloat(0.5, 5.0, precision=2)  # Random score between 0.5 and 5.0
    timestamp = factory.LazyFunction(datetime.now)  # Current timestamp
