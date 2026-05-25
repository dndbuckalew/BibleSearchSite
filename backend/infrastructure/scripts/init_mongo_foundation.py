# File: backend/infrastructure/scripts/init_mongo_foundation.py
# Purpose: Initialize governed MongoDB foundation collections for BTA Version 4.
# Run from project root when instructed:
# python backend/infrastructure/scripts/init_mongo_foundation.py

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(".env.local")

mongo_uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB_NAME")

REQUIRED_COLLECTIONS = [
    "translation_registry",
    "license_registry",
    "source_registry",
    "language_registry",
    "book_registry",
    "scripture_passages",
    "validation_hold",
]

if not mongo_uri:
    raise RuntimeError("MONGODB_URI is missing from .env.local")

if not db_name:
    raise RuntimeError("MONGODB_DB_NAME is missing from .env.local")

client = MongoClient(mongo_uri)
db = client[db_name]

print(f"Mongo Foundation Target Database: {db_name}")

existing_collections = set(db.list_collection_names())

for collection_name in REQUIRED_COLLECTIONS:
    if collection_name not in existing_collections:
        db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection already exists: {collection_name}")

print("Mongo foundation initialization check complete.")
