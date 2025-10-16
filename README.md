# DBMS Project Report  
## CoreDB – A Minimal SQL Database Engine  

---

## 1. Introduction

**CoreDB** is a minimal yet functional SQL Database Management System (DBMS) implemented entirely in Python. It provides a simplified SQL interface inspired by SQLite but is built from scratch without using any external database libraries.

This project is designed for educational purposes — to demonstrate how database systems parse, store, and execute SQL commands internally.

### Objectives
- Understand the internal architecture of a DBMS.  
- Implement a minimal SQL engine supporting essential database operations.  
- Explore schema management and persistent data storage using JSON.  
- Provide an interactive SQL shell for executing commands in real-time.  

---

## 2. Features

CoreDB offers the following core features:

- **SQL Parser:** Supports basic SQL statements such as `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, and `DELETE`.  
- **Storage Engine:** JSON-based data persistence system for tables and schemas.  
- **Query Executor:** Executes parsed SQL statements and supports basic `WHERE` conditions.  
- **Interactive REPL:** Provides a command-line SQL shell.  
- **Type System:** Supports `INT`, `TEXT`, `FLOAT`, and `BOOLEAN` data types.  
- **Schema Management:** Manages table definitions, columns, and constraints.  
- **Error Handling:** Provides robust validation and detailed error messages.  

---

## 3. System Architecture Diagram

Below is a high-level overview of the **CoreDB architecture** showing how different components interact internally.

```mermaid
flowchart TD

A[User Input / SQL Command] --> B[Lexer]
B --> C[Parser]
C --> D[Abstract Syntax Tree (AST)]
D --> E[Query Executor]
E --> F[Storage Manager]
F --> G[JSON Files (schema.json, table_data.json)]
E --> H[Result Formatter]
H --> I[Output to REPL Console]

subgraph CoreDB Engine
    B
    C
    D
    E
    F
end

style A fill:#E3F2FD,stroke:#1565C0,stroke-width:1px
style CoreDB Engine fill:#E8F5E9,stroke:#2E7D32,stroke-width:1px
style G fill:#FFF3E0,stroke:#EF6C00,stroke-width:1px
style I fill:#F3E5F5,stroke:#6A1B9A,stroke-width:1px



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

Each component mirrors a core subsystem of a traditional DBMS.

```

### 4. Installation and Setup

#### Requirements
- Python **3.6 or higher**
- No external dependencies required

#### Installation Steps
```bash
# Clone or download the repository
cd CoreDB

# Run directly
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
