# F1 Stats Application

A Flask-based application for tracking and analyzing Formula 1 statistics using the OpenF1 API.

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the application:
```bash
cd backend
python app.py
```

The API will be available at `http://localhost:5000`.

## Features

- Real-time F1 data synchronization
- Driver statistics and standings
- Session information and lap times
- Position tracking
- Race and sprint results

## Development

The application is structured as follows:

```
f1-stats-app/
├── backend/
│   ├── app.py              # Main application entry point
│   ├── config.py           # Configuration settings
│   ├── models.py           # Database models
│   ├── routes/             # API routes
│   │   ├── drivers.py
│   │   ├── sessions.py
│   │   ├── sync.py
│   │   ├── stats.py
│   │   └── years.py
│   └── utils/              # Utility functions
│       └── blueprint_utils.py
└── frontend/              # Frontend application (if applicable)
```

## API Endpoints

- `/api/drivers` - Driver information and statistics
- `/api/sessions` - Session data and results
- `/api/sync` - Data synchronization endpoints
- `/api/stats` - Statistical analysis
- `/api/years` - Year-based data access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request 