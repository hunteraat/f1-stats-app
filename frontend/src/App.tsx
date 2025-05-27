import React, { useState } from 'react';
import { Container, Box, Typography, Button, CircularProgress, AppBar, Toolbar } from '@mui/material';
import { useF1Data } from './hooks/useF1Data';
import { SyncProgress } from './components/SyncProgress';
import { ThemeProvider } from './contexts/ThemeContext';
import { ThemeToggle } from './components/ThemeToggle';

function AppContent() {
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const { data, isLoading, error, syncData, syncStatus } = useF1Data(selectedYear);

  return (
    <>
      <AppBar position="static" color="default" elevation={0}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            F1 Statistics
          </Typography>
          <ThemeToggle />
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Season {selectedYear}
          </Typography>

          <SyncProgress syncStatus={syncStatus} />

          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          <Box sx={{ mb: 2 }}>
            <Button 
              variant="contained" 
              onClick={() => syncData()}
              disabled={syncStatus?.status === 'in_progress'}
              startIcon={syncStatus?.status === 'in_progress' ? <CircularProgress size={20} /> : null}
            >
              {syncStatus?.status === 'in_progress' ? 'Syncing...' : 'Sync Data'}
            </Button>
          </Box>

          {isLoading ? (
            <CircularProgress />
          ) : data ? (
            <Box>
              {/* Your data visualization components here */}
              <pre>{JSON.stringify(data, null, 2)}</pre>
            </Box>
          ) : null}
        </Box>
      </Container>
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App; 