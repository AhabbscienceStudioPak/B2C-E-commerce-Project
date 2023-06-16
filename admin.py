from main import app, db
from models import *
from flask_sqlalchemy import SQLAlchemy
from flask import flash,render_template,request,session, redirect, url_for
import uuid
import logging
from werkzeug.utils import secure_filename
import os
from datetime import date
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

#routing the app to the login page.(In this case this is my starting page for now)
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
         return render_template('admin_login.html')
    
    # Verify reCAPTCHA
    # response = request.form.get('g-recaptcha-response')
    # if not response:
    #     return render_template('login.html', error='Please complete the reCAPTCHA.')
    

    admin_id = request.form.get('admin_id')
    entered_password = request.form.get('password')

    if admin_id and entered_password:
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if admin and admin.login_id == entered_password:
            session['admin_id'] = admin.admin_id
            return render_template('admin_dashboard.html')
        else:
            error = 'Invalid Credentials. Please try again.'
    else:
        error = 'Missing username or password. Please try again.'
    return render_template('admin_login.html', error=error)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        unit_weight = request.form['weight']
        quantity = request.form['quantity']

        # Check if product already exists
        existing_product = Product.query.filter_by(product_name=name, product_description=description, price=price, category=category, unit_weight=unit_weight).first()
        if existing_product:
            # Return an error message if the product already exists
            return render_template('admin_dashboard.html', message="Product already exists")

        # save uploaded image file
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_product = Product(product_id = str(uuid.uuid4())[:20], product_name=name, product_description=description, price=price, quantity_pu = quantity, product_image = filename, category = category, unit_weight=unit_weight)
        db.session.add(new_product)
        db.session.commit()

    return render_template('admin_dashboard.html')

@app.route('/edit_product', methods=['GET', 'POST'])
def edit_product():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    product_id = request.form['product_id']
    product = Product.query.filter_by(product_id=product_id).first() 
    
    if request.method == 'POST':
        product.product_name = request.form['new_name']
        product.product_description = request.form['new_description']
        product.price = request.form['new_price']

        db.session.commit()

    return render_template('admin_dashboard.html')

@app.route('/remove_product', methods=['POST'])
def remove_product():
    product_id = request.form['product_id']
    
    # check if product exists
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        flash('Product not found.')
        return redirect(url_for('admin'))
    
    # remove product from database
    db.session.delete(product)
    db.session.commit()
    
    flash('Product removed successfully.')
    return render_template('admin_dashboard.html')

@app.route('/orders')
def admin_orders():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))

    orders = OrderInfo.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/analytics/')
def analytics():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))    
    
    return dash_app.index()

# create Dash app
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/analytics/')


#helper function to get product sales and revenue data
def get_product_sales():
    with app.app_context():
        product_sales = []
        for product in Product.query.all():
            order_dates = []
            quantity_sold = []
            revenue = []
            for order_date, sum_quantity, sum_price in db.session.query(Order.order_date, db.func.sum(OrderItem.quantity), db.func.sum(OrderItem.unit_price)).join(OrderItem).filter_by(product_id=product.product_id).group_by(Order.order_date):
                order_dates.append(order_date)
                quantity_sold.append(sum_quantity)
                revenue.append(sum_price)
            product_sales.append({'product_name': product.product_name, 'order_dates': order_dates, 'quantity_sold': quantity_sold, 'revenue': revenue})
        return product_sales

    # helper function to get total revenue by date
def get_revenue_by_date():
    with app.app_context():
        revenue_by_date = []
        for order_date, total_revenue in db.session.query(Order.order_date, db.func.sum(OrderItem.unit_price * OrderItem.quantity)).join(OrderItem).group_by(Order.order_date):
            revenue_by_date.append({'order_date': order_date, 'total_revenue': total_revenue})
        return revenue_by_date

# define Dash layout
dash_app.layout = html.Div(children=[
    html.H1(children='Product Sales'),
    html.H2(children='Quantity of each Product sold'),
    dcc.Graph(
        id='product-sales-quantity-graph',
        figure={
            'data': [
                go.Scatter(
                    x=product_sales['order_dates'],
                    y=product_sales['quantity_sold'],
                    name=product_sales['product_name']
                )
                for product_sales in get_product_sales()
            ],
            'layout': go.Layout(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Quantity Sold'},
                title='Quantity of each Product sold'
            )
        }
    ),
    html.H2(children='Revenue generated by each Product'),
    dcc.Graph(
        id='product-sales-revenue-graph',
        figure={
            'data': [
                go.Scatter(
                    x=product_sales['order_dates'],
                    y=product_sales['revenue'],
                    name=product_sales['product_name']
                )
                for product_sales in get_product_sales()
            ],
            'layout': go.Layout(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Revenue'},
                title='Revenue generated by each Product'
            )
        }
    ),
    html.H2(children='Total Revenue by Date'),
    dcc.Graph(
        id='total-revenue-by-date',
        figure={
            'data': [go.Scatter(
            x=[rbd['order_date'] for rbd in get_revenue_by_date()],
            y=[rbd['total_revenue'] for rbd in get_revenue_by_date()]
            )],
            'layout': go.Layout(title='Total Revenue by Date', xaxis=dict(title='Date'), yaxis=dict(title='Revenue'))
        }
    )
])
