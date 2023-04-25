from flask import Flask, render_template, request, session, redirect, flash
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


# @app.before_request
# def before_request():
#     session.clear()


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
        user_type = request.form['user_type']
        result = conn.execute(text('select * from users where username=:username and password=:password and user_type=:user_type').params(username=username, password=password, user_type=user_type))
        if result.rowcount == 1 and user_type == 'customer':
            session['username'] = username
            flash(f"You successfully logged in as {username}")
            return redirect('products')
        elif result.rowcount == 1 and user_type == 'vendor':
            session['username'] = username
            flash(f"Vendor {username} successfully logged in")
            return redirect('vendor')
        elif result.rowcount == 1 and user_type == 'admin':
            session['username'] = username
            flash(f"Admin {username} successfully logged in")
            return render_template('admin.html', username=username)
        elif result.rowcount == 0:
            flash("Invalid login credentials please try again", 'error')
            return redirect('/')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    flash("Successfully logged out")
    return redirect('/')


@app.route('/products', methods=['POST', 'GET'])
def products():
    return render_template('products.html')


@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
    return render_template('vendor.html')


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    return render_template('admin.html')


@app.route('/user_profile')
def profile():
    username = session['username']
    result = conn.execute(text('select username, first_name, last_name, email, user_type from users where username=:username ').params(username=username))
    return render_template('user_profile.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
