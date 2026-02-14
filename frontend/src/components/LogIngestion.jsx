import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Snackbar, Alert, Grid } from '@mui/material';

function LogIngestion() {
  const [logData, setLogData] = useState({
    source: '',
    event_type: '',
    message: '',
    metadata: '{}', // Stringified JSON
  });
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const handleChange = (e) => {
    setLogData({ ...logData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Parse metadata string to JSON object
      const parsedMetadata = JSON.parse(logData.metadata);

      const logToSend = {
        ...logData,
        timestamp: new Date().toISOString(), // Use current time for timestamp
        metadata: parsedMetadata,
      };

      const response = await fetch('http://127.0.0.1:8000/ingest-log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logToSend),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      await response.json(); // Consume the response
      setSnackbarMessage("Log ingested successfully!");
      setSnackbarSeverity("success");
      setLogData({ // Clear form fields after successful ingestion
        source: '',
        event_type: '',
        message: '',
        metadata: '{}',
      });
    } catch (e) {
      setSnackbarMessage(`Failed to ingest log: ${e.message}`);
      setSnackbarSeverity("error");
      console.error("Failed to ingest log:", e);
    } finally {
      setLoading(false);
      setSnackbarOpen(true);
    }
  };

  const handleTrainModel = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/train-model', {
        method: 'POST',
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSnackbarMessage(data.message);
      setSnackbarSeverity("success");
    } catch (e) {
      setSnackbarMessage(`Failed to train model: ${e.message}`);
      setSnackbarSeverity("error");
      console.error("Failed to train model:", e);
    } finally {
      setLoading(false);
      setSnackbarOpen(true);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  return (
    <Card sx={{ mt: 4 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Manual Log Ingestion & Model Training
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Source (e.g., workstation-01)"
                name="source"
                value={logData.source}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Event Type (e.g., authentication, process_execution)"
                name="event_type"
                value={logData.event_type}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Message"
                name="message"
                value={logData.message}
                onChange={handleChange}
                multiline
                rows={2}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Metadata (JSON format, e.g., {'user': 'admin', 'ip_address': '10.0.0.1'})"
                name="metadata"
                value={logData.metadata}
                onChange={handleChange}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <Button type="submit" variant="contained" disabled={loading} sx={{ mr: 2 }}>
                {loading ? 'Ingesting...' : 'Ingest Log'}
              </Button>
              <Button variant="outlined" onClick={handleTrainModel} disabled={loading}>
                {loading ? 'Training...' : 'Train Anomaly Model'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Card>
  );
}

export default LogIngestion;
