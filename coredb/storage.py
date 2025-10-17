"""
Storage engine for CoreDB.

This module handles data persistence and schema management using JSON files
for simplicity and portability.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .types import Column, Table, Schema, DataType
from .exceptions import (
    TableNotFoundError, 
    DuplicateTableError, 
    StorageError,
    ColumnNotFoundError
)


class StorageManager:
    """
    Manages data storage and schema persistence for CoreDB.
    
    Uses JSON files for data storage:
    - Schema is stored in 'schema.json'
    - Table data is stored in separate files: '{table_name}.json'
    """
    
    def __init__(self, db_path: str = "coredb_data"):
        """
        Initialize storage manager.
        
        Args:
            db_path: Directory path for storing database files
        """
        self.db_path = Path(db_path)
        self.schema_file = self.db_path / "schema.json"
        self.schema = Schema()
        
        # Create database directory if it doesn't exist
        self.db_path.mkdir(exist_ok=True)
        
        # Load existing schema if available
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load schema from disk if it exists."""
        if self.schema_file.exists():
            try:
                with open(self.schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    self.schema = Schema.from_dict(schema_data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise StorageError(f"Failed to load schema: {e}")
    
    def _save_schema(self) -> None:
        """Save schema to disk."""
        try:
            with open(self.schema_file, 'w', encoding='utf-8') as f:
                json.dump(self.schema.to_dict(), f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to save schema: {e}")
    
    def _get_table_file(self, table_name: str) -> Path:
        """Get the file path for a table's data."""
        return self.db_path / f"{table_name}.json"
    
    def _load_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Load table data from disk."""
        table_file = self._get_table_file(table_name)
        if not table_file.exists():
            return []
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError, IOError) as e:
            raise StorageError(f"Failed to load table data for '{table_name}': {e}")
    
    def _save_table_data(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """Save table data to disk."""
        table_file = self._get_table_file(table_name)
        try:
            with open(table_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to save table data for '{table_name}': {e}")
    
    def create_table(self, table: Table) -> None:
        """
        Create a new table.
        
        Args:
            table: Table object to create
            
        Raises:
            DuplicateTableError: If table already exists
            StorageError: If storage operation fails
        """
        if self.schema.get_table(table.name):
            raise DuplicateTableError(table.name)
        
        # Add table to schema
        self.schema.add_table(table)
        
        # Save schema
        self._save_schema()
        
        # Create empty data file
        self._save_table_data(table.name, [])
    
    def drop_table(self, table_name: str) -> bool:
        """
        Drop a table and its data.
        
        Args:
            table_name: Name of table to drop
            
        Returns:
            True if table was dropped, False if it didn't exist
        """
        table = self.schema.get_table(table_name)
        if not table:
            return False
        
        # Remove from schema
        self.schema.drop_table(table_name)
        
        # Save schema
        self._save_schema()
        
        # Remove data file
        table_file = self._get_table_file(table_name)
        if table_file.exists():
            try:
                table_file.unlink()
            except OSError as e:
                raise StorageError(f"Failed to delete table file for '{table_name}': {e}")
        
        return True
    
    def get_table(self, table_name: str) -> Optional[Table]:
        """
        Get a table with its data loaded.
        
        Args:
            table_name: Name of table to retrieve
            
        Returns:
            Table object with data loaded, or None if not found
        """
        table = self.schema.get_table(table_name)
        if not table:
            return None
        
        # Load table data
        data = self._load_table_data(table_name)
        table.data = data
        
        return table
    
    def insert_data(self, table_name: str, rows: List[Dict[str, Any]]) -> int:
        """
        Insert data into a table.
        
        Args:
            table_name: Name of table to insert into
            rows: List of row data dictionaries
            
        Returns:
            Number of rows inserted
            
        Raises:
            TableNotFoundError: If table doesn't exist
            StorageError: If storage operation fails
        """
        table = self.get_table(table_name)
        if not table:
            raise TableNotFoundError(table_name)
        
        # Validate and insert rows
        inserted_count = 0
        for row in rows:
            try:
                # Validate foreign key constraints
                self._validate_foreign_keys(table, row)
                table.insert_row(row)
                inserted_count += 1
            except ValueError as e:
                raise StorageError(f"Failed to insert row: {e}")
        
        # Save updated data
        self._save_table_data(table_name, table.data)
        
        return inserted_count
    
    def select_data(self, table_name: str, columns: Optional[List[str]] = None, 
                   where_clause: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Select data from a table.
        
        Args:
            table_name: Name of table to select from
            columns: List of column names to select (None for all)
            where_clause: WHERE clause for filtering (not implemented yet)
            
        Returns:
            List of row dictionaries
            
        Raises:
            TableNotFoundError: If table doesn't exist
        """
        table = self.get_table(table_name)
        if not table:
            raise TableNotFoundError(table_name)
        
        # Filter columns if specified
        if columns and '*' not in columns:
            # Validate column names
            for col_name in columns:
                if not table.get_column(col_name):
                    raise ColumnNotFoundError(col_name, table_name)
            
            # Select only specified columns
            result = []
            for row in table.data:
                filtered_row = {col: row.get(col) for col in columns}
                result.append(filtered_row)
            return result
        
        return table.data.copy()
    
    def update_data(self, table_name: str, set_clause: Dict[str, Any], 
                   where_clause: Optional[Any] = None) -> int:
        """
        Update data in a table.
        
        Args:
            table_name: Name of table to update
            set_clause: Dictionary of column -> value mappings
            where_clause: WHERE clause for filtering (not implemented yet)
            
        Returns:
            Number of rows updated
            
        Raises:
            TableNotFoundError: If table doesn't exist
            StorageError: If storage operation fails
        """
        table = self.get_table(table_name)
        if not table:
            raise TableNotFoundError(table_name)
        
        # Validate column names
        for col_name in set_clause.keys():
            if not table.get_column(col_name):
                raise ColumnNotFoundError(col_name, table_name)
        
        # Update rows
        updated_count = 0
        for row in table.data:
            # For now, update all rows (WHERE clause not implemented)
            for col_name, new_value in set_clause.items():
                col = table.get_column(col_name)
                if col:
                    try:
                        row[col_name] = col.validate_value(new_value)
                        updated_count += 1
                    except ValueError as e:
                        raise StorageError(f"Failed to update column '{col_name}': {e}")
        
        # Save updated data
        self._save_table_data(table_name, table.data)
        
        return updated_count
    
    def delete_data(self, table_name: str, where_clause: Optional[Any] = None) -> int:
        """
        Delete data from a table.
        
        Args:
            table_name: Name of table to delete from
            where_clause: WHERE clause for filtering (not implemented yet)
            
        Returns:
            Number of rows deleted
            
        Raises:
            TableNotFoundError: If table doesn't exist
        """
        table = self.get_table(table_name)
        if not table:
            raise TableNotFoundError(table_name)
        
        # For now, delete all rows (WHERE clause not implemented)
        deleted_count = len(table.data)
        table.data.clear()
        
        # Save updated data
        self._save_table_data(table_name, table.data)
        
        return deleted_count
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names."""
        return list(self.schema.tables.keys())
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return self.schema.get_table(table_name) is not None
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a table.
        
        Args:
            table_name: Name of table
            
        Returns:
            Dictionary with table information or None if not found
        """
        table = self.schema.get_table(table_name)
        if not table:
            return None
        
        return {
            'name': table.name,
            'columns': [
                {
                    'name': col.name,
                    'type': col.data_type.value,
                    'nullable': col.nullable,
                    'primary_key': col.primary_key
                }
                for col in table.columns
            ],
            'row_count': len(self._load_table_data(table_name))
        }
    
    def backup_database(self, backup_path: str) -> None:
        """
        Create a backup of the entire database.
        
        Args:
            backup_path: Path to save the backup
            
        Raises:
            StorageError: If backup operation fails
        """
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy schema
            import shutil
            shutil.copy2(self.schema_file, backup_dir / "schema.json")
            
            # Copy all table data files
            for table_name in self.get_table_names():
                table_file = self._get_table_file(table_name)
                if table_file.exists():
                    shutil.copy2(table_file, backup_dir / f"{table_name}.json")
            
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to create backup: {e}")
    
    def restore_database(self, backup_path: str) -> None:
        """
        Restore database from a backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Raises:
            StorageError: If restore operation fails
        """
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            raise StorageError(f"Backup directory not found: {backup_path}")
        
        try:
            # Clear existing data
            for table_file in self.db_path.glob("*.json"):
                table_file.unlink()
            
            # Copy schema
            backup_schema = backup_dir / "schema.json"
            if backup_schema.exists():
                import shutil
                shutil.copy2(backup_schema, self.schema_file)
                self._load_schema()
            
            # Copy table data files
            for table_name in self.get_table_names():
                backup_table_file = backup_dir / f"{table_name}.json"
                if backup_table_file.exists():
                    import shutil
                    shutil.copy2(backup_table_file, self._get_table_file(table_name))
            
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to restore backup: {e}")
    
    def _validate_foreign_keys(self, table: Table, row: Dict[str, Any]) -> None:
        """
        Validate foreign key constraints for a row.
        
        Args:
            table: Table being inserted into
            row: Row data to validate
            
        Raises:
            StorageError: If foreign key constraint is violated
        """
        for col in table.columns:
            if col.foreign_key and col.name in row:
                fk_value = row[col.name]
                
                # Skip NULL values (they're allowed unless column is NOT NULL)
                if fk_value is None:
                    continue
                
                # Check if referenced table exists
                ref_table = self.get_table(col.foreign_key.referenced_table)
                if not ref_table:
                    raise StorageError(
                        f"Foreign key constraint violation: Referenced table "
                        f"'{col.foreign_key.referenced_table}' not found"
                    )
                
                # Check if referenced column exists
                ref_col = ref_table.get_column(col.foreign_key.referenced_column)
                if not ref_col:
                    raise StorageError(
                        f"Foreign key constraint violation: Referenced column "
                        f"'{col.foreign_key.referenced_column}' not found in table "
                        f"'{col.foreign_key.referenced_table}'"
                    )
                
                # Check if the foreign key value exists in the referenced table
                found = False
                for ref_row in ref_table.data:
                    if ref_row.get(ref_col.name) == fk_value:
                        found = True
                        break
                
                if not found:
                    raise StorageError(
                        f"Foreign key constraint violation: Value '{fk_value}' not found "
                        f"in referenced table '{col.foreign_key.referenced_table}' "
                        f"column '{col.foreign_key.referenced_column}'"
                    )
