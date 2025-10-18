# Mini SQL Playground Frontend

A modern React frontend for the Mini SQL Playground, featuring Monaco Editor for SQL editing, real-time query execution, and comprehensive result visualization.

## Features

- **Monaco Editor**: Professional SQL editor with syntax highlighting and autocomplete
- **Query Execution**: Execute SQL queries with real-time results
- **Result Tables**: Beautiful, responsive tables for query results
- **Query History**: Track and replay previous queries
- **Real-time Feedback**: Execution time and success/error indicators
- **Modern UI**: Clean, responsive design with dark theme support
- **Mobile Friendly**: Responsive design for all screen sizes

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Running Mini SQL Playground Backend (FastAPI)

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

### Configuration

The frontend connects to the backend via the `config.ts` file:

```typescript
export const config = {
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  // ... other settings
};
```

To change the backend URL, either:
- Set the `REACT_APP_API_BASE_URL` environment variable
- Modify the `API_BASE_URL` in `src/config.ts`

## Usage

### Writing SQL Queries

1. **Use the Monaco Editor** to write your SQL queries
2. **Syntax highlighting** and **autocomplete** are provided
3. **Multi-line queries** are supported
4. **Keyboard shortcuts**:
   - `Ctrl+Enter` (or `Cmd+Enter` on Mac) to execute query
   - Standard Monaco Editor shortcuts

### Executing Queries

1. **Click the "Run Query" button** or use `Ctrl+Enter`
2. **View results** in the result table below
3. **Check execution time** and affected rows
4. **Handle errors** with clear error messages

### Query History

1. **Click "History"** to view previous queries
2. **Click any query** to load it back into the editor
3. **See execution details** including success/failure and timing
4. **Track affected rows** for DML operations

### Database Management

- **Reset Database**: Click "Reset DB" to clear all data (for testing)

## Supported SQL Features

The frontend supports all SQL features provided by the CoreDB backend:

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

## Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── ...
├── src/
│   ├── App.tsx              # Main application component
│   ├── App.css              # Application styles
│   ├── config.ts            # Configuration settings
│   ├── index.tsx            # Application entry point
│   ├── index.css            # Global styles
│   └── ...
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

## Components

### App.tsx
Main application component containing:
- Monaco Editor integration
- Query execution logic
- Result display
- History management
- Error handling

### ResultTable
Displays query results in a responsive table format with:
- Column headers
- Data rows
- NULL value handling
- Hover effects

## Styling

The application uses modern CSS with:
- **CSS Grid and Flexbox** for layouts
- **CSS Custom Properties** for theming
- **Responsive design** for mobile compatibility
- **Smooth animations** and transitions
- **Accessibility features** (focus indicators, ARIA labels)

## API Integration

The frontend communicates with the backend via REST API:

### Endpoints Used
- `POST /api/v1/execute` - Execute SQL queries
- `GET /api/v1/history` - Get query history
- `POST /api/v1/reset` - Reset database

### Error Handling
- Network errors are caught and displayed
- Backend errors are shown with clear messages
- Loading states provide user feedback

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Dependencies

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Monaco Editor** - SQL editor
- **Axios** - HTTP client
- **Lucide React** - Icons

## Production Build

To create a production build:

```bash
npm run build
```

The build files will be in the `build/` directory.

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure the backend is running on `http://localhost:8000`
   - Check CORS settings in the backend
   - Verify the API_BASE_URL in config.ts

2. **Monaco Editor Not Loading**
   - Check browser console for errors
   - Ensure all dependencies are installed
   - Try clearing browser cache

3. **Query Execution Fails**
   - Check the backend logs
   - Verify SQL syntax
   - Ensure tables exist for SELECT queries

### Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
