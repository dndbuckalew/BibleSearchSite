import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(".env.local")

mongo_uri = os.getenv("MONGODB_URI")
db_name = os.getenv("MONGODB_DB_NAME")

print(f"Database Target: {db_name}")

client = MongoClient(mongo_uri)

try:
    client.admin.command("ping")
    print("MongoDB connection successful.")
except Exception as e:
    print("MongoDB connection failed.")
    print(e)
    