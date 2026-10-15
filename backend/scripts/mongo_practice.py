from app.config import settings
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING

"""
Simple python script to test out basic mongoDB operations using pymongo
"""

def test_operations():
    URI = settings.mongodb_uri
    client = MongoClient(URI)
    events = client["practice"]["equipment_events"] # db and collection are created on first insert

    # Create
    events.insert_one({
        "equipment_id": 2,
        "type": "status_change",
        "message": "Moved to maintenance: battery below threshold",
        "timestamp": datetime.now(timezone.utc),
    })

    events.insert_many([
        {"equipment_id": 2, "type": "checkout", "message": "Checked out by ER",
            "timestamp": datetime.now(timezone.utc)},
        {"equipment_id": 4, "type": "status_change", "message": "Back in service",
            "timestamp": datetime.now(timezone.utc)},
    ])

    # Read
    for doc in events.find({"equipment_id": 2}).sort("timestamp", DESCENDING).limit(10):
        print(doc)

    # Update
    events.update_one({"equipment_id": 4}, {"$set": {"message": "returned to service"}})

    # Aggregate: count events per equipment
    for row in events.aggregate([
        {"$group": {"_id": "$equipment_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]):
        print(row)

    # index
    events.create_index([("equipment_id", 1), ("timestamp", -1)])

    # delete
    events.delete_many({"type": "checkout"})

if __name__ == "__main__":
    test_operations()

