"""
===========================================================
HCGO Source Acquisition & Staging Service (SASS)

Startup Validation

Purpose:
    Discovers, validates, registers, and inspects
    configured HCGO domains.

Platform:
    Human-Centered Governed Orchestration (HCGO)
===========================================================
"""

from pathlib import Path

from .config_loader import ConfigurationLoader
from .validator import ConfigurationValidator
from .registry import DomainRegistry
from .acquisition.acquisition_engine import AcquisitionEngine


SOURCE_LIBRARY = Path(r"D:\HCGO_Data\Source_Library")


def main():

    print()
    print("===================================================")
    print("HCGO Source Acquisition & Staging Service")
    print("Platform Startup")
    print("===================================================")
    print()

    loader = ConfigurationLoader(SOURCE_LIBRARY)
    validator = ConfigurationValidator()
    registry = DomainRegistry()
    acquisition = AcquisitionEngine()

    domains = loader.discover_domains()

    for domain in domains:

        domain_ok, _ = validator.validate_domain(
            domain.domain_config
        )

        acquisition_ok, _ = validator.validate_acquisition(
            domain.acquisition_config
        )

        if domain_ok and acquisition_ok:

            registry.register(domain)

            print(f"REGISTERED : {domain.domain_id}")

        else:

            print(f"FAILED     : {domain.domain_id}")

    print()
    print("===================================================")
    print("Source Inspection")
    print("===================================================")
    print()

    for domain in registry.all():

        result = acquisition.inspect_sources(domain)

        print(f"Domain : {result['domain']}")
        print(f"Status : {result['status']}")

        if len(result["files"]) == 0:

            print("Files  : None Found")

        else:

            print(f"Files  : {len(result['files'])}")

            for file in result["files"]:

                print(
                    f"    {file['name']} ({file['size']} bytes)"
                )

        print()

    print("===================================================")
    print(f"Validated Domains : {registry.count()}")
    print("Startup Complete")
    print("===================================================")


if __name__ == "__main__":
    main()
