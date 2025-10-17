"""
Main entry point and REPL for CoreDB.

This module provides an interactive SQL shell for executing SQL commands.
"""

import sys
import os
from typing import List, Optional
from pathlib import Path

from .storage import StorageManager
from .executor import QueryExecutor
from .parser import SQLParser
from .exceptions import CoreDBError


class CoreDBShell:
    """
    Interactive SQL shell for CoreDB.
    
    Provides a command-line interface for executing SQL statements
    and managing the database.
    """
    
    def __init__(self, db_path: str = "coredb_data"):
        """
        Initialize the shell.
        
        Args:
            db_path: Path to database directory
        """
        self.storage = StorageManager(db_path)
        self.executor = QueryExecutor(self.storage)
        self.running = True
        self.history: List[str] = []
    
    def run(self) -> None:
        """Start the interactive shell."""
        print("CoreDB v0.1.0 - A minimal SQL database engine")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 50)
        
        while self.running:
            try:
                # Get user input (support multiline)
                sql_lines = []
                line = input("coredb> ").strip()
                
                if not line:
                    continue
                
                # Add to history
                self.history.append(line)
                
                # Handle special commands
                if self._handle_special_commands(line):
                    continue
                
                # Check for multiline SQL (ends with backslash)
                if line.endswith('\\'):
                    sql_lines.append(line[:-1])  # Remove backslash
                    while True:
                        continuation = input("    -> ").strip()
                        if continuation.endswith('\\'):
                            sql_lines.append(continuation[:-1])
                        else:
                            sql_lines.append(continuation)
                            break
                    sql = ' '.join(sql_lines)
                else:
                    sql = line
                
                # Execute SQL
                self._execute_sql(sql)
                
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _handle_special_commands(self, line: str) -> bool:
        """
        Handle special shell commands.
        
        Args:
            line: Input line
            
        Returns:
            True if command was handled, False otherwise
        """
        command = line.lower().strip()
        
        if command in ['quit', 'exit', 'q']:
            self.running = False
            print("Goodbye!")
            return True
        
        elif command == 'help':
            self._show_help()
            return True
        
        elif command == 'tables':
            self._list_tables()
            return True
        
        elif command.startswith('describe '):
            table_name = line[9:].strip()
            self._describe_table(table_name)
            return True
        
        elif command == 'history':
            self._show_history()
            return True
        
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            return True
        
        elif command.startswith('load '):
            filename = line[5:].strip()
            self._load_sql_file(filename)
            return True
        
        return False
    
    def _execute_sql(self, sql: str) -> None:
        """
        Execute a SQL statement.
        
        Args:
            sql: SQL statement to execute
        """
        try:
            result = self.executor.execute_raw_sql(sql)
            
            if result.success:
                if result.data is not None:
                    # Display query results
                    self._display_results(result.data)
                else:
                    # Display success message
                    print(f"✓ {result.message}")
                    if result.affected_rows > 0:
                        print(f"  ({result.affected_rows} row(s) affected)")
            else:
                print(f"✗ {result.message}")
                
        except CoreDBError as e:
            print(f"✗ {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    def _display_results(self, data: List[dict]) -> None:
        """
        Display query results in a formatted table.
        
        Args:
            data: List of row dictionaries
        """
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
        
        print(f"\n({len(data)} row(s) returned)")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
CoreDB Commands:
  SQL Statements:
    CREATE TABLE table_name (col1 TYPE [PRIMARY KEY] [REFERENCES table(col)], ...)
    INSERT INTO table_name VALUES (val1, val2, ...)
    SELECT * FROM table_name [WHERE condition]
    SELECT * FROM table1 JOIN table2 ON table1.id = table2.foreign_id
    UPDATE table_name SET col1=val1 [WHERE condition]
    DELETE FROM table_name [WHERE condition]
  
  JOIN Types:
    INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN
  
  Shell Commands:
    help          - Show this help
    tables        - List all tables
    describe <table> - Show table structure
    history       - Show command history
    clear         - Clear screen
    load <file>   - Execute SQL from file
    quit/exit     - Exit the shell
  
  Multiline Queries:
    End lines with \\ to continue on next line
  
  Data Types:
    INT, TEXT, FLOAT, BOOLEAN
  
  Examples:
    CREATE TABLE users (id INT PRIMARY KEY, name TEXT);
    CREATE TABLE orders (id INT PRIMARY KEY, user_id INT REFERENCES users(id));
    SELECT u.name, o.id FROM users u JOIN orders o ON u.id = o.user_id;
    SELECT * FROM users \\
        WHERE age > 20 \\
        ORDER BY name;
        """
        print(help_text)
    
    def _list_tables(self) -> None:
        """List all tables in the database."""
        tables = self.executor.list_tables()
        if not tables:
            print("No tables found.")
            return
        
        print("Tables:")
        for table_name in tables:
            info = self.executor.get_table_info(table_name)
            if info:
                print(f"  {table_name} ({info['row_count']} rows)")
    
    def _describe_table(self, table_name: str) -> None:
        """
        Show table structure.
        
        Args:
            table_name: Name of table to describe
        """
        info = self.executor.get_table_info(table_name)
        if not info:
            print(f"Table '{table_name}' not found.")
            return
        
        print(f"Table: {info['name']}")
        print("Columns:")
        
        for col in info['columns']:
            constraints = []
            if col['primary_key']:
                constraints.append("PRIMARY KEY")
            if not col['nullable']:
                constraints.append("NOT NULL")
            
            constraint_str = f" ({', '.join(constraints)})" if constraints else ""
            print(f"  {col['name']} {col['type']}{constraint_str}")
        
        print(f"Rows: {info['row_count']}")
    
    def _show_history(self) -> None:
        """Show command history."""
        if not self.history:
            print("No command history.")
            return
        
        print("Command History:")
        for i, cmd in enumerate(self.history[-10:], 1):  # Show last 10 commands
            print(f"  {i:2d}. {cmd}")
    
    def _load_sql_file(self, filename: str) -> None:
        """
        Execute SQL statements from a file.
        
        Args:
            filename: Path to SQL file
        """
        try:
            file_path = Path(filename)
            if not file_path.exists():
                print(f"File not found: {filename}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                print("File is empty.")
                return
            
            print(f"Executing SQL from {filename}...")
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                print(f"\n[{i}/{len(statements)}] {statement}")
                self._execute_sql(statement)
                
        except Exception as e:
            print(f"Error loading file: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CoreDB - A minimal SQL database engine")
    parser.add_argument(
        '--db-path', 
        default='coredb_data',
        help='Path to database directory (default: coredb_data)'
    )
    parser.add_argument(
        '--file', '-f',
        help='Execute SQL from file and exit'
    )
    parser.add_argument(
        '--command', '-c',
        help='Execute SQL command and exit'
    )
    
    args = parser.parse_args()
    
    # Create shell
    shell = CoreDBShell(args.db_path)
    
    # Handle command-line execution
    if args.file:
        shell._load_sql_file(args.file)
        return
    
    if args.command:
        shell._execute_sql(args.command)
        return
    
    # Start interactive shell
    shell.run()


if __name__ == "__main__":
    main()
