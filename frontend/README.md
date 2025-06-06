# F1 Stats Frontend

This is the frontend for the F1 Stats App, built with React.

## Features

- Displays F1 statistics from the backend API.
- User-friendly interface for browsing data.
- Built with React, Material-UI, and TypeScript.

## Getting Started

### Prerequisites

- Node.js and npm

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/f1-stats-app.git
    cd f1-stats-app/frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

### Running the Application

```bash
npm start
```

This runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.

### Connecting to the Backend

This frontend is configured to proxy API requests to `http://localhost:5000`, where the backend Flask application is expected to be running. Make sure the backend is running before starting the frontend.

## Available Scripts

-   `npm start`: Runs the app in development mode.
-   `npm test`: Launches the test runner.
-   `npm run build`: Builds the app for production.
-   `npm run eject`: Ejects from Create React App.

## Learn More

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app). You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).
