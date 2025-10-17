#!/usr/bin/env python3
"""
Advanced tests for CoreDB functionality including foreign keys and JOINs.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add the coredb package to the path
sys.path.insert(0, str(Path(__file__).parent))

from coredb.storage import StorageManager
from coredb.executor import QueryExecutor
from coredb.parser import SQLParser
from coredb.exceptions import CoreDBError, StorageError


def test_foreign_keys():
    """Test foreign key constraints."""
    print("Testing foreign key constraints...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        # Create parent table
        result = executor.execute_raw_sql(
            "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)"
        )
        assert result.success
        
        # Create child table with foreign key
        result = executor.execute_raw_sql(
            "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id), product TEXT)"
        )
        assert result.success
        
        # Insert into parent table
        result = executor.execute_raw_sql(
            "INSERT INTO users VALUES (1, 'Alice')"
        )
        assert result.success
        
        # Insert into child table with valid foreign key
        result = executor.execute_raw_sql(
            "INSERT INTO orders VALUES (1, 1, 'Laptop')"
        )
        assert result.success
        
        # Try to insert into child table with invalid foreign key
        result = executor.execute_raw_sql(
            "INSERT INTO orders VALUES (2, 999, 'Mouse')"
        )
        assert not result.success
        assert "Foreign key constraint violation" in result.message
        
        print("✓ Foreign key tests passed")


def test_joins():
    """Test JOIN operations."""
    print("Testing JOIN operations...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        # Create tables
        executor.execute_raw_sql("CREATE TABLE users (id INT PRIMARY KEY, name TEXT)")
        executor.execute_raw_sql("CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, product TEXT)")
        
        # Insert data
        executor.execute_raw_sql("INSERT INTO users VALUES (1, 'Alice')")
        executor.execute_raw_sql("INSERT INTO users VALUES (2, 'Bob')")
        executor.execute_raw_sql("INSERT INTO orders VALUES (1, 1, 'Laptop')")
        executor.execute_raw_sql("INSERT INTO orders VALUES (2, 1, 'Mouse')")
        executor.execute_raw_sql("INSERT INTO orders VALUES (3, 2, 'Keyboard')")
        
        # Test INNER JOIN
        result = executor.execute_raw_sql(
            "SELECT u.name, o.product FROM users u INNER JOIN orders o ON u.id = o.user_id"
        )
        assert result.success
        assert len(result.data) == 3
        assert result.data[0]['name'] == 'Alice'
        
        # Test LEFT JOIN
        result = executor.execute_raw_sql(
            "SELECT u.name, o.product FROM users u LEFT JOIN orders o ON u.id = o.user_id"
        )
        assert result.success
        assert len(result.data) == 3  # Should include all users
        
        print("✓ JOIN tests passed")


def test_multiline_queries():
    """Test multiline query parsing."""
    print("Testing multiline query parsing...")
    
    # Test multiline CREATE TABLE
    multiline_sql = """
    CREATE TABLE products (
        id INT PRIMARY KEY,
        name TEXT,
        price FLOAT
    )
    """
    
    parser = SQLParser(multiline_sql.strip())
    ast = parser.parse()
    
    from coredb.parser import CreateTableStatement
    assert isinstance(ast, CreateTableStatement)
    assert ast.table_name == "products"
    assert len(ast.columns) == 3
    
    # Test multiline SELECT with JOIN
    multiline_select = """
    SELECT u.name, o.product 
    FROM users u 
    INNER JOIN orders o 
    ON u.id = o.user_id 
    WHERE u.name = 'Alice'
    """.strip()
    
    parser = SQLParser(multiline_select)
    ast = parser.parse()
    
    from coredb.parser import SelectStatement
    assert isinstance(ast, SelectStatement)
    assert len(ast.joins) == 1
    assert ast.joins[0].join_type == "INNER"
    
    print("✓ Multiline query tests passed")


def test_parser_foreign_keys():
    """Test parser foreign key syntax."""
    print("Testing parser foreign key syntax...")
    
    # Test foreign key parsing
    sql = "CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id))"
    parser = SQLParser(sql)
    ast = parser.parse()
    
    from coredb.parser import CreateTableStatement
    assert isinstance(ast, CreateTableStatement)
    assert ast.columns[1].foreign_key is not None
    assert ast.columns[1].foreign_key.referenced_table == "users"
    assert ast.columns[1].foreign_key.referenced_column == "id"
    
    print("✓ Parser foreign key tests passed")


def test_parser_joins():
    """Test parser JOIN syntax."""
    print("Testing parser JOIN syntax...")
    
    # Test INNER JOIN
    sql = "SELECT * FROM users u INNER JOIN orders o ON u.id = o.user_id"
    parser = SQLParser(sql)
    ast = parser.parse()
    
    from coredb.parser import SelectStatement
    assert isinstance(ast, SelectStatement)
    assert len(ast.joins) == 1
    assert ast.joins[0].join_type == "INNER"
    assert ast.joins[0].table_name == "orders"
    assert ast.joins[0].alias == "o"
    assert ast.joins[0].on_condition is not None
    
    # Test LEFT JOIN
    sql = "SELECT * FROM users LEFT JOIN orders ON users.id = orders.user_id"
    parser = SQLParser(sql)
    ast = parser.parse()
    
    assert len(ast.joins) == 1
    assert ast.joins[0].join_type == "LEFT"
    
    # Test FULL OUTER JOIN
    sql = "SELECT * FROM users FULL OUTER JOIN orders ON users.id = orders.user_id"
    parser = SQLParser(sql)
    ast = parser.parse()
    
    assert len(ast.joins) == 1
    assert ast.joins[0].join_type == "FULL OUTER"
    
    print("✓ Parser JOIN tests passed")


def run_advanced_demo():
    """Run an advanced demo with foreign keys and JOINs."""
    print("Running advanced demo...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        # Create normalized database schema
        print("\n1. Creating normalized database schema...")
        
        # Users table
        result = executor.execute_raw_sql("""
            CREATE TABLE users (
                id INT PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """)
        print(f"   Users table: {result.message}")
        
        # Products table
        result = executor.execute_raw_sql("""
            CREATE TABLE products (
                id INT PRIMARY KEY,
                name TEXT,
                price FLOAT
            )
        """)
        print(f"   Products table: {result.message}")
        
        # Orders table with foreign keys
        result = executor.execute_raw_sql("""
            CREATE TABLE orders (
                id INT PRIMARY KEY,
                user_id INT REFERENCES users(id),
                product_id INT REFERENCES products(id),
                quantity INT
            )
        """)
        print(f"   Orders table: {result.message}")
        
        # Insert sample data
        print("\n2. Inserting sample data...")
        
        users_data = [
            (1, 'Alice Johnson', 'alice@example.com'),
            (2, 'Bob Smith', 'bob@example.com'),
            (3, 'Charlie Brown', 'charlie@example.com')
        ]
        
        for user in users_data:
            result = executor.execute_raw_sql(f"INSERT INTO users VALUES {user}")
            print(f"   Inserted user: {result.message}")
        
        products_data = [
            (1, 'Laptop', 999.99),
            (2, 'Mouse', 29.99),
            (3, 'Keyboard', 79.99)
        ]
        
        for product in products_data:
            result = executor.execute_raw_sql(f"INSERT INTO products VALUES {product}")
            print(f"   Inserted product: {result.message}")
        
        orders_data = [
            (1, 1, 1, 1),  # Alice ordered 1 Laptop
            (2, 1, 2, 2),  # Alice ordered 2 Mice
            (3, 2, 3, 1),  # Bob ordered 1 Keyboard
            (4, 3, 1, 1)   # Charlie ordered 1 Laptop
        ]
        
        for order in orders_data:
            result = executor.execute_raw_sql(f"INSERT INTO orders VALUES {order}")
            print(f"   Inserted order: {result.message}")
        
        # Test foreign key constraint
        print("\n3. Testing foreign key constraint...")
        result = executor.execute_raw_sql("INSERT INTO orders VALUES (5, 999, 1, 1)")
        if not result.success:
            print(f"   ✓ Foreign key constraint works: {result.message}")
        
        # Test JOIN queries
        print("\n4. Testing JOIN queries...")
        
        # Simple INNER JOIN
        result = executor.execute_raw_sql("""
            SELECT u.name, p.name as product, o.quantity
            FROM users u
            INNER JOIN orders o ON u.id = o.user_id
            INNER JOIN products p ON o.product_id = p.id
        """)
        print(f"   INNER JOIN result ({len(result.data)} rows):")
        for row in result.data:
            print(f"     {row['name']} ordered {row['quantity']}x {row['product']}")
        
        # LEFT JOIN to show all users
        result = executor.execute_raw_sql("""
            SELECT u.name, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id, u.name
        """)
        print(f"   LEFT JOIN result (showing all users):")
        for row in result.data:
            print(f"     {row['name']}: {row.get('order_count', 0)} orders")
        
        print("\n🎉 Advanced demo completed!")


def run_all_advanced_tests():
    """Run all advanced tests."""
    print("🧪 Running CoreDB Advanced Tests")
    print("=" * 40)
    
    try:
        test_parser_foreign_keys()
        test_parser_joins()
        test_multiline_queries()
        test_foreign_keys()
        test_joins()
        
        print("\n🎉 All advanced tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CoreDB Advanced Tests")
    parser.add_argument('--demo', action='store_true', help='Run advanced demo')
    
    args = parser.parse_args()
    
    if args.demo:
        run_advanced_demo()
    else:
        success = run_all_advanced_tests()
        sys.exit(0 if success else 1)
