from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
checkout_blueprint = Blueprint('checkout', __name__, template_folder='templates')


@checkout_blueprint.route('/checkout', methods=['POST', 'GET'])
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


@checkout_blueprint.route('/new_address', methods=['POST', 'GET'])
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


@checkout_blueprint.route('/payment', methods=['POST', 'GET'])
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
        conn.execute(text('delete from cart where user_id=:user_id').params(user_id=user_id))
        conn.commit()
        return redirect('orders')
