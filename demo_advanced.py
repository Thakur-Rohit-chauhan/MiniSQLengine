#!/usr/bin/env python3
"""
Advanced CoreDB Demo - Foreign Keys, JOINs, and Multiline Queries
"""

import sys
import os
from pathlib import Path
import tempfile

# Add the coredb package to the path
sys.path.insert(0, str(Path(__file__).parent))

from coredb.storage import StorageManager
from coredb.executor import QueryExecutor


def run_advanced_demo():
    """Run an advanced demo showcasing foreign keys, JOINs, and multiline queries."""
    print("🚀 CoreDB Advanced Demo - Foreign Keys, JOINs & Multiline Queries")
    print("=" * 65)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        print("\n1. 📋 Creating Normalized Database Schema")
        print("-" * 40)
        
        # Create users table
        result = executor.execute_raw_sql("""
            CREATE TABLE users (
                id INT PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        print(f"✓ Users table: {result.message}")
        
        # Create products table
        result = executor.execute_raw_sql("""
            CREATE TABLE products (
                id INT PRIMARY KEY,
                name TEXT,
                price FLOAT
            )
        """)
        print(f"✓ Products table: {result.message}")
        
        # Create orders table with foreign keys
        result = executor.execute_raw_sql("""
            CREATE TABLE orders (
                id INT PRIMARY KEY,
                user_id INT REFERENCES users(id),
                product_id INT REFERENCES products(id),
                quantity INT
            )
        """)
        print(f"✓ Orders table with foreign keys: {result.message}")
        
        print("\n2. 📝 Inserting Sample Data")
        print("-" * 30)
        
        # Insert users
        users = [
            (1, 'Alice Johnson', 'alice@example.com'),
            (2, 'Bob Smith', 'bob@example.com'),
            (3, 'Charlie Brown', 'charlie@example.com')
        ]
        
        for user in users:
            result = executor.execute_raw_sql(f"INSERT INTO users VALUES {user}")
            print(f"✓ User: {user[1]}")
        
        # Insert products
        products = [
            (1, 'Laptop', 999.99),
            (2, 'Mouse', 29.99),
            (3, 'Keyboard', 79.99),
            (4, 'Monitor', 299.99)
        ]
        
        for product in products:
            result = executor.execute_raw_sql(f"INSERT INTO products VALUES {product}")
            print(f"✓ Product: {product[1]} (${product[2]})")
        
        # Insert orders
        orders = [
            (1, 1, 1, 1),  # Alice ordered 1 Laptop
            (2, 1, 2, 2),  # Alice ordered 2 Mice
            (3, 2, 3, 1),  # Bob ordered 1 Keyboard
            (4, 3, 1, 1),  # Charlie ordered 1 Laptop
            (5, 3, 4, 2)   # Charlie ordered 2 Monitors
        ]
        
        for order in orders:
            result = executor.execute_raw_sql(f"INSERT INTO orders VALUES {order}")
            print(f"✓ Order: User {order[1]} ordered {order[3]}x Product {order[2]}")
        
        print("\n3. 🔒 Testing Foreign Key Constraints")
        print("-" * 35)
        
        # Try to insert invalid foreign key
        result = executor.execute_raw_sql("INSERT INTO orders VALUES (6, 999, 1, 1)")
        if not result.success:
            print(f"✓ Foreign key constraint enforced: {result.message}")
        
        print("\n4. 🔗 Testing JOIN Operations")
        print("-" * 30)
        
        # Simple INNER JOIN
        print("\n📊 INNER JOIN - Users and their orders:")
        result = executor.execute_raw_sql("""
            SELECT u.name, p.name as product, o.quantity
            FROM users u
            INNER JOIN orders o ON u.id = o.user_id
            INNER JOIN products p ON o.product_id = p.id
        """)
        
        if result.success and result.data:
            for row in result.data:
                print(f"   {row['u.name']} ordered {row['quantity']}x {row['product']}")
        else:
            print(f"   Query failed: {result.message}")
        
        # LEFT JOIN to show all users
        print("\n📊 LEFT JOIN - All users and their order counts:")
        result = executor.execute_raw_sql("""
            SELECT u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
        """)
        
        if result.success and result.data:
            for row in result.data:
                print(f"   {row['u.name']}: {row.get('order_count', 0)} orders")
        
        # Complex query with WHERE clause
        print("\n📊 Complex Query - High-value orders:")
        result = executor.execute_raw_sql("""
            SELECT u.name, p.name as product, o.quantity, p.price
            FROM users u
            INNER JOIN orders o ON u.id = o.user_id
            INNER JOIN products p ON o.product_id = p.id
            WHERE p.price > 100
        """)
        
        if result.success and result.data:
            for row in result.data:
                total = row['quantity'] * row['price']
                print(f"   {row['u.name']}: {row['quantity']}x {row['product']} = ${total:.2f}")
        
        print("\n5. 📄 Testing Multiline Queries")
        print("-" * 32)
        
        # Demonstrate multiline query capability
        print("✓ Multiline queries are supported in the interactive shell")
        print("  End lines with \\ to continue on the next line")
        print("  Example:")
        print("  coredb> SELECT u.name, p.name \\")
        print("      -> FROM users u \\")
        print("      -> INNER JOIN orders o ON u.id = o.user_id \\")
        print("      -> INNER JOIN products p ON o.product_id = p.id;")
        
        print("\n6. 🎯 Database Normalization Benefits")
        print("-" * 35)
        
        print("✓ Data is stored in normalized form (3NF)")
        print("✓ Foreign key constraints ensure data integrity")
        print("✓ JOINs allow flexible data retrieval")
        print("✓ No data duplication across tables")
        print("✓ Easy to maintain and update")
        
        print("\n🎉 Advanced Demo Completed!")
        print("\nTo try CoreDB interactively, run:")
        print("python3 -m coredb.main")


if __name__ == "__main__":
    run_advanced_demo()
