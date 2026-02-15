import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, CircularProgress, Box } from '@mui/material';

function DashboardSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_FASTAPI_URL}/risk-dashboard-summary`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSummary(data);
      } catch (e) {
        setError(e);
        console.error("Failed to fetch dashboard summary:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
    const interval = setInterval(fetchSummary, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Typography color="error">Error: {error.message}</Typography>;
  }

  if (!summary) {
    return <Typography>No summary data available.</Typography>;
  }

  const getRiskColor = (score) => {
    if (score >= 80) return 'error.main'; // Critical
    if (score >= 60) return 'warning.main'; // High
    if (score >= 30) return 'info.main';    // Medium
    return 'success.main';                  // Low
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card raised>
          <CardContent>
            <Typography color="textSecondary" gutterBottom variant="h6">
              Total Logs Processed
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
              {summary.total_logs}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card raised>
          <CardContent>
            <Typography color="textSecondary" gutterBottom variant="h6">
              Total Anomalies Detected
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: summary.total_anomalies > 0 ? 'error.main' : 'success.main' }}>
              {summary.total_anomalies}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card raised>
          <CardContent>
            <Typography color="textSecondary" gutterBottom variant="h6">
              Average Risk Score
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: getRiskColor(parseFloat(summary.average_risk_score)) }}>
              {summary.average_risk_score}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12}>
        <Card raised>
          <CardContent>
            <Typography color="textSecondary" gutterBottom variant="h6">
              Risk Distribution
            </Typography>
            <Grid container spacing={1} sx={{ mt: 2 }}>
              {Object.entries(summary.risk_distribution).map(([level, count]) => (
                <Grid item xs={6} sm={3} key={level}>
                  <Typography variant="body1" sx={{ color: getRiskColor(
                    level === 'Critical' ? 100 :
                    level === 'High' ? 70 :
                    level === 'Medium' ? 45 : 10
                  ) }}>
                    {level}: {count}
                  </Typography>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default DashboardSummary;
