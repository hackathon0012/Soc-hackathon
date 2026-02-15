import React, { useState, useMemo } from 'react';
import Layout from './components/Layout';
import DashboardSummary from './components/DashboardSummary';
import AnomalyList from './components/AnomalyList';
import { Box, Typography, CssBaseline } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

function App() {
  const [mode, setMode] = useState('dark'); // Default to dark mode

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // palette values for light mode
                primary: {
                  main: '#1976d2',
                },
                secondary: {
                  main: '#dc004e',
                },
                background: {
                  default: '#f4f6f8',
                  paper: '#ffffff',
                },
                text: {
                  primary: '#333333',
                  secondary: '#666666',
                },
              }
            : {
                // palette values for dark mode
                primary: {
                  main: '#90caf9',
                },
                secondary: {
                  main: '#f48fb1',
                },
                background: {
                  default: '#121212',
                  paper: '#1e1e1e',
                },
                text: {
                  primary: '#ffffff',
                  secondary: '#aaaaaa',
                },
              }),
        },
      }),
    [mode],
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout toggleColorMode={toggleColorMode} currentMode={mode}>
        <Typography variant="h4" component="h2" gutterBottom>
          Overview
        </Typography>
        <DashboardSummary />
        
        <Typography variant="h4" component="h2" gutterBottom sx={{ mt: 4 }}>
          Anomalies
        </Typography>
        <AnomalyList />
      </Layout>
    </ThemeProvider>
  );
}

export default App;
