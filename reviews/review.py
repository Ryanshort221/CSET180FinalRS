from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
review_blueprint = Blueprint('review', __name__, template_folder='templates')


@review_blueprint.route('/review', methods=['POST', 'GET'])
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
        reviews = conn.execute(text('select p.title, p.product_id, p.vendor_id, pv.product_img,  pv.size, pv.variant_id, pv.color, u.first_name, u.last_name, r.rating, r.date as review_date, r.description from reviews r join product_variants pv on r.variant_id=pv.variant_id join products p on p.product_id=pv.product_id join users u on u.user_id=r.user_id'))
        return render_template('review.html', reviews=reviews)


@review_blueprint.route('/filter_reviews', methods=['POST', 'GET'])
def filter_reviews():
    if request.method == 'POST':
        rating = request.form['rating']
        reviews = conn.execute(text('select p.title, p.vendor_id, p.product_id, pv.product_img, pv.size, pv.variant_id, pv.color, u.first_name, u.last_name, r.rating, r.date as review_date, r.description from reviews r join product_variants pv on r.variant_id=pv.variant_id join products p on p.product_id=pv.product_id join users u on u.user_id=r.user_id where r.rating=:rating').params(rating=rating))
        return render_template('review.html', reviews=reviews)
    else:
        return redirect('review')
