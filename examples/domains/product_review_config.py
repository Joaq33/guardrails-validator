"""
Domain configuration for product review sentiment analysis.
Simple example with fewer items for quick testing.
"""
from pydantic import BaseModel, Field

class ProductReview(BaseModel):
    """Schema for product review analysis."""
    is_positive: bool = Field(description="Whether the review has positive sentiment")
    mentions_quality: bool = Field(description="Whether quality is mentioned")
    mentions_price: bool = Field(description="Whether price is mentioned")

# Validation configuration
VALIDATION_TASK = "product review sentiment analysis"

ITEMS_TO_VALIDATE = [
    "Great product, totally worth it!",
    "Poor quality, not worth the money",
    "Amazing value for the price",
    "Disappointing purchase"
]

VALIDATION_SCHEMA = ProductReview

# Optional: Custom database path
DATABASE_PATH = "product_reviews.db"
