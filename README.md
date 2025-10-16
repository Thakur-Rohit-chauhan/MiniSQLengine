# CoreDB - A Minimal SQL Database Engine

CoreDB is a minimal but functional SQL database management system (DBMS) implemented entirely in Python. It provides a simplified SQL interface similar to SQLite, built from scratch without external database dependencies.

## 🚀 Features

- **SQL Parser**: Supports basic SQL statements (CREATE TABLE, INSERT, SELECT, UPDATE, DELETE)
- **Storage Engine**: JSON-based persistence for tables and data
- **Query Executor**: Executes parsed SQL statements with basic WHERE clause support
- **Interactive REPL**: Command-line interface for running SQL commands
- **Type System**: Supports INT, TEXT, FLOAT, and BOOLEAN data types
- **Schema Management**: Tracks table structures and constraints
- **Error Handling**: Comprehensive error reporting and validation

## 📁 Project Structure

```
coredb/
├── __init__.py          # Package initialization
├── exceptions.py        # Custom exceptions
├── types.py            # Data types and schema definitions
├── lexer.py            # SQL tokenization
├── parser.py           # SQL parsing and AST generation
├── storage.py          # Data persistence and schema management
├── executor.py         # Query execution engine
└── main.py             # REPL interface
```

## 🛠️ Installation

CoreDB requires only Python 3.6+ with no external dependencies:

```bash
# Clone or download the project
cd CoreDB

# No installation required - just run directly!
python -m coredb.main
```

## 🎯 Quick Start

### Interactive Shell

Start the interactive SQL shell:

```bash
python -m coredb.main
```

```sql
coredb> CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT);
✓ Table 'users' created successfully

coredb> INSERT INTO users VALUES (1, 'Alice', 25);
✓ Inserted 1 row(s) into 'users'

coredb> SELECT * FROM users;
id | name  | age
---|-------|----
1  | Alice | 25
(1 row(s) returned)
```

### Demo Script

Run the demo to see CoreDB in action:

```bash
python demo.py
```

### Basic Tests

Run the test suite:

```bash
python test_basic.py
```

## 📚 Supported SQL Syntax

### Data Types
- `INT` - Integer numbers
- `TEXT` - Text strings
- `FLOAT` - Floating-point numbers
- `BOOLEAN` - True/false values

### Statements

#### CREATE TABLE
```sql
CREATE TABLE table_name (
    column1 TYPE [PRIMARY KEY] [NOT NULL],
    column2 TYPE,
    ...
);
```

#### INSERT INTO
```sql
INSERT INTO table_name VALUES (value1, value2, ...);
INSERT INTO table_name (col1, col2) VALUES (val1, val2);
```

#### SELECT
```sql
SELECT * FROM table_name;
SELECT column1, column2 FROM table_name;
SELECT * FROM table_name WHERE condition;
```

#### UPDATE
```sql
UPDATE table_name SET column1 = value1, column2 = value2;
UPDATE table_name SET column1 = value1 WHERE condition;
```

#### DELETE
```sql
DELETE FROM table_name;
DELETE FROM table_name WHERE condition;
```

### WHERE Clause Conditions
- `=`, `!=`, `<`, `>`, `<=`, `>=`
- `AND`, `OR` operators
- String and numeric comparisons
- NULL handling

## 🎮 Interactive Commands

The CoreDB shell supports several special commands:

- `help` - Show help information
- `tables` - List all tables
- `describe <table>` - Show table structure
- `history` - Show command history
- `clear` - Clear screen
- `load <file>` - Execute SQL from file
- `quit`/`exit` - Exit the shell

## 📝 Example Usage

```python
from coredb.storage import StorageManager
from coredb.executor import QueryExecutor

# Initialize database
storage = StorageManager("my_database")
executor = QueryExecutor(storage)

# Execute SQL
result = executor.execute_raw_sql("CREATE TABLE products (id INT, name TEXT, price FLOAT)")
result = executor.execute_raw_sql("INSERT INTO products VALUES (1, 'Laptop', 999.99)")
result = executor.execute_raw_sql("SELECT * FROM products WHERE price > 500")
```

## 🗂️ Data Storage

CoreDB stores data in JSON files:
- `schema.json` - Table definitions and metadata
- `{table_name}.json` - Table data

This makes the database portable and easy to inspect or backup.

## 🧪 Testing

Run the basic test suite:

```bash
python test_basic.py
```

The tests cover:
- Lexer and parser functionality
- Storage engine operations
- Query execution
- Error handling

## 🚧 Limitations

CoreDB is a minimal implementation with some limitations:

- No JOIN operations
- Limited WHERE clause support (basic comparisons only)
- No indexes or query optimization
- No transactions or ACID properties
- No concurrent access support
- Limited data type validation

## 🔮 Future Enhancements

Potential improvements for CoreDB:

- [ ] Advanced WHERE clause support (LIKE, IN, BETWEEN)
- [ ] JOIN operations
- [ ] Indexes for performance
- [ ] Transaction support
- [ ] Concurrent access
- [ ] Query optimization
- [ ] Additional data types
- [ ] Backup and restore utilities

## 📄 License

This project is for educational purposes. Feel free to use, modify, and distribute.

## 🤝 Contributing

This is a learning project, but suggestions and improvements are welcome!

---

**CoreDB v0.1.0** - Built with ❤️ in Python