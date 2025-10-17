"""
Query executor for CoreDB.

This module executes parsed SQL statements against the storage engine.
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from .parser import (
    ASTNode, CreateTableStatement, InsertStatement, SelectStatement,
    UpdateStatement, DeleteStatement, WhereClause, Condition
)
from .storage import StorageManager
from .types import Table, Column
from .exceptions import CoreDBError, TableNotFoundError, ColumnNotFoundError


@dataclass
class QueryResult:
    """Represents the result of a query execution."""
    
    success: bool
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    affected_rows: int = 0
    execution_time: float = 0.0
    
    def __str__(self) -> str:
        if self.success:
            if self.data is not None:
                return f"Query executed successfully. {len(self.data)} rows returned."
            else:
                return f"Query executed successfully. {self.affected_rows} rows affected."
        else:
            return f"Query failed: {self.message}"


class QueryExecutor:
    """
    Executes SQL statements against the storage engine.
    
    This class takes parsed AST nodes and executes them, returning
    results that can be displayed to the user.
    """
    
    def __init__(self, storage_manager: StorageManager):
        """
        Initialize query executor.
        
        Args:
            storage_manager: Storage manager instance
        """
        self.storage = storage_manager
    
    def execute(self, ast_node: ASTNode) -> QueryResult:
        """
        Execute a parsed SQL statement.
        
        Args:
            ast_node: Root AST node of the parsed SQL statement
            
        Returns:
            QueryResult with execution results
        """
        import time
        start_time = time.time()
        
        try:
            if isinstance(ast_node, CreateTableStatement):
                result = self._execute_create_table(ast_node)
            elif isinstance(ast_node, InsertStatement):
                result = self._execute_insert(ast_node)
            elif isinstance(ast_node, SelectStatement):
                result = self._execute_select(ast_node)
            elif isinstance(ast_node, UpdateStatement):
                result = self._execute_update(ast_node)
            elif isinstance(ast_node, DeleteStatement):
                result = self._execute_delete(ast_node)
            else:
                result = QueryResult(
                    success=False,
                    message=f"Unsupported statement type: {type(ast_node).__name__}"
                )
            
            result.execution_time = time.time() - start_time
            return result
            
        except CoreDBError as e:
            return QueryResult(
                success=False,
                message=str(e),
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Unexpected error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _execute_create_table(self, stmt: CreateTableStatement) -> QueryResult:
        """Execute CREATE TABLE statement."""
        # Convert AST columns to Table columns
        columns = []
        for col_def in stmt.columns:
            from .types import Column, DataType, ForeignKey
            
            # Create foreign key if specified
            foreign_key = None
            if col_def.foreign_key:
                foreign_key = ForeignKey(
                    column=col_def.name,
                    referenced_table=col_def.foreign_key.referenced_table,
                    referenced_column=col_def.foreign_key.referenced_column
                )
            
            column = Column(
                name=col_def.name,
                data_type=col_def.data_type,
                nullable=col_def.nullable,
                primary_key=col_def.primary_key,
                foreign_key=foreign_key
            )
            columns.append(column)
        
        # Create table
        table = Table(name=stmt.table_name, columns=columns)
        self.storage.create_table(table)
        
        return QueryResult(
            success=True,
            message=f"Table '{stmt.table_name}' created successfully",
            affected_rows=0
        )
    
    def _execute_insert(self, stmt: InsertStatement) -> QueryResult:
        """Execute INSERT INTO statement."""
        # Convert values to row dictionaries
        rows = []
        for value_list in stmt.values:
            if stmt.columns:
                # Column names specified
                if len(value_list) != len(stmt.columns):
                    raise ValueError(
                        f"Number of values ({len(value_list)}) doesn't match "
                        f"number of columns ({len(stmt.columns)})"
                    )
                row = dict(zip(stmt.columns, value_list))
            else:
                # No column names specified - need to get from table
                table = self.storage.get_table(stmt.table_name)
                if not table:
                    raise TableNotFoundError(stmt.table_name)
                
                if len(value_list) != len(table.columns):
                    raise ValueError(
                        f"Number of values ({len(value_list)}) doesn't match "
                        f"number of columns ({len(table.columns)})"
                    )
                
                row = {}
                for i, col in enumerate(table.columns):
                    row[col.name] = value_list[i]
            
            rows.append(row)
        
        # Insert rows
        affected_rows = self.storage.insert_data(stmt.table_name, rows)
        
        return QueryResult(
            success=True,
            message=f"Inserted {affected_rows} row(s) into '{stmt.table_name}'",
            affected_rows=affected_rows
        )
    
    def _execute_select(self, stmt: SelectStatement) -> QueryResult:
        """Execute SELECT statement."""
        # Handle JOINs if present
        if stmt.joins:
            data = self._execute_join(stmt)
        else:
            # Get data from single table
            data = self.storage.select_data(
                table_name=stmt.table_name,
                columns=stmt.columns if '*' not in stmt.columns else None
            )
            
            # Apply WHERE clause filtering
            if stmt.where_clause:
                data = self._apply_where_clause(data, stmt.where_clause, stmt.table_name)
        
        return QueryResult(
            success=True,
            message=f"Selected {len(data)} row(s)",
            data=data,
            affected_rows=len(data)
        )
    
    def _execute_update(self, stmt: UpdateStatement) -> QueryResult:
        """Execute UPDATE statement."""
        # For now, update all rows (WHERE clause filtering not implemented)
        affected_rows = self.storage.update_data(
            table_name=stmt.table_name,
            set_clause=stmt.set_clause,
            where_clause=stmt.where_clause
        )
        
        return QueryResult(
            success=True,
            message=f"Updated {affected_rows} row(s) in '{stmt.table_name}'",
            affected_rows=affected_rows
        )
    
    def _execute_delete(self, stmt: DeleteStatement) -> QueryResult:
        """Execute DELETE statement."""
        # For now, delete all rows (WHERE clause filtering not implemented)
        affected_rows = self.storage.delete_data(
            table_name=stmt.table_name,
            where_clause=stmt.where_clause
        )
        
        return QueryResult(
            success=True,
            message=f"Deleted {affected_rows} row(s) from '{stmt.table_name}'",
            affected_rows=affected_rows
        )
    
    def _apply_where_clause(self, data: List[Dict[str, Any]], 
                          where_clause: WhereClause, table_name: str) -> List[Dict[str, Any]]:
        """
        Apply WHERE clause filtering to data.
        
        Args:
            data: List of row dictionaries
            where_clause: WHERE clause to apply
            table_name: Name of table (for error messages)
            
        Returns:
            Filtered list of row dictionaries
        """
        if not where_clause.conditions:
            return data
        
        filtered_data = []
        
        for row in data:
            # Evaluate all conditions
            condition_results = []
            for condition in where_clause.conditions:
                result = self._evaluate_condition(row, condition, table_name)
                condition_results.append(result)
            
            # Apply logical operators
            if not condition_results:
                continue
            
            # Start with first condition result
            final_result = condition_results[0]
            
            # Apply operators between conditions
            for i, operator in enumerate(where_clause.operators):
                if i + 1 < len(condition_results):
                    next_result = condition_results[i + 1]
                    
                    if operator.upper() == 'AND':
                        final_result = final_result and next_result
                    elif operator.upper() == 'OR':
                        final_result = final_result or next_result
                    else:
                        raise ValueError(f"Unsupported logical operator: {operator}")
            
            # Include row if final result is True
            if final_result:
                filtered_data.append(row)
        
        return filtered_data
    
    def _evaluate_condition(self, row: Dict[str, Any], condition: Condition, 
                          table_name: str) -> bool:
        """
        Evaluate a single condition against a row.
        
        Args:
            row: Row data dictionary
            condition: Condition to evaluate
            table_name: Name of table (for error messages)
            
        Returns:
            Boolean result of condition evaluation
        """
        # Get column value
        if condition.column not in row:
            raise ColumnNotFoundError(condition.column, table_name)
        
        column_value = row[condition.column]
        condition_value = condition.value
        
        # Handle NULL comparisons
        if column_value is None or condition_value is None:
            if condition.operator == '=':
                return column_value is None and condition_value is None
            elif condition.operator == '!=':
                return column_value is not None or condition_value is not None
            else:
                # Other operators with NULL always return False
                return False
        
        # Perform comparison
        try:
            if condition.operator == '=':
                return column_value == condition_value
            elif condition.operator == '!=':
                return column_value != condition_value
            elif condition.operator == '<':
                return column_value < condition_value
            elif condition.operator == '>':
                return column_value > condition_value
            elif condition.operator == '<=':
                return column_value <= condition_value
            elif condition.operator == '>=':
                return column_value >= condition_value
            else:
                raise ValueError(f"Unsupported comparison operator: {condition.operator}")
        
        except TypeError as e:
            raise ValueError(
                f"Cannot compare {type(column_value).__name__} with "
                f"{type(condition_value).__name__} for column '{condition.column}': {e}"
            )
    
    def execute_raw_sql(self, sql: str) -> QueryResult:
        """
        Execute raw SQL string.
        
        Args:
            sql: SQL string to execute
            
        Returns:
            QueryResult with execution results
        """
        from .parser import SQLParser
        
        try:
            # Parse SQL
            parser = SQLParser(sql)
            ast_node = parser.parse()
            
            # Execute
            return self.execute(ast_node)
            
        except Exception as e:
            return QueryResult(
                success=False,
                message=f"Failed to execute SQL: {str(e)}"
            )
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a table."""
        return self.storage.get_table_info(table_name)
    
    def list_tables(self) -> List[str]:
        """Get list of all table names."""
        return self.storage.get_table_names()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return self.storage.table_exists(table_name)
    
    def _execute_join(self, stmt: SelectStatement) -> List[Dict[str, Any]]:
        """
        Execute a SELECT statement with JOINs.
        
        Args:
            stmt: SELECT statement with JOINs
            
        Returns:
            List of joined row dictionaries
        """
        # Get base table data
        base_table = self.storage.get_table(stmt.table_name)
        if not base_table:
            raise TableNotFoundError(stmt.table_name)
        
        base_data = base_table.data.copy()
        
        # Apply table alias if specified
        if stmt.table_alias:
            base_data = self._apply_table_alias(base_data, stmt.table_alias)
        
        # Process each JOIN
        for join in stmt.joins:
            # Get joined table data
            join_table = self.storage.get_table(join.table_name)
            if not join_table:
                raise TableNotFoundError(join.table_name)
            
            join_data = join_table.data.copy()
            
            # Apply table alias if specified
            if join.alias:
                join_data = self._apply_table_alias(join_data, join.alias)
            
            # Perform the join
            base_data = self._perform_join(
                base_data, join_data, join.join_type, join.on_condition
            )
        
        # Apply WHERE clause filtering
        if stmt.where_clause:
            base_data = self._apply_where_clause(base_data, stmt.where_clause, stmt.table_name)
        
        # Select columns if specified
        if stmt.columns and '*' not in stmt.columns:
            base_data = self._select_columns(base_data, stmt.columns)
        
        return base_data
    
    def _apply_table_alias(self, data: List[Dict[str, Any]], alias: str) -> List[Dict[str, Any]]:
        """
        Apply table alias to column names.
        
        Args:
            data: List of row dictionaries
            alias: Table alias
            
        Returns:
            Data with prefixed column names
        """
        aliased_data = []
        for row in data:
            aliased_row = {}
            for col_name, value in row.items():
                aliased_row[f"{alias}.{col_name}"] = value
            aliased_data.append(aliased_row)
        return aliased_data
    
    def _perform_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                     join_type: str, on_condition: Optional[Any]) -> List[Dict[str, Any]]:
        """
        Perform a JOIN operation between two datasets.
        
        Args:
            left_data: Left table data
            right_data: Right table data
            join_type: Type of join (INNER, LEFT, RIGHT, FULL OUTER)
            on_condition: JOIN condition
            
        Returns:
            Joined data
        """
        if not on_condition:
            # Cartesian product if no ON condition
            result = []
            for left_row in left_data:
                for right_row in right_data:
                    combined_row = {**left_row, **right_row}
                    result.append(combined_row)
            return result
        
        # Perform join based on condition
        result = []
        
        if join_type.upper() in ['INNER', 'INNER JOIN']:
            result = self._inner_join(left_data, right_data, on_condition)
        elif join_type.upper() in ['LEFT', 'LEFT JOIN', 'LEFT OUTER', 'LEFT OUTER JOIN']:
            result = self._left_join(left_data, right_data, on_condition)
        elif join_type.upper() in ['RIGHT', 'RIGHT JOIN', 'RIGHT OUTER', 'RIGHT OUTER JOIN']:
            result = self._right_join(left_data, right_data, on_condition)
        elif join_type.upper() in ['FULL', 'FULL OUTER', 'FULL OUTER JOIN']:
            result = self._full_outer_join(left_data, right_data, on_condition)
        else:
            # Default to INNER JOIN
            result = self._inner_join(left_data, right_data, on_condition)
        
        return result
    
    def _inner_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                   on_condition: Any) -> List[Dict[str, Any]]:
        """Perform INNER JOIN."""
        result = []
        for left_row in left_data:
            for right_row in right_data:
                if self._evaluate_join_condition(left_row, right_row, on_condition):
                    combined_row = {**left_row, **right_row}
                    result.append(combined_row)
        return result
    
    def _left_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                  on_condition: Any) -> List[Dict[str, Any]]:
        """Perform LEFT JOIN."""
        result = []
        for left_row in left_data:
            matched = False
            for right_row in right_data:
                if self._evaluate_join_condition(left_row, right_row, on_condition):
                    combined_row = {**left_row, **right_row}
                    result.append(combined_row)
                    matched = True
            
            # Add left row with NULL right values if no match
            if not matched:
                null_right_row = {col: None for col in right_data[0].keys() if right_data}
                combined_row = {**left_row, **null_right_row}
                result.append(combined_row)
        
        return result
    
    def _right_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                   on_condition: Any) -> List[Dict[str, Any]]:
        """Perform RIGHT JOIN."""
        result = []
        for right_row in right_data:
            matched = False
            for left_row in left_data:
                if self._evaluate_join_condition(left_row, right_row, on_condition):
                    combined_row = {**left_row, **right_row}
                    result.append(combined_row)
                    matched = True
            
            # Add right row with NULL left values if no match
            if not matched:
                null_left_row = {col: None for col in left_data[0].keys() if left_data}
                combined_row = {**null_left_row, **right_row}
                result.append(combined_row)
        
        return result
    
    def _full_outer_join(self, left_data: List[Dict[str, Any]], right_data: List[Dict[str, Any]], 
                        on_condition: Any) -> List[Dict[str, Any]]:
        """Perform FULL OUTER JOIN."""
        # Start with LEFT JOIN
        result = self._left_join(left_data, right_data, on_condition)
        
        # Add unmatched right rows
        for right_row in right_data:
            matched = False
            for left_row in left_data:
                if self._evaluate_join_condition(left_row, right_row, on_condition):
                    matched = True
                    break
            
            if not matched:
                null_left_row = {col: None for col in left_data[0].keys() if left_data}
                combined_row = {**null_left_row, **right_row}
                result.append(combined_row)
        
        return result
    
    def _evaluate_join_condition(self, left_row: Dict[str, Any], right_row: Dict[str, Any], 
                               condition: Any) -> bool:
        """
        Evaluate a JOIN condition between two rows.
        
        Args:
            left_row: Left table row
            right_row: Right table row
            condition: JOIN condition
            
        Returns:
            True if condition is satisfied
        """
        # Handle table.column syntax in JOIN conditions
        # Format: "table1.column1 = table2.column2"
        
        # Split the condition into left and right parts
        if condition.operator == '=':
            # For JOIN conditions, we need to match left.column with right.column
            left_col = condition.column
            right_col = condition.value
            
            # Get values from appropriate rows
            left_value = None
            right_value = None
            
            # Handle left side (table.column)
            if '.' in left_col:
                parts = left_col.split('.')
                if len(parts) == 2:
                    table_name, col_name = parts
                    # Check if this table alias matches our left row
                    if any(key.startswith(f"{table_name}.") for key in left_row.keys()):
                        left_value = left_row.get(f"{table_name}.{col_name}")
                    elif col_name in left_row:
                        left_value = left_row.get(col_name)
            else:
                left_value = left_row.get(left_col)
            
            # Handle right side (table.column)
            if '.' in right_col:
                parts = right_col.split('.')
                if len(parts) == 2:
                    table_name, col_name = parts
                    # Check if this table alias matches our right row
                    if any(key.startswith(f"{table_name}.") for key in right_row.keys()):
                        right_value = right_row.get(f"{table_name}.{col_name}")
                    elif col_name in right_row:
                        right_value = right_row.get(col_name)
            else:
                right_value = right_row.get(right_col)
            
            # Perform comparison
            return left_value == right_value
        
        # For other operators, use the original logic
        left_value = left_row.get(condition.column)
        right_value = right_row.get(condition.value)
        
        if condition.operator == '!=':
            return left_value != right_value
        else:
            # For other operators, try to compare
            try:
                if condition.operator == '<':
                    return left_value < right_value
                elif condition.operator == '>':
                    return left_value > right_value
                elif condition.operator == '<=':
                    return left_value <= right_value
                elif condition.operator == '>=':
                    return left_value >= right_value
            except TypeError:
                return False
        
        return False
    
    def _select_columns(self, data: List[Dict[str, Any]], columns: List[str]) -> List[Dict[str, Any]]:
        """
        Select specific columns from data.
        
        Args:
            data: List of row dictionaries
            columns: List of column names to select
            
        Returns:
            Data with only selected columns
        """
        if not data:
            return data
        
        result = []
        for row in data:
            selected_row = {}
            for col in columns:
                if col in row:
                    selected_row[col] = row[col]
                else:
                    # Handle table.column format
                    for key, value in row.items():
                        if key.endswith(f'.{col}') or key == col:
                            selected_row[col] = value
                            break
            result.append(selected_row)
        
        return result
