"""
HCGO PostgreSQL Architecture Audit

Purpose:
    Read-only inspection of the current PostgreSQL database structure
    for HCGO Version 6 architecture validation.

Evaluates database structure relevant to:

    AREA 1 - HCGO Platform / Semantic Metadata
    AREA 2 - Canonical Domain Knowledge
    AREA 3 - Runtime Access / Publication Boundary

IMPORTANT:
    This script DOES NOT modify the database.

Version: 6.0
"""

import os
from pathlib import Path

import psycopg


# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

import getpass

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "bta_dev"
DB_USER = "postgres"

DB_PASSWORD = getpass.getpass("PostgreSQL Password: ")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------------------------------------------------------------
# Output Helpers
# ------------------------------------------------------------------

def heading(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def subheading(title: str) -> None:
    print()
    print("-" * 80)
    print(title)
    print("-" * 80)


# ------------------------------------------------------------------
# Database Queries
# ------------------------------------------------------------------

def get_database_info(cursor):
    cursor.execute(
        """
        SELECT
            current_database(),
            current_user,
            version();
        """
    )
    return cursor.fetchone()


def get_schemas(cursor):
    cursor.execute(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT IN (
            'pg_catalog',
            'information_schema',
            'pg_toast'
        )
        ORDER BY schema_name;
        """
    )
    return cursor.fetchall()


def get_tables(cursor):
    cursor.execute(
        """
        SELECT
            table_schema,
            table_name
        FROM information_schema.tables
        WHERE table_type = 'BASE TABLE'
          AND table_schema NOT IN (
              'pg_catalog',
              'information_schema'
          )
        ORDER BY table_schema, table_name;
        """
    )
    return cursor.fetchall()


def get_columns(cursor, schema_name, table_name):
    cursor.execute(
        """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchall()


def get_primary_keys(cursor, schema_name, table_name):
    cursor.execute(
        """
        SELECT
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = %s
          AND tc.table_name = %s
        ORDER BY kcu.ordinal_position;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchall()


def get_foreign_keys(cursor, schema_name, table_name):
    cursor.execute(
        """
        SELECT
            kcu.column_name,
            ccu.table_schema AS referenced_schema,
            ccu.table_name AS referenced_table,
            ccu.column_name AS referenced_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema = %s
          AND tc.table_name = %s
        ORDER BY kcu.column_name;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchall()


def get_unique_constraints(cursor, schema_name, table_name):
    cursor.execute(
        """
        SELECT
            tc.constraint_name,
            kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'UNIQUE'
          AND tc.table_schema = %s
          AND tc.table_name = %s
        ORDER BY tc.constraint_name, kcu.ordinal_position;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchall()


def get_indexes(cursor, schema_name, table_name):
    cursor.execute(
        """
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = %s
          AND tablename = %s
        ORDER BY indexname;
        """,
        (schema_name, table_name),
    )
    return cursor.fetchall()


def get_row_count(cursor, schema_name, table_name):
    safe_schema = '"' + schema_name.replace('"', '""') + '"'
    safe_table = '"' + table_name.replace('"', '""') + '"'

    cursor.execute(
        f"SELECT COUNT(*) FROM {safe_schema}.{safe_table};"
    )

    return cursor.fetchone()[0]


def get_views(cursor):
    cursor.execute(
        """
        SELECT
            table_schema,
            table_name
        FROM information_schema.views
        WHERE table_schema NOT IN (
            'pg_catalog',
            'information_schema'
        )
        ORDER BY table_schema, table_name;
        """
    )
    return cursor.fetchall()


# ------------------------------------------------------------------
# Architecture Classification
# ------------------------------------------------------------------

PLATFORM_TERMS = {
    "domain",
    "knowledge_asset",
    "asset",
    "semantic_profile",
    "profile",
    "provenance",
    "source",
    "ingestion",
    "publication",
    "publish",
}

BTA_TERMS = {
    "translation",
    "translations",
    "book",
    "books",
    "chapter",
    "chapters",
    "verse",
    "verses",
    "scripture",
    "scripture_text",
}


def classify_table(table_name: str) -> str:
    name = table_name.lower()

    if any(term in name for term in PLATFORM_TERMS):
        return "AREA 1 - HCGO Platform / Semantic Metadata"

    if any(term in name for term in BTA_TERMS):
        return "AREA 2 - Canonical Domain Knowledge"

    return "UNCLASSIFIED - Requires Review"


# ------------------------------------------------------------------
# Main Audit
# ------------------------------------------------------------------

def main() -> None:

    heading("HCGO PostgreSQL Architecture Audit")

    print(f"Database     : {DB_NAME}")
    print(f"Host         : {DB_HOST}:{DB_PORT}")
    print(f"User         : {DB_USER}")
    print("Mode         : READ ONLY")
    print("Version      : 6.0")

    try:
        with psycopg.connect(DATABASE_URL) as connection:

            # Enforce read-only transaction behavior.
            connection.execute("SET TRANSACTION READ ONLY")

            with connection.cursor() as cursor:

                # --------------------------------------------------
                # Database Information
                # --------------------------------------------------

                heading("DATABASE INFORMATION")

                database_name, database_user, version = get_database_info(cursor)

                print(f"Database : {database_name}")
                print(f"User     : {database_user}")
                print(f"Version  : {version}")

                # --------------------------------------------------
                # Schemas
                # --------------------------------------------------

                heading("DATABASE SCHEMAS")

                schemas = get_schemas(cursor)

                for schema in schemas:
                    print(f"- {schema[0]}")

                # --------------------------------------------------
                # Tables
                # --------------------------------------------------

                tables = get_tables(cursor)

                heading("TABLE INVENTORY")

                if not tables:
                    print("No application tables found.")

                for schema_name, table_name in tables:
                    classification = classify_table(table_name)

                    print(
                        f"{schema_name}.{table_name}"
                        f"  -->  {classification}"
                    )

                # --------------------------------------------------
                # Detailed Table Inspection
                # --------------------------------------------------

                heading("DETAILED TABLE STRUCTURE")

                for schema_name, table_name in tables:

                    subheading(f"{schema_name}.{table_name}")

                    print(
                        f"Architecture Area : "
                        f"{classify_table(table_name)}"
                    )

                    # Row Count

                    try:
                        row_count = get_row_count(
                            cursor,
                            schema_name,
                            table_name,
                        )
                        print(f"Row Count         : {row_count}")
                    except Exception as exc:
                        print(f"Row Count         : ERROR ({exc})")
                        connection.rollback()
                        connection.execute("SET TRANSACTION READ ONLY")

                    # Columns

                    print()
                    print("COLUMNS")

                    columns = get_columns(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    for (
                        column_name,
                        data_type,
                        nullable,
                        default,
                    ) in columns:

                        print(
                            f"  {column_name}"
                            f" | {data_type}"
                            f" | Nullable={nullable}"
                            f" | Default={default}"
                        )

                    # Primary Keys

                    print()
                    print("PRIMARY KEY")

                    primary_keys = get_primary_keys(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    if primary_keys:
                        for key in primary_keys:
                            print(f"  {key[0]}")
                    else:
                        print("  NONE")

                    # Foreign Keys

                    print()
                    print("FOREIGN KEYS")

                    foreign_keys = get_foreign_keys(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    if foreign_keys:
                        for (
                            column,
                            ref_schema,
                            ref_table,
                            ref_column,
                        ) in foreign_keys:

                            print(
                                f"  {column}"
                                f" -> "
                                f"{ref_schema}.{ref_table}"
                                f".{ref_column}"
                            )
                    else:
                        print("  NONE")

                    # Unique Constraints

                    print()
                    print("UNIQUE CONSTRAINTS")

                    unique_constraints = get_unique_constraints(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    if unique_constraints:
                        for constraint, column in unique_constraints:
                            print(
                                f"  {constraint}: {column}"
                            )
                    else:
                        print("  NONE")

                    # Indexes

                    print()
                    print("INDEXES")

                    indexes = get_indexes(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    if indexes:
                        for index_name, index_definition in indexes:
                            print(f"  {index_name}")
                            print(f"    {index_definition}")
                    else:
                        print("  NONE")

                # --------------------------------------------------
                # Area 1
                # --------------------------------------------------

                heading(
                    "AREA 1 - HCGO PLATFORM / SEMANTIC METADATA"
                )

                print(
                    "Target capabilities to evaluate:"
                )
                print("  - Domain identity")
                print("  - Knowledge asset identity")
                print("  - Semantic profile identity/version")
                print("  - Source / provenance")
                print("  - Ingestion state")
                print("  - Publication state")

                print()
                print("Candidate Existing Tables:")

                area1_found = False

                for schema_name, table_name in tables:
                    if classify_table(table_name).startswith("AREA 1"):
                        print(f"  - {schema_name}.{table_name}")
                        area1_found = True

                if not area1_found:
                    print("  NONE IDENTIFIED")

                # --------------------------------------------------
                # Area 2
                # --------------------------------------------------

                heading(
                    "AREA 2 - CANONICAL DOMAIN KNOWLEDGE"
                )

                print("Current production domain: BTA")
                print()
                print("Target semantic hierarchy:")
                print()
                print("  Translation")
                print("      -> Book")
                print("          -> Chapter")
                print("              -> Verse")
                print("                  -> Scripture Text")

                print()
                print("Candidate Existing Tables:")

                area2_found = False

                for schema_name, table_name in tables:
                    if classify_table(table_name).startswith("AREA 2"):
                        print(f"  - {schema_name}.{table_name}")
                        area2_found = True

                if not area2_found:
                    print("  NONE IDENTIFIED")

                # --------------------------------------------------
                # Area 3
                # --------------------------------------------------

                heading(
                    "AREA 3 - RUNTIME ACCESS / PUBLICATION BOUNDARY"
                )

                print(
                    "Architectural requirement:"
                )
                print()
                print(
                    "QueryService must consume governed,"
                )
                print(
                    "published canonical knowledge only."
                )

                print()
                print(
                    "The audit should determine whether the schema"
                )
                print(
                    "contains a reliable mechanism to distinguish:"
                )
                print()
                print("  - Processing knowledge")
                print("  - Validated knowledge")
                print("  - Published knowledge")
                print("  - Runtime-consumable knowledge")

                # Views may represent runtime publication surfaces.

                views = get_views(cursor)

                print()
                print("DATABASE VIEWS")

                if views:
                    for schema_name, view_name in views:
                        print(f"  - {schema_name}.{view_name}")
                else:
                    print("  NONE")

                # --------------------------------------------------
                # Relationship Summary
                # --------------------------------------------------

                heading("FOREIGN KEY RELATIONSHIP MAP")

                relationship_found = False

                for schema_name, table_name in tables:

                    foreign_keys = get_foreign_keys(
                        cursor,
                        schema_name,
                        table_name,
                    )

                    for (
                        column,
                        ref_schema,
                        ref_table,
                        ref_column,
                    ) in foreign_keys:

                        relationship_found = True

                        print(
                            f"{schema_name}.{table_name}.{column}"
                            f" -> "
                            f"{ref_schema}.{ref_table}.{ref_column}"
                        )

                if not relationship_found:
                    print("No foreign-key relationships found.")

                # --------------------------------------------------
                # Final
                # --------------------------------------------------

                heading("AUDIT COMPLETE")

                print("Database modifications performed : NONE")
                print()
                print(
                    "Next Step:"
                )
                print(
                    "Review this inventory against the HCGO"
                )
                print(
                    "Platform / Semantic Metadata,"
                )
                print(
                    "Canonical Domain Knowledge, and"
                )
                print(
                    "Runtime Publication Boundary requirements."
                )

    except psycopg.Error as exc:

        heading("DATABASE CONNECTION ERROR")

        print(exc)

        raise SystemExit(1)


if __name__ == "__main__":
    main()
    