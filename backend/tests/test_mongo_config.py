# File: backend/tests/test_mongo_config.py
# Purpose:
# Validate centralized Mongo configuration onboarding
# for BTA Version 4 infrastructure governance.


from backend.core.config.mongo_config import MongoConfig


def test_database_connection():
    db = MongoConfig.get_database()

    print(f"Database Target: {db.name}")
    print("Centralized MongoConfig operational.")


if __name__ == "__main__":
    test_database_connection()