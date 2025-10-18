"""
Tests for the Mini SQL Playground backend API.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.schemas import ExecuteResponse
from app.engine.executor import QueryExecutor
from app.engine.storage import StorageManager


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_executor():
    """Create mock query executor."""
    executor = MagicMock(spec=QueryExecutor)
    return executor


@pytest.fixture
def mock_storage():
    """Create mock storage manager."""
    storage = MagicMock(spec=StorageManager)
    return storage


class TestExecuteEndpoint:
    """Test cases for the /execute endpoint."""
    
    def test_execute_successful_select(self, client):
        """Test successful SELECT query execution."""
        with patch('app.api.execute.query_executor') as mock_executor:
            # Mock successful query result
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.data = [{"id": 1, "name": "Alice"}]
            mock_result.message = "Selected 1 row(s)"
            mock_result.affected_rows = 1
            
            mock_executor.execute_raw_sql.return_value = mock_result
            
            response = client.post(
                "/api/v1/execute",
                json={
                    "query": "SELECT * FROM users",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["result"] == [{"id": 1, "name": "Alice"}]
            assert data["message"] == "Selected 1 row(s)"
            assert "time_ms" in data
    
    def test_execute_failed_query(self, client):
        """Test failed query execution."""
        with patch('app.api.execute.query_executor') as mock_executor:
            # Mock failed query result
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.data = None
            mock_result.message = "Table 'users' not found"
            mock_result.affected_rows = 0
            
            mock_executor.execute_raw_sql.return_value = mock_result
            
            response = client.post(
                "/api/v1/execute",
                json={
                    "query": "SELECT * FROM users",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["error"] == "Table 'users' not found"
            assert data["result"] is None
    
    def test_execute_without_session_id(self, client):
        """Test query execution without session ID."""
        with patch('app.api.execute.query_executor') as mock_executor:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.data = []
            mock_result.message = "Selected 0 row(s)"
            mock_result.affected_rows = 0
            
            mock_executor.execute_raw_sql.return_value = mock_result
            
            response = client.post(
                "/api/v1/execute",
                json={"query": "SELECT * FROM empty_table"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_execute_invalid_query(self, client):
        """Test execution with invalid query."""
        with patch('app.api.execute.query_executor') as mock_executor:
            mock_executor.execute_raw_sql.side_effect = Exception("Syntax error")
            
            response = client.post(
                "/api/v1/execute",
                json={
                    "query": "INVALID SQL",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Syntax error" in data["error"]
    
    def test_execute_empty_query(self, client):
        """Test execution with empty query."""
        response = client.post(
            "/api/v1/execute",
            json={"query": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_execute_query_too_long(self, client):
        """Test execution with query that's too long."""
        long_query = "SELECT * FROM table " + "WHERE id = 1 " * 1000
        
        response = client.post(
            "/api/v1/execute",
            json={"query": long_query}
        )
        
        assert response.status_code == 422  # Validation error


class TestHistoryEndpoint:
    """Test cases for the /history endpoint."""
    
    def test_get_history_success(self, client):
        """Test successful history retrieval."""
        # First execute a query to create history
        with patch('app.api.execute.query_executor') as mock_executor:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.data = []
            mock_result.message = "Selected 0 row(s)"
            mock_result.affected_rows = 0
            
            mock_executor.execute_raw_sql.return_value = mock_result
            
            # Execute a query
            client.post(
                "/api/v1/execute",
                json={
                    "query": "SELECT * FROM test",
                    "session_id": "history-test"
                }
            )
        
        # Get history
        response = client.get("/api/v1/history?session_id=history-test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "history-test"
        assert len(data["queries"]) == 1
        assert data["queries"][0]["query"] == "SELECT * FROM test"
    
    def test_get_history_empty_session(self, client):
        """Test history retrieval for empty session."""
        response = client.get("/api/v1/history?session_id=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "nonexistent"
        assert data["queries"] == []
        assert data["total"] == 0


class TestResetEndpoint:
    """Test cases for the /reset endpoint."""
    
    def test_reset_database(self, client):
        """Test database reset."""
        with patch('app.api.execute.storage_manager') as mock_storage:
            mock_storage.get_table_names.return_value = ["table1", "table2"]
            mock_storage.drop_table.return_value = None
            
            response = client.post("/api/v1/reset")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["tables_dropped"] == 2


class TestTablesEndpoint:
    """Test cases for the /tables endpoint."""
    
    def test_get_tables(self, client):
        """Test table information retrieval."""
        with patch('app.api.execute.storage_manager') as mock_storage:
            # Mock table data
            mock_table = MagicMock()
            mock_table.columns = []
            mock_table.data = [{"id": 1}, {"id": 2}]
            
            mock_storage.get_table_names.return_value = ["test_table"]
            mock_storage.get_table.return_value = mock_table
            
            response = client.get("/api/v1/tables")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["tables"]) == 1
            assert data["tables"][0]["name"] == "test_table"
            assert data["tables"][0]["row_count"] == 2


class TestHealthEndpoint:
    """Test cases for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestEngineIntegration:
    """Integration tests with the actual CoreDB engine."""
    
    def test_create_table_integration(self, client):
        """Test CREATE TABLE with actual engine."""
        response = client.post(
            "/api/v1/execute",
            json={"query": "CREATE TABLE test_users (id INT PRIMARY KEY, name TEXT)"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "created successfully" in data["message"]
    
    def test_insert_and_select_integration(self, client):
        """Test INSERT and SELECT with actual engine."""
        # Create table
        client.post(
            "/api/v1/execute",
            json={"query": "CREATE TABLE test_data (id INT PRIMARY KEY, value TEXT)"}
        )
        
        # Insert data
        response = client.post(
            "/api/v1/execute",
            json={"query": "INSERT INTO test_data VALUES (1, 'test')"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Select data
        response = client.post(
            "/api/v1/execute",
            json={"query": "SELECT * FROM test_data"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["result"]) == 1
        assert data["result"][0]["id"] == 1
        assert data["result"][0]["value"] == "test"
