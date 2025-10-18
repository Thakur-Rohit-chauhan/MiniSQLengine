import React, { useState, useCallback, useEffect } from 'react';
import MonacoEditor from '@monaco-editor/react';
import axios from 'axios';
import { Play, History, Database, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import config from './config';
import './App.css';

// Types
interface QueryResult {
  success: boolean;
  result: any[] | null;
  columns: string[] | null;
  time_ms: number;
  message: string | null;
  error: string | null;
  affected_rows: number | null;
}

interface QueryHistory {
  query: string;
  timestamp: number;
  success: boolean;
  time_ms: number;
  affected_rows: number | null;
}

interface HistoryResponse {
  session_id: string;
  queries: QueryHistory[];
  total: number;
}

const App: React.FC = () => {
  // State
  const [query, setQuery] = useState<string>(config.DEFAULT_QUERY);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [history, setHistory] = useState<QueryHistory[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [sessionId] = useState<string>(() => `session-${Date.now()}`);
  const [showHistory, setShowHistory] = useState<boolean>(false);

  // Load query history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Load query history
  const loadHistory = useCallback(async () => {
    try {
      const response = await axios.get<HistoryResponse>(
        `${config.API_BASE_URL}/api/v1/history?session_id=${sessionId}&limit=${config.MAX_HISTORY_ITEMS}`
      );
      setHistory(response.data.queries);
    } catch (error) {
      console.error('Failed to load history:', error);
    }
  }, [sessionId]);

  // Execute SQL query
  const executeQuery = useCallback(async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post<QueryResult>(`${config.API_BASE_URL}/api/v1/execute`, {
        query: query.trim(),
        session_id: sessionId
      });

      setResult(response.data);
      
      // Reload history to include the new query
      await loadHistory();
    } catch (error: any) {
      setResult({
        success: false,
        result: null,
        columns: null,
        time_ms: 0,
        message: 'Network error',
        error: error.response?.data?.error || error.message,
        affected_rows: 0
      });
    } finally {
      setLoading(false);
    }
  }, [query, sessionId, loadHistory]);

  // Handle keyboard shortcuts
  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
      event.preventDefault();
      executeQuery();
    }
  }, [executeQuery]);

  // Load query from history
  const loadQueryFromHistory = useCallback((historyQuery: string) => {
    setQuery(historyQuery);
    setShowHistory(false);
  }, []);

  // Reset database
  const resetDatabase = useCallback(async () => {
    if (!window.confirm('Are you sure you want to reset the database? This will delete all data.')) {
      return;
    }

    try {
      await axios.post(`${config.API_BASE_URL}/api/v1/reset`);
      setResult(null);
      setHistory([]);
      alert('Database reset successfully!');
    } catch (error) {
      alert('Failed to reset database');
    }
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <Database className="header-icon" />
            <h1>Mini SQL Playground</h1>
          </div>
          <div className="header-right">
            <button 
              className="btn btn-secondary" 
              onClick={() => setShowHistory(!showHistory)}
            >
              <History size={16} />
              History ({history.length})
            </button>
            <button 
              className="btn btn-danger" 
              onClick={resetDatabase}
            >
              Reset DB
            </button>
          </div>
        </div>
      </header>

      <div className="app-content">
        <div className="editor-section">
          <div className="editor-header">
            <h2>SQL Editor</h2>
            <button 
              className="btn btn-primary run-button" 
              onClick={executeQuery}
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <Loader className="spinner" size={16} />
              ) : (
                <Play size={16} />
              )}
              Run Query
            </button>
          </div>
          
          <div className="editor-container" onKeyDown={handleKeyDown}>
            <MonacoEditor
              height={config.EDITOR_HEIGHT}
              language={config.EDITOR_LANGUAGE}
              value={query}
              onChange={(value) => setQuery(value || '')}
              theme={config.EDITOR_THEME}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 2,
                wordWrap: 'on',
                suggestOnTriggerCharacters: true,
                acceptSuggestionOnEnter: 'on',
                quickSuggestions: true,
                suggest: {
                  showKeywords: true,
                  showSnippets: true
                }
              }}
            />
          </div>
          
          <div className="editor-footer">
            <small>Press Ctrl+Enter (Cmd+Enter on Mac) to run query</small>
          </div>
        </div>

        {showHistory && (
          <div className="history-section">
            <div className="history-header">
              <h3>Query History</h3>
              <button 
                className="btn btn-small" 
                onClick={() => setShowHistory(false)}
              >
                Close
              </button>
            </div>
            <div className="history-list">
              {history.length === 0 ? (
                <p className="no-history">No queries executed yet</p>
              ) : (
                history.map((item, index) => (
                  <div 
                    key={index} 
                    className={`history-item ${item.success ? 'success' : 'error'}`}
                    onClick={() => loadQueryFromHistory(item.query)}
                  >
                    <div className="history-item-header">
                      <div className="history-status">
                        {item.success ? (
                          <CheckCircle size={14} className="success-icon" />
                        ) : (
                          <XCircle size={14} className="error-icon" />
                        )}
                        <span className="history-time">
                          {new Date(item.timestamp * 1000).toLocaleTimeString()}
                        </span>
                      </div>
                      <div className="history-meta">
                        <Clock size={12} />
                        <span>{item.time_ms.toFixed(2)}ms</span>
                        {item.affected_rows !== null && (
                          <span className="affected-rows">
                            ({item.affected_rows} rows)
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="history-query">
                      {item.query.length > 100 
                        ? `${item.query.substring(0, 100)}...` 
                        : item.query
                      }
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {result && (
          <div className="result-section">
            <div className="result-header">
              <h3>Query Result</h3>
              <div className="result-meta">
                <div className={`result-status ${result.success ? 'success' : 'error'}`}>
                  {result.success ? (
                    <CheckCircle size={16} className="success-icon" />
                  ) : (
                    <XCircle size={16} className="error-icon" />
                  )}
                  <span>{result.success ? 'Success' : 'Error'}</span>
                </div>
                <div className="result-time">
                  <Clock size={14} />
                  <span>{result.time_ms.toFixed(2)}ms</span>
                </div>
                {result.affected_rows !== null && (
                  <div className="result-rows">
                    {result.affected_rows} row(s) affected
                  </div>
                )}
              </div>
            </div>

            {result.success && result.result ? (
              <div className="result-table-container">
                <ResultTable data={result.result} columns={result.columns} />
              </div>
            ) : (
              <div className="result-error">
                <p><strong>Error:</strong> {result.error || result.message}</p>
              </div>
            )}

            {result.message && result.success && (
              <div className="result-message">
                <p>{result.message}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Result Table Component
interface ResultTableProps {
  data: any[];
  columns: string[] | null;
}

const ResultTable: React.FC<ResultTableProps> = ({ data, columns }) => {
  if (!data || data.length === 0) {
    return <div className="no-data">No data returned</div>;
  }

  // Get column names from data if not provided
  const tableColumns = columns || Object.keys(data[0] || {});

  return (
    <div className="table-container">
      <table className="result-table">
        <thead>
          <tr>
            {tableColumns.map((col, index) => (
              <th key={index}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {tableColumns.map((col, colIndex) => (
                <td key={colIndex}>
                  {row[col] !== null && row[col] !== undefined 
                    ? String(row[col]) 
                    : <span className="null-value">NULL</span>
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;