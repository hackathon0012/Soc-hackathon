import React, { useState, useEffect } from 'react';
import {
  Card, CardContent, Typography, List, ListItem, ListItemText, CircularProgress, Box,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, Snackbar, Alert, Grid
} from '@mui/material';

function AnomalyList() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openReportDialog, setOpenReportDialog] = useState(false);
  const [currentReport, setCurrentReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_FASTAPI_URL}/anomalies`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAnomalies(data.anomalies);
    } catch (e) {
      setError(e);
      console.error("Failed to fetch anomalies:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleGenerateReport = async (logId) => {
    setReportLoading(true);
    setCurrentReport(null);
    try {
      const response = await fetch(`${import.meta.env.VITE_FASTAPI_URL}/generate-incident-report/${logId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const reportData = await response.json();
      setCurrentReport(reportData);
      setOpenReportDialog(true);
      setSnackbarMessage("Incident report generated successfully!");
      setSnackbarSeverity("success");
    } catch (e) {
      setSnackbarMessage(`Failed to generate report: ${e.message}`);
      setSnackbarSeverity("error");
      console.error("Failed to generate report:", e);
    } finally {
      setReportLoading(false);
      setSnackbarOpen(true);
    }
  };

  const handleCloseReportDialog = () => {
    setOpenReportDialog(false);
    setCurrentReport(null);
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

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

  return (
    <Card sx={{ mt: 4 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Detected Anomalies
        </Typography>
        {anomalies.length === 0 ? (
          <Typography>No anomalies detected yet.</Typography>
        ) : (
          <List>
            {anomalies.map((anomaly) => (
              <ListItem key={anomaly.id} divider>
                <Grid container alignItems="center" spacing={2}>
                  <Grid item xs={12} sm={8}>
                    <ListItemText
                      primary={`Log ID: ${anomaly.id} - Risk Score: ${anomaly.final_risk_score.toFixed(2)}`}
                      secondary={
                        <React.Fragment>
                          <Typography
                            sx={{ display: 'inline' }}
                            component="span"
                            variant="body2"
                            color="text.primary"
                          >
                            {anomaly.raw_log.message}
                          </Typography>
                          {' — Source: '} {anomaly.raw_log.source} {' | Type: '} {anomaly.raw_log.event_type}
                        </React.Fragment>
                      }
                    />
                  </Grid>
                  <Grid item xs={12} sm={4} sx={{ textAlign: { xs: 'left', sm: 'right' } }}>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => handleGenerateReport(anomaly.id)}
                      disabled={reportLoading}
                    >
                      {reportLoading ? <CircularProgress size={24} /> : 'Generate Report'}
                    </Button>
                  </Grid>
                </Grid>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
      <Dialog open={openReportDialog} onClose={handleCloseReportDialog} maxWidth="md" fullWidth>
        <DialogTitle>Incident Report (Log ID: {currentReport?.["Incident ID"]})</DialogTitle>
        <DialogContent dividers>
          {currentReport ? (
            <Box>
              <Typography variant="subtitle1" gutterBottom>Summary:</Typography>
              <Typography paragraph>{currentReport["Summary"]}</Typography>

              <Typography variant="subtitle1" gutterBottom>Severity Level:</Typography>
              <Typography paragraph>{currentReport["Severity Level"]} (Score: {currentReport["Final Risk Score"]})</Typography>

              <Typography variant="subtitle1" gutterBottom>Affected Systems/Sources:</Typography>
              <Typography paragraph>{currentReport["Affected Systems/Sources"]}</Typography>

              <Typography variant="subtitle1" gutterBottom>Possible Attack Type:</Typography>
              <Typography paragraph>{currentReport["Possible Attack Type"]}</Typography>

              <Typography variant="subtitle1" gutterBottom>Detailed Explanation:</Typography>
              <Typography paragraph>{currentReport["Detailed Explanation"]}</Typography>

              <Typography variant="subtitle1" gutterBottom>Recommended Actions:</Typography>
              <List dense>
                {currentReport["Recommended Actions"].map((action, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`- ${action}`} />
                  </ListItem>
                ))}
              </List>
              
              <Typography variant="subtitle1" gutterBottom>Prevention Strategy:</Typography>
              <List dense>
                {currentReport["Prevention Strategy"].map((strategy, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`- ${strategy}`} />
                  </ListItem>
                ))}
              </List>

              <Typography variant="subtitle1" gutterBottom>MITRE ATT&CK Mapping:</Typography>
              <Typography paragraph>{currentReport["MITRE ATT&CK Mapping"].join(', ')}</Typography>

              <Typography variant="h6" sx={{ mt: 2 }} gutterBottom>Executive Summary:</Typography>
              <Typography paragraph>{currentReport["Executive Summary"]}</Typography>
            </Box>
          ) : (
            <Typography>Loading report...</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseReportDialog}>Close</Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Card>
  );
}

export default AnomalyList;
