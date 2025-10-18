# Mini SQL Playground Backend

A FastAPI-based REST API for executing SQL queries using the CoreDB engine.

## Features

- **SQL Execution**: Execute SQL queries via REST API
- **Query History**: Track query execution history per session
- **Real-time Results**: Get query results with execution time
- **CORS Support**: Ready for frontend integration
- **Error Handling**: Comprehensive error handling and logging
- **Database Management**: Create, query, and manage tables
- **Session Management**: Track queries per session

## API Endpoints

### Core Endpoints

- `POST /api/v1/execute` - Execute SQL queries
- `GET /api/v1/history` - Get query history for a session
- `POST /api/v1/reset` - Reset database (for testing)
- `GET /api/v1/tables` - Get table information

### Utility Endpoints

- `GET /` - API information
- `GET /health` - Health check

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CoreDB/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Build the image
docker build -t mini-sql-playground-backend .

# Run the container
docker run -p 8000:8000 mini-sql-playground-backend
```

## API Usage

### Execute SQL Query

```bash
curl -X POST "http://localhost:8000/api/v1/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)",
       "session_id": "my-session"
     }'
```

**Response:**
```json
{
  "success": true,
  "result": null,
  "columns": null,
  "time_ms": 15.2,
  "message": "Table 'users' created successfully",
  "affected_rows": 0
}
```

### Get Query History

```bash
curl "http://localhost:8000/api/v1/history?session_id=my-session&limit=10"
```

**Response:**
```json
{
  "session_id": "my-session",
  "queries": [
    {
      "query": "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)",
      "timestamp": 1703123456.789,
      "success": true,
      "time_ms": 15.2,
      "affected_rows": 0
    }
  ],
  "total": 1
}
```

## Supported SQL Features

### Data Types
- `INT` - Integer numbers
- `TEXT` - Text strings  
- `FLOAT` - Floating-point numbers
- `BOOLEAN` - True/false values

### Statements
- `CREATE TABLE` - Create tables with constraints
- `INSERT INTO` - Insert data
- `SELECT` - Query data with JOINs, WHERE, GROUP BY, ORDER BY
- `UPDATE` - Update data with WHERE clauses
- `DELETE` - Delete data with WHERE clauses
- `DROP TABLE` - Drop tables

### Advanced Features
- **Foreign Keys**: Referential integrity constraints
- **JOINs**: INNER, LEFT, RIGHT, FULL OUTER JOINs
- **Aggregates**: COUNT, SUM, AVG, MAX, MIN
- **Column Aliases**: AS keyword support
- **Multiline Queries**: Support for complex queries

## Configuration

The application can be configured using environment variables:

- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- `DB_PATH` - Database storage path
- `MAX_QUERY_LENGTH` - Maximum query length
- `MAX_RESULT_ROWS` - Maximum result rows
- `LOG_LEVEL` - Logging level

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run integration tests
pytest -m integration
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── schemas.py           # Pydantic models
│   ├── api/
│   │   └── execute.py       # API endpoints
│   └── engine/              # CoreDB engine
│       ├── __init__.py
│       ├── lexer.py
│       ├── parser.py
│       ├── executor.py
│       ├── storage.py
│       ├── types.py
│       └── exceptions.py
├── tests/
│   └── test_api.py          # API tests
├── requirements.txt         # Dependencies
├── Dockerfile              # Container configuration
└── pytest.ini             # Test configuration
```

### Adding New Endpoints

1. Create endpoint function in `app/api/execute.py`
2. Add route to the router
3. Update schemas in `app/schemas.py` if needed
4. Add tests in `tests/test_api.py`

### Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid query syntax
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Unexpected errors

All errors return structured JSON responses with error details.

## Performance

- **Query Execution**: Optimized for small to medium datasets
- **Memory Usage**: Efficient in-memory processing
- **Response Time**: Sub-millisecond for simple queries
- **Concurrency**: Supports multiple concurrent requests

## Security

- **Input Validation**: All inputs are validated using Pydantic
- **Query Length Limits**: Prevents excessively long queries
- **CORS Configuration**: Configurable allowed origins
- **Error Sanitization**: Sensitive information is not exposed in errors

## Monitoring

The API includes:

- **Structured Logging**: All requests and responses are logged
- **Health Checks**: Built-in health check endpoint
- **Performance Metrics**: Query execution times
- **Error Tracking**: Comprehensive error logging

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:

1. Check the API documentation at `/docs`
2. Review the test cases for usage examples
3. Open an issue on GitHub