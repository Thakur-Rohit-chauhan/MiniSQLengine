"""
Custom exceptions for the CoreDB SQL engine.
"""


class CoreDBError(Exception):
    """Base exception for all CoreDB errors."""
    pass


class SQLSyntaxError(CoreDBError):
    """Raised when SQL syntax is invalid."""
    
    def __init__(self, message: str, position: int = None):
        super().__init__(message)
        self.position = position


class TableNotFoundError(CoreDBError):
    """Raised when a table doesn't exist."""
    
    def __init__(self, table_name: str):
        super().__init__(f"Table '{table_name}' not found")
        self.table_name = table_name


class ColumnNotFoundError(CoreDBError):
    """Raised when a column doesn't exist in a table."""
    
    def __init__(self, column_name: str, table_name: str):
        super().__init__(f"Column '{column_name}' not found in table '{table_name}'")
        self.column_name = column_name
        self.table_name = table_name


class TypeMismatchError(CoreDBError):
    """Raised when data type doesn't match column type."""
    
    def __init__(self, expected_type: str, actual_value, column_name: str):
        super().__init__(
            f"Type mismatch: expected {expected_type}, got {type(actual_value).__name__} "
            f"for column '{column_name}'"
        )
        self.expected_type = expected_type
        self.actual_value = actual_value
        self.column_name = column_name


class DuplicateTableError(CoreDBError):
    """Raised when trying to create a table that already exists."""
    
    def __init__(self, table_name: str):
        super().__init__(f"Table '{table_name}' already exists")
        self.table_name = table_name


class StorageError(CoreDBError):
    """Raised when storage operations fail."""
    pass
