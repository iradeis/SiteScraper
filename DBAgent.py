# mongoDB agent
# two methods: write, read
import pymongo
from pymongo import MongoClient

class DBAgent:

    def __init__(self, connectionString: str):
        
        #format of connectionstring mongodb://localhost:27017
        self.mongoClient = MongoClient(connectionString)
        self.db = self.mongoClient["AmazonProductResearch"]
        self.productRawCollection = self.db["ProductRawHTML"]
        self.productInfoCollection = self.db["ProductInfo"]
        self.productReviewCollection = self.db["ProductReview"]

    # method writes search term, raw html and asin to database
    # input raw and asin
    # output to database
    def WriteRaw(self, raw):
        inserted = self.productRawCollection.insert_one(raw)
    
    # method write product detail
    # input as dict
    # output into database
    # uses asin as id
    def WriteProductInfo(self, json):
        insert = self.productInfoCollection.insert_one(json)

    def ReadProductInfoByPrice(self, maxPrice: float, minPrice: float):
        filter = { 
                    'price': { '$gte': minPrice, '$lte': maxPrice } }
        cursor = self.productInfoCollection.find(filter)

        return list(cursor)
    
    # method read
    # input as keyword (maybe product name)
    # output dict
    def ReadProductRaw(self, ASIN):
        return self.productRawCollection.find_one({'asin': ASIN})
    
    # method read
    # input as keyword (maybe product name)
    # output dict
    def ReadProductInfo(self, ASIN):
        return self.productInfoCollection.find_one({'ASIN': ASIN})

    def APICreation(self):



        
        return

    # method write product review 
    # input as dict
    # output into database

    # - product details
    # - product reviews
    #   - review id
    #       - product id
    #       - rating
    #       - text
    #   - review 2

myAgent = DBAgent("mongodb://localhost:27017")