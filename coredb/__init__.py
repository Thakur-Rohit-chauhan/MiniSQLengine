"""
CoreDB - A minimal SQL database engine implementation in Python.

This package provides a simple but functional SQL database management system
that supports basic SQL operations like CREATE TABLE, INSERT, SELECT, UPDATE, and DELETE.
"""

__version__ = "0.1.0"
__author__ = "CoreDB Team"

from .types import Column, Table, Schema
from .storage import StorageManager
from .lexer import SQLTokenizer
from .parser import SQLParser
from .executor import QueryExecutor

__all__ = [
    "Column",
    "Table", 
    "Schema",
    "StorageManager",
    "SQLTokenizer",
    "SQLParser",
    "QueryExecutor"
]
