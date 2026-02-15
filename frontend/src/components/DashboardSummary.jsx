import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, CircularProgress, Box, useTheme } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from 'recharts';

function DashboardSummary() {
  const [summary, setSummary] = useState(null);
  const [logData, setLogData] = useState([]); // New state for historical logs
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const theme = useTheme();

  useEffect(() => {
    const fetchSummaryAndLogs = async () => {
      try {
        // Fetch summary data
        const summaryResponse = await fetch(`${import.meta.env.VITE_FASTAPI_URL}/risk-dashboard-summary`);
        if (!summaryResponse.ok) {
          throw new Error(`HTTP error! status: ${summaryResponse.status}`);
        }
        const summaryData = await summaryResponse.json();
        setSummary(summaryData);

        // Fetch historical logs
        const logsResponse = await fetch(`${import.meta.env.VITE_FASTAPI_URL}/logs`);
        if (!logsResponse.ok) {
          throw new Error(`HTTP error! status: ${logsResponse.status}`);
        }
        const logsData = await logsResponse.json();
        setLogData(logsData.logs);

      } catch (e) {
        setError(e);
        console.error("Failed to fetch dashboard data:", e);
      } finally {
        setLoading(false);
      }
    };

    fetchSummaryAndLogs();
    const interval = setInterval(fetchSummaryAndLogs, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  // Process logData for log volume chart
  const logVolumeMap = logData.reduce((acc, log) => {
    const date = new Date(log.processed_at).toLocaleDateString();
    acc[date] = (acc[date] || 0) + 1;
    return acc;
  }, {});

  const logVolumeChartData = Object.entries(logVolumeMap).map(([date, count]) => ({
    date,
    count,
  })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  
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
    if (score >= 80) return theme.palette.error.main; // Critical
    if (score >= 60) return theme.palette.warning.main; // High
    if (score >= 30) return theme.palette.info.main;    // Medium
    return theme.palette.success.main;                  // Low
  };

  // Define colors for the pie chart slices
  const COLORS = {
    'Critical': theme.palette.error.main,
    'High': theme.palette.warning.main,
    'Medium': theme.palette.info.main,
    'Low': theme.palette.success.main,
  };

  // Prepare data for the pie chart
  const pieChartData = Object.entries(summary.risk_distribution).map(([name, value]) => ({
    name,
    value,
  }));

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
              Log Volume Over Time
            </Typography>
            {logVolumeChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart
                  data={logVolumeChartData}
                  margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                  }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke={theme.palette.primary.main} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Typography>No log data to display volume over time.</Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}

export default DashboardSummary;
