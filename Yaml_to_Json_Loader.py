import yaml
import json
import sys
from pymongo import MongoClient

client= MongoClient("mongodb+srv://linduan:19970616@cluster0.jxdfk.mongodb.net/dairy_user_info?retryWrites=true&w=majority")
database=client.dairy_user_info
collection=database.Product

id_generator=10002007001
for i in range(1,len(sys.argv)):
    data=yaml.load(open(sys.argv[i]))
    data['_id']=id_generator
    collection.insert(data)
    id_generator=id_generator+1

    


