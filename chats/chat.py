from flask import Flask, render_template, request, session, redirect, flash, Blueprint
from sqlalchemy import text
from db import conn
app = Flask(__name__)
app.secret_key = 'apple'
chat_blueprint = Blueprint('chat', __name__, template_folder='templates')


@chat_blueprint.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'GET':
        if session['username'] == 'vendor':
            user_id = session['user_id']
            messages = conn.execute(text('select * from chat')).fetchall()
            chats = conn.execute(text('select c.customer_id, c.admin_vendor_id, c.title, c.date, u.username from chat c join users u on customer_id=user_id where message is null and admin_vendor_id=:user_id').params(user_id=user_id)).fetchall()
            return render_template('chat.html', chats=chats, messages=messages)
        elif session['username'] == 'admin':
            user_id = session['user_id']
            messages = conn.execute(text('select * from chat')).fetchall()
            chats = conn.execute(text('select c.customer_id, c.admin_vendor_id, c.title, c.date, u.username from chat c join users u on customer_id=user_id where message is null and admin_vendor_id=:user_id').params(user_id=user_id)).fetchall()
            return render_template('chat.html', chats=chats, messages=messages)
        else:
            user_id = session['user_id']
            admins = conn.execute(text('select user_id, username from users where user_type="admin"'))
            vendors = conn.execute(text('select user_id, username from users where user_type="vendor"'))
            messages = conn.execute(text('select * from chat')).fetchall()
            chats = conn.execute(text('select c.customer_id, c.admin_vendor_id, c.title, c.date, u.username from chat c join users u on admin_vendor_id=user_id where message is null and customer_id=:user_id').params(user_id=user_id)).fetchall()
            return render_template('chat.html', admins=admins, vendors=vendors, chats=chats, messages=messages)


@chat_blueprint.route('/start_chat', methods=['POST'])
def start_chat():
    user_id = session['user_id']
    conn.execute(text('insert into chat (customer_id, admin_vendor_id, title, date) values(:user_id, :admin_vendor_id, :title, curdate())').params(user_id=user_id), request.form)
    conn.commit()
    return redirect('chat')


@chat_blueprint.route('/send_message', methods=['POST'])
def send_message():
    if request.method == 'POST':
        user_id = session['user_id']
        if session['username'] == 'vendor':
            conn.execute(text('insert into chat (admin_vendor_id, sender_id, customer_id, receiver_id, message, date) values(:user_id, :user_id, :customer_id, :customer_id, :message, curdate())').params(user_id=user_id), request.form)
            conn.commit()
            return redirect('chat')
        elif session['username'] == 'admin':
            conn.execute(text('insert into chat (admin_vendor_id, sender_id, customer_id, receiver_id, message, date) values(:user_id, :user_id, :customer_id, :customer_id, :message, curdate())').params(user_id=user_id), request.form)
            conn.commit()
            return redirect('chat')
        else:
            conn.execute(text('insert into chat (customer_id, sender_id, admin_vendor_id, receiver_id, message, date) values(:user_id, :user_id, :admin_vendor_id, :admin_vendor_id, :message, curdate())').params(user_id=user_id), request.form)
            conn.commit()
            return redirect('chat')
