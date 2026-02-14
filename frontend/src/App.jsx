import Layout from './components/Layout';
import DashboardSummary from './components/DashboardSummary';
import AnomalyList from './components/AnomalyList';
import LogIngestion from './components/LogIngestion';
import { Box, Typography } from '@mui/material';

function App() {
  console.log("VITE_FASTAPI_URL:", import.meta.env.VITE_FASTAPI_URL); // ADD THIS LINE

  return (
    <Layout>
      <Typography variant="h4" component="h2" gutterBottom>
        Overview
      </Typography>
      <DashboardSummary />
      
      <Typography variant="h4" component="h2" gutterBottom sx={{ mt: 4 }}>
        Logs & Training
      </Typography>
      <LogIngestion />

      <Typography variant="h4" component="h2" gutterBottom sx={{ mt: 4 }}>
        Anomalies
      </Typography>
      <AnomalyList />
    </Layout>
  );
}

export default App;
