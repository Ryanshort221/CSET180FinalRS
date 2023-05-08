from flask import Flask, render_template, request, session, redirect, flash
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
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
                return redirect('admin')
        flash("Invalid login credentials please try again", 'error')
        return redirect('/')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    flash("Successfully logged out")
    return redirect('/')


@app.route('/products', methods=['POST', 'GET'])
def products():
    result = conn.execute(text('select * from products natural join product_variants'))
    return render_template('products.html', result=result)


@app.route('/vendor', methods=['POST', 'GET'])
def vendor():
    vendor_id = session['user_id']
    result = conn.execute(text('select * from products natural join product_variants where vendor_id=:vendor_id').params(vendor_id=vendor_id))
    return render_template('vendor.html', result=result)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    result = conn.execute(text('select * from products natural join product_variants'))
    return render_template('admin.html', result=result)


@app.route('/user_profile')
def profile():
    username = session['username']
    user_id = session['user_id']
    result = conn.execute(text('select username, first_name, last_name, email, user_type from users where username=:username ').params(username=username))
    address = conn.execute(text('select * from shipping_address where user_id=:user_id').params(user_id=user_id))
    return render_template('user_profile.html', result=result, address=address)


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
        if session['username'] == 'vendor':
            vendor_id = session['user_id']
        else:
            vendor_id = request.form['vendor_id']
        result = conn.execute(text('select * from products where title=:title and vendor_id=:vendor_id').params(title=title, vendor_id=vendor_id))
        if result.rowcount >= 1:
            if session['username'] == 'vendor':
                flash('Item already exists')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Item already exists')
                return redirect('admin')
        if discounted_price == '' and discount_over_date == '':
            result = conn.execute(text('insert into products (vendor_id, category, title, description) values(:vendor_id, :category, :title, :description)').params(vendor_id=vendor_id, category=category, title=title, description=description))
            conn.commit()
            product_id = conn.execute(text('select * from products where vendor_id=:vendor_id and title=:title').params(vendor_id=vendor_id, title=title)).fetchone()[0]
            result = conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status))
            conn.commit()
            if session['username'] == 'vendor':
                flash('Item successfully added')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Item successfully added')
                return redirect('admin')
        if discounted_price != '' and discount_over_date != '':
            conn.execute(text('insert into products (vendor_id, category, title, description) values(:vendor_id, :category, :title, :description)').params(vendor_id=vendor_id, category=category, title=title, description=description))
            product_id = conn.execute(text('select * from products where vendor_id=:vendor_id and title=:title').params(vendor_id=vendor_id, title=title)).fetchone()[0]
            result = conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status, discounted_price, discount_over_date) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status, :discounted_price, :discount_over_date)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status, discounted_price=discounted_price, discount_over_date=discount_over_date))
            conn.commit()
            if session['username'] == 'vendor':
                flash('Item successfully added')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Item successfully added')
                return redirect('admin')
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
        if session['username'] == 'vendor':
            flash('Your product has been deleted')
            return redirect('vendor')
        elif session['username'] == 'admin':
            flash('Your product has been deleted')
            return redirect('admin')


@app.route('/update_item', methods=['POST', 'GET'])
def update_item():
    if request.method == 'POST':
        product_id = request.form['product_id']
        vendor_id = session['user_id']
        update_fields = {}
        for field_name in ['title', 'description', 'category']:
            if field_name in request.form and request.form[field_name]:
                update_fields[field_name] = request.form[field_name]
        result = conn.execute(text('select * from products where product_id=:product_id').params(product_id=product_id))
        if result.rowcount == 0:
            if session['username'] == 'vendor':
                flash("Product doesn't exist, try again.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Product doesn't exist, try again.")
                return redirect('admin')
        else:
            update_query = 'update products set '
            for field_name, field_value in update_fields.items():
                update_query += f'{field_name}=:{field_name}, '
            update_query = update_query.rstrip(', ') + ' where product_id=:product_id'
            result = conn.execute(text(update_query).params(**update_fields, product_id=product_id))
            conn.commit()
            if session['username'] == 'vendor':
                flash("Item successfully updated.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Item successfully updated.")
                return redirect('admin')
    else:
        if session['username'] == 'vendor':
            return redirect('vendor')
        elif session['username'] == 'admin':
            return redirect('admin')


@app.route('/add_variant', methods=['POST', 'GET'])
def add_variant():
    if request.method == 'POST':
        product_id = request.form['product_id']
        color = request.form['color']
        size = request.form['size']
        price = request.form['price']
        inventory = request.form['inventory']
        stock_status = request.form['stock_status']
        discounted_price = request.form['discounted_price']
        discount_over_date = request.form['discount_over_date']
        product_img = request.form['product_img']
        result = conn.execute(text('select * from product_variants where product_id=:product_id and color=:color and size=:size').params(product_id=product_id, color=color, size=size))
        if result.rowcount >= 1:
            if session['username'] == 'vendor':
                flash('Variant already exists')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Variant already exists')
                return redirect('admin')
        if discounted_price == '' and discount_over_date == '':
            conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status))
            conn.commit()
            if session['username'] == 'vendor':
                flash('Variant successfully added')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Variant successfully added')
                return redirect('admin')
        if discounted_price != '' and discount_over_date != '':
            conn.execute(text('insert into product_variants (product_id, price, product_img, color, size, inventory, stock_status, discounted_price, discount_over_date) values(:product_id, :price, :product_img, :color, :size, :inventory, :stock_status, :discounted_price, :discount_over_date)').params(product_id=product_id, price=price, product_img=product_img, color=color, size=size, inventory=inventory, stock_status=stock_status, discounted_price=discounted_price, discount_over_date=discount_over_date))
            conn.commit()
            if session['username'] == 'vendor':
                flash('Variant successfully added')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Variant successfully added')
                return redirect('admin')
        else:
            if session['username'] == 'vendor':
                flash('Invalid input')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Invalid input')
                return redirect('admin')
    else:
        if session['username'] == 'vendor':
            return redirect('vendor')
        elif session['username'] == 'admin':
            return redirect('admin')


@app.route('/update_variant', methods=['POST', 'GET'])
def update_variant():
    if request.method == 'POST':
        variant_id = request.form['variant_id']
        product_id = request.form['product_id']
        price = request.form['price']
        inventory = request.form['inventory']
        stock_status = request.form['stock_status']
        discounted_price = request.form['discounted_price']
        discount_over_date = request.form['discount_over_date']
        color = request.form['color']
        product_img = request.form['product_img']
        size = request.form['size']
        result = conn.execute(text('select * from product_variants where product_id=:product_id and variant_id=:variant_id').params(product_id=product_id, variant_id=variant_id))
        if result.rowcount == 0:
            if session['username'] == 'vendor':
                flash("Variant doesn't exist, try again.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Variant doesn't exist, try again.")
                return redirect('admin')
        if discounted_price == '' and discount_over_date == '':
            result = conn.execute(text('update product_variants set price=:price, inventory=:inventory, stock_status=:stock_status, discounted_price=Null, discount_over_date=Null, color=:color, product_img=:product_img, size=:size where variant_id=:variant_id and product_id=product_id').params(price=price, inventory=inventory, stock_status=stock_status, color=color, size=size, product_img=product_img, variant_id=variant_id, product_id=product_id))
            conn.commit()
            if session['username'] == 'vendor':
                flash("Variant successfully updated.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Variant successfully updated.")
                return redirect('admin')
        elif discounted_price != '' and discount_over_date != '':
            result = conn.execute(text('update product_variants set price=:price, inventory=:inventory, stock_status=:stock_status, discounted_price=:discounted_price, discount_over_date=:discount_over_date, color=:color, product_img=:product_img, size=:size where variant_id=:variant_id and product_id=product_id').params(price=price, inventory=inventory, stock_status=stock_status, discounted_price=discounted_price, discount_over_date=discount_over_date, color=color, size=size, product_img=product_img, variant_id=variant_id, product_id=product_id))
            conn.commit()
            if session['username'] == 'vendor':
                flash("Variant successfully updated.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Variant successfully updated.")
                return redirect('admin')
        else:
            if session['username'] == 'vendor':
                flash("Variant not updated, try again.")
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash("Variant not updated, try again.")
                return redirect('admin')
    else:
        if session['username'] == 'vendor':
            return redirect('vendor')
        elif session['username'] == 'admin':
            return redirect('admin')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' in session:
        user_id = session['user_id']
        variant_id = request.form['variant_id']
        quantity = request.form['quantity']
        result = conn.execute(text("select * from product_variants where variant_id=:variant_id and stock_status='in stock'").params(variant_id=variant_id))
        if result.rowcount == 0:
            flash('Item out of stock')
            return redirect('products')
        result = conn.execute(text('select * from cart where user_id=:user_id and variant_id=:variant_id').params(user_id=user_id, variant_id=variant_id))
        if result.rowcount == 0:
            conn.execute(text('insert into cart values(:user_id, :variant_id, :quantity)').params(user_id=user_id, variant_id=variant_id, quantity=quantity))
            conn.commit()
            flash('Item added to cart')
            return redirect('products')
        else:
            flash('Item already in cart')
            return redirect('products')
    else:
        flash('Please login first')
        return redirect('index')


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if 'user_id' in session:
        user_id = session['user_id']
        result = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
        if result.rowcount == 0:
            cart = conn.execute(text('select product_variants.price, product_variants.inventory, product_variants.variant_id, product_variants.discounted_price, product_variants.product_img, product_variants.color, product_variants.size, products.title, products.category, products.description, products.product_id from cart join product_variants on cart.variant_id = product_variants.variant_id join products on product_variants.product_id = products.product_id where cart.user_id = :user_id;').params(user_id=user_id))
            return render_template('cart.html', cart=cart)
        else:
            cart = conn.execute(text('select product_variants.price, product_variants.inventory, product_variants.variant_id, cart.quantity, product_variants.discounted_price, product_variants.product_img, product_variants.color, product_variants.size, products.title, products.category, products.description, products.product_id from cart join product_variants on cart.variant_id = product_variants.variant_id join products on product_variants.product_id = products.product_id where cart.user_id = :user_id;').params(user_id=user_id))
            return render_template('cart.html', cart=cart)
    else:
        flash('Please login first')
        return redirect('index')


@app.route('/update_cart', methods=['POST', 'GET'])
def update_cart():
    if 'user_id' in session:
        user_id = session['user_id']
        variant_id = request.form['variant_id']
        quantity = request.form['quantity']
        action = request.form['action']
        if action.startswith('update-'):
            conn.execute(text('update cart set quantity=:quantity where user_id=:user_id and variant_id=:variant_id').params(quantity=quantity, user_id=user_id, variant_id=variant_id))
            conn.commit()
            flash('Cart updated')
            return redirect('cart')
        elif action.startswith('remove-'):
            variant_id = action.split('-')[1]
            cart = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
            for c in cart.fetchall():
                if str(c.variant_id) == variant_id:
                    conn.execute(text('delete from cart where user_id=:user_id and variant_id=:variant_id').params(user_id=user_id, variant_id=variant_id))
                    conn.commit()
                    flash('Item removed from cart')
                    return redirect('cart')
        elif action == 'checkout':
            result = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
            if result.rowcount == 0:
                flash('Cart empty')
                return redirect('cart')
            else:
                return redirect('checkout')
    else:
        flash('Please login first')
        return redirect('index')


@app.route('/clear_cart', methods=['POST', 'GET'])
def clear_cart():
    if 'user_id' in session:
        user_id = session['user_id']
        result = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
        if result.rowcount == 0:
            flash('Cart empty')
            return redirect('cart')
        else:
            conn.execute(text('delete from cart where user_id=:user_id').params(user_id=user_id))
            conn.commit()
            flash('Cart cleared')
            return redirect('cart')
    else:
        flash('Please login first')
        return redirect('index')


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if request.method == 'GET':
        user_id = session['user_id']
        result = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
        if result.rowcount == 0:
            flash('Cart empty')
            return redirect('cart')
        else:
            cart = conn.execute(text('select product_variants.price, product_variants.inventory, product_variants.variant_id, cart.quantity, product_variants.discounted_price, product_variants.product_img, product_variants.color, product_variants.size, products.title, products.category, products.description, products.product_id from cart join product_variants on cart.variant_id = product_variants.variant_id join products on product_variants.product_id = products.product_id where cart.user_id = :user_id;').params(user_id=user_id))
            shipping_address = conn.execute(text('select * from shipping_address where user_id=:user_id and is_default="Yes"').params(user_id=user_id))
            return render_template('checkout.html', cart=cart, shipping_address=shipping_address)
    elif request.method == 'POST':
        user_id = session['user_id']
        name = request.form['name']
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        phone_number = request.form['phone_number']
        country = request.form['country']
        result = conn.execute(text('select address_id from shipping_address where user_id=:user_id and name=:name and street_address=:street_address and city=:city and state=:state and zip_code=:zip_code and phone_number=:phone_number and country=:country').params(user_id=user_id), request.form)
        if result.rowcount == 1:
            address_id = result.fetchone()[0]
            conn.execute(text('insert into orders (user_id, address_id) values(:user_id, :address_id)').params(user_id=user_id, address_id=address_id))
            conn.commit()
            return redirect('payment')
        result = conn.execute(text('select * from shipping_address where user_id=:user_id and is_default="Yes"').params(user_id=user_id))
        if result.rowcount == 1:
            conn.execute(text('insert into shipping_address(user_id, name, street_address, city, state, zip_code, phone_number, country) values (:user_id, :name, :street_address, :city, :state, :zip_code, :phone_number, :country)').params(user_id=user_id, name=name, street_address=street_address, city=city, state=state, zip_code=zip_code, phone_number=phone_number, country=country))
            conn.commit()
            result = conn.execute(text('select address_id from shipping_address where user_id=:user_id and name=:name and street_address=:street_address and city=:city and state=:state and zip_code=:zip_code and phone_number=:phone_number and country=:country').params(user_id=user_id, name=name, street_address=street_address, city=city, state=state, zip_code=zip_code, phone_number=phone_number, country=country))
            address_id = result.fetchone()[0]
            conn.execute(text('insert into orders(user_id, address_id) values (:user_id, :address_id)').params(user_id=user_id, address_id=address_id))
            conn.commit()
            return redirect('payment')
        else:
            conn.execute(text('insert into shipping_address(user_id, name, street_address, city, state, zip_code, phone_number, country, is_default) values (:user_id, :name, :street_address, :city, :state, :zip_code, :phone_number, :country, "Yes")').params(user_id=user_id, name=name, street_address=street_address, city=city, state=state, zip_code=zip_code, phone_number=phone_number, country=country))
            conn.commit()
            result = conn.execute(text('select address_id from shipping_address where user_id=:user_id and name=:name and street_address=:street_address and city=:city and state=:state and zip_code=:zip_code and phone_number=:phone_number and country=:country').params(user_id=user_id, name=name, street_address=street_address, city=city, state=state, zip_code=zip_code, phone_number=phone_number, country=country))
            address_id = result.fetchone()[0]
            conn.execute(text('insert into orders(user_id, address_id) values (:user_id, :address_id)').params(user_id=user_id, address_id=address_id))
            conn.commit()
            return redirect('payment')


@app.route('/new_address', methods=['POST', 'GET'])
def new_address():
    if request.method == 'POST':
        user_id = session['user_id']
        name = request.form['name']
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        phone_number = request.form['phone_number']
        country = request.form['country']
        conn.execute(text('insert into shipping_address(user_id, name, street_address, city, state, zip_code, phone_number, country) values (:user_id, :name, :street_address, :city, :state, :zip_code, :phone_number, :country)').params(user_id=user_id, name=name, street_address=street_address, city=city, state=state, zip_code=zip_code, phone_number=phone_number, country=country))
        conn.commit()
        address_id = conn.execute(text('select last_insert_id()')).fetchone()[0]
        conn.execute(text('insert into orders(user_id, address_id) values (:user_id, :address_id)').params(user_id=user_id, address_id=address_id))
        conn.commit()
        return redirect('payment')


@app.route('/payment', methods=['POST', 'GET'])
def payment():
    if request.method == 'GET':
        user_id = session['user_id']
        cart = conn.execute(text('select product_variants.price, product_variants.inventory, product_variants.variant_id, cart.quantity, product_variants.discounted_price, product_variants.product_img, product_variants.color, product_variants.size, products.title, products.category, products.description, products.product_id from cart join product_variants on cart.variant_id = product_variants.variant_id join products on product_variants.product_id = products.product_id where cart.user_id = :user_id;').params(user_id=user_id))
        shipping_address = conn.execute(text('select * from shipping_address where user_id=:user_id').params(user_id=user_id))
        return render_template('payment.html', cart=cart, shipping_address=shipping_address)
    elif request.method == 'POST':
        user_id = session['user_id']
        total = request.form['total']
        total = total.split('$')[1]
        conn.execute(text('update orders set total=:total, order_date=curdate(), status="pending" where user_id=:user_id order by order_id desc limit 1').params(total=total, user_id=user_id))
        conn.commit()
        order = conn.execute(text('select * from orders where user_id=:user_id order by order_id desc limit 1').params(user_id=user_id)).fetchone()
        order_id = order[0]
        cart = conn.execute(text('select * from cart where user_id=:user_id').params(user_id=user_id))
        for item in cart:
            conn.execute(text('insert into order_items(order_id, variant_id, quantity) values (:order_id, :variant_id, :quantity)').params(order_id=order_id, variant_id=item[1], quantity=item[2]))
            conn.commit()
            flash('Your order has successfully been placed')
        # will also need to subtract the quantities from product_variants after order is placed and if inventory=0 set stock_status to out of stock otherwise just update inventory-quantity
        conn.execute(text('delete from cart where user_id=:user_id').params(user_id=user_id))
        conn.commit()
        return redirect('orders')


@app.route('/orders', methods=['POST', 'GET'])
def orders():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            if session['username'] != 'admin' or 'vendor':
                orders = conn.execute(text('select * from orders where user_id=:user_id order by order_id').params(user_id=user_id)).fetchall()
                products = []
                for order in orders:
                    order_products = conn.execute(text('select o.order_id, oi.quantity, oi.order_id, oi.variant_id, p.product_id, p.title, p.vendor_id, pv.product_img, pv.size, pv.color, pv.price, pv.discounted_price from orders o join order_items oi on o.order_id = oi.order_id join product_variants pv on oi.variant_id = pv.variant_id join products p on pv.product_id = p.product_id where o.user_id =:user_id and oi.order_id=:order_id order by oi.order_id').params(user_id=user_id, order_id=order.order_id)).fetchall()
                    products.extend(order_products)
                return render_template('orders.html', orders=orders, products=products)


@app.route('/vendor_orders', methods=['POST', 'GET'])
def vendor_orders():
    if 'user_id' in session:
        user_id = session['user_id']
        if session['username'] == 'vendor':
            orders = conn.execute(text('select o.order_id, o.status, o.order_date, o.total, p.vendor_id from orders o join order_items oi on o.order_id=oi.order_id join product_variants pv on oi.variant_id=pv.variant_id join products p on pv.product_id = p.product_id where p.vendor_id =:user_id group by o.order_id').params(user_id=user_id).params(user_id=user_id))
            products = conn.execute(text('select o.order_id, oi.quantity, oi.order_id, oi.variant_id, p.product_id, p.title, p.vendor_id, pv.product_img, pv.size, pv.color, pv.price, pv.discounted_price from orders o join order_items oi on o.order_id = oi.order_id join product_variants pv on oi.variant_id = pv.variant_id join products p on pv.product_id = p.product_id where p.vendor_id =:user_id order by oi.order_id').params(user_id=user_id)).fetchall()
            return render_template('vendor_orders.html', orders=orders, products=products)


@app.route('/review', methods=['POST', 'GET'])
def review():
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            variant_id = request.form['variant_id']
            description = request.form['description']
            rating = request.form['rating']
            conn.execute(text('insert into reviews (user_id, variant_id, rating, description, date) values (:user_id, :variant_id, :rating, :description, curdate())').params(user_id=user_id, variant_id=variant_id, description=description, rating=rating))
            conn.commit()
            flash('Review submitted')
            return redirect('orders')
        else:
            flash('Please login')
            return redirect('login')
    else:
        reviews = conn.execute(text('select p.title, pv.size, pv.variant_id, pv.color, u.first_name, u.last_name, r.rating, r.date as review_date, r.description from reviews r join product_variants pv on r.variant_id=pv.variant_id join products p on p.product_id=pv.product_id join users u on u.user_id=r.user_id'))
        return render_template('review.html', reviews=reviews)


@app.route('/filter_reviews', methods=['POST', 'GET'])
def filter_reviews():
    if request.method == 'POST':
        rating = request.form['rating']
        reviews = conn.execute(text('select p.title, pv.size, pv.variant_id, pv.color, u.first_name, u.last_name, r.rating, r.date as review_date, r.description from reviews r join product_variants pv on r.variant_id=pv.variant_id join products p on p.product_id=pv.product_id join users u on u.user_id=r.user_id where r.rating=:rating').params(rating=rating))
        return render_template('review.html', reviews=reviews)
    else:
        return redirect('review')


@app.route('/update_status', methods=['POST', 'GET'])
def update_status():
    if request.method == 'POST':
        order_id = request.form['order_id']
        status = request.form['status']
        conn.execute(text('update orders set status=:status where order_id=:order_id').params(status=status, order_id=order_id))
        conn.commit()
        flash('Order Status Updated')
        return redirect('vendor_orders')
    else:
        return redirect('vendor_orders')


@app.route('/complaints', methods=['POST', 'GET'])
def complaints():
    if request.method == 'POST':
        user_id = session['user_id']
        variant_id = request.form['variant_id']
        order_id = request.form['order_id']
        title = request.form['title']
        description = request.form['description']
        demands = request.form['demands']
        conn.execute(text('insert into complaints (user_id, variant_id, order_id, title, description, demands, date) values(:user_id, :variant_id, :order_id, :title, :description, :demands, curdate())').params(user_id=user_id, variant_id=variant_id, order_id=order_id, title=title, description=description, demands=demands))
        conn.commit()
        flash('Complaint submitted')
        return redirect('orders')
    else:
        if session['username'] == 'vendor':
            vendor_id = session['user_id']
            complaints = conn.execute(text('select c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_desciption, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.color, pv.size, pv.price, pv.discounted_price, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id join products p on p.product_id=pv.product_id where p.vendor_id=:vendor_id').params(vendor_id=vendor_id))
            return render_template('complaints.html', complaints=complaints)
        elif session['username'] == 'admin':
            complaints = conn.execute(text('select c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_description, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.color, pv.size, pv.price, pv.discounted_price, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id join products p on p.product_id=pv.product_id order by c.complaint_id'))
            return render_template('complaints.html', complaints=complaints)
        else:
            user_id = session['user_id']
            complaints = conn.execute(text('select c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_description, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.color, pv.size, pv.price, pv.discounted_price, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id join products p on p.product_id=pv.product_id where c.user_id=:user_id').params(user_id=user_id))
            return render_template('complaints.html', complaints=complaints)


@app.route('/update_complaints', methods=['POST', 'GET'])
def update_complaints():
    if request.method == 'POST':
        complaint_id = request.form['complaint_id']
        status = request.form['complaint_status']
        settled_by = session['user_id']
        conn.execute(text('update complaints set status=:status, settled_by=:settled_by where complaint_id=:complaint_id').params(status=status, complaint_id=complaint_id, settled_by=settled_by))
        conn.commit()
        flash('Complaint Status Updated')
        return redirect('complaints')
    else:
        return redirect('complaints')


if __name__ == '__main__':
    app.run(debug=True)
