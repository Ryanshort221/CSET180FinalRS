from flask import Flask, render_template, request, session, redirect
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


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = encryptor(request.form['password'])
        user_type = request.form['user_type']
        result = conn.execute(text('select * from users where username=:username').params(username=username))
        if result.rowcount == 1:
            return render_template('register.html', message='Username already in use')
        result = conn.execute(text('select * from users where email=:email').params(email=email))
        if result.rowcount == 1:
            return render_template('register.html', message='Email already in use')
        conn.execute(text('insert into users (username, first_name, last_name, email, password, user_type) values(:username, :first_name, :last_name, :email, :password, :user_type)').params(username=username, first_name=first_name, last_name=last_name, email=email, password=password, user_type=user_type))
        conn.commit()
        return redirect('/')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = encryptor(request.form['password'])
        result = conn.execute(text('select * from users where username=:username and password=:password').params(username=username, password=password))
        if result.rowcount == 1:
            session['username'] = username
            return redirect('products')
        else:
            return render_template('index.html', message='incorrect login credentials try again')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop['username', None]
    return render_template('index.html')


@app.route('/products', methods=['POST', 'GET'])
def products():
    return render_template('products.html')


if __name__ == '__main__':
    app.run(debug=True)
