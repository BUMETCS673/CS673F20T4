import collections

from flask import Blueprint, render_template, request
from flask_bcrypt import Bcrypt

import pymongo

import yaml
import jwt

product_api = Blueprint('product_api', __name__)

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.safe_load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]
db_collection_product=db['Product']


@product_api.route('/products.html', methods=['GET'])
def product():
    # click product, query db and show all items
    Product_Dictionary = collections.defaultdict(dict)
    for each_product in db_collection_product.find({}):
        _id = str(each_product['_id'])
        Product_Dictionary[_id] = each_product
    return render_template("products.html", product_dict = Product_Dictionary)