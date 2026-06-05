# ADR-001 — Persistence Architecture Transition

## Status

Approved

---

## Decision Date

2026-06-05

---

## Context

BTA Version 4 initiated a controlled persistence validation effort using MongoDB Atlas.

The purpose of the MongoDB implementation was intentionally limited to:

* Infrastructure onboarding validation
* Connectivity validation
* Configuration pattern validation
* Registry foundation experimentation
* Development workflow validation

No production scripture ingestion occurred.

No registry population occurred.

No semantic indexing occurred.

No production migration requirements existed.

MongoDB foundation validation was successfully completed and archived.

---

## Decision

MongoDB is retired as the future canonical persistence platform for BTA.

PostgreSQL + pgvector is adopted as the future persistence architecture direction.

MongoDB foundation validation artifacts are preserved in:

```text
archive/mongo-foundation-validation
```

---

## Rationale

MongoDB was retired not because of technical failure, but because BTA's long-term architecture evolved toward PostgreSQL + pgvector.

The decision was driven by alignment with:

* Deterministic orchestration architecture
* Governance-first registry management
* Future semantic indexing and vector capabilities
* Multi-translation coordination
* Future multilingual expansion
* Broader NSF/SBIR semantic research objectives
* Long-term AWS platform consolidation

MongoDB successfully fulfilled its intended validation objectives.

The architectural direction changed as BTA matured beyond initial persistence validation into a broader semantic orchestration and research platform.

---

## Consequences

### Retained

The following concepts remain part of the future persistence architecture:

* Translation Registry
* License Registry
* Source Registry
* Language Registry
* Book Registry
* Scripture Persistence
* Validation Hold Governance
* Persistence Connectivity Validation Pattern
* Persistence Foundation Initialization Pattern

### Retired

The following MongoDB-specific implementation artifacts were retired:

* MongoDB runtime dependencies
* MongoDB connectivity implementation
* MongoDB foundation initialization implementation
* MongoDB configuration dependencies
* MongoDB registry implementation

### Preserved

The following historical artifacts were intentionally preserved:

* MongoDB validation branch
* Architectural decision history
* Governance rationale
* Persistence validation patterns

---

## Future Direction

Future persistence architecture execution will introduce:

* PostgreSQL
* pgvector
* Governance registry persistence
* Translation participation hierarchy support
* Semantic indexing support
* Future multilingual expansion support
* Semantic bridge research support

PostgreSQL + pgvector becomes the canonical persistence platform for future BTA architecture execution.

---

## Related Artifacts

### Archive Branch

```text
archive/mongo-foundation-validation
```

### Repository Artifacts

```text
backend/infrastructure/scripts/init_persistence_foundation.py

backend/test_persistence_connection.py
```

---

## Architectural Note

This decision should not be interpreted as a rejection of MongoDB.

MongoDB was successfully evaluated and validated.

The retirement decision reflects an architectural evolution toward PostgreSQL + pgvector to better support BTA's long-term governance, semantic orchestration, multilingual, and NSF/SBIR research objectives.

This record is retained to preserve architectural traceability and prevent duplicate future evaluation efforts.
