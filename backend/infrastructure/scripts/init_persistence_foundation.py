"""
Persistence Foundation Initialization

Purpose:
Initialize governance registries and persistence
structures required by BTA.

MongoDB foundation initialization has been retired.
MongoDB was retired not because of technical failure, but because
BTA's long-term architecture evolved toward PostgreSQL + pgvector.

The decision was driven by alignment with:
- Deterministic orchestration architecture
- Governance-first registry management
- Future semantic indexing and vector capabilities
- Multi-translation coordination
- Future multilingual expansion
- Broader NSF/SBIR semantic research objectives
- Long-term platform consolidation on AWS

Mongo foundation validation remains archived in:
archive/mongo-foundation-validation

PostgreSQL + pgvector foundation initialization will be introduced
during persistence architecture execution.

Expected foundation domains:

- translation_registry
- license_registry
- source_registry
- language_registry
- book_registry
- scripture_passages
- validation_hold
"""