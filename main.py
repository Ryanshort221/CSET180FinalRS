from flask import Flask, render_template, request, session, redirect, flash
from sqlalchemy import create_engine, text
import hashlib

app = Flask(__name__)
app.secret_key = 'apple'


def encryptor(password):
    salt = 'apple'
    encrypted_password = hashlib.sha224(password.encode('utf-8')).hexdigest() + salt
    return encrypted_password


conn_str = 'mysql://root:1012@localhost/cset180final'
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


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
        flash("Successfully registered")
        return redirect('/')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
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
                return render_template('admin.html', username=username)
        flash("Invalid login credentials please try again", 'error')
        return redirect('/')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash("Successfully logged out")
    return redirect('/')


@app.route('/products', methods=['POST', 'GET'])
def products():
    return render_template('products.html')


@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
    vendor_id = session['user_id']
    # result = conn.execute(text('select p.product_id, p.vendor_id, p.category, p.title, p.description, pv.price, pv.discounted_price, pv.discount_over_date, pv.product_img, pv.color, pv.size, pv.inventory, pv.stock_status, pv.variant_id from products p inner join product_variants pv on p.product_id = pv.product_id where p.vendor_id=:vendor_id').params(vendor_id=vendor_id))
    result = conn.execute(text('select * from products natural join product_variants where vendor_id=:vendor_id').params(vendor_id=vendor_id))
    return render_template('vendor.html', result=result)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    return render_template('admin.html')


@app.route('/user_profile')
def profile():
    username = session['username']
    result = conn.execute(text('select username, first_name, last_name, email, user_type from users where username=:username ').params(username=username))
    return render_template('user_profile.html', result=result)


@app.route('/add_item', methods=['POST', 'GET'])
def add_item():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        inventory = request.form['inventory']
        vendor_id = session['user_id']
        stock_status = request.form['stock_status']
        discounted_price = request.form['discounted_price']
        discount_over_date = request.form['discount_over_date']
        color = request.form['color']
        product_img = request.form['product_img']
        size = request.form['size']
        category = request.form['category']
        result = conn.execute(text('select * from products where title=:title and vendor_id=:vendor_id').params(title=title, vendor_id=vendor_id))
        if result.rowcount >= 1:
            flash('Item already exists')
            return redirect('vendor')
        if discounted_price == '' and discount_over_date == '':
            result = conn.execute(text('insert into products (vendor_id, category, title, description) values(:vendor_id, :category, :title, :description)').params(vendor_id=vendor_id, category=category, title=title, description=description))
            conn.commit()
            product_id = conn.execute(text('select * from products where vendor_id=:vendor_id and title=:title').params(vendor_id=vendor_id, title=title)).fetchone()[0]
            result = conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status))
            conn.commit()
            flash('Item successfully added')
            return redirect('vendor')
        if discounted_price != '' and discount_over_date != '':
            conn.execute(text('insert into products (vendor_id, category, title, description) values(:vendor_id, :category, :title, :description)').params(vendor_id=vendor_id, category=category, title=title, description=description))
            product_id = conn.execute(text('select * from products where vendor_id=:vendor_id and title=:title').params(vendor_id=vendor_id, title=title)).fetchone()[0]
            result = conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status, discounted_price, discount_over_date) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status, :discounted_price, :discount_over_date)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status, discounted_price=discounted_price, discount_over_date=discount_over_date))
            conn.commit()
            flash('Item successfully added')
            return redirect('vendor')
    else:
        return redirect('vendor.html')


@app.route('/delete_item', methods=['POST', 'GET'])
def delete_item():
    if request.method == 'POST':
        variant_id = request.form['variant_id']
        product_id = request.form['product_id']
        conn.execute(text('delete from product_variants where variant_id=:variant_id').params(variant_id=variant_id))
        conn.commit()
        result = conn.execute(text('select * from product_variants where product_id=:product_id').params(product_id=product_id))
        if result.rowcount == 0:
            conn.execute(text('delete from products where product_id=:product_id').params(product_id=product_id))
            conn.commit()
            flash('Your product has been deleted')
            return redirect('vendor')
        flash('Your product has been deleted')
        return redirect('vendor')
    else:
        return redirect('vendor')


@app.route('/update_item', methods=['POST', 'GET'])
def update_item():
    if request.method == 'POST':
        product_id = request.form['product_id']
        vendor_id = session['user_id']
        update_fields = {}
        for field_name in ['title', 'description', 'category']:
            if field_name in request.form and request.form[field_name]:
                update_fields[field_name] = request.form[field_name]
        result = conn.execute(text('select * from products where product_id=:product_id and vendor_id=:vendor_id').params(product_id=product_id, vendor_id=vendor_id))
        if result.rowcount == 0:
            flash("Product doesn't exist, try again.")
            return redirect('vendor')
        else:
            update_query = 'update products set '
            for field_name, field_value in update_fields.items():
                update_query += f'{field_name}=:{field_name}, '
            update_query = update_query.rstrip(', ') + ' where product_id=:product_id and vendor_id=:vendor_id'
            result = conn.execute(text(update_query).params(**update_fields, product_id=product_id, vendor_id=vendor_id))
            conn.commit()
            flash("Item successfully updated.")
            return redirect('vendor')

    else:
        return redirect('vendor')


@app.route('/add_variant', methods=['POST', 'GET'])
def add_variant():
    if request.method == 'POST':
        product_id = request.form['product_id']
        color = request.form['color']
        size = request.form['size']
        result = conn.execute(text('select * from product_variants where product_id=:product_id and color=:color and size=:size').params(product_id=product_id, color=color, size=size))
        if result.rowcount >= 1:
            flash('Variant already exists')
            return redirect('vendor')
        update_fields = {}
        for field_name in ['color', 'size', 'inventory', 'price', 'stock_status', 'discounted_price', 'discount_over_date', 'product_img', 'product_id']:
            if field_name in request.form and request.form[field_name]:
                update_fields[field_name] = request.form[field_name]
            update_query = 'insert into product_variants( '
            for field_name, field_value in update_fields.items():
                update_query += f'{field_name}, '
            update_query = update_query.rstrip(', ') + ') values('
            for field_name, field_value in update_fields.items():
                update_query += f':{field_name}, '
            update_query = update_query.rstrip(', ') + ')'
            result = conn.execute(text(update_query).params(**update_fields))
            conn.commit()
            flash('Variant successfully added')
            return redirect('vendor')
        # come back later and figure out issue
    else:
        return redirect('vendor')


@app.route('/update_variant', methods=['POST', 'GET'])
def update_variant():
    redirect('vendor')


if __name__ == '__main__':
    app.run(debug=True)
