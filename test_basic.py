#!/usr/bin/env python3
"""
Basic tests for CoreDB functionality.

This script runs basic tests to verify that CoreDB is working correctly.
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
from coredb.exceptions import CoreDBError, TableNotFoundError, DuplicateTableError


def test_lexer_parser():
    """Test the lexer and parser."""
    print("Testing lexer and parser...")
    
    # Test CREATE TABLE parsing
    sql = "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)"
    parser = SQLParser(sql)
    ast = parser.parse()
    
    from coredb.parser import CreateTableStatement
    assert isinstance(ast, CreateTableStatement)
    assert ast.table_name == "users"
    assert len(ast.columns) == 3
    assert ast.columns[0].name == "id"
    assert ast.columns[0].primary_key == True
    
    print("✓ Lexer and parser tests passed")


def test_storage():
    """Test the storage engine."""
    print("Testing storage engine...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        
        # Test table creation
        from coredb.types import Table, Column, DataType
        
        table = Table(
            name="test_table",
            columns=[
                Column("id", DataType.INT, primary_key=True),
                Column("name", DataType.TEXT),
                Column("age", DataType.INT)
            ]
        )
        
        storage.create_table(table)
        
        # Test table retrieval
        retrieved_table = storage.get_table("test_table")
        assert retrieved_table is not None
        assert retrieved_table.name == "test_table"
        assert len(retrieved_table.columns) == 3
        
        # Test data insertion
        rows = [
            {"id": 1, "name": "Alice", "age": 25},
            {"id": 2, "name": "Bob", "age": 30}
        ]
        
        affected_rows = storage.insert_data("test_table", rows)
        assert affected_rows == 2
        
        # Test data selection
        data = storage.select_data("test_table")
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"
        
        print("✓ Storage engine tests passed")


def test_executor():
    """Test the query executor."""
    print("Testing query executor...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        # Test CREATE TABLE
        result = executor.execute_raw_sql(
            "CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)"
        )
        assert result.success
        
        # Test INSERT
        result = executor.execute_raw_sql(
            "INSERT INTO users VALUES (1, 'Alice', 25)"
        )
        assert result.success
        assert result.affected_rows == 1
        
        # Test SELECT
        result = executor.execute_raw_sql("SELECT * FROM users")
        assert result.success
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0]["name"] == "Alice"
        
        # Test UPDATE
        result = executor.execute_raw_sql(
            "UPDATE users SET age = 26 WHERE name = 'Alice'"
        )
        assert result.success
        
        # Verify update
        result = executor.execute_raw_sql("SELECT * FROM users")
        assert result.data[0]["age"] == 26
        
        print("✓ Query executor tests passed")


def test_error_handling():
    """Test error handling."""
    print("Testing error handling...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = StorageManager(temp_dir)
        executor = QueryExecutor(storage)
        
        # Test table not found
        result = executor.execute_raw_sql("SELECT * FROM nonexistent")
        assert not result.success
        assert "not found" in result.message.lower()
        
        # Test duplicate table creation
        executor.execute_raw_sql("CREATE TABLE test (id INT)")
        result = executor.execute_raw_sql("CREATE TABLE test (id INT)")
        assert not result.success
        assert "already exists" in result.message.lower()
        
        print("✓ Error handling tests passed")


def run_all_tests():
    """Run all tests."""
    print("🧪 Running CoreDB Tests")
    print("=" * 30)
    
    try:
        test_lexer_parser()
        test_storage()
        test_executor()
        test_error_handling()
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
