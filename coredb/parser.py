"""
SQL Parser for CoreDB.

This module provides parsing of SQL tokens into Abstract Syntax Tree (AST) nodes
that can be executed by the query executor.
"""

from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .lexer import SQLTokenizer, Token, TokenType
from .types import Column, DataType
from .exceptions import SQLSyntaxError


class ASTNode(ABC):
    """Base class for all AST nodes."""
    
    @abstractmethod
    def __str__(self) -> str:
        pass


@dataclass
class ColumnDefinition(ASTNode):
    """Represents a column definition in CREATE TABLE."""
    
    name: str
    data_type: DataType
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional['ForeignKeyDefinition'] = None
    
    def __str__(self) -> str:
        pk_str = " PRIMARY KEY" if self.primary_key else ""
        null_str = "" if self.nullable else " NOT NULL"
        fk_str = f" {self.foreign_key}" if self.foreign_key else ""
        return f"{self.name} {self.data_type.value}{pk_str}{null_str}{fk_str}"


@dataclass
class ForeignKeyDefinition(ASTNode):
    """Represents a foreign key definition in CREATE TABLE."""
    
    referenced_table: str
    referenced_column: str
    
    def __str__(self) -> str:
        return f"REFERENCES {self.referenced_table}({self.referenced_column})"


@dataclass
class CreateTableStatement(ASTNode):
    """Represents a CREATE TABLE statement."""
    
    table_name: str
    columns: List[ColumnDefinition]
    
    def __str__(self) -> str:
        cols_str = ", ".join(str(col) for col in self.columns)
        return f"CREATE TABLE {self.table_name} ({cols_str})"


@dataclass
class InsertStatement(ASTNode):
    """Represents an INSERT INTO statement."""
    
    table_name: str
    columns: Optional[List[str]] = None
    values: List[List[Any]] = None
    
    def __str__(self) -> str:
        cols_str = f" ({', '.join(self.columns)})" if self.columns else ""
        values_str = ", ".join(f"({', '.join(str(v) for v in row)})" for row in self.values)
        return f"INSERT INTO {self.table_name}{cols_str} VALUES {values_str}"


@dataclass
class JoinClause(ASTNode):
    """Represents a JOIN clause."""
    
    join_type: str  # 'INNER', 'LEFT', 'RIGHT', 'FULL'
    table_name: str
    alias: Optional[str] = None
    on_condition: Optional['Condition'] = None
    
    def __str__(self) -> str:
        alias_str = f" AS {self.alias}" if self.alias else ""
        on_str = f" ON {self.on_condition}" if self.on_condition else ""
        return f"{self.join_type} JOIN {self.table_name}{alias_str}{on_str}"


@dataclass
class SelectStatement(ASTNode):
    """Represents a SELECT statement."""
    
    columns: List[str]  # ['*'] for SELECT *
    table_name: str
    table_alias: Optional[str] = None
    joins: List[JoinClause] = None
    where_clause: Optional['WhereClause'] = None
    order_by: Optional[str] = None
    limit: Optional[int] = None
    
    def __post_init__(self):
        if self.joins is None:
            self.joins = []
    
    def __str__(self) -> str:
        cols_str = ", ".join(self.columns)
        alias_str = f" AS {self.table_alias}" if self.table_alias else ""
        joins_str = " ".join(str(join) for join in self.joins)
        where_str = f" WHERE {self.where_clause}" if self.where_clause else ""
        order_str = f" ORDER BY {self.order_by}" if self.order_by else ""
        limit_str = f" LIMIT {self.limit}" if self.limit else ""
        return f"SELECT {cols_str} FROM {self.table_name}{alias_str} {joins_str}{where_str}{order_str}{limit_str}"


@dataclass
class UpdateStatement(ASTNode):
    """Represents an UPDATE statement."""
    
    table_name: str
    set_clause: Dict[str, Any]  # column -> value mappings
    where_clause: Optional['WhereClause'] = None
    
    def __str__(self) -> str:
        set_str = ", ".join(f"{col} = {val}" for col, val in self.set_clause.items())
        where_str = f" WHERE {self.where_clause}" if self.where_clause else ""
        return f"UPDATE {self.table_name} SET {set_str}{where_str}"


@dataclass
class DeleteStatement(ASTNode):
    """Represents a DELETE statement."""
    
    table_name: str
    where_clause: Optional['WhereClause'] = None
    
    def __str__(self) -> str:
        where_str = f" WHERE {self.where_clause}" if self.where_clause else ""
        return f"DELETE FROM {self.table_name}{where_str}"


@dataclass
class WhereClause(ASTNode):
    """Represents a WHERE clause with conditions."""
    
    conditions: List['Condition']
    operators: List[str]  # 'AND', 'OR' operators between conditions
    
    def __str__(self) -> str:
        if not self.conditions:
            return ""
        
        result = str(self.conditions[0])
        for i, op in enumerate(self.operators):
            result += f" {op} {self.conditions[i + 1]}"
        return result


@dataclass
class Condition(ASTNode):
    """Represents a single condition in a WHERE clause."""
    
    column: str
    operator: str  # '=', '!=', '<', '>', '<=', '>='
    value: Any
    
    def __str__(self) -> str:
        if isinstance(self.value, str):
            value_str = f"'{self.value}'"
        else:
            value_str = str(self.value)
        return f"{self.column} {self.operator} {value_str}"


class SQLParser:
    """
    SQL parser that converts tokens into AST nodes.
    
    Supports the following SQL statements:
    - CREATE TABLE
    - INSERT INTO
    - SELECT
    - UPDATE
    - DELETE
    """
    
    def __init__(self, sql: str):
        """Initialize parser with SQL string."""
        self.tokenizer = SQLTokenizer(sql)
        self.tokens = self.tokenizer.get_tokens()
        self.position = 0
    
    def parse(self) -> ASTNode:
        """Parse the SQL statement and return the AST root node."""
        if not self.tokens:
            raise SQLSyntaxError("Empty SQL statement")
        
        # Skip leading whitespace/comments
        while (self.position < len(self.tokens) and 
               self.tokens[self.position].type in [TokenType.EOF]):
            self.position += 1
        
        if self.position >= len(self.tokens):
            raise SQLSyntaxError("No valid SQL statement found")
        
        # Parse based on first token
        first_token = self.tokens[self.position]
        
        if first_token.type == TokenType.CREATE:
            return self._parse_create_table()
        elif first_token.type == TokenType.INSERT:
            return self._parse_insert()
        elif first_token.type == TokenType.SELECT:
            return self._parse_select()
        elif first_token.type == TokenType.UPDATE:
            return self._parse_update()
        elif first_token.type == TokenType.DELETE:
            return self._parse_delete()
        else:
            raise SQLSyntaxError(
                f"Unexpected token: {first_token.type.value}",
                first_token.position
            )
    
    def _current_token(self) -> Optional[Token]:
        """Get current token without consuming it."""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    def _consume_token(self, expected_type: Optional[TokenType] = None) -> Optional[Token]:
        """Consume and return current token."""
        if self.position >= len(self.tokens):
            return None
        
        token = self.tokens[self.position]
        
        if expected_type and token.type != expected_type:
            raise SQLSyntaxError(
                f"Expected {expected_type.value}, got {token.type.value}",
                token.position
            )
        
        self.position += 1
        return token
    
    def _expect_token(self, expected_type: TokenType) -> Token:
        """Expect and consume a specific token type."""
        token = self._consume_token(expected_type)
        if not token:
            raise SQLSyntaxError(f"Expected {expected_type.value}, got EOF")
        return token
    
    def _parse_create_table(self) -> CreateTableStatement:
        """Parse CREATE TABLE statement."""
        # CREATE
        self._expect_token(TokenType.CREATE)
        
        # TABLE
        self._expect_token(TokenType.TABLE)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # (
        self._expect_token(TokenType.LEFT_PAREN)
        
        # column definitions
        columns = []
        while True:
            # column_name
            col_name_token = self._expect_token(TokenType.IDENTIFIER)
            col_name = col_name_token.value
            
            # data_type
            data_type_token = self._consume_token()
            if data_type_token.type not in [TokenType.INT, TokenType.TEXT, TokenType.FLOAT, TokenType.BOOLEAN]:
                raise SQLSyntaxError(
                    f"Expected data type, got {data_type_token.type.value}",
                    data_type_token.position
                )
            
            try:
                data_type = DataType(data_type_token.value.upper())
            except ValueError:
                raise SQLSyntaxError(
                    f"Unsupported data type: {data_type_token.value}",
                    data_type_token.position
                )
            
            # Optional constraints
            nullable = True
            primary_key = False
            foreign_key = None
            
            while self._current_token() and self._current_token().type in [
                TokenType.IDENTIFIER, TokenType.NOT, TokenType.REFERENCES
            ]:
                token = self._consume_token()
                if token.value.upper() == 'PRIMARY' and self._current_token() and self._current_token().value.upper() == 'KEY':
                    self._consume_token()  # consume 'KEY'
                    primary_key = True
                elif token.value.upper() == 'NOT' and self._current_token() and self._current_token().value.upper() == 'NULL':
                    self._consume_token()  # consume 'NULL'
                    nullable = False
                elif token.type == TokenType.REFERENCES:
                    # Parse foreign key: REFERENCES table(column)
                    ref_table_token = self._expect_token(TokenType.IDENTIFIER)
                    self._expect_token(TokenType.LEFT_PAREN)
                    ref_col_token = self._expect_token(TokenType.IDENTIFIER)
                    self._expect_token(TokenType.RIGHT_PAREN)
                    foreign_key = ForeignKeyDefinition(
                        referenced_table=ref_table_token.value,
                        referenced_column=ref_col_token.value
                    )
                    break  # Foreign key is always last constraint
            
            columns.append(ColumnDefinition(
                name=col_name,
                data_type=data_type,
                nullable=nullable,
                primary_key=primary_key,
                foreign_key=foreign_key
            ))
            
            # Check for comma or closing parenthesis
            if self._current_token() and self._current_token().type == TokenType.COMMA:
                self._consume_token()  # consume comma
            else:
                break
        
        # )
        self._expect_token(TokenType.RIGHT_PAREN)
        
        return CreateTableStatement(table_name=table_name, columns=columns)
    
    def _parse_insert(self) -> InsertStatement:
        """Parse INSERT INTO statement."""
        # INSERT
        self._expect_token(TokenType.INSERT)
        
        # INTO
        self._expect_token(TokenType.INTO)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # Optional column list
        columns = None
        if self._current_token() and self._current_token().type == TokenType.LEFT_PAREN:
            self._consume_token()  # consume (
            columns = []
            
            while True:
                col_token = self._expect_token(TokenType.IDENTIFIER)
                columns.append(col_token.value)
                
                if self._current_token() and self._current_token().type == TokenType.COMMA:
                    self._consume_token()  # consume comma
                else:
                    break
            
            self._expect_token(TokenType.RIGHT_PAREN)
        
        # VALUES
        self._expect_token(TokenType.VALUES)
        
        # Parse value lists
        values = []
        while True:
            # (
            self._expect_token(TokenType.LEFT_PAREN)
            
            # Parse values in this row
            row_values = []
            while True:
                value = self._parse_value()
                row_values.append(value)
                
                if self._current_token() and self._current_token().type == TokenType.COMMA:
                    self._consume_token()  # consume comma
                else:
                    break
            
            # )
            self._expect_token(TokenType.RIGHT_PAREN)
            values.append(row_values)
            
            # Check for more rows
            if self._current_token() and self._current_token().type == TokenType.COMMA:
                self._consume_token()  # consume comma
            else:
                break
        
        return InsertStatement(
            table_name=table_name,
            columns=columns,
            values=values
        )
    
    def _parse_select(self) -> SelectStatement:
        """Parse SELECT statement."""
        # SELECT
        self._expect_token(TokenType.SELECT)
        
        # column list
        columns = []
        if self._current_token() and self._current_token().type == TokenType.ASTERISK:
            self._consume_token()  # consume *
            columns = ['*']
        else:
            while True:
                # Handle table.column syntax
                col_parts = []
                col_token = self._expect_token(TokenType.IDENTIFIER)
                col_parts.append(col_token.value)
                
                # Check for table.column syntax
                if self._current_token() and self._current_token().type == TokenType.DOT:
                    self._consume_token()  # consume dot
                    col_token2 = self._expect_token(TokenType.IDENTIFIER)
                    col_parts.append(col_token2.value)
                    column = ".".join(col_parts)
                else:
                    column = col_parts[0]
                
                # Check for column alias (AS keyword or direct alias)
                if self._current_token() and self._current_token().type == TokenType.AS:
                    self._consume_token()  # consume AS
                    alias_token = self._expect_token(TokenType.IDENTIFIER)
                    column = f"{column} AS {alias_token.value}"
                elif (self._current_token() and 
                      self._current_token().type == TokenType.IDENTIFIER and
                      not self._current_token().value.upper() in ['FROM', 'WHERE', 'ORDER', 'GROUP', 'HAVING']):
                    # Direct alias without AS keyword
                    alias_token = self._consume_token()
                    column = f"{column} AS {alias_token.value}"
                
                columns.append(column)
                
                if self._current_token() and self._current_token().type == TokenType.COMMA:
                    self._consume_token()  # consume comma
                else:
                    break
        
        # FROM
        self._expect_token(TokenType.FROM)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # Optional table alias
        table_alias = None
        if self._current_token() and self._current_token().type == TokenType.AS:
            self._consume_token()  # consume AS
            alias_token = self._expect_token(TokenType.IDENTIFIER)
            table_alias = alias_token.value
        elif self._current_token() and self._current_token().type == TokenType.IDENTIFIER:
            # Alias without AS keyword
            alias_token = self._consume_token()
            table_alias = alias_token.value
        
        # Parse JOINs
        joins = []
        while self._current_token() and self._current_token().type in [
            TokenType.JOIN, TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL
        ]:
            join_clause = self._parse_join_clause()
            joins.append(join_clause)
        
        # Optional WHERE clause
        where_clause = None
        if self._current_token() and self._current_token().type == TokenType.WHERE:
            where_clause = self._parse_where_clause()
        
        return SelectStatement(
            columns=columns,
            table_name=table_name,
            table_alias=table_alias,
            joins=joins,
            where_clause=where_clause
        )
    
    def _parse_update(self) -> UpdateStatement:
        """Parse UPDATE statement."""
        # UPDATE
        self._expect_token(TokenType.UPDATE)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # SET
        self._expect_token(TokenType.SET)
        
        # Parse SET clause
        set_clause = {}
        while True:
            # column = value
            col_token = self._expect_token(TokenType.IDENTIFIER)
            column = col_token.value
            
            self._expect_token(TokenType.EQUALS)
            
            value = self._parse_value()
            set_clause[column] = value
            
            if self._current_token() and self._current_token().type == TokenType.COMMA:
                self._consume_token()  # consume comma
            else:
                break
        
        # Optional WHERE clause
        where_clause = None
        if self._current_token() and self._current_token().type == TokenType.WHERE:
            where_clause = self._parse_where_clause()
        
        return UpdateStatement(
            table_name=table_name,
            set_clause=set_clause,
            where_clause=where_clause
        )
    
    def _parse_delete(self) -> DeleteStatement:
        """Parse DELETE statement."""
        # DELETE
        self._expect_token(TokenType.DELETE)
        
        # FROM
        self._expect_token(TokenType.FROM)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # Optional WHERE clause
        where_clause = None
        if self._current_token() and self._current_token().type == TokenType.WHERE:
            where_clause = self._parse_where_clause()
        
        return DeleteStatement(
            table_name=table_name,
            where_clause=where_clause
        )
    
    def _parse_join_clause(self) -> JoinClause:
        """Parse a JOIN clause."""
        # Determine join type
        join_type = "INNER"  # default
        
        if self._current_token() and self._current_token().type in [
            TokenType.INNER, TokenType.LEFT, TokenType.RIGHT, TokenType.FULL
        ]:
            type_token = self._consume_token()
            join_type = type_token.value.upper()
            
            # Handle FULL OUTER JOIN
            if join_type == "FULL" and self._current_token() and self._current_token().type == TokenType.OUTER:
                self._consume_token()  # consume OUTER
                join_type = "FULL OUTER"
        
        # JOIN
        self._expect_token(TokenType.JOIN)
        
        # table_name
        table_name_token = self._expect_token(TokenType.IDENTIFIER)
        table_name = table_name_token.value
        
        # Optional table alias
        alias = None
        if self._current_token() and self._current_token().type == TokenType.AS:
            self._consume_token()  # consume AS
            alias_token = self._expect_token(TokenType.IDENTIFIER)
            alias = alias_token.value
        elif self._current_token() and self._current_token().type == TokenType.IDENTIFIER:
            # Alias without AS keyword
            alias_token = self._consume_token()
            alias = alias_token.value
        
        # Optional ON condition
        on_condition = None
        if self._current_token() and self._current_token().type == TokenType.ON:
            self._consume_token()  # consume ON
            on_condition = self._parse_condition()
        
        return JoinClause(
            join_type=join_type,
            table_name=table_name,
            alias=alias,
            on_condition=on_condition
        )
    
    def _parse_where_clause(self) -> WhereClause:
        """Parse WHERE clause."""
        # WHERE
        self._expect_token(TokenType.WHERE)
        
        conditions = []
        operators = []
        
        # Parse first condition
        conditions.append(self._parse_condition())
        
        # Parse additional conditions with operators
        while self._current_token() and self._current_token().type in [TokenType.AND, TokenType.OR]:
            op_token = self._consume_token()
            operators.append(op_token.value.upper())
            conditions.append(self._parse_condition())
        
        return WhereClause(conditions=conditions, operators=operators)
    
    def _parse_condition(self) -> Condition:
        """Parse a single condition."""
        # column (may be table.column)
        column_parts = []
        col_token = self._expect_token(TokenType.IDENTIFIER)
        column_parts.append(col_token.value)
        
        # Check for table.column syntax
        if self._current_token() and self._current_token().type == TokenType.DOT:
            self._consume_token()  # consume dot
            col_token2 = self._expect_token(TokenType.IDENTIFIER)
            column_parts.append(col_token2.value)
            column = ".".join(column_parts)
        else:
            column = column_parts[0]
        
        # operator
        op_token = self._consume_token()
        if op_token.type not in [
            TokenType.EQUALS, TokenType.NOT_EQUALS, TokenType.LESS_THAN,
            TokenType.GREATER_THAN, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL
        ]:
            raise SQLSyntaxError(
                f"Expected comparison operator, got {op_token.type.value}",
                op_token.position
            )
        operator = op_token.value
        
        # value (may be table.column)
        if self._current_token() and self._current_token().type == TokenType.IDENTIFIER:
            # Check if this is a table.column reference
            peek_token = self.tokens[self.position + 1] if self.position + 1 < len(self.tokens) else None
            if peek_token and peek_token.type == TokenType.DOT:
                # This is table.column syntax
                value_parts = []
                value_token = self._consume_token()
                value_parts.append(value_token.value)
                self._consume_token()  # consume dot
                value_token2 = self._expect_token(TokenType.IDENTIFIER)
                value_parts.append(value_token2.value)
                value = ".".join(value_parts)
            else:
                # Regular identifier
                value_token = self._consume_token()
                value = value_token.value
        else:
            # Regular value
            value = self._parse_value()
        
        return Condition(column=column, operator=operator, value=value)
    
    def _parse_value(self) -> Any:
        """Parse a literal value."""
        token = self._consume_token()
        
        if token.type == TokenType.STRING_LITERAL:
            return token.value
        elif token.type == TokenType.NUMBER_LITERAL:
            # Try to parse as int first, then float
            try:
                if '.' in token.value:
                    return float(token.value)
                else:
                    return int(token.value)
            except ValueError:
                raise SQLSyntaxError(f"Invalid number: {token.value}", token.position)
        elif token.type == TokenType.BOOLEAN_LITERAL:
            return token.value.lower() == 'true'
        elif token.type == TokenType.NULL:
            return None
        else:
            raise SQLSyntaxError(
                f"Expected literal value, got {token.type.value}",
                token.position
            )
