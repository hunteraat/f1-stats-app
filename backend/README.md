# F1 Stats Backend

The Flask backend for the F1 Stats App.

## Features

- API endpoints for F1 statistics (drivers, sessions, etc.).
- Data synchronization with the OpenF1 API.
- AI-powered insights using OpenAI.
- Database management with Flask-SQLAlchemy and Flask-Migrate.

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/f1-stats-app.git
    cd f1-stats-app/backend
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    poetry install
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the `backend` directory and add the following:

    ```
    SECRET_KEY='a-strong-secret-key'
    OPENAI_API_KEY='your-openai-api-key'
    # For development, a default database is configured.
    # For production, you can add:
    # DATABASE_URL='your-production-database-url'
    ```

### Running the Application

1.  **Initialize the database:**

    ```bash
    poetry run flask db init
    poetry run flask db migrate -m "Initial migration."
    poetry run flask db upgrade
    ```

2.  **Run the Flask development server:**

    ```bash
    poetry run flask run
    ```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

The following API endpoints are available:

-   `/api/drivers`: Get all drivers.
-   `/api/sessions`: Get all sessions.
-   `/api/sync`: Synchronize data with the OpenF1 API.
-   `/api/overview`: Get an overview of the data.
-   `/api/years`: Get available years.
-   `/api/constructors`: Get all constructors.
-   `/api/ai`: Get AI-powered insights.

## Project Structure

```
backend/
├── app.py           # Flask application factory
├── config.py        # Configuration settings
├── models.py        # SQLAlchemy database models
├── routes/          # API blueprints
├── services/        # Business logic and external API communication
├── utils/           # Utility functions
├── tests/           # Application tests
├── pyproject.toml   # Project dependencies
└── ...
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request. 