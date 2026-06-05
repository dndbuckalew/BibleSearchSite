# File: backend/core/config/mongo_config.py
# Purpose:
# Centralized MongoDB configuration and client access
# for BTA Version 4 infrastructure onboarding.
#
# Constitutional Boundaries:
# - Infrastructure only
# - No orchestration logic
# - No semantic logic
# - No presentation behavior
# - No QueryService participation


from pymongo import MongoClient
from backend.core.config.settings import settings


class MongoConfig:
    """
    Centralized Mongo infrastructure configuration.
    """

    @staticmethod
    def get_client() -> MongoClient:
        return MongoClient(settings.MONGO_URI)

    @staticmethod
    def get_database():
        client = MongoConfig.get_client()
        return client[settings.MONGO_DB_NAME]
