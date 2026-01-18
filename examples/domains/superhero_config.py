"""
Domain configuration for superhero capabilities validation.
"""

from models import HeroCapabilities

# What you're validating
VALIDATION_TASK = "superhero capabilities"

# Items to validate
ITEMS_TO_VALIDATE = [
    "Thor",
    "Iron Man",
    "Captain America",
    "Wolverine",
    "Superman",
    "Aquaman",
    "Spiderman",
    "Black Panther",
    "Hulk",
    "Black Widow",
]

# Pydantic schema to use
VALIDATION_SCHEMA = HeroCapabilities

# Optional: Custom database path (relative to data/ directory)
# If not specified, uses the default validation_logs.db
DATABASE_PATH = "superhero_validation.db"
