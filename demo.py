#!/usr/bin/env python3
"""
Demo script for CoreDB - A minimal SQL database engine.

This script demonstrates the basic functionality of CoreDB by creating
tables, inserting data, and running queries.
"""

import sys
import os
from pathlib import Path

# Add the coredb package to the path
sys.path.insert(0, str(Path(__file__).parent))

from coredb.storage import StorageManager
from coredb.executor import QueryExecutor
from coredb.parser import SQLParser
from coredb.exceptions import CoreDBError


def run_demo():
    """Run a demonstration of CoreDB functionality."""
    print("🚀 CoreDB Demo - A minimal SQL database engine")
    print("=" * 50)
    
    # Initialize storage and executor
    storage = StorageManager("demo_data")
    executor = QueryExecutor(storage)
    
    # Demo SQL statements
    demo_statements = [
        # Create tables
        "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT, email TEXT)",
        "CREATE TABLE products (id INT PRIMARY KEY, name TEXT, price FLOAT, in_stock BOOLEAN)",
        
        # Insert data
        "INSERT INTO users VALUES (1, 'Alice Johnson', 25, 'alice@example.com')",
        "INSERT INTO users VALUES (2, 'Bob Smith', 30, 'bob@example.com')",
        "INSERT INTO users VALUES (3, 'Charlie Brown', 35, 'charlie@example.com')",
        
        "INSERT INTO products VALUES (1, 'Laptop', 999.99, true)",
        "INSERT INTO products VALUES (2, 'Mouse', 29.99, true)",
        "INSERT INTO products VALUES (3, 'Keyboard', 79.99, false)",
        
        # Queries
        "SELECT * FROM users",
        "SELECT name, age FROM users WHERE age > 25",
        "SELECT * FROM products WHERE in_stock = true",
        "SELECT * FROM products WHERE price < 100",
        
        # Updates
        "UPDATE users SET age = 26 WHERE name = 'Alice Johnson'",
        "UPDATE products SET price = 949.99 WHERE name = 'Laptop'",
        
        # More queries after updates
        "SELECT * FROM users WHERE name = 'Alice Johnson'",
        "SELECT * FROM products WHERE name = 'Laptop'",
        
        # Delete
        "DELETE FROM products WHERE in_stock = false",
        "SELECT * FROM products",
    ]
    
    print("Executing demo SQL statements...\n")
    
    for i, sql in enumerate(demo_statements, 1):
        print(f"[{i:2d}] {sql}")
        
        try:
            result = executor.execute_raw_sql(sql)
            
            if result.success:
                if result.data is not None:
                    # Display query results
                    display_results(result.data)
                else:
                    print(f"✓ {result.message}")
                    if result.affected_rows > 0:
                        print(f"  ({result.affected_rows} row(s) affected)")
            else:
                print(f"✗ {result.message}")
                
        except CoreDBError as e:
            print(f"✗ {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
        
        print()
    
    print("Demo completed! 🎉")
    print("\nTo start the interactive shell, run:")
    print("python -m coredb.main")


def display_results(data):
    """Display query results in a formatted table."""
    if not data:
        print("(No rows returned)")
        return
    
    # Get column names
    columns = list(data[0].keys())
    
    # Calculate column widths
    col_widths = {}
    for col in columns:
        col_widths[col] = max(
            len(str(col)),  # Header width
            max(len(str(row.get(col, ''))) for row in data)  # Data width
        )
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print data rows
    for row in data:
        row_str = " | ".join(
            str(row.get(col, '')).ljust(col_widths[col]) 
            for col in columns
        )
        print(row_str)
    
    print(f"({len(data)} row(s) returned)")


if __name__ == "__main__":
    run_demo()
