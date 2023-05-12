from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
import hashlib
# app = Flask(__name__)
# app.secret_key = 'apple'
loginRegistration = Blueprint('loginRegistration', __name__, template_folder='templates')


def encryptor(password):
    salt = 'apple'
    encrypted_password = hashlib.sha224(password.encode('utf-8')).hexdigest() + salt
    return encrypted_password


@loginRegistration.route('/')
def index():
    categories = conn.execute(text('select distinct category from products'))
    return render_template('index.html', categories=categories)


@loginRegistration.route('/register', methods=['POST', 'GET'])
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
        flash("Successfully registered")
        return redirect('/')
    else:
        return render_template('register.html')


@loginRegistration.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = encryptor(request.form['password'])
        result = conn.execute(text('select user_id, username, password, user_type from users where username=:username and password=:password').params(username=username, password=password))
        row = result.fetchone()
        if row is not None:
            user_type = row[3]
            user_id = row[0]
            if user_type == 'customer':
                session['username'] = username
                session['user_id'] = user_id
                flash(f"You successfully logged in as {username}")
                return redirect('products')
            elif user_type == 'vendor':
                session['username'] = 'vendor'
                session['user_id'] = user_id
                flash(f"Vendor {username} successfully logged in")
                return redirect('vendor')
            elif user_type == 'admin':
                session['username'] = 'admin'
                session['user_id'] = user_id
                flash(f"Admin {username} successfully logged in")
                return redirect('admin')
        flash("Invalid login credentials please try again", 'error')
        return redirect('/')


@loginRegistration.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash("Successfully logged out")
    return redirect('/')


@loginRegistration.route('/user_profile')
def profile():
    username = session['username']
    user_id = session['user_id']
    result = conn.execute(text('select username, first_name, last_name, email, user_type from users where username=:username ').params(username=username))
    address = conn.execute(text('select * from shipping_address where user_id=:user_id').params(user_id=user_id))
    return render_template('user_profile.html', result=result, address=address)


@loginRegistration.route('/set_default', methods=['POST', 'GET'])
def set_default():
    user_id = session['user_id']
    conn.execute(text('update shipping_address set is_default=Null where user_id=:user_id').params(user_id=user_id))
    conn.commit()
    conn.execute(text('update shipping_address set is_default="Yes" where user_id=:user_id and address_id=:address_id').params(user_id=user_id), request.form)
    conn.commit()
    return redirect('user_profile')


@loginRegistration.route('/delete_address', methods=['POST'])
def delete_address():
    conn.execute(text('delete from shipping_address where address_id=:address_id'), request.form)
    conn.commit()
    return redirect('user_profile')


@loginRegistration.route('/update_address', methods=['POST'])
def update_address():
    conn.execute(text('update shipping_address set street_address=:street_address, city=:city, state=:state, zip_code=:zip_code, country=:country, phone_number=:phone_number, name=:name where address_id=:address_id'), request.form)
    conn.commit()
    return redirect('user_profile')


@loginRegistration.route('/add_address', methods=['POST'])
def add_address():
    user_id = session['user_id']
    conn.execute(text('insert into shipping_address(user_id, name, phone_number, street_address, city, state, zip_code, country) values(:user_id, :name, :phone_number, :street_address, :city, :state, :zip_code,  :country)').params(user_id=user_id), request.form)
    conn.commit()
    return redirect('user_profile')
