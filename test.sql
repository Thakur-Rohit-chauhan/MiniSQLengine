CREATE TABLE customers (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price FLOAT,
    category_id INT REFERENCES categories(id),
    supplier_id INT REFERENCES suppliers(id)
);

CREATE TABLE categories (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE suppliers (
    id INT PRIMARY KEY,
    name TEXT NOT NULL,
    contact_email TEXT,
    phone TEXT
);

CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    order_date TEXT,
    status TEXT,
    total_amount FLOAT
);

CREATE TABLE order_items (
    id INT PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price FLOAT,
    total_price FLOAT
);
INSERT INTO categories (id, name, description)
VALUES (1, 'Electronics', 'Devices and gadgets');
INSERT INTO categories (id, name, description)
VALUES (2, 'Furniture', 'Home and office furniture');
INSERT INTO categories (id, name, description)
VALUES (3, 'Clothing', 'Men and Women apparel');
INSERT INTO suppliers (id, name, contact_email, phone)
VALUES (1, 'TechWorld Inc.', 'contact@techworld.com', '9876543210');
INSERT INTO suppliers (id, name, contact_email, phone)
VALUES (2, 'FurniCraft', 'sales@furnicraft.com', '9123456789');
INSERT INTO suppliers (id, name, contact_email, phone)
VALUES (3, 'FashionHub', 'info@fashionhub.com', '9988776655');
INSERT INTO customers (id, name, email, phone, address)
VALUES (1, 'Alice Johnson', 'alice@example.com', '9000000001', '123 Maple Street');
INSERT INTO customers (id, name, email, phone, address)
VALUES (2, 'Bob Smith', 'bob@example.com', '9000000002', '45 Elm Avenue');
INSERT INTO customers (id, name, email, phone, address)
VALUES (3, 'Carol White', 'carol@example.com', '9000000003', '78 Oak Drive');
INSERT INTO products (id, name, description, price, category_id, supplier_id)
VALUES (1, 'Smartphone', 'Android smartphone with 128GB storage', 35000.00, 1, 1);
INSERT INTO products (id, name, description, price, category_id, supplier_id)
VALUES (2, 'Office Chair', 'Ergonomic mesh chair', 8500.00, 2, 2);
INSERT INTO products (id, name, description, price, category_id, supplier_id)
VALUES (3, 'T-Shirt', 'Cotton round-neck T-shirt', 1200.00, 3, 3);
INSERT INTO orders (id, customer_id, order_date, status, total_amount)
VALUES (1, 1, '2025-10-15', 'Processing', 36200.00);
INSERT INTO orders (id, customer_id, order_date, status, total_amount)
VALUES (2, 2, '2025-10-16', 'Delivered', 8500.00);
INSERT INTO orders (id, customer_id, order_date, status, total_amount)
VALUES (3, 3, '2025-10-17', 'Pending', 1200.00);
INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, total_price)
VALUES (1, 1, 1, 1, 35000.00, 35000.00);
INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, total_price)
VALUES (2, 1, 3, 1, 1200.00, 1200.00);
INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, total_price)
VALUES (3, 2, 2, 1, 8500.00, 8500.00);

SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    o.order_date,
    o.status,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id;


SELECT 
    p.name AS product_name,
    c.name AS category_name,
    s.name AS supplier_name,
    p.price
FROM products p
JOIN categories c ON p.category_id = c.id
JOIN suppliers s ON p.supplier_id = s.id;


SELECT 
    oi.id AS order_item_id,
    o.id AS order_id,
    c.name AS customer_name,
    p.name AS product_name,
    oi.quantity,
    oi.unit_price,
    oi.total_price
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
JOIN products p ON oi.product_id = p.id
JOIN customers c ON o.customer_id = c.id
ORDER BY o.id;


SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.total_amount > 10000;


SELECT 
    p.name AS product_name,
    p.price,
    s.name AS supplier_name
FROM products p
JOIN suppliers s ON p.supplier_id = s.id
WHERE s.name = 'TechWorld Inc.';


SELECT DISTINCT 
    c.name AS customer_name,
    cat.name AS category
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
JOIN categories cat ON p.category_id = cat.id
WHERE cat.name = 'Electronics';


SELECT 
    c.name AS customer_name,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.name
ORDER BY total_spent DESC;

SELECT 
    cat.name AS category_name,
    COUNT(DISTINCT o.id) AS total_orders
FROM categories cat
JOIN products p ON cat.id = p.category_id
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
GROUP BY cat.name;

SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    o.order_date,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date BETWEEN '2025-10-15' AND '2025-10-16';

SELECT 
    c.name AS category_name,
    p.name AS product_name,
    MAX(p.price) AS highest_price
FROM categories c
JOIN products p ON c.id = p.category_id
GROUP BY c.name, p.name
ORDER BY highest_price DESC;
