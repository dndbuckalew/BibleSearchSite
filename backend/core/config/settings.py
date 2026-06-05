# File: backend/config/settings.py
# Purpose:
# Centralized infrastructure environment settings
# for BTA Version 4 infrastructure services.
#
# Constitutional Boundaries:
# - Infrastructure configuration only
# - No orchestration logic
# - No semantic logic
# - No presentation logic


import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Centralized infrastructure settings authority.
    """

    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "bta_v4_dev")


settings = Settings()
