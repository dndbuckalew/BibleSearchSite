# File: backend/core/services/registry_service.py
# Purpose:
# Centralized governance registry access layer for BTA Version 4.
#
# Responsibilities:
# - translation registry resolution
# - license registry validation
# - source registry validation
# - language registry coordination
# - runtime eligibility governance
#
# Constitutional Boundaries:
# - NOT QueryService orchestration
# - NOT semantic generation
# - NOT retrieval orchestration
# - NOT presentation coordination


from backend.core.config.mongo_config import MongoConfig


class RegistryService:
    """
    Governance-only registry infrastructure service.
    """

    def __init__(self):
        self.db = MongoConfig.get_database()
        self.translation_registry = self.db["translation_registry"]