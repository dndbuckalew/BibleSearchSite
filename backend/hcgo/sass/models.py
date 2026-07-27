"""
HCGO Source Acquisition & Staging Service (SASS)

Domain Models
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DomainConfiguration:
    """
    Represents a configured HCGO knowledge domain.
    """

    domain_id: str
    display_name: str
    domain_path: Path

    enabled: bool

    acquisition_mode: str

    domain_config: dict = field(default_factory=dict)
    acquisition_config: dict = field(default_factory=dict)
