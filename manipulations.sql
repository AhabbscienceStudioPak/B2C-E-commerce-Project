--7/5/23
ALTER TABLE cart_products add column quantity INTEGER;
select * from customer;
select * from product;
DELETE FROM product;
DELETE FROM supplier;
delete from category;

INSERT INTO supplier(supplier_id, first_name, last_name)
VALUES('electro','ahabb','sheraz');
INSERT INTO supplier(supplier_id, first_name, last_name)
VALUES('TOYSTORE','Mr','Glass'),
('Clothers','MIAN','HARNANDEZ');

INSERT INTO category (category_id, category_name, description)
VALUES ('C001', 'Electronics', 'Products related to electronic devices and gadgets');
update category set description = 'Products related to clothes and acesories' where category_id = 'C002'; 

INSERT INTO category (category_id, category_name, description)
VALUES ('C002', 'Clothes', 'Products related to clothongs and accessories!!');

INSERT INTO category (category_id, category_name, description)
VALUES ('C003', 'Toys', 'Products related to toys and fun!!');


--15/5/23
INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier_ID, category_id) 
VALUES ('10000', 10, 'Mouse 2.0','mouse.JPG', 20,  400, 'A good camera fella', 'electro', 'C001'),
('10001', 10, 'Camera 1466FGFG','camera.JPG', 400,  15000, 'the OG camera', 'electro', 'C001'),
('10002',10,'Small adapters 2.0','smalladapters.JPG',50,800, 'adapters for everything ','electro','C001');

INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier_ID, category_id)
VALUES ('10010', 10, 'Blue shirt','blueshirt.JPG', 5,  800, 'A good shirt mister', 'Clothers', 'C002'),
('10012', 10, 'Black Pants','blackpant.JPG', 10,  4000, 'the OG pant is back', 'Clothers', 'C002');



INSERT INTO product (product_id, quantity_pu, product_name,product_image, unit_weight, price, product_description, supplier_ID, category_id)
VALUES ('10020', 10, 'Car','car.JPEG', 5,  40, 'A good car', 'TOYSTORE', 'C003'),
('10022', 10, 'Teddy bear','bear.JPEG', 10,  200, 'the OG BEAR', 'TOYSTORE', 'C003');
