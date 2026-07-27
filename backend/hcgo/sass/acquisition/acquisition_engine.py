"""
HCGO Source Acquisition & Staging Service (SASS)

Acquisition Engine
"""

from pathlib import Path

from ..models import DomainConfiguration


class AcquisitionEngine:

    def inspect_sources(self, domain: DomainConfiguration):

        source_path = domain.domain_path / "source"

        if not source_path.exists():

            return {
                "domain": domain.domain_id,
                "status": "SOURCE_FOLDER_MISSING",
                "files": []
            }

        files = []

        for item in sorted(source_path.iterdir()):

            if item.is_file():

                files.append({
                    "name": item.name,
                    "size": item.stat().st_size
                })

        return {
            "domain": domain.domain_id,
            "status": "READY",
            "files": files
        }
