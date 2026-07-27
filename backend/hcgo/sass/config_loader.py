"""
HCGO Source Acquisition & Staging Service (SASS)

Configuration Loader
"""

from pathlib import Path
import yaml

from .models import DomainConfiguration


class ConfigurationLoader:

    def __init__(self, source_library: Path):
        self.source_library = source_library

    def discover_domains(self):

        configured_domains = []

        for folder in sorted(self.source_library.iterdir()):

            if not folder.is_dir():
                continue

            domain_yaml = folder / "domain.yaml"
            acquisition_yaml = folder / "acquisition.yaml"

            if not domain_yaml.exists():
                continue

            if not acquisition_yaml.exists():
                continue

            with open(domain_yaml, "r", encoding="utf-8") as f:
                domain = yaml.safe_load(f)

            with open(acquisition_yaml, "r", encoding="utf-8") as f:
                acquisition = yaml.safe_load(f)

            configured_domains.append(
                DomainConfiguration(
                    domain_id=domain["domain"]["id"],
                    display_name=domain["domain"]["display_name"],
                    domain_path=folder,
                    enabled=(domain["domain"]["status"] == "active"),
                    acquisition_mode=acquisition["acquisition"]["mode"],
                    domain_config=domain,
                    acquisition_config=acquisition,
                )
            )

        return configured_domains
