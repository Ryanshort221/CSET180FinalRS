from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
product = Blueprint('product', __name__, template_folder='templates')


@product.route('/products', methods=['POST', 'GET'])
def products():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    return render_template('products.html', result=result, colors=colors, categories=categories, sizes=sizes)


@product.route('/filter_color', methods=['POST'])
def filter_color():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants where color=:color'), request.form)
    return render_template('products.html', result=result, categories=categories, sizes=sizes, colors=colors)


@product.route('/filter_category', methods=['POST'])
def filter_category():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    selected_category = request.form['category']
    result = conn.execute(text('select * from products natural join product_variants where category=:category'), {'category': selected_category})
    # result = conn.execute(text('select * from products natural join product_variants where category=:category'), request.form)
    return render_template('products.html', result=result, categories=categories, sizes=sizes, colors=colors)


@product.route('/filter_size', methods=['POST'])
def filter_size():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants where size=:size'), request.form)
    return render_template('products.html', result=result, categories=categories, sizes=sizes, colors=colors)


@product.route('/search', methods=['POST'])
def search():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants where title like :search or description like :search or vendor_id like :search '), {'search': f'%{request.form["search"]}%'})
    return render_template('products.html', result=result, categories=categories, sizes=sizes, colors=colors)


@product.route('/filter_availability', methods=['POST'])
def filter_availability():
    colors = conn.execute(text('select distinct color from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants')).fetchall()
    categories = conn.execute(text('select distinct category from products'))
    sizes = conn.execute(text('select distinct size from product_variants'))
    result = conn.execute(text('select * from products natural join product_variants where stock_status=:availability'), request.form)
    return render_template('products.html', result=result, categories=categories, sizes=sizes, colors=colors)


@product.route('/vendor', methods=['POST', 'GET'])
def vendor():
    vendor_id = session['user_id']
    result = conn.execute(text('select * from products natural join product_variants where vendor_id=:vendor_id').params(vendor_id=vendor_id))
    return render_template('vendor.html', result=result)


@product.route('/admin', methods=['POST', 'GET'])
def admin():
    result = conn.execute(text('select * from products natural join product_variants'))
    vendor_id = conn.execute(text('select distinct vendor_id from products'))
    return render_template('admin.html', result=result, vendor_id=vendor_id)


@product.route('/add_item', methods=['POST', 'GET'])
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


@product.route('/delete_item', methods=['POST', 'GET'])
def delete_item():
    if request.method == 'POST':
        variant_id = request.form['variant_id']
        product_id = request.form['product_id']
        result = conn.execute(text('select * from cart where variant_id=:variant_id').params(variant_id=variant_id))
        if result.rowcount >= 1:
            if session['username'] == 'vendor':
                flash('Item in cart, cannot delete')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Item in cart, cannot delete')
                return redirect('admin')
        result = conn.execute(text('select * from order_items where variant_id=:variant_id').params(variant_id=variant_id))
        if result.rowcount >= 1:
            if session['username'] == 'vendor':
                flash('Item in order, cannot delete')
                return redirect('vendor')
            elif session['username'] == 'admin':
                flash('Item in order, cannot delete')
                return redirect('admin')
        else:
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


@product.route('/update_item', methods=['POST', 'GET'])
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


@product.route('/add_variant', methods=['POST', 'GET'])
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


@product.route('/update_variant', methods=['POST', 'GET'])
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
