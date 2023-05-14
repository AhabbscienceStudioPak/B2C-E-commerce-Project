from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, render_template, request, session, redirect, url_for, abort
#from strgen import StringGenerator as SG
from sqlalchemy import create_engine
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
import uuid
import logging
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
import requests
import stripe
from datetime import date

load_dotenv()

# stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
# stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
# stripe_public_key = <STRIPE_PUBLISHABLE_KEY>
# stripe.api_key = <STRIPE_SECRET_KEY>

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config['ALLOWED_EXTENSIONS']


# configure app to enable it to interact with your database
# format: 'postgresql://user:password@localhost/database name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pgadmin@localhost:5432/ecommsite'

db = SQLAlchemy(app)

# Database relational models based on flask-SQLAlchemy ORM syntax


class Admin(db.Model):
    __tablename__ = 'admin'

    admin_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    login_id = db.Column(db.String(20), unique=True)


class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.String(20), primary_key=True)
    nop = db.Column(db.Integer)
    total_price = db.Column(db.Integer)
    customer_id = db.Column(db.ForeignKey('customer.customer_id'))


class CartProduct(db.Model):
    __tablename__ = 'cart_products'

    cart_id = db.Column(db.String(20), db.ForeignKey(
        'cart.cart_id'), primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey(
        'product.product_id'), primary_key=True)
    quantity = db.Column(db.Integer)


class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.String(20), primary_key=True)
    category_name = db.Column(db.String(20))
    description = db.Column(db.String(50))


class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    loginid = db.Column(db.String(10), unique=True)
    passwd = db.Column(db.String(20), unique=True)
    contact_num = db.Column(db.String)


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.Date, nullable=False)
    shipped_date = db.Column(db.Date)
    shipper_id = db.Column(db.Integer, db.ForeignKey('shipper.shipper_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.order_id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.product_id'), primary_key=True)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Float, nullable=False)


class PersonalInfo(db.Model):
    __tablename__ = 'personal_info'

    dummy_id = db.Column(db.String(20), primary_key=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(80))
    city = db.Column(db.String(10))
    country = db.Column(db.String(20))
    postal_code = db.Column(db.Integer)
    email = db.Column(db.String(30), unique=True)
    passwd = db.Column(db.String(20))
    login_id = db.Column(db.String(20), unique=True)
    customer_id = db.Column(db.ForeignKey('customer.customer_id'))

    customer1 = db.relationship(
        'Customer', primaryjoin='PersonalInfo.customer_id == Customer.customer_id', backref='personal_infos')


class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.String(20), primary_key=True)
    quantity_pu = db.Column(db.Integer)
    product_name = db.Column(db.String(20))
    product_image = db.Column(db.String)
    stock_units = db.Column(db.Integer)
    unit_weight = db.Column(db.Float(53))
    discount = db.Column(db.Float(53))
    reorder_level = db.Column(db.Integer)
    price = db.Column(db.Integer)
    product_description = db.Column(db.String(30))
    supplier_id = db.Column(db.ForeignKey('supplier.supplier_id'))
    category_id = db.Column(db.ForeignKey('category.category_id'))

    category1 = db.relationship(
        'Category', primaryjoin='Product.category_id == Category.category_id', backref='products')


class Shipper(db.Model):
    __tablename__ = 'shipper'

    shipper_id = db.Column(db.String(40), primary_key=True)
    phone = db.Column(db.String(20))
    company_name = db.Column(db.String(20))


class Supplier(db.Model):
    __tablename__ = 'supplier'

    supplier_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))


# set secret key for the app in order to use sessions
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', error=None)

    # Verify reCAPTCHA
    # response = request.form.get('g-recaptcha-response')
    # if not response:
    #     return render_template('login.html', error='Please complete the reCAPTCHA.')

    usr = request.form.get('username')
    entered_password = request.form.get('password')

    if usr and entered_password:
        customer = Customer.query.filter_by(loginid=usr).first()
        if customer and customer.passwd == entered_password:
            session['username'] = usr
            session['customer_id'] = customer.customer_id
            flash('You are successfully logged in')
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
    else:
        error = 'Missing username or password. Please try again.'

    return render_template('login.html', error=error)


# routing to createuser page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fn = request.form['first_name']
        ln = request.form['last_name']
        usr = request.form['loginid']
        cno = request.form['contact_num']
        pwd = request.form['passwd']

        error = None

        if not (fn and ln and usr and cno and pwd):
            error = "Failure: Credentials are not filled in properly."
            return render_template('register.html', error)

        usr_exists = Customer.query.filter_by(loginid=usr).first()
        if usr_exists:
            error = "Failure: Username already exists"
            return render_template('register.html', error)

        c_id = str(uuid.uuid4())[:8]
        new_customer = Customer(customer_id=c_id, first_name=fn,
                                last_name=ln, loginid=usr, passwd=pwd, contact_num=cno)
        db.session.add(new_customer)
        db.session.commit()
        flash('User successfully created')
        return redirect(url_for('login'))

    return render_template('register.html', error=None)


def getLoginDetails():
    loggedIn = False
    firstName = ''
    noOfItems = 0

    if 'username' in session:
        loggedIn = True
        usr = session['username']

        # get the number of items in the cart for the current user
        user = Customer.query.filter_by(loginid=usr).first()
        if user:
            cart = Cart.query.filter_by(customer_id=user.customer_id).all()
            noOfItems = len(cart)

    return loggedIn, firstName, noOfItems


@app.route("/category")
def displayCategory():
    category_id = request.args.get('categoryId')
    category = Category.query.filter_by(category_id=category_id).first()
    products = db.session.query(Product).join(Category, Product.category_id ==
                                              Category.category_id).filter(Category.category_id == category_id).all()
    return render_template('category.html', products=products, category=category)


@app.route("/productDescription")
def productDescription():
    product_id = request.args.get('productId')
    productData = Product.query.filter_by(product_id=product_id).first()
    return render_template("product.html", productdata=productData)


@app.route("/addToCart", methods=["POST"])
def addToCart():
    if 'username' not in session:
        return redirect(url_for('login'))

    else:
        product_id = request.args.get('productId')
        cust_id = session['customer_id']

        productData = Product.query.filter_by(product_id=product_id).first()
        # Check if the product is already in the cart
        cart = Cart.query.filter_by(customer_id=cust_id).first()

        if not cart:
            # If the customer doesn't have a cart, create a new one
            cart = Cart(cart_id=str(uuid.uuid4())[
                        :20], customer_id=cust_id, nop=0, total_price=0)
            db.session.add(cart)

        # Check if the product is already in the cart
        cart_product = CartProduct.query.filter_by(
            cart_id=cart.cart_id, product_id=product_id).first()

        if cart_product:
            cart_product.quantity += int(request.form['quantity'])
            cart.nop += int(request.form['quantity'])
            productData.quantity_pu -= int(request.form['quantity'])
        else:
            cart_product = CartProduct(
                cart_id=cart.cart_id, product_id=product_id, quantity=int(request.form['quantity']))
            cart.nop += int(request.form['quantity'])
            db.session.add(cart_product)
            productData.quantity_pu -= int(request.form['quantity'])

        # Update the total price
        product = Product.query.get(product_id)
        cart.total_price += product.price * int(request.form['quantity'])

        db.session.commit()

        msg = "Added successfully"
        return redirect(url_for('cart'))


@app.route("/cart")
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cust_id = session['customer_id']
    cust = Customer.query.filter_by(customer_id=cust_id).first()

    products = (
        db.session.query(Product, CartProduct.quantity)
        .join(CartProduct)
        .join(Cart)
        .filter(Cart.customer_id == cust_id)
        .all()
    )

    cart = Cart.query.filter_by(customer_id=cust_id).first()
    if cart:
        total_price = cart.total_price
        nop = cart.nop
    else:
        return render_template("cart.html", totalPrice=0, noOfItems=0)
    return render_template("cart.html", products=products, totalPrice=total_price, noOfItems=nop)


@app.route("/removeFromCart", methods=["POST"])
def removeFromCart():
    if 'username' not in session:
        return redirect(url_for('login'))

    usr = session['username']
    cust_id = session['customer_id']
    product_id = request.form['productId']

    cust = Customer.query.filter_by(loginid=usr).first()
    cart = Cart.query.filter_by(customer_id=cust_id).first()

    try:
        cart_product = CartProduct.query.filter_by(
            cart_id=cart.cart_id, product_id=product_id).first()
        db.session.delete(cart_product)
        cart.nop -= cart_product.quantity
        product = Product.query.get(product_id)
        product.quantity_pu += cart_product.quantity
        cart.total_price -= product.price * cart_product.quantity
        db.session.commit()
        msg = "removed successfully"
    except Exception as e:
        db.session.rollback()
        msg = "error occurred"
        logging.error(f"Error removing item from cart: {msg}. Exception: {e}")

    return redirect(url_for('cart'))


@app.route("/")
def index():

    productData = db.session.query(Product).all()
    categoryData = db.session.query(Category).all()

    return render_template('index.html', productData=productData, categoryData=categoryData)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'customer_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    cust_id = session['customer_id']
    cart = Cart.query.filter_by(customer_id=cust_id).first()
    total_price = cart.total_price
    nop = cart.nop
    products = (
        db.session.query(Product, CartProduct.quantity)
        .join(CartProduct)
        .join(Cart)
        .filter(Cart.customer == cust_id)
        .all()
    )

    if request.method == 'POST':
        cart_products = CartProduct.query.filter_by(cart_id=cart.cart_id).all()
        line_items = []
        for cart_product in cart_products:
            product = Product.query.get(cart_product.product_id)
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.product_name,
                        'images': [product.product_image],
                    },
                    'unit_amount': product.price * cart_product.quantity * 100,
                },
                'quantity': cart_product.quantity,
            })

        session['line_items'] = line_items
        session['description'] = 'Order from Kuchu Muchu'
        session['amount'] = total_price
        session['nop'] = nop
        session['cart_id'] = cart.cart_id
        session['customer_email'] = Customer.query.get(cust_id).loginid

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )

        return redirect(checkout_session.url, code=303)

    return render_template('checkout.html', totalPrice=total_price, noOfItems=nop, stripe_public_key=os.environ.get('STRIPE_PUBLISHABLE_KEY'), cart_items=products)


@app.route('/success')
def success():
    description = session['description']
    amount = session['amount']
    nop = session['nop']
    cart_id = session['cart_id']
    cust_id = session['customer_id']

    # Update cart and commit changes
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    product= Product.query.filter_by()
    cart.nop = 0
    cart.total_price = 0
    db.session.commit()


    # Create an Aboutorder entry
    order = Order(customer_id=cust_id,
                  order_date=date.today(), shipper_id='S123')
    db.session.add(order)
    db.session.commit()

    products = (
        db.session.query(Product, CartProduct.quantity)
        .join(CartProduct)
        .filter(CartProduct.cart_id == cart_id)
        .all()
    )

    # Add order details to the database
    cart_products = CartProduct.query.filter_by(cart_id=cart_id).all()
    for product, quantity in products:
        orderItems = OrderItem(unit_price=quantity * product.price, discount=0,
                               quantity=quantity, product_id=product.product_id, order_id=order.order_id)
        db.session.add(orderItems)
    db.session.commit()

    # Clear the shopping cart
    for cp in cart_products:
        db.session.delete(cp)
    db.session.commit()

    return render_template('success.html', description=description, amount=amount, nop=nop)


@app.route('/cancel')
def cancel():
    return render_template('cancel.html')


@app.route('/webhook', methods=['POST'])
def webhook_received():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ['STRIPE_ENDPOINT_SECRET']
        )
    except ValueError as e:
        return str(e), 400
    except stripe.error.SignatureVerificationError as e:
        return str(e), 400

    # Process the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle successful payment (e.g., fulfill the order)

    return '', 200


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# routing the app to the login page.(In this case this is my starting page for now)
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
        discount = request.form['discount']
        quantity = request.form['quantity']

        # Check if product already exists
        existing_product = Product.query.filter_by(
            product_name=name, product_description=description, price=price, category_id=category, discount=discount).first()
        if existing_product:
            # Return an error message if the product already exists
            return render_template('admin_dashboard.html', message="Product already exists")

        # save uploaded image file
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename))

        new_product = Product(product_id=str(uuid.uuid4())[:20], product_name=name, product_description=description,
                              price=price, quantity_pu=quantity, product_image=filename, category_id=category, discount=discount)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin'))

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


if __name__ == '__main__':
    app.run(debug=True)
