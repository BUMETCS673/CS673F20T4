from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_session import Session
import pymongo
import hashlib
import yaml
import re

from redis import Redis

register_api = Blueprint('register_api', __name__)

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]



@register_api.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")


@register_api.route('/register-result', methods=['POST'])
def register():
    web_email = request.form.get("email")
    web_name = request.form.get("name")
    web_age = request.form.get("age")
    web_username = request.form.get("username")
    web_password = request.form.get("password")
    web_gender = request.form.get("gender")

    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    warning_empty = "The username or Email cannot be empty!"
    warning_emailFormatInvalid = "The Email format is invalid! Please check and retry."

    def password_encrypt(password):
        _password = hashlib.md5(password.encode('utf8')).hexdigest()
        return _password

    # Function to validate the username and email
    def nullfield_check(email: str, username: str):
        if email.split() == "" or username.split() == "":
            return False

        return True

    def unique_email_check(email):
        if db_collection_User.find_one({"email": email}):
            return False
        return True

    # Function to validate the email format
    def email_format_check(email: str):
        if re.search(email_regex, email):
            return True
        else:
            return False

    # Function to validate the password
    def password_check(passwd):
        special_sym = ['$', '@', '#', '%']
        message = ""

        if not (8 <= len(passwd) <= 20):
            message = "Password should have length between 8~20"

        if not any(char.isdigit() for char in passwd):
            message = 'Password should have at least one numeral'

        if not any(char.isupper() for char in passwd):
            message = 'Password should have at least one uppercase letter'

        if not any(char.islower() for char in passwd):
            message = 'Password should have at least one lowercase letter'

        if not any(char in special_sym for char in passwd):
            message = 'Password should have at least one of the symbols $@#'

        return message

    msg = password_check(web_password)

    # insert one user into DB if passed all checks
    if nullfield_check(web_email, web_username) and email_format_check(web_email) \
            and msg == "" and unique_email_check(web_email):
        user = {"email": web_email,
                "name": web_name,
                "age": web_age,
                "username": web_username,
                "password": password_encrypt(web_password),
                "gender": web_gender}
        _id = db_collection_User.insert_one(user)
        flash("You have successfully created your account. Congrats!")
        return redirect(url_for("default"))

    error_ = ""

    if not nullfield_check(web_email, web_username):
        error_ = warning_empty

    if not email_format_check(web_email):
        error_ = warning_emailFormatInvalid

    if msg != "":
        error_ = msg

    return render_template("register.html", error=error_)
