from main import db

class MyView(db.Model):
    __tablename__ = 'myview'

    product_name = db.Column(db.String(20), primary_key = True)
    quantity_pu = db.Column(db.Integer)
    supplier_id= db.Column(db.String(20))
    first_name = db.Column(db.String(20))
    last_name  = db.Column(db.String(20))


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
    customer = db.Column(db.ForeignKey('customer.customer_id'))

    
class CartProduct(db.Model):
    __tablename__ = 'cart_products'
    
    cart_id = db.Column(db.String(20), db.ForeignKey('cart.cart_id'), primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.product_id'), primary_key=True)
    quantity = db.Column(db.Integer) 



class WishList(db.Model):
    __tablename__ = 'wishlist'

    list_id = db.Column(db.String(20), primary_key=True)
    nop = db.Column(db.Integer)
    customer = db.Column(db.ForeignKey('customer.customer_id'))

    
class WishProduct(db.Model):
    __tablename__ = 'wish_products'
    
    list_id = db.Column(db.String(20), db.ForeignKey('wishlist.list_id'), primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.product_id'), primary_key=True)
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
    loginid = db.Column(db.String(10), unique = True)
    passwd = db.Column(db.String(20), unique=True)
    contact_num = db.Column(db.String)



class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.Date, nullable=False)
    shipped_date = db.Column(db.Date)
    shipper_id = db.Column(db.Integer, db.ForeignKey('shipper.shipper_id'))
    customer_id = db.Column(db.String(20), db.ForeignKey('customer.customer_id'))
    address = db.Column(db.String(100))


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('product.product_id'), primary_key=True)
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Float, nullable=False)



class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.String(20), primary_key=True)
    quantity_pu = db.Column(db.Integer)
    product_name = db.Column(db.String(20))
    product_image = db.Column(db.String)
    price = db.Column(db.Integer)
    product_description = db.Column(db.String(30))
    unit_weight = db.Column(db.Integer)
    supplier = db.Column(db.ForeignKey('supplier.supplier_id'))
    category = db.Column(db.ForeignKey('category.category_id'))

class ProductView(db.Model):
    __tablename__ = 'product_view'
    
    product_id = db.Column(db.String(20), primary_key=True)
    quantity_pu = db.Column(db.Integer)
    product_name = db.Column(db.String(20))
    product_image = db.Column(db.String)
    price = db.Column(db.Integer)
    product_description = db.Column(db.String(30))
    category = db.Column(db.ForeignKey('category.category_id'))
    quantity = db.Column(db.Integer)
    customer = db.Column(db.ForeignKey('customer.customer_id'))


class OrderInfo(db.Model):
    __tablename__ = 'order_info'

    order_id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.Date, nullable=False)
    shipped_date = db.Column(db.Date)
    shipper_id = db.Column(db.Integer, db.ForeignKey('shipper.shipper_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    customer_name = db.Column(db.String(40))
    address = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    product_name = db.Column(db.String(20))
    unit_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    product = db.relationship("Product")



class Shipper(db.Model):
    __tablename__ = 'shipper'

    shipper_id = db.Column(db.String(40), primary_key=True)
    phone = db.Column(db.String(20))
    company_name = db.Column(db.String(20))
    aboutorder = db.Column(db.ForeignKey('Order.order_id'))

class Supplier(db.Model):
    __tablename__ = 'supplier'

    supplier_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
