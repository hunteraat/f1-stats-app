# F1 Stats Application

A full-stack application for tracking and analyzing Formula 1 statistics using the OpenF1 API. Built with React frontend and Python (Flask) backend with an SQLite database.

## Features

- **Real-time F1 Data**: Synchronization with OpenF1 API
- **Driver Statistics**: Comprehensive driver stats, standings, and detailed profiles
- **Constructor Analysis**: Team standings, statistics, and performance tracking
- **Session Information**: Race and sprint session data with lap times
- **Position Tracking**: Real-time position changes during sessions
- **AI Integration**: OpenAI-powered insights and analysis
- **Year-based Analysis**: Historical data from multiple F1 seasons
- **Modern UI**: React-based interface with Material-UI components

## Tech Stack

### Frontend
- **React** with TypeScript
- **Material-UI** for component library
- **Axios** for API communication
- **React Hooks** for state management

### Backend
- **Flask** REST API
- **SQLAlchemy** ORM with SQLite database
- **Flask-Migrate** for database migrations
- **Flask-CORS** for cross-origin requests
- **OpenAI Integration** for AI-powered features

## Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (optional):
Create a `.env` file in the backend directory for any environment-specific configuration.

5. Initialize the database:
```bash
python app.py
```

The API will be available at `http://localhost:5000`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to the backend.

## Project Structure

```
f1-stats-app/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration settings
│   ├── models.py                 # SQLAlchemy database models
│   ├── extensions.py             # Flask extensions initialization
│   ├── utils.py                  # Utility functions
│   ├── requirements.txt          # Python dependencies
│   ├── routes/                   # API route modules
│   │   ├── __init__.py
│   │   ├── drivers.py           # Driver-related endpoints
│   │   ├── sessions.py          # Session data endpoints
│   │   ├── sync.py              # Data synchronization
│   │   ├── overview.py          # Overview statistics
│   │   ├── years.py             # Year-based data access
│   │   ├── constructors.py      # Constructor/team endpoints
│   │   └── ai.py                # AI-powered features
│   ├── utils/                   # Backend utilities
│   ├── logs/                    # Application logs
│   ├── migrations/              # Database migration files
│   └── instance/                # SQLite database location
└── frontend/
    ├── src/
    │   ├── App.tsx              # Main React application
    │   ├── components/          # React components
    │   │   ├── DriversTab/      # Driver statistics UI
    │   │   ├── ConstructorsTab/ # Constructor standings UI
    │   │   ├── SessionsTab/     # Session data UI
    │   │   ├── OverviewTab/     # Overview dashboard
    │   │   ├── DriverDetails/   # Detailed driver profiles
    │   │   ├── YearSelector/    # Year selection component
    │   │   ├── TabNavigation/   # Navigation interface
    │   │   └── ErrorMessage/    # Error handling UI
    │   ├── services/            # API service layer
    │   ├── types/               # TypeScript type definitions
    │   ├── hooks/               # Custom React hooks
    │   ├── contexts/            # React context providers
    │   ├── utils/               # Frontend utilities
    │   ├── styles/              # CSS and styling
    │   └── constants/           # Application constants
    ├── public/                  # Static assets
    ├── package.json             # Node.js dependencies
    └── tsconfig.json            # TypeScript configuration
```

## API Endpoints

### Core Data
- `GET /api/drivers` - Driver information and statistics
- `GET /api/drivers/{driver_number}` - Individual driver details
- `GET /api/constructors` - Constructor/team standings and stats
- `GET /api/sessions` - Session data and race results
- `GET /api/sessions/{session_key}` - Specific session data
- `GET /api/overview` - Overview statistics and summaries

### Data Management
- `POST /api/sync` - Synchronize data from OpenF1 API
- `GET /api/years` - Available years and sync status

### AI Features
- `POST /api/ai` - AI-powered insights and analysis

## Database Models

The application uses several key models:
- **Driver**: F1 driver information and metadata
- **Session**: Race and practice session data
- **DriverSession**: Driver performance in specific sessions
- **Position**: Position tracking during sessions
- **Lap**: Individual lap times and data
- **DriverStats**: Aggregated driver statistics by year
- **ConstructorStats**: Aggregated constructor statistics/standings by year
- **YearData**: Sync status and metadata for each season

## Development

### Running in Development Mode

1. Start the backend (from `backend/` directory):
```bash
python app.py
```

2. Start the frontend (from `frontend/` directory):
```bash
npm start
```

Both servers support hot reloading for development.

### Database Migrations

When making model changes:
```bash
cd backend
flask db migrate -m "Description of changes"
flask db upgrade
```

### Logging

Application logs are stored in `backend/logs/f1_stats.log` with automatic rotation.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is for educational and personal use. 