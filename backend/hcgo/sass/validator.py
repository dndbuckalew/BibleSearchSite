"""
===========================================================
HCGO Source Acquisition & Staging Service (SASS)

Configuration Validator

Purpose:
    Validates HCGO domain configuration files before
    acquisition processing begins.

Author:
    TAD Concepts LLC

Platform:
    Human-Centered Governed Orchestration (HCGO)
===========================================================
"""

from pathlib import Path


class ConfigurationValidator:
    """
    Validates HCGO domain configuration.
    """

    REQUIRED_DOMAIN_KEYS = [
        "schema_version",
        "domain",
        "governance",
        "lifecycle",
    ]

    REQUIRED_ACQUISITION_KEYS = [
        "schema_version",
        "domain_id",
        "acquisition",
        "sources",
        "validation",
        "processing",
        "publication",
    ]

    def validate_domain(self, domain: dict):

        missing = [
            key for key in self.REQUIRED_DOMAIN_KEYS
            if key not in domain
        ]

        return (len(missing) == 0, missing)

    def validate_acquisition(self, acquisition: dict):

        missing = [
            key for key in self.REQUIRED_ACQUISITION_KEYS
            if key not in acquisition
        ]

        return (len(missing) == 0, missing)
