import collections
import os

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, Response, flash, \
    sessions
from login import login_api, getFirstName, getUserLoginEmail, setFirstName, setUserLoginEmail, getLastName
from register import register_api
import pymongo

import re
import jwt
import yaml
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message

import os
from datetime import timedelta
from functools import wraps
import datetime
import json
from bson import ObjectId, json_util
from flask_bcrypt import Bcrypt
from search import search_api

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.safe_load(data)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SECRET_KEY'] = os.urandom(24)
app.register_blueprint(login_api)
app.register_blueprint(register_api)
app.register_blueprint(search_api)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client['dairy_user_info']
db_collection_User = db['User']
db_collection_OAuthUser = db['OAUTH_USER_DETAILS']
db_collection_product = db['Product']
db_collection_cart_history = db[yaml_reader['collection_Cart_History']]
db_collection_address= db['Address']
db_collection_payment= db['PaymentInfo']
db_collection_order_history= db['Order_History']

# dotenv setup
from dotenv import load_dotenv

load_dotenv()

URL = 'http://127.0.0.1:5000/'
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="510040117441-bhjkhpcm8r1l1skiaj6auagd7g0titpf.apps.googleusercontent.com",
    client_secret="Vuw2wpmvi7teEqEGWrOXneF2",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    # userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

FB_CLIENT_ID = '130193744280198'
FB_CLIENT_SECRET = '54432f153c538026224ea90a07809b37'

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": yaml_reader['email_address'],
    "MAIL_PASSWORD": yaml_reader['email_password']
}
app.config.update(mail_settings)
mail = Mail(app)
bcrypt = Bcrypt()
app.add_template_global(getFirstName, 'getFirstName')
app.add_template_global(getLastName, 'getLastName')
app.add_template_global(getUserLoginEmail, 'getUserLoginEmail')

user = ""
token = ""
error_ = ""
cartNum = None
forget_email_addr = ""

@app.route('/', methods=['GET'])
def default():
    return render_template("index.html")


@app.route('/home', methods=['GET', 'POST'])
def home_page1():
    return render_template("index.html")


@app.route('/index.html', methods=['GET'])
def home_page2():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    google = oauth.create_client('google')
    redirect_url = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_url)


@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    global token
    if request.method == 'POST':
        fid = request.args.get('fid')  # Your form's
        name = request.args.get('name')
        user_info = {
            "fid": fid,
            "name": name
        }

    else:
        google = oauth.create_client('google')  # create the google oauth client
        token = google.authorize_access_token()  # Access token from google (needed to get user info)
        resp = google.get('userinfo', token=token)  # userinfo contains stuff u specificed in the scrope
        user_info = resp.json()

        if db_collection_OAuthUser.find_one({"email": user_info['email']}) is None:
            db_collection_OAuthUser.insert_one(user_info)
        setFirstName(user_info['given_name'])
        setUserLoginEmail(user_info['email'])

        token = jwt.encode({'public_id': user_info['email'],
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])

    session['profile'] = user_info
    session.permanent = True  # make the session permanent so it keeps existing after browser gets closed
    return redirect('/')


def add_JWT():
    return {"x-access-token": token}


def getToken():
    return token

def getCartNum():
    user_cart_info = db_collection_cart_history.find_one({"email":getUserLoginEmail()})['productInfo']
    count = 0
    if user_cart_info:
        for val in user_cart_info.values():
            count += int(val)
    print(count)
    return count

app.add_template_global(getToken, "getToken")
app.add_template_global(getCartNum, "getCartNum")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global token
        token = request.args.get("token")
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = user
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/login-result', methods=["POST"])
def login1():
    ajax_json = request.get_json()

    em, login_password = ajax_json["email"], ajax_json["password"]
    if not em or not login_password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    query = {"email": em}
    info = db_collection_User.find_one(query)
    if not info:
        return json.dumps('none')

    if bcrypt.check_password_hash(pw_hash= info['password_hash'],
                                      password=login_password):
        setUserLoginEmail(email=em)
        setFirstName(info['firstname'])
        global cartNum
        global user
        user = json.loads(json_util.dumps(list(db_collection_User.find(query))))
        tempOutput = []
        for curr in user:
            tempOutput.append(curr)
        global token
        token = jwt.encode(
            {'public_id': tempOutput[0]['password_hash'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'])

        r = {"token":token.decode('ascii')}
        return jsonify(r)

    return json.dumps('wrong')


@app.route('/register-result', methods=['POST'])
def register():
    '''
    register_info = {
        first_name:first_name,
        last_name:last_name,
        email_address:email_address,
        password_2:password_2,
        password_3:password_3
    };
    :return:
    '''
    ajax_json = request.get_json()
    web_email = ajax_json['email_address']
    web_firstname = ajax_json['first_name']
    web_lastname = ajax_json['last_name']
    web_password1 = ajax_json['password_2']
    web_password2 = ajax_json['password_3']

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

        message = ""

        if not (8 <= len(passwd) <= 20):
            message = "Password should have length between 8~20"

        if not any(char.isdigit() for char in passwd):
            message = 'Password should have at least one numeral'

        if not any(char.isupper() for char in passwd):
            message = 'Password should have at least one uppercase letter'

        if not any(char.islower() for char in passwd):
            message = 'Password should have at least one lowercase letter'

        return message

    msg = password_check(web_password1)
    pwd_hash = password_encrypt(web_password1)

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
                "password_hash": pwd_hash,
                }
        user_cart_history = {
            "email": web_email,
            "modifiedOn": datetime.datetime.now(),
            "productInfo": {
            }
        }
        _id = db_collection_User.insert_one(user)
        db_collection_cart_history.insert_one(user_cart_history)

        setFirstName(web_firstname)
        setUserLoginEmail(web_email)
        global token
        token = jwt.encode(
            {'public_id': pwd_hash,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'])
        print("You have successfully created your account. Congrats!")
        return json.dumps("OK")

    global error_

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

    return json.dumps(error_)


@app.route('/product2cart', methods=['POST'])
def product2cart():
    em = getUserLoginEmail()
    query = {"email": em}
    ajax_json = request.get_json()

    prod_info = db_collection_cart_history.find_one(query)['productInfo'] # info := {"10002007001" : qty}

    prod_id, prod_qty = str(ajax_json['id']), int(ajax_json['quantity'])
    if prod_id in prod_info:
        qty = prod_info[prod_id]
        prod_info[prod_id] = qty + prod_qty
        db_collection_cart_history.update_one(query, {"$set" : {"productInfo": prod_info}})
    else:
        prod_info[prod_id] = int(prod_qty)
        db_collection_cart_history.update_one(query, {"$set": {"productInfo": prod_info}})

    return json.dumps("")

@app.route('/cart', methods=['GET'])
def cart():
    # print(getUserLoginEmail())
    query_em = {"email":getUserLoginEmail()}
    user_cart_info = db_collection_cart_history.find_one(query_em)['productInfo']

    # send info back to html
    dict_id_qty_prc_nm_dsc_vol = {}
    subtotal = 0
    for prod_id, prod_qty in user_cart_info.items():
        prod_info = db_collection_product.find_one({"_id": int(prod_id)})
        subtotal += float(prod_info["Product Price"][1:]) * prod_qty
        if prod_info:
            dict_id_qty_prc_nm_dsc_vol[prod_id] = {
                "qty": prod_qty,
                "totalPrice": "$" + str(round(float(prod_info["Product Price"][1:]) * prod_qty, 2)),
                "unitPrice": float(prod_info["Product Price"][1:]),
                "productName": prod_info["Product Name"],
                "description": prod_info["Description"],
                "weight": prod_info["Weight"]
            }
    if subtotal >=35:
        total = subtotal
    else:
        total = subtotal+7
    global cartNum
    cartNum = sum(user_cart_info.values()) if user_cart_info else 0
    return render_template("cart.html", dict_id_qty_prc_nm_dsc_vol = dict_id_qty_prc_nm_dsc_vol, subtotal = round(subtotal,2), d_left=round(35-subtotal,2),total=round(total,2))

@app.route("/cartremove", methods=["POST"])
def cartRemove():
    ajax_json = request.get_json()
    pid = ajax_json['pid']
    query_em = {"email":getUserLoginEmail()}
    user_cart_info = db_collection_cart_history.find_one(query_em)['productInfo']
    user_cart_info.pop(pid)
    db_collection_cart_history.update_one(query_em, {"$set" : {"productInfo": user_cart_info}})
    return json.dumps("True")


@app.route("/cartchange", methods=["POST"])
def cartChange():
    ajax_json = request.get_json()
    change_type, pid = ajax_json['change_type'], ajax_json['pid']
    query_em = {"email": getUserLoginEmail()}
    prod_info = db_collection_cart_history.find_one(query_em)['productInfo']
    if change_type == '+':
        prod_info[pid] += 1
        db_collection_cart_history.update_one(query_em, {"$set": {"productInfo": prod_info}})
    else:
        prod_info[pid] -= 1
        if prod_info[pid] == 0:
            prod_info.pop(pid)
        db_collection_cart_history.update_one(query_em, {"$set": {"productInfo": prod_info}})

    return json.dumps("True")



@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


@app.route('/forget-password', methods=['POST'])
def email():
    ajax_json = request.get_json()
    global forget_email_addr
    forget_email_addr = ajax_json['email_address']
    msg = Message("Reset Your MooDairy Password",
                  sender="lincelot97@gmail.com",
                  recipients=[forget_email_addr])
    fname = getFirstName()
    msg.body = "Hello " + fname + "!\n" \
                                  "Thanks for using MooDairy. \n" \
                                  "Maintaining your security is our top priority. \n" \
                                  "Please click the link below to finish resetting your password.\n" \
                                  "http://localhost:5000/forget_password.html"
    mail.send(msg)
    return json.dumps("Sent")

@app.route('/forget-reset', methods=["POST"])
def forgetAndReset():
    user_email = forget_email_addr
    query = {"email": user_email}
    ajax_json = request.get_json()
    pwd1 = ajax_json['password1']
    pwd2 = ajax_json['password2']
    update_query = { "$set" : { "password_hash" : bcrypt.generate_password_hash(password=pwd1).decode("utf-8") }}
    db_collection_User.update_one(user_email, update_query)
    return json.dumps("True")


@app.route('/profile-account', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        ajax_json = request.get_json()
        data = ajax_json["data"]

        if data:
            return json.dumps("True")
        else:
            return json.dumps('False')

    if request.method == 'GET':
        if getToken():
            query = {"email": getUserLoginEmail()}
            result_address = []
            result_payment = []
            for each_product in db_collection_address.find(query):
                result_address.append(each_product)
            for each_product in db_collection_payment.find(query):
                result_payment.append(each_product)
            return render_template("profile.html",address=result_address,payment=result_payment)
        else:
            return render_template("notfound.html")

# @app.route('/update-address', methods=['POST'])
# def updateaddress():
#     ajax_json = request.get_json()
#     key, default_address = ajax_json["key"],ajax_json["address"]
#     ######  ###
#     return json.dumps('True')


@app.route('/updateaddress', methods=['POST'])
def updateaddress():
    ajax_json = request.get_json()
    to_be_updated_key, to_be_made_default_address = ajax_json["key"],ajax_json["address"]
    query = {"email":getUserLoginEmail()}
    person=db_collection_address.find(query)
    def_address=""
    for each in person:
        def_address=each['Defaultaddress']
    print(def_address,to_be_made_default_address,to_be_updated_key)
    db_collection_address.update_one(query, {"$set": {"Defaultaddress": to_be_made_default_address,"Address_list."+to_be_updated_key:def_address}})
    return json.dumps("True")

@app.route('/updatepayment', methods=['POST'])
def updatepayment():
    ajax_json = request.get_json()
    to_be_updated_key, to_be_made_default_payment = ajax_json["key"],ajax_json["payment"]
    query = {"email":getUserLoginEmail()}
    person=db_collection_payment.find(query)
    def_card=""
    def_card_type=""
    to_be_changed_card_type=""
    for each in person:
        def_card=each['default_card_no']
        def_card_type=each['default_card_type']
        to_be_changed_card_type=each['card_list'][to_be_updated_key]['card_type']
    temp_list=to_be_made_default_payment.split(" ")
    to_be_updated=""
    for i in range(len(temp_list)):
        if i!=0 and i!=len(temp_list)-1:
            to_be_updated=to_be_updated+temp_list[i]
            to_be_updated=to_be_updated+" "
        if i==len(temp_list)-1:
            to_be_updated=to_be_updated+temp_list[i]
    db_collection_payment.update_one(query, {"$set": {"default_card_no": to_be_updated,"card_list."+to_be_updated_key+".card_type":def_card_type,"card_list."+to_be_updated_key+".card_no":def_card,"default_card_type":to_be_changed_card_type}})
    return json.dumps("True")


@app.route('/profile-order', methods=['GET', 'POST'])
def order_history():
    if request.method == 'POST':
        ajax_json = request.get_json()
        data = ajax_json["data"]

        if data:
            return json.dumps("True")
        else:
            return json.dumps('False')

    if request.method == 'GET':
        if getToken():
            query = {"email": getUserLoginEmail()}
            result = []
            for each_product in db_collection_order_history.find(query):
                result.append(each_product)
            print(result)
            return render_template("order_history.html", order=result)
        else:
            return render_template("notfound.html")

@app.route('/order-detail', methods=['GET', 'POST'])
def vieworder():
    if request.method == 'POST':
        ajax_json = request.get_json()
        order_id = ajax_json["order_id"]

        if data:
            return json.dumps("True")
        else:
            return json.dumps('False')

    if request.method == 'GET':
        if getToken():
            query = {"email": getUserLoginEmail()}
            result = []
            for each_product in db_collection_order_history.find(query):
                result.append(each_product)
            print(result[0])
            return render_template("order_detail.html",order=result)
        else:
            return render_template("notfound.html")

@app.route('/profile/', methods=['GET', 'POST'])
def funcProfile():
    if request.method == "POST":
        hash_decode = jwt.decode(getToken(),
                                 app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['public_id']
        query = {"password_hash": hash_decode}
        ajax_json = request.get_json()
        if "currentpassword" in ajax_json:
            current_password = ajax_json['currentpassword']
            pwd1 = ajax_json['password1']
            pwd2 = ajax_json['password2']

            if bcrypt.check_password_hash(pw_hash= hash_decode,
                                          password=current_password):
                # verify current user pwd
                # update user new pwd
                update_query = { "$set" : { "password_hash" : bcrypt.generate_password_hash(password=pwd1).decode("utf-8") }}
                db_collection_User.update_one(query, update_query)
                return json.dumps('True')
            else:
                return json.dumps('False')

        if "type_name" in ajax_json:
            _type, _name = 0, 1
            new_type_name = ajax_json['type_name']
            if new_type_name[_type] == "First Name":
                update_query = { "$set" : { "firstname" : new_type_name[_name],
                                            "fullname": new_type_name[_name]+
                                                        " "+
                                                        db_collection_User.find_one(query)['lastname'] }}
                db_collection_User.update_one(query, update_query)
                setFirstName(new_type_name[_name])
            else:
                update_query = {"$set": {"lastname": new_type_name[_name],
                                         "fullname": db_collection_User.find_one(query)['lastname']+
                                                     " " +
                                                     new_type_name[_name]
                                         }}
                db_collection_User.update_one(query, update_query)
            return json.dumps("True")

        return json.dumps('True')

@app.route("/log-out", methods=["POST"])
def logout():
    global token
    token = ""
    return json.dumps('True')


@app.route('/products.html', methods=['GET'])
def product():
    category = request.args.get("category")
    cate_dict = {"milk":1, "yogurt":2, "butter":3,"cream":4, "cheese":5}
    if category=="all":
        query = {}
    else:
        query = {"Category":cate_dict[category]}
    Product_Dictionary = collections.defaultdict(dict)
    for each_product in db_collection_product.find(query):
        _id = str(each_product['_id'])
        Product_Dictionary[_id] = each_product
    return render_template("products.html", product_dict=Product_Dictionary)

@app.route('/orderhistory', methods=['GET'])
def orderhistory():
    query = {"email":getUserLoginEmail()}
    result=[]
    for each_product in db_collection_order_history.find(query):
        result.append(each_product)
    return render_template("order_history.html", order=result)



@app.route('/forget_password', methods=['GET'])
def forget_password():
    return render_template("forget_password.html")


@app.route('/service', methods=['GET'])
def service():
    return render_template("service.html")

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
