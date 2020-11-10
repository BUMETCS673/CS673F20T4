from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_session import Session
import pymongo
import hashlib
import yaml
import re

from redis import Redis

register_api = Blueprint('register_api', __name__)
bcrypt = Bcrypt()
f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]


@register_api.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")


@register_api.route('/register.html', methods=['GET'])
def register_page1():
    return render_template("register.html")


@register_api.route('/register-result', methods=['POST'])
def register():
    web_email = request.form.get("email")
    web_firstname = request.form.get("firstname")
    web_lastname = request.form.get("lastname")
    web_password1 = request.form.get("password2")
    web_password2 = request.form.get("password3")

    email_regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    warning_empty = "The username or Email cannot be empty!"
    warning_email_format_invalid = "The Email format is invalid! Please check and retry."

    def password_encrypt(password):
        _password = bcrypt.generate_password_hash(password).decode("utf-8")
        return _password

    def password_confirm_check(passwd: str, cfm_passwd: str):
        return passwd == cfm_passwd

    # Function to validate the username and email
    def null_check(email: str, field: str):
        if email.split() == "" or field.split() == "":
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
        # special_sym = ['$', '@', '#', '%']
        message = ""

        if not (8 <= len(passwd) <= 20):
            message = "Password should have length between 8~20"

        if not any(char.isdigit() for char in passwd):
            message = 'Password should have at least one numeral'

        if not any(char.isupper() for char in passwd):
            message = 'Password should have at least one uppercase letter'

        if not any(char.islower() for char in passwd):
            message = 'Password should have at least one lowercase letter'
        #
        # if not any(char in special_sym for char in passwd):
        #     message = 'Password should have at least one of the symbols $@#'

        return message

    msg = password_check(web_password1)

    # insert one user into DB if passed all checks
    if null_check(web_email, web_firstname) and \
            null_check(web_email, web_lastname) and \
            password_confirm_check(web_password1, web_password2) and \
            email_format_check(web_email) and msg == "" and \
            unique_email_check(web_email):
        user = {"email": web_email,
                "fullname": web_firstname + " " + web_lastname,
                "firstname": web_firstname,
                "lastname": web_lastname,
                "password_hash": password_encrypt(web_password1),
                }
        _id = db_collection_User.insert_one(user)
        print("You have successfully created your account. Congrats!")
        return redirect(url_for("default"))

    error_ = ""

    if not null_check(web_email, web_firstname) or not null_check(web_email, web_lastname):
        error_ = warning_empty

    if not email_format_check(web_email):
        error_ = warning_email_format_invalid

    if not password_confirm_check(web_password1, web_password2):
        error_ = "Password and confirm password must be same. Please try again!"

    if not unique_email_check(web_email):
        error_ = "This Email account has been registered, please try another!"

    if msg != "":
        error_ = msg


    print(error_)

    return redirect("register.html")
