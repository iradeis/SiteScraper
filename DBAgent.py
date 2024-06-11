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
    def ReadProductInfo(self, ASIN):
        return self.productInfoCollection.find_one({'ASIN': ASIN})


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

json = {"url": "https://www.amazon.com/New-Balance-Running-Aluminum-Metallic/dp/B09H3N5J27/",
        "ASIN": "B09H3P7CWQ",
        "product_name": "New Balance Men's Fresh Foam Arishi V4 Running Shoe", 
        "brand_name": "New Balance", "price": 69.99, "discount": 0, 
        "rating_avg": 4.4, "total_reviews": 4088, "rating_stars": [6, 3, 7, 15, 69], 
        "deal": True, "free_delivery": False, "free_return": False, "amazon_choice": False, 
        "date_first_available": "October 22, 2021", "rank_number": "1525", "description": 
        "Product details    \nCare instructions \n  \nMachine Wash \n    \nOrigin \n  \nImported \n    \nSole material \n  \nRubber \n    \nOuter material \n  \nRubber,Mesh,Suede \n    About this item   Fresh Foam midsole cushioning is precision engineered to deliver an ultra-cushioned, lightweight ride   Mesh upper with suede and knit hits   Upper features no-sew overlays for a sleek fit and feel   Textured logo and embroidered details   Durable rubber outsole   See more About this item" }

myAgent.WriteProductInfo(json)