from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
cart_blueprint = Blueprint('cart', __name__, template_folder='templates')


@cart_blueprint.route('/add_to_cart', methods=['POST'])
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
        return redirect('products')


@cart_blueprint.route('/cart', methods=['POST', 'GET'])
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


@cart_blueprint.route('/update_cart', methods=['POST', 'GET'])
def update_cart():
    if 'user_id' in session:
        user_id = session['user_id']
        if 'variant_id' not in request.form:
            flash('Cart empty')
            return redirect('cart')
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
            return redirect('checkout')
    else:
        flash('Please login first')
        return redirect('index')


@cart_blueprint.route('/clear_cart', methods=['POST', 'GET'])
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
