CREATE TABLE admin (
    admin_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    login_id VARCHAR(20) UNIQUE
);

CREATE TABLE supplier (
    supplier_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20)
);

CREATE TABLE customer (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    loginid VARCHAR(10) UNIQUE,
    passwd VARCHAR(20) UNIQUE,
    contact_num VARCHAR
);

CREATE TABLE category (
    category_id VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(20),
    description VARCHAR(50)
);

CREATE TABLE cart (
    cart_id VARCHAR(20) PRIMARY KEY,
    nop INTEGER,
    total_price INTEGER,
    customer VARCHAR(20),
    FOREIGN KEY (customer) REFERENCES customer (customer_id)
);

CREATE TABLE product (
    product_id VARCHAR(20) PRIMARY KEY,
    quantity_pu INTEGER,
    product_name VARCHAR(20),
    product_image VARCHAR,
    price INTEGER,
    product_description VARCHAR(30),
    unit_weight INTEGER,
    supplier VARCHAR(20),
    category VARCHAR(20),
    FOREIGN KEY (supplier) REFERENCES supplier (supplier_id),
    FOREIGN KEY (category) REFERENCES category (category_id)
);

CREATE TABLE cart_products (
    cart_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    PRIMARY KEY (cart_id, product_id),
    FOREIGN KEY (cart_id) REFERENCES cart (cart_id),
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE wishlist (
    list_id VARCHAR(20) PRIMARY KEY,
    nop INTEGER,
    customer VARCHAR(20),
    FOREIGN KEY (customer) REFERENCES customer (customer_id)
);

CREATE TABLE wish_products (
    list_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    PRIMARY KEY (list_id, product_id),
    FOREIGN KEY (list_id) REFERENCES wishlist (list_id),
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL,
    shipped_date DATE,
    shipper_id INTEGER,
    customer_id TEXT,
    address VARCHAR(100),
    FOREIGN KEY (customer_id) REFERENCES customer (customer_id)
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id TEXT,
    unit_price FLOAT NOT NULL,
    quantity INTEGER NOT NULL,
    discount FLOAT NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);

CREATE TABLE shipper (
    shipper_id VARCHAR(40) PRIMARY KEY,
    phone VARCHAR(20),
    company_name VARCHAR(20),
    order_id INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

CREATE VIEW product_view AS
SELECT p.*, c.customer, cp.quantity
FROM product p
JOIN cart_products cp ON p.product_id = cp.product_id
JOIN cart c ON cp.cart_id = c.cart_id;


CREATE VIEW order_info AS
SELECT
    o.order_id,
    o.order_date,
    o.shipped_date,
    o.shipper_id,
    o.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    o.address,
    oi.product_id,
    p.product_name,
    oi.unit_price,
    oi.quantity
FROM
    orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN customer c ON o.customer_id = c.customer_id
    JOIN product p ON oi.product_id = p.product_id;
	

CREATE OR REPLACE FUNCTION update_product_quantity_on_cart_product_add()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE product
    SET quantity_pu = quantity_pu - NEW.quantity
    WHERE product_id = NEW.product_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_product_quantity_trigger
AFTER INSERT ON cart_products
FOR EACH ROW
EXECUTE FUNCTION update_product_quantity_on_cart_product_add();

INSERT INTO category (category_id, category_name, description)
VALUES ('C001', 'Electronics', 'Products related to electronic devices and gadgets');

INSERT INTO category (category_id, category_name, description)
VALUES ('C002', 'Clothes', 'Products related to clothongs and accessories');

INSERT INTO category (category_id, category_name, description)
VALUES ('C003', 'Miscellaneous', 'Miscellaneous products');

insert into supplier values('ABC123','Ali','Khan');

INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier, category) 
VALUES ('10000', 10, 'Mouse 2.0','mouse.JPG', 20,  400, 'A good camera fella', 'ABC123', 'C001'),
('10001', 10, 'Camera 1466FGFG','camera.JPG', 400,  15000, 'the OG camera', 'ABC123', 'C001'),
('10002',10,'Small adapters 2.0','smalladapters.JPG',50,800, 'adapters for everything ','ABC123','C001');

INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier, category)
VALUES ('10010', 10, 'Blue shirt','blueshirt.JPG', 5,  800, 'A good shirt mister', 'ABC123', 'C002'),
('10012', 10, 'Black Pants','blackpant.JPG', 10,  4000, 'the OG pant is back', 'ABC123', 'C002');

INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier, category)
VALUES ('10020', 10, 'Car','car.JPEG', 5,  40, 'Toy car', 'ABC123', 'C003'),
('10022', 10, 'Teddy bear','bear.JPEG', 10,  200, 'the OG BEAR', 'ABC123', 'C003');


CREATE VIEW myview AS
(
	SELECT p.product_name,p.quantity_pu, s.supplier_id, s.first_name,s.last_name
	FROM product p JOIN supplier s 
	ON p.supplier_id = s.supplier_id
)

CREATE OR REPLACE FUNCTION count_it()
RETURNS INTEGER
LANGUAGE plpgsql
AS
$$
DECLARE
pcount int;
BEGIN
SELECT count(*) INTO pcount FROM product;
RETURN pcount;
END;
$$;

INSERT INTO admin(admin_id,first_name,last_name,loginid)
VALUES('A001','SOHAIB','NASIR','A001');