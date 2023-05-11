from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
complaints_blueprint = Blueprint('complaints', __name__, template_folder='templates')


@complaints_blueprint.route('/complaints', methods=['POST', 'GET'])
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
            complaints = conn.execute(text('select distinct c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_description, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id and oi.order_id=c.order_id join products p on p.product_id=pv.product_id where p.vendor_id=:vendor_id').params(vendor_id=vendor_id))
            return render_template('complaints.html', complaints=complaints)
        elif session['username'] == 'admin':
            complaints = conn.execute(text('select distinct c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_description, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id and oi.order_id=c.order_id join products p on p.product_id=pv.product_id order by c.complaint_id'))
            return render_template('complaints.html', complaints=complaints)
        else:
            user_id = session['user_id']
            complaints = conn.execute(text('select distinct c.complaint_id, c.status as complaint_status, c.date, c.title as complaint_title, c.user_id, c.order_id, c.description as complaint_description, c.demands, c.variant_id, pv.variant_id, o.order_id, o.order_date, oi.order_id, oi.quantity, pv.product_id, p.category, p.title, p.description, p.vendor_id from complaints c join product_variants pv on c.variant_id=pv.variant_id join orders o on o.order_id=c.order_id join order_items oi on oi.variant_id=pv.variant_id and oi.order_id=c.order_id join products p on p.product_id=pv.product_id where c.user_id=:user_id').params(user_id=user_id))
            return render_template('complaints.html', complaints=complaints)


@complaints_blueprint.route('/update_complaints', methods=['POST', 'GET'])
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
