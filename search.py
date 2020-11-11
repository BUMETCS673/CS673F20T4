from flask import Blueprint, render_template, request
from flask_bcrypt import Bcrypt

import pymongo

import yaml
import jwt

search_api = Blueprint('search_api', __name__)
bcrypt = Bcrypt()
f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]
db_collection_product=db['Product']

def getItemList():
    itemDict = {}
    for item in db_collection_product.find({}):
        itemDict[str(item['_id'])] = item
    return itemDict

@search_api.route('/search-result', methods=['POST'])
def searchProducts():
    keyword = request.form.get('keyword').strip()
    itemDict = getItemList()
    resDict = itemDict.copy()

    if not keyword:
        return render_template("search_product.html", search_dict = resDict)

    import re
    for _id, info in itemDict.items():
        if not re.findall(r'\b' + keyword.lower() + r'\b', info['Product Name'].lower()):
            del resDict[_id]
    return render_template("search_product.html", search_dict = resDict)