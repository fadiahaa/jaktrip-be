#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path
from sqlalchemy import text

# Ensure backend package is in python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.connection import engine
from app.database.base import Base

# Import all models so SQLAlchemy metadata registers them
import app.models.user
import app.models.wisata
import app.models.planner
import app.models.itinerary
import app.models.itinerary_detail

def init_database():
    print(f"Connecting to database via engine ({engine.url.drivername})...")

    # 1. Auto-create all tables and enum types
    print("Creating all tables and types (Base.metadata.create_all)...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # 2. Look for jaktrip_planner.sql to seed initial data
    possible_sql_paths = [
        Path(__file__).resolve().parent.parent / "jaktrip_planner.sql",
        Path(__file__).resolve().parent / "jaktrip_planner.sql",
    ]

    sql_path = next((p for p in possible_sql_paths if p.exists()), None)
    if not sql_path:
        print("Notice: jaktrip_planner.sql not found for data seeding. Skipping seed.")
        return

    print(f"Reading seed data from {sql_path.name}...")
    content = sql_path.read_text(encoding="utf-8")

    # Extract all INSERT INTO statements
    insert_statements = re.findall(r"^INSERT INTO .*?;\s*$", content, flags=re.MULTILINE | re.DOTALL)

    if not insert_statements:
        print("No INSERT INTO statements found in SQL file.")
        return

    print(f"Found {len(insert_statements)} INSERT statements. Populating database...")
    with engine.begin() as conn:
        for stmt in insert_statements:
            # Replace backticks with PostgreSQL compatible double quotes for table/column names if postgresql
            clean_stmt = stmt
            if "postgresql" in engine.url.drivername:
                # Replace backticks with double quotes
                clean_stmt = clean_stmt.replace("`", '"')
                # Replace invalid '0000-00-00 00:00:00' timestamps with NULL or default
                clean_stmt = clean_stmt.replace("'0000-00-00 00:00:00'", "NULL")

            conn.execute(text(clean_stmt))


    # 3. Sync auto-increment sequences with seeded explicit IDs
    # (seeding rows with explicit id values does NOT advance Postgres SERIAL sequences)
    if "postgresql" in engine.url.drivername:
        print("Syncing auto-increment sequences...")
        with engine.begin() as conn:
            for table in Base.metadata.sorted_tables:
                for col in table.primary_key.columns:
                    seq = f"{table.name}_{col.name}_seq"
                    conn.execute(text(
                        f'SELECT setval(\'{seq}\', '
                        f'COALESCE((SELECT MAX("{col.name}") FROM "{table.name}"), 0) + 1, false)'
                    ))
                    print(f"  {seq} -> next id = COALESCE(MAX({col.name}),0)+1")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    init_database()
