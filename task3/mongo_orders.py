
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create database
db = client["order_database"]

# Create collection
orders = db["order_events"]

# Clear previous records for testing
orders.delete_many({})

# Insert 5 order events
events = [
    {"customer_id": 1, "order_id": 101, "amount": 500},
    {"customer_id": 1, "order_id": 102, "amount": 300},
    {"customer_id": 2, "order_id": 103, "amount": 700},
    {"customer_id": 1, "order_id": 104, "amount": 500},
    {"customer_id": 2, "order_id": 105, "amount": 400}
]

orders.insert_many(events)

print("5 order events inserted successfully!")

# MongoDB aggregation
pipeline = [
    {
        "$group": {
            "_id": "$customer_id",
            "total_amount": {"$sum": "$amount"}
        }
    },
    {
        "$sort": {"_id": 1}
    }
]

results = orders.aggregate(pipeline)

print("\nMongoDB Order Totals:")

for item in results:
    print(
        f"Customer {item['_id']} -> "
        f"{item['total_amount']}"
    )

client.close()