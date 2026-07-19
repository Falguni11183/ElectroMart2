from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017/")
db = client["electromart"]
customers = db["customers"]
print("MongoDB Connected Successfully!")