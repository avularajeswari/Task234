from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")

except Exception as e:
    print("Connection failed:", e)