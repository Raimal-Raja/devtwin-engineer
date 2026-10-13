# Database migration review (draft workflow)

Activation: review a proposed schema/data migration, or implement an authorized correction in the project's migration system.

Required evidence: database engine/version, migration order, old and new schema, existing-data assumptions, affected readers/writers, transaction behavior, representative synthetic records and rollback/recovery expectations. An empty-database success is not evidence for populated databases.

Investigation: trace constraints and default/backfill requirements against existing data. Check old/new application overlap, nullable transitions, indexes, foreign keys, deployment order and data-loss possibilities where relevant. Identify which operations require locks or rebuilds on the actual engine; consult official engine documentation when those facts are not established by the local exercise.

Actions: keep reviews read-only. For an authorized correction, use the established migration convention and synthetic or isolated data. Do not execute a migration against a live database merely to establish whether it works. Distinguish a reversible schema operation from restoration of data already overwritten or dropped.

Verification: exercise an existing-data fixture, new inserts, relevant constraints and the chosen rollback/recovery mechanism. Record engine/version and actual commands. A small in-memory SQLite test does not establish production locking, throughput or another engine's DDL semantics.

Failure handling: if production scale, engine details, old application compatibility or backups are unavailable, state those gaps. A failed migration remains unresolved until both recovery and the candidate are checked where possible.

Example: adding a NOT NULL status column without a default fails on populated SQLite orders. A synthetic contract requiring existing orders to be pending supports testing a default/backfill candidate; real status semantics still require project evidence.

Failure case: a rollback drops a column containing new information. Schema rollback alone cannot recover that information.

Expected output: concrete data/compatibility risks, source evidence, focused candidate if authorized, executed checks and explicit concurrency/recovery limits. Agent-level behavior remains unverified.
