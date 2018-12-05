
"""
This file refines some string data into int/float values.
Upwork represents money-related values in the form of $100k+.
This kind of values are converted into native variable types.
"""

from pymongo import MongoClient


def parse_job_rate(x):
    return int(x[:-1])


def parse_hour_rate(x):
    if x == "":
        return 0
    return float(x[1:])


def parse_total_earned(x):
    if x == "":
        return 0
    return int(x[1:-2])


def parse_skill(x):
    if x == "":
        return x
    return x.split(",")[:-1]


client = MongoClient()
db = client.get_database("upwork")
collection = db.freelancers

set_values = {}

cursor = collection.find({}, {"JobRate": 1, "HourRate": 1, "TotalEarned": 1, "Skills": 1})
for doc in cursor:
    doc_id = doc["_id"]

    set_values["JobRate"] = parse_job_rate(doc["JobRate"])
    set_values["HourRate"] = parse_hour_rate(doc["HourRate"])
    set_values["TotalEarned"] = parse_total_earned(doc["TotalEarned"])
    set_values["Skills"] = parse_skill(doc["Skills"])

    collection.update({"_id": doc_id}, {"$set": set_values})
    print("Processed: ", doc_id)
