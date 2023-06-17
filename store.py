from main import app, db
from models import *
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash,render_template,request,session, redirect, url_for
import uuid
import logging
from werkzeug.utils import secure_filename
import os
import stripe
from datetime import date
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@app.route("/<string:name>")
def invalid(name):
    return render_template('404.html')


#routing the app to the login page.(In this case this is my starting page for now)
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


#routing to createuser page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        fn=request.form['first_name']
        ln=request.form['last_name']
        usr=request.form['loginid']
        cno=request.form['contact_num']
        pwd=request.form['passwd']

        error = None

        if not (fn and ln and usr and cno and pwd):
            error = "Failure: Credentials are not filled in properly."
            return render_template('register.html', error)

        usr_exists = Customer.query.filter_by(loginid=usr).first()
        if usr_exists:
            error = "Failure: Username already exists"  
            return render_template('register.html', error)
                
        c_id = str(uuid.uuid4())[:8]
        new_customer = Customer(customer_id=c_id, first_name=fn, last_name=ln, loginid=usr, passwd=pwd, contact_num=cno)
        db.session.add(new_customer)
        db.session.commit()
        flash('User successfully created')
        return redirect(url_for('login'))
    
    return render_template('register.html', error = None)



@app.route('/user_info/<login_id>')
def user_info(login_id):
    customer = Customer.query.filter_by(loginid=login_id).first()
    if customer is None:
        flash("Customer not found.")
        return redirect(url_for('index'))  # Redirect to the home page or an error page

    return render_template('user_info.html', customer=customer)



@app.route("/category")
def displayCategory():
    category_id = request.args.get('categoryId')
    category = Category.query.filter_by(category_id=category_id).first()
    products = db.session.query(Product).join(Category, Product.category == Category.category_id).filter(Category.category_id == category_id).all()
    return render_template('category.html', products=products, category = category)

@app.route("/productDescription")
def productDescription():
    product_id = request.args.get('productId')
    productData = Product.query.filter_by(product_id=product_id).first()
    category = Category.query.filter_by(category_id=productData.category).first()
    return render_template("product.html", productdata=productData, category = category)

# # Define a function to update product quantity when a cart product is added
# def update_product_quantity_on_cart_product_add(mapper, connection, target):
#     product_id = target.product_id
#     quantity = target.quantity
#     product = Product.query.get(product_id)
#     product.quantity_pu -= quantity
#
# # Register the trigger function to execute when a CartProduct object is added
# event.listen(CartProduct, 'after_insert', update_product_quantity_on_cart_product_add)

@app.route("/addToCart", methods=["POST"])
def addToCart():
    if 'username' not in session:
        return redirect(url_for('login'))

    else:
        product_id = request.args.get('productId')
        cust_id = session['customer_id']
    
        productData = Product.query.filter_by(product_id=product_id).first()
        # Check if the product is already in the cart
        cart = Cart.query.filter_by(customer=cust_id).first()

        if not cart:
            # If the customer doesn't have a cart, create a new one
            cart = Cart(cart_id=str(uuid.uuid4())[:20], customer=cust_id, nop=0, total_price=0)

        # Check if the product is already in the cart
        cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()

        if cart_product:
            cart_product.quantity += int(request.form['quantity'])
            cart.nop += int(request.form['quantity'])  
            #productData.quantity_pu -= int(request.form['quantity'])
        else:
            cart_product = CartProduct(cart_id=cart.cart_id, product_id=product_id, quantity=int(request.form['quantity']))
            cart.nop += int(request.form['quantity'])
            db.session.add(cart_product)
            #productData.quantity_pu -= int(request.form['quantity'])

        # Update the total price
        product = Product.query.get(product_id)
        cart.total_price += product.price * int(request.form['quantity'])

        db.session.add(cart) # Move this line before event registration
        db.session.commit()

        msg = "Added successfully"
        return redirect(url_for('cart'))


    
@app.route("/cart")
def cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cust_id = session['customer_id']
    cust = Customer.query.filter_by(customer_id=cust_id).first()

    #products = (
    #    db.session.query(Product, CartProduct.quantity)
    #    .join(CartProduct)
    #    .join(Cart)
    #    .filter(Cart.customer == cust_id)
    #    .all()
    #    )
    products = (
        db.session.query(ProductView)
        .filter(Cart.customer == cust_id)
        .all()
        )

    cart = Cart.query.filter_by(customer=cust_id).first()
    if cart:
        total_price = cart.total_price
        nop = cart.nop
    else:
        return render_template("cart.html", totalPrice=0, noOfItems=0)
    return render_template("cart.html", products=products, totalPrice=total_price, noOfItems=nop)



@app.route("/addToWishlist", methods=["POST"])
def addToWishlist():
    if 'username' not in session:
        return redirect(url_for('login'))

    else:
        product_id = request.args.get('productId')
        cust_id = session['customer_id']
    
        productData = Product.query.filter_by(product_id=product_id).first()
        # Check if the product is already in the cart
        wishList = WishList.query.filter_by(customer=cust_id).first()

        if not wishList:
            # If the customer doesn't have a cart, create a new one
            wishList = WishList(list_id=str(uuid.uuid4())[:20], customer=cust_id, nop=0)

        # Check if the product is already in the cart
        wish_product = WishProduct.query.filter_by(list_id=wishList.list_id, product_id=product_id).first()

        if wish_product:
            wishList.nop += 1
        else:
            wish_product = WishProduct(list_id=wishList.list_id, product_id=product_id)
            wishList.nop += 1
            db.session.add(wish_product)


        db.session.add(wishList) # Move this line before event registration
        db.session.commit()

        msg = "Added successfully"
        return redirect(url_for('wishlist'))


    
@app.route("/wishlist")
def wishlist():
    if 'username' not in session:
        return redirect(url_for('login'))

    cust_id = session['customer_id']
    cust = Customer.query.filter_by(customer_id=cust_id).first()

    products = (
       db.session.query(Product, WishProduct.quantity)
       .join(Product)
       .join(WishList)
       .filter(WishList.customer == cust_id)
       .all()
       )

    wishlist = WishList.query.filter_by(customer=cust_id).first()
    if wishlist:
        nop = wishlist.nop
    else:
        return render_template("wishlist.html", noOfItems=0)
    return render_template("wishlist.html", products=products, noOfItems=nop)





@app.route("/removeFromCart", methods=["POST"])
def removeFromCart():
    if 'username' not in session:
        return redirect(url_for('login'))

    usr = session['username']
    cust_id = session['customer_id']
    product_id = request.form['productId']

    cust = Customer.query.filter_by(loginid=usr).first()
    cart = Cart.query.filter_by(customer=cust_id).first()

    try:
        cart_product = CartProduct.query.filter_by(cart_id=cart.cart_id, product_id=product_id).first()
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
    
    address = request.form.get('address')
    cust_id = session['customer_id']
    cart = Cart.query.filter_by(customer=cust_id).first()
    total_price = cart.total_price
    nop = cart.nop
    # products = (
    #     db.session.query(Product, CartProduct.quantity)
    #     .join(CartProduct)
    #     .join(Cart)
    #     .filter(Cart.customer == cust_id)
    #     .all()
    #     )

    products = (
        db.session.query(ProductView)
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
                    'currency': 'pkr',
                    'product_data': {
                        'name': product.product_name,
                        'images': [product.product_image],
                    },
                    'unit_amount': product.price * 100,
                },
                'quantity': cart_product.quantity,
            })

        session['line_items'] = line_items
        session['description'] = 'Order from Kuchu Muchu'
        session['amount'] = total_price
        session['nop'] = nop
        session['cart_id'] = cart.cart_id
        session['customer_email'] = Customer.query.get(cust_id).loginid
        session['customer_address'] = address
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        
        return redirect(checkout_session.url, code=303)
    
    return render_template('checkout.html', totalPrice=total_price, noOfItems=nop, stripe_public_key=os.environ.get('STRIPE_PUBLISHABLE_KEY'), cart_items = products)

@app.route('/success')
def success():
    description = session['description']
    amount = session['amount']
    nop = session['nop']
    cart_id = session['cart_id']
    cust_id = session['customer_id']
    address = session['customer_address'] 
    
    # Update cart and commit changes
    cart = Cart.query.filter_by(cart_id=cart_id).first()
    cart.nop = 0
    cart.total_price = 0
    db.session.commit()
    
    # Create an Aboutorder entry
    order = Order(customer_id=cust_id, order_date = date.today(), shipper_id = 123, address = address)
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
        orderItems = OrderItem(unit_price=quantity * product.price, discount=0, quantity=quantity, product_id=product.product_id, order_id=order.order_id)
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