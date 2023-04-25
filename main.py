from flask import Flask, render_template, request, session
from sqlalchemy import create_engine, text
import hashlib
from decimal import Decimal


app = Flask(__name__)
app.secret_key = 'apple'

def encryptor(password):
    salt = 'apple'
    encrypted_password = hashlib.sha224(password.encode('utf-8')).hexdigest() + salt
    return encrypted_password


conn_str = 'mysql://root:1012@localhost/cset180final'
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.before_request
def before_request():
    session.clear()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
