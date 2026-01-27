#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Read schema.sql
with open('schema.sql', 'r') as f:
    schema_sql = f.read()

print("Setting up database schema...")

try:
    with engine.connect() as connection:
        # Execute schema in parts (split by semicolon)
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            try:
                connection.execute(text(statement))
                print(f"✓ Executed statement {i+1}/{len(statements)}")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"- Statement {i+1} skipped (already exists)")
                else:
                    print(f"✗ Statement {i+1} failed: {e}")
        
        connection.commit()
        print("✓ Database schema setup complete!")
        
except Exception as e:
    print(f"✗ Schema setup failed: {e}")