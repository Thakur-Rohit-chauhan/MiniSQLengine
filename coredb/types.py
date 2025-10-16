"""
Data types and schema definitions for CoreDB.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field


class DataType(Enum):
    """Supported SQL data types."""
    INT = "INT"
    TEXT = "TEXT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"


@dataclass
class Column:
    """Represents a database column with name and type."""
    
    name: str
    data_type: DataType
    nullable: bool = True
    primary_key: bool = False
    
    def __post_init__(self):
        """Validate column definition."""
        if not self.name or not self.name.strip():
            raise ValueError("Column name cannot be empty")
        
        # Convert string to DataType if needed
        if isinstance(self.data_type, str):
            try:
                self.data_type = DataType(self.data_type.upper())
            except ValueError:
                raise ValueError(f"Unsupported data type: {self.data_type}")
    
    def validate_value(self, value: Any) -> Any:
        """Validate and convert a value to match this column's type."""
        if value is None:
            if not self.nullable:
                raise ValueError(f"Column '{self.name}' cannot be NULL")
            return None
        
        if self.data_type == DataType.INT:
            try:
                return int(value)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert '{value}' to INT for column '{self.name}'")
        
        elif self.data_type == DataType.FLOAT:
            try:
                return float(value)
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert '{value}' to FLOAT for column '{self.name}'")
        
        elif self.data_type == DataType.TEXT:
            return str(value)
        
        elif self.data_type == DataType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert column to dictionary for serialization."""
        return {
            'name': self.name,
            'data_type': self.data_type.value,
            'nullable': self.nullable,
            'primary_key': self.primary_key
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        """Create column from dictionary."""
        return cls(
            name=data['name'],
            data_type=DataType(data['data_type']),
            nullable=data.get('nullable', True),
            primary_key=data.get('primary_key', False)
        )


@dataclass
class Table:
    """Represents a database table with columns and data."""
    
    name: str
    columns: List[Column] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate table definition."""
        if not self.name or not self.name.strip():
            raise ValueError("Table name cannot be empty")
        
        # Check for duplicate column names
        column_names = [col.name for col in self.columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError("Duplicate column names are not allowed")
        
        # Validate primary key constraints
        primary_keys = [col for col in self.columns if col.primary_key]
        if len(primary_keys) > 1:
            raise ValueError("Multiple primary keys are not supported")
    
    def get_column(self, name: str) -> Optional[Column]:
        """Get column by name."""
        for col in self.columns:
            if col.name.lower() == name.lower():
                return col
        return None
    
    def get_primary_key_column(self) -> Optional[Column]:
        """Get the primary key column if it exists."""
        for col in self.columns:
            if col.primary_key:
                return col
        return None
    
    def validate_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert a row of data."""
        validated_row = {}
        
        # Check for extra columns
        for key in row.keys():
            if not self.get_column(key):
                raise ValueError(f"Column '{key}' not found in table '{self.name}'")
        
        # Validate each column
        for col in self.columns:
            value = row.get(col.name)
            validated_row[col.name] = col.validate_value(value)
        
        return validated_row
    
    def insert_row(self, row: Dict[str, Any]) -> None:
        """Insert a validated row into the table."""
        validated_row = self.validate_row(row)
        
        # Check primary key constraint
        pk_col = self.get_primary_key_column()
        if pk_col:
            pk_value = validated_row[pk_col.name]
            if pk_value is not None:
                for existing_row in self.data:
                    if existing_row[pk_col.name] == pk_value:
                        raise ValueError(f"Primary key '{pk_value}' already exists")
        
        self.data.append(validated_row)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table to dictionary for serialization."""
        return {
            'name': self.name,
            'columns': [col.to_dict() for col in self.columns],
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create table from dictionary."""
        columns = [Column.from_dict(col_data) for col_data in data['columns']]
        return cls(
            name=data['name'],
            columns=columns,
            data=data.get('data', [])
        )


@dataclass
class Schema:
    """Represents a database schema with multiple tables."""
    
    tables: Dict[str, Table] = field(default_factory=dict)
    
    def add_table(self, table: Table) -> None:
        """Add a table to the schema."""
        if table.name in self.tables:
            raise ValueError(f"Table '{table.name}' already exists in schema")
        self.tables[table.name] = table
    
    def get_table(self, name: str) -> Optional[Table]:
        """Get table by name (case-insensitive)."""
        for table_name, table in self.tables.items():
            if table_name.lower() == name.lower():
                return table
        return None
    
    def drop_table(self, name: str) -> bool:
        """Drop a table from the schema."""
        table = self.get_table(name)
        if table:
            del self.tables[table.name]
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary for serialization."""
        return {
            'tables': {name: table.to_dict() for name, table in self.tables.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schema':
        """Create schema from dictionary."""
        schema = cls()
        for table_name, table_data in data['tables'].items():
            table = Table.from_dict(table_data)
            schema.tables[table_name] = table
        return schema
