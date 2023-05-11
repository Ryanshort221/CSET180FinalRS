from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
orders_blueprint = Blueprint('orders', __name__, template_folder='templates')


@orders_blueprint.route('/orders', methods=['POST', 'GET'])
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


@orders_blueprint.route('/vendor_orders', methods=['POST', 'GET'])
def vendor_orders():
    if 'user_id' in session:
        user_id = session['user_id']
        if session['username'] == 'vendor':
            orders = conn.execute(text('select o.order_id, o.status, o.order_date, o.total, p.vendor_id from orders o join order_items oi on o.order_id=oi.order_id join product_variants pv on oi.variant_id=pv.variant_id join products p on pv.product_id = p.product_id where p.vendor_id =:user_id group by o.order_id').params(user_id=user_id).params(user_id=user_id))
            products = conn.execute(text('select o.order_id, oi.quantity, oi.order_id, oi.variant_id, p.product_id, p.title, p.vendor_id, pv.product_img, pv.size, pv.color, pv.price, pv.discounted_price from orders o join order_items oi on o.order_id = oi.order_id join product_variants pv on oi.variant_id = pv.variant_id join products p on pv.product_id = p.product_id where p.vendor_id =:user_id order by oi.order_id').params(user_id=user_id)).fetchall()
            return render_template('vendor_orders.html', orders=orders, products=products)


@orders_blueprint.route('/update_status', methods=['POST', 'GET'])
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
