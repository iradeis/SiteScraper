from flask import Flask, jsonify, request
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://richard:nuclear97@59.120.52.19:27017/?authMechanism=DEFAULT")
db = client["AmazonProductResearch"] 
collection = db["ProductInfo"] 
collection2 = db["ProductRawHTML"]

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    # Return a welcome message or some information about your API
    return jsonify({"message": "Welcome to my Flask API!"})

# Route to get all documents in the collection
@app.route("/api/v1/documents", methods=["GET"])
def get_all_documents():
    documents = list(collection.find())
    return jsonify(documents)

# Route to get a specific document by ASIN
@app.route("/api/v1/documents/<search_term>", methods=["GET"])
def get_document(search_term):
    document = collection.find_one({"ASIN": search_term})
    if document:
        return jsonify(document)
    else:
        return jsonify({"error": "Document not found"}), 404

# Route to create a new document (adjust request body structure as needed)
@app.route("/api/v1/documents", methods=["POST"])
def create_document(dict):
    if dict:
        collection2.insert_one(dict)
        return jsonify({"message": "Raw HTML inserted successfully"}), 201
    else:
        return jsonify({"error": "Missing data in request body"}), 400


if __name__ == "__main__":
    app.run(debug=True)