from flask import Flask
from sqlalchemy import create_engine
from login.loginRegistration import loginRegistration
from products.product import product
from cart.cart import cart_blueprint
from checkout.checkoutPayment import checkout_blueprint
from allOrders.orders import orders_blueprint
from reviews.review import review_blueprint
from complaint.complaints import complaints_blueprint
from chats.chat import chat_blueprint

app = Flask(__name__)
app.secret_key = 'apple'
app.register_blueprint(loginRegistration)
app.register_blueprint(product)
app.register_blueprint(cart_blueprint)
app.register_blueprint(checkout_blueprint)
app.register_blueprint(orders_blueprint)
app.register_blueprint(review_blueprint)
app.register_blueprint(complaints_blueprint)
app.register_blueprint(chat_blueprint)
conn_str = 'mysql://root:1012@localhost/cset180final'
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


if __name__ == '__main__':
    app.run(debug=True)
