--7/5/23
ALTER TABLE cart_products add column quantity INTEGER;
select * from customer;
select * from product;

UPDATE product SET product_image = 'ExampleProduct.JPG';

INSERT INTO category (category_id, category_name, description)
VALUES ('C001', 'Electronics', 'Products related to electronic devices and gadgets');

INSERT INTO supplier(supplier_id, first_name, last_name)
VALUES('ABC123','FN','LN');

INSERT INTO product (product_id, quantity_pu, product_name, stock_units,product_image, unit_weight, discount, reorder_level, product_description, supplier_ID, category_id) 
VALUES ('12345', 10, 'Example Product', 100,'ExampleProduct.JPG', 0.5,  0.1, 5, 'This is an example product', 'ABC123', 'C001');
DELETE FROM product;
