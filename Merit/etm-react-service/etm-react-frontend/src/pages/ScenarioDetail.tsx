import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  CalendarToday,
  LocationOn,
  Assessment,
} from '@mui/icons-material';
import { useScenario } from '../contexts/ScenarioContext';
import apiClient from '../services/api';

const ScenarioDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { loadScenario } = useScenario();
  const [scenario, setScenario] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(true);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<Record<string, any>>({});

  useEffect(() => {
    const loadScenarioData = async () => {
      if (!id) return;
      
      setDetailLoading(true);
      setDetailError(null);
      
      try {
        const scenarioData = await apiClient.getScenario(Number(id));
        setScenario(scenarioData);
        
        // Fetch key metrics
        try {
          const results = await apiClient.getBatchGQueries(Number(id), [
            'co2_emissions_of_used_electricity',
            'renewability',
            'total_costs',
            'final_demand_electricity',
            'total_co2_emissions',
          ]);
          setMetrics(results);
        } catch (err) {
          console.error('Failed to fetch metrics:', err);
        }
      } catch (err: any) {
        setDetailError(
          err instanceof Error ? err.message : 'Failed to load scenario'
        );
      } finally {
        setDetailLoading(false);
      }
    };

    loadScenarioData();
  }, [id]);

  const handleDelete = async () => {
    if (!id || !window.confirm('Are you sure you want to delete this scenario?')) {
      return;
    }

    try {
      await apiClient.deleteScenario(Number(id));
      navigate('/');
    } catch (err) {
      console.error('Failed to delete scenario:', err);
      alert('Failed to delete scenario');
    }
  };

  const handleViewDashboard = async () => {
    if (!id || !loadScenario) return;
    
    try {
      await loadScenario(Number(id));
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to load scenario:', err);
      alert('Failed to load scenario');
    }
  };

  if (detailLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (detailError || !scenario) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {detailError || 'Scenario not found'}
        </Alert>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/')}
          sx={{ mt: 2 }}
        >
          Back to Home
        </Button>
      </Container>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatNumber = (value: number, unit: string = '') => {
    if (value === 0 || !value) return '0';
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(2)}M ${unit}`;
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(2)}K ${unit}`;
    }
    return `${value.toFixed(2)} ${unit}`;
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/')}
            sx={{ mb: 2 }}
          >
            Back
          </Button>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {scenario.title || `${scenario.area_code} ${scenario.end_year} Scenario`}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<LocationOn />}
                  label={scenario.area_code}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  icon={<CalendarToday />}
                  label={`${scenario.start_year} - ${scenario.end_year}`}
                  color="secondary"
                  variant="outlined"
                />
                {scenario.private && (
                  <Chip label="Private" color="warning" size="small" />
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<Edit />}
                onClick={() => {
                  // Navigate to scenario builder with current scenario data
                  if (scenario) {
                    navigate('/scenario/new');
                  }
                }}
              >
                Edit
              </Button>
              <Button
                variant="outlined"
                color="error"
                startIcon={<Delete />}
                onClick={handleDelete}
              >
                Delete
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  CO2 Emissions
                </Typography>
                <Typography variant="h5">
                  {metrics['co2_emissions_of_used_electricity']?.future
                    ? formatNumber(
                        metrics['co2_emissions_of_used_electricity'].future,
                        metrics['co2_emissions_of_used_electricity'].unit || 'Mton'
                      )
                    : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Future: {metrics['co2_emissions_of_used_electricity']?.present
                    ? formatNumber(
                        metrics['co2_emissions_of_used_electricity'].present,
                        metrics['co2_emissions_of_used_electricity'].unit || 'Mton'
                      )
                    : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Renewability
                </Typography>
                <Typography variant="h5">
                  {metrics['renewability']?.future
                    ? `${metrics['renewability'].future.toFixed(1)}%`
                    : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Present: {metrics['renewability']?.present
                    ? `${metrics['renewability'].present.toFixed(1)}%`
                    : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Costs
                </Typography>
                <Typography variant="h5">
                  {metrics['total_costs']?.future
                    ? formatNumber(
                        metrics['total_costs'].future,
                        metrics['total_costs'].unit || 'EUR'
                      )
                    : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Present: {metrics['total_costs']?.present
                    ? formatNumber(
                        metrics['total_costs'].present,
                        metrics['total_costs'].unit || 'EUR'
                      )
                    : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Electricity Demand
                </Typography>
                <Typography variant="h5">
                  {metrics['final_demand_electricity']?.future
                    ? formatNumber(
                        metrics['final_demand_electricity'].future,
                        metrics['final_demand_electricity'].unit || 'PJ'
                      )
                    : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Present: {metrics['final_demand_electricity']?.present
                    ? formatNumber(
                        metrics['final_demand_electricity'].present,
                        metrics['final_demand_electricity'].unit || 'PJ'
                      )
                    : 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        {/* Scenario Details */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Scenario Information
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell><strong>ID</strong></TableCell>
                      <TableCell>{scenario.id}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Area Code</strong></TableCell>
                      <TableCell>{scenario.area_code}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Start Year</strong></TableCell>
                      <TableCell>{scenario.start_year}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>End Year</strong></TableCell>
                      <TableCell>{scenario.end_year}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Created</strong></TableCell>
                      <TableCell>{formatDate(scenario.created_at)}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell><strong>Updated</strong></TableCell>
                      <TableCell>{formatDate(scenario.updated_at)}</TableCell>
                    </TableRow>
                    {scenario.source && (
                      <TableRow>
                        <TableCell><strong>Source</strong></TableCell>
                        <TableCell>{scenario.source}</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                User Values
              </Typography>
              {scenario.user_values && Object.keys(scenario.user_values).length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Input</strong></TableCell>
                        <TableCell align="right"><strong>Value</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(scenario.user_values).slice(0, 10).map(([key, value]) => (
                        <TableRow key={key}>
                          <TableCell>{key}</TableCell>
                          <TableCell align="right">{String(value)}</TableCell>
                        </TableRow>
                      ))}
                      {Object.keys(scenario.user_values).length > 10 && (
                        <TableRow>
                          <TableCell colSpan={2} align="center">
                            <Typography variant="body2" color="text.secondary">
                              ... and {Object.keys(scenario.user_values).length - 10} more
                            </Typography>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No user values set
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>

        {/* Actions */}
        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<Assessment />}
            onClick={handleViewDashboard}
          >
            View Dashboard
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate('/scenario/new')}
          >
            Create New Scenario
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default ScenarioDetail;
