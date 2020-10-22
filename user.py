from flask_login import UserMixin
from bson.objectid import ObjectId
import logging

from db import get_db
import json

class User(UserMixin):
    def __init__(self, gid, name, email, profile_pic):
        self.id = gid
        self.gid = gid
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(gid):
        db = get_db()
        user = db.users.find_one({"gid": gid})

        if not user:
            return None
        
        print(user)
        user = User(
            gid=user['gid'], name=user['name'], email=user['email'], profile_pic=user['profile_pic']
        )
        return user

    @staticmethod
    def create(gid,name, email, profile_pic):
        db = get_db()
        
        res=db.users.insert_one({
            "gid":gid,
            "name":name,
            "email":email,
            "profile_pic":profile_pic
        })
        print('One post: {0}'.format(res.inserted_id))
        