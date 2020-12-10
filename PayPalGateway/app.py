from flask import Flask, render_template,jsonify,Request,url_for
import stripe
import paypalrestsdk
from paypalrestsdk import Payment
# from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
# # from paypalcheckoutsdk.orders import OrdersCreateRequest
# from paypalhttp import HttpError

app = Flask(__name__)

app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51HvSsqEE1Lypx909t5DgIxvtS7J4GFix4WgXXfIfV3V5XMbqEnHTEqWBOG0Lbn1aTwfz5WBX2lX4tf8oA8V31Bzd00j01v23Ct'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51HvSsqEE1Lypx909A6v1BcQPuKrApRqNuc4Ux4MUhkRbUb6iuj798iOcsSbXwLt5ZAFd5uAuzYzMvl7aUpa8dZ9A00BZNcuImT'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
  "client_id": "AVk1QhaiIHTy_geDe5hanyCMZpZRdYuHeqGrbXKXfCJMzcghCCRgBSRhX3KiMsYcLAqlBieifx8bY2Bq",
  "client_secret": "ENMvhCfRDStot4J1ybcXD_JJEMmtfkjvcGtUspXmdP9WFYZJnGeZ2JMHg6LXItZyZU--8YzyQrNZ7h2D"
})

# client_id = "AVk1QhaiIHTy_geDe5hanyCMZpZRdYuHeqGrbXKXfCJMzcghCCRgBSRhX3KiMsYcLAqlBieifx8bY2Bq"
# client_secret = "ENMvhCfRDStot4J1ybcXD_JJEMmtfkjvcGtUspXmdP9WFYZJnGeZ2JMHg6LXItZyZU--8YzyQrNZ7h2D"
# # Creating an environment
# environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
# client = PayPalHttpClient(environment)

# @app.route('/')
# def index():
#     session = stripe.checkout.Session.create(
#         payment_method_types=['card'],
#         line_items=[{
#             'price': 'price_1HvSyLEE1Lypx909bJheMyuF',
#             'quantity': 1,
#         }],
#         mode='payment',
#         success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
#         cancel_url=url_for('index', _external=True),
#     )
    
#     return render_template(
#         'index.html', 
#         checkout_session_id=session['id'], 
#         checkout_public_key=app.config['STRIPE_PUBLIC_KEY']
#     )

# @app.route('/thanks')
# def thanks():
#     return render_template('thanks.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment',methods=['POST'])
def payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "t",
                    "sku": "89889",
                    "price": "8990",
                    "currency": "USD",
                    "quantity": 1}]},
            "amount": {
                "total": "59000.00",
                "currency": "USD"},
            "description": "This is the payment transaction description."}]})

    if payment.create():
        # Extract redirect url
        for link in payment.links:
            if link.method == "REDIRECT":
                # Capture redirect url
                redirect_url = (link.href)
        print('payment success')
    else:
        print("Error while creating payment:")
        print(payment.error)

    return jsonify({'paymentID':payment.id})

# @app.route('/payment',methods=['POST'])
# def payment():
#     request = OrdersCreateRequest()

#     request.prefer('return=representation')

#     request.request_body (
#         {
#             "intent": "CAPTURE",
#             "purchase_units": [
#                 {
#                     "amount": {
#                         "currency_code": "USD",
#                         "value": "100.00"
#                     }
#                 }
#             ]
#         }
#     )
#     try:
#     # Call API with your client and get a response for your call
#         response = client.execute(request)
#         print ('Order With Complete Payload:')
#         print ('Status Code:', response.status_code)
#         print ('Status:', response.result.status)
#         print ('Order ID:', response.result.id)
#         print ('Intent:', response.result.intent)
#         print ('Links:')
#         for link in response.result.links:
#             print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
#             print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
#             response.result.purchase_units[0].amount.value))
#             # If call returns body in response, you can get the deserialized version from the result attribute of the response
#             order = response.result
#             print(order)
#     except IOError as ioe:
#         print(ioe)
#         if isinstance(ioe, HttpError):
#             # Something went wrong server-side
#             print(ioe.status_code)

@app.route('/execute', methods=['POST'])
def execute():
    success = False
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute success!')
        success = True
    else:
        print(payment.error)

    return jsonify({'success' : success})

if __name__ == '__main__':
    app.run(
            host='127.0.0.1',
            port=8085,
            debug=True
        )
