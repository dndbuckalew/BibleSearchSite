"""
===========================================================
HCGO Source Acquisition & Staging Service (SASS)

Domain Registry

Purpose:
    Maintains the collection of configured HCGO domains
    after discovery and validation.

Author:
    TAD Concepts LLC

Platform:
    Human-Centered Governed Orchestration (HCGO)
===========================================================
"""

from .models import DomainConfiguration


class DomainRegistry:
    """
    Registry of validated HCGO domains.
    """

    def __init__(self):

        self._domains = {}

    def register(self, domain: DomainConfiguration):

        self._domains[domain.domain_id] = domain

    def get(self, domain_id: str):

        return self._domains.get(domain_id)

    def all(self):

        return list(self._domains.values())

    def count(self):

        return len(self._domains)
