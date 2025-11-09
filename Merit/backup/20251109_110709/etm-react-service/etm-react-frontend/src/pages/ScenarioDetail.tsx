import React, { useEffect, useState, useCallback, useMemo } from 'react';
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
  IconButton,
  Tooltip,
  LinearProgress,
  Tabs,
  Tab,
} from '@mui/material';
import {
  ArrowBack,
  Edit,
  Delete,
  CalendarToday,
  LocationOn,
  Assessment,
  Refresh,
  ContentCopy,
  TrendingUp,
  TrendingDown,
  DownloadOutlined,
  SaveOutlined,
  InfoOutlined,
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useScenario } from '../contexts/ScenarioContext';
import apiClient from '../services/api';

const ScenarioDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { loadScenario } = useScenario();
  const [scenario, setScenario] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(true);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<Record<string, any>>({});
  const [activeTab, setActiveTab] = useState(0);

  const loadScenarioData = useCallback(async () => {
    if (!id) return;
    
    setDetailLoading(true);
    setDetailError(null);
    
    try {
      const scenarioData = await apiClient.getScenario(Number(id));
      setScenario(scenarioData);
    } catch (err: any) {
      setDetailError(
        err instanceof Error ? err.message : 'Failed to load scenario'
      );
    } finally {
      setDetailLoading(false);
    }
  }, [id]);

  const loadMetrics = useCallback(async () => {
    if (!id) return;
    
    setMetricsLoading(true);
    try {
      const results = await apiClient.getBatchGQueries(Number(id), [
        'co2_emissions_of_used_electricity',
        'renewability',
        'total_costs',
        'final_demand_electricity',
        'total_co2_emissions',
        'dashboard_renewability',
        'dashboard_total_costs',
      ]);
      setMetrics(results);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
    } finally {
      setMetricsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadScenarioData();
  }, [loadScenarioData]);

  useEffect(() => {
    if (scenario && !detailLoading) {
      loadMetrics();
    }
  }, [scenario, detailLoading, loadMetrics]);

  const handleDelete = async () => {
    if (!id || !window.confirm('Are you sure you want to delete this scenario?')) {
      return;
    }

    try {
      await apiClient.deleteScenario(Number(id));
      navigate('/scenarios');
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

  const handleRefresh = () => {
    loadScenarioData();
    loadMetrics();
  };

  const handleCopyId = () => {
    if (scenario?.id) {
      navigator.clipboard.writeText(String(scenario.id));
    }
  };

  const handleSaveSnapshot = () => {
    if (!scenario) return;
    const payload = {
      ts: new Date().toISOString(),
      scenario: {
        id: scenario.id,
        title: scenario.title,
        area_code: scenario.area_code,
        start_year: scenario.start_year,
        end_year: scenario.end_year,
      },
      metrics,
      user_values: scenario.user_values,
    };
    localStorage.setItem(`scenario_snapshot_${scenario.id}`, JSON.stringify(payload));
    alert('Snapshot saved locally');
  };

  const handleExportCSV = () => {
    if (!scenario) return;
    
    const rows: string[][] = [];
    rows.push(['Metric', 'Present', 'Future', 'Unit']);
    
    Object.entries(metrics).forEach(([key, value]) => {
      if (value && typeof value === 'object') {
        rows.push([
          key,
          String(value.present || ''),
          String(value.future || ''),
          String(value.unit || ''),
        ]);
      }
    });
    
    const csv = rows.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scenario_${scenario.id}_metrics.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Generate time series data for charts
  const timeSeriesData = useMemo(() => {
    if (!scenario || !metrics) return [];
    
    const startYear = scenario.start_year || 2020;
    const endYear = scenario.end_year || 2050;
    const years = [];
    for (let y = startYear; y <= endYear; y += 5) {
      years.push(y);
    }
    
    const co2Present = getMetricValue('co2_emissions_of_used_electricity', 'present') || 
                       getMetricValue('total_co2_emissions', 'present') || 0;
    const co2Future = getMetricValue('co2_emissions_of_used_electricity', 'future') || 
                      getMetricValue('total_co2_emissions', 'future') || 0;
    const renewabilityPresent = metrics['renewability']?.present || metrics['dashboard_renewability']?.present || 0;
    const renewabilityFuture = metrics['renewability']?.future || metrics['dashboard_renewability']?.future || 0;
    const costPresent = metrics['total_costs']?.present || metrics['dashboard_total_costs']?.present || 0;
    const costFuture = metrics['total_costs']?.future || metrics['dashboard_total_costs']?.future || 0;
    
    return years.map((year, index) => {
      const progress = index / (years.length - 1);
      return {
        year,
        co2: co2Present + (co2Future - co2Present) * progress,
        renewability: renewabilityPresent + (renewabilityFuture - renewabilityPresent) * progress,
        cost: costPresent + (costFuture - costPresent) * progress,
        demand: (metrics['final_demand_electricity']?.present || 0) + 
                ((metrics['final_demand_electricity']?.future || 0) - (metrics['final_demand_electricity']?.present || 0)) * progress,
      };
    });
  }, [scenario, metrics]);

  // Energy mix data for radar chart
  const energyMixData = useMemo(() => {
    if (!scenario?.user_values) return [];
    
    const mix: Record<string, number> = {};
    const keys = Object.keys(scenario.user_values);
    
    // Extract energy mix from user values
    keys.forEach(key => {
      if (key.includes('solar') || key.includes('pv')) {
        mix['Solar'] = (mix['Solar'] || 0) + (Number(scenario.user_values[key]) || 0);
      } else if (key.includes('wind')) {
        mix['Wind'] = (mix['Wind'] || 0) + (Number(scenario.user_values[key]) || 0);
      } else if (key.includes('hydro')) {
        mix['Hydro'] = (mix['Hydro'] || 0) + (Number(scenario.user_values[key]) || 0);
      } else if (key.includes('fossil') || key.includes('coal') || key.includes('gas')) {
        mix['Fossil'] = (mix['Fossil'] || 0) + (Number(scenario.user_values[key]) || 0);
      }
    });
    
    // Normalize to percentage if needed
    const total = Object.values(mix).reduce((a, b) => a + b, 0);
    if (total > 0) {
      Object.keys(mix).forEach(key => {
        mix[key] = (mix[key] / total) * 100;
      });
    }
    
    return Object.entries(mix).map(([key, value]) => ({ key, value: Math.round(value) }));
  }, [scenario]);

  if (detailLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 8 }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
            Loading scenario...
          </Typography>
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
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate('/scenarios')}
            variant="outlined"
          >
            Back to Scenarios
          </Button>
          <Button
            onClick={handleRefresh}
            startIcon={<Refresh />}
            variant="outlined"
          >
            Retry
          </Button>
        </Box>
      </Container>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
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

  const getMetricValue = (key: string, type: 'present' | 'future') => {
    const metric = metrics[key];
    if (!metric) return null;
    return type === 'present' ? metric.present : metric.future;
  };

  const getMetricUnit = (key: string) => {
    return metrics[key]?.unit || '';
  };

  const co2Present = getMetricValue('co2_emissions_of_used_electricity', 'present') || 
                     getMetricValue('total_co2_emissions', 'present');
  const co2Future = getMetricValue('co2_emissions_of_used_electricity', 'future') || 
                    getMetricValue('total_co2_emissions', 'future');
  const co2Unit = getMetricUnit('co2_emissions_of_used_electricity') || 
                  getMetricUnit('total_co2_emissions') || 'Mton';
  
  const renewability = metrics['renewability'] || metrics['dashboard_renewability'];
  const totalCosts = metrics['total_costs'] || metrics['dashboard_total_costs'];

  const co2Delta = co2Present && co2Future ? ((co2Future - co2Present) / co2Present) * 100 : 0;
  const renewabilityDelta = renewability?.present && renewability?.future 
    ? ((renewability.future - renewability.present) / renewability.present) * 100 
    : 0;
  const costDelta = totalCosts?.present && totalCosts?.future
    ? ((totalCosts.future - totalCosts.present) / totalCosts.present) * 100
    : 0;

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Button
              startIcon={<ArrowBack />}
              onClick={() => navigate('/scenarios')}
              variant="outlined"
              size="small"
            >
              Back to Scenarios
            </Button>
            <Tooltip title="Refresh data">
              <IconButton onClick={handleRefresh} size="small" sx={{ ml: 1 }}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Save snapshot">
              <IconButton onClick={handleSaveSnapshot} size="small">
                <SaveOutlined />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export CSV">
              <IconButton onClick={handleExportCSV} size="small">
                <DownloadOutlined />
              </IconButton>
            </Tooltip>
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 0 }}>
                  {scenario.title || `${scenario.area_code} ${scenario.end_year} Scenario`}
                </Typography>
                <Tooltip title="Copy Scenario ID">
                  <IconButton onClick={handleCopyId} size="small">
                    <ContentCopy fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                <Chip
                  icon={<LocationOn />}
                  label={scenario.area_code?.toUpperCase() || 'N/A'}
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  icon={<CalendarToday />}
                  label={`${scenario.start_year || 'N/A'} - ${scenario.end_year || 'N/A'}`}
                  color="secondary"
                  variant="outlined"
                />
                {scenario.private && (
                  <Chip label="Private" color="warning" size="small" />
                )}
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Edit />}
                onClick={() => navigate('/scenario/new')}
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

        {metricsLoading && (
          <Box sx={{ mb: 3 }}>
            <LinearProgress />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              Loading metrics...
            </Typography>
          </Box>
        )}

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Overview" />
            <Tab label="Metrics" />
            <Tab label="Charts" />
            <Tab label="Details" />
          </Tabs>
        </Paper>

        {/* Overview Tab */}
        {activeTab === 0 && (
          <Box>
            {/* KPI Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500 }}>
                        CO₂ Emissions
                      </Typography>
                      <InfoOutlined fontSize="small" sx={{ color: 'text.secondary' }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                      {co2Future !== null && co2Future !== undefined
                        ? formatNumber(co2Future, co2Unit)
                        : 'N/A'}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {co2Delta < 0 ? (
                        <TrendingDown color="success" fontSize="small" />
                      ) : co2Delta > 0 ? (
                        <TrendingUp color="error" fontSize="small" />
                      ) : null}
                      <Typography variant="body2" color="text.secondary">
                        {co2Delta !== 0 ? `${Math.abs(co2Delta).toFixed(1)}%` : '0%'} vs baseline
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Present: {co2Present !== null && co2Present !== undefined
                        ? formatNumber(co2Present, co2Unit)
                        : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500 }}>
                        Renewability
                      </Typography>
                      <InfoOutlined fontSize="small" sx={{ color: 'text.secondary' }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                      {renewability?.future !== null && renewability?.future !== undefined
                        ? `${renewability.future.toFixed(1)}%`
                        : 'N/A'}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {renewabilityDelta > 0 ? (
                        <TrendingUp color="success" fontSize="small" />
                      ) : renewabilityDelta < 0 ? (
                        <TrendingDown color="error" fontSize="small" />
                      ) : null}
                      <Typography variant="body2" color="text.secondary">
                        {renewabilityDelta !== 0 ? `${Math.abs(renewabilityDelta).toFixed(1)}%` : '0%'} vs baseline
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Present: {renewability?.present !== null && renewability?.present !== undefined
                        ? `${renewability.present.toFixed(1)}%`
                        : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500 }}>
                        Total Costs
                      </Typography>
                      <InfoOutlined fontSize="small" sx={{ color: 'text.secondary' }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                      {totalCosts?.future !== null && totalCosts?.future !== undefined
                        ? formatNumber(totalCosts.future, totalCosts.unit || 'EUR')
                        : 'N/A'}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {costDelta < 0 ? (
                        <TrendingDown color="success" fontSize="small" />
                      ) : costDelta > 0 ? (
                        <TrendingUp color="error" fontSize="small" />
                      ) : null}
                      <Typography variant="body2" color="text.secondary">
                        {costDelta !== 0 ? `${Math.abs(costDelta).toFixed(1)}%` : '0%'} vs baseline
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Present: {totalCosts?.present !== null && totalCosts?.present !== undefined
                        ? formatNumber(totalCosts.present, totalCosts.unit || 'EUR')
                        : 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 500 }}>
                        Electricity Demand
                      </Typography>
                      <InfoOutlined fontSize="small" sx={{ color: 'text.secondary' }} />
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
                      {metrics['final_demand_electricity']?.future !== null && metrics['final_demand_electricity']?.future !== undefined
                        ? formatNumber(
                            metrics['final_demand_electricity'].future,
                            metrics['final_demand_electricity'].unit || 'PJ'
                          )
                        : 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Present: {metrics['final_demand_electricity']?.present !== null && metrics['final_demand_electricity']?.present !== undefined
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

            {/* Quick Actions */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 4 }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Assessment />}
                onClick={handleViewDashboard}
                sx={{ minWidth: 180 }}
              >
                View Dashboard
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/scenario/new')}
                sx={{ minWidth: 180 }}
              >
                Create New Scenario
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => navigate('/scenarios')}
                sx={{ minWidth: 180 }}
              >
                Browse All Scenarios
              </Button>
            </Box>
          </Box>
        )}

        {/* Metrics Tab */}
        {activeTab === 1 && (
          <Box>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
                All Metrics
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Metric</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Present</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Future</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Unit</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>Change</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(metrics).map(([key, value]) => {
                      if (!value || typeof value !== 'object') return null;
                      const present = value.present || 0;
                      const future = value.future || 0;
                      const change = present !== 0 ? ((future - present) / present) * 100 : 0;
                      return (
                        <TableRow key={key} hover>
                          <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                            {key}
                          </TableCell>
                          <TableCell align="right">{formatNumber(present, '')}</TableCell>
                          <TableCell align="right">{formatNumber(future, '')}</TableCell>
                          <TableCell align="right">{value.unit || 'N/A'}</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${change > 0 ? '+' : ''}${change.toFixed(1)}%`}
                              size="small"
                              color={change < 0 ? 'success' : change > 0 ? 'error' : 'default'}
                              variant="outlined"
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Box>
        )}

        {/* Charts Tab */}
        {activeTab === 2 && (
          <Box>
            <Grid container spacing={3}>
              {/* CO2 Emissions Trend */}
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      CO₂ Emissions Trend
                    </Typography>
                    <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                      <ResponsiveContainer>
                        <LineChart data={timeSeriesData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <RTooltip />
                          <Legend />
                          <Line type="monotone" dataKey="co2" stroke="#ef4444" strokeWidth={2} name="CO₂ (Mton)" />
                        </LineChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* System Cost */}
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      System Cost Trend
                    </Typography>
                    <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                      <ResponsiveContainer>
                        <BarChart data={timeSeriesData}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <RTooltip />
                          <Legend />
                          <Bar dataKey="cost" fill="#0ea5e9" name="Cost" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Renewability Trend */}
              <Grid item xs={12} md={6}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      Renewability Trend
                    </Typography>
                    <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                      <ResponsiveContainer>
                        <AreaChart data={timeSeriesData}>
                          <defs>
                            <linearGradient id="renewabilityGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <RTooltip />
                          <Legend />
                          <Area type="monotone" dataKey="renewability" stroke="#10b981" fill="url(#renewabilityGradient)" name="Renewability (%)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Energy Mix Radar */}
              {energyMixData.length > 0 && (
                <Grid item xs={12} md={6}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                        Energy Mix Distribution
                      </Typography>
                      <Box sx={{ width: '100%', height: 300, mt: 2 }}>
                        <ResponsiveContainer>
                          <RadarChart data={energyMixData}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="key" />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} />
                            <Radar name="Mix %" dataKey="value" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.3} />
                            <RTooltip />
                          </RadarChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Box>
        )}

        {/* Details Tab */}
        {activeTab === 3 && (
          <Box>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Scenario Information
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableBody>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600, width: '40%' }}>ID</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {scenario.id}
                              <Tooltip title="Copy ID">
                                <IconButton onClick={handleCopyId} size="small" sx={{ p: 0.5 }}>
                                  <ContentCopy fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Area Code</TableCell>
                          <TableCell>{scenario.area_code || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Start Year</TableCell>
                          <TableCell>{scenario.start_year || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>End Year</TableCell>
                          <TableCell>{scenario.end_year || 'N/A'}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Created</TableCell>
                          <TableCell>{formatDate(scenario.created_at)}</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell sx={{ fontWeight: 600 }}>Updated</TableCell>
                          <TableCell>{formatDate(scenario.updated_at)}</TableCell>
                        </TableRow>
                        {scenario.source && (
                          <TableRow>
                            <TableCell sx={{ fontWeight: 600 }}>Source</TableCell>
                            <TableCell>{scenario.source}</TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 3, height: '100%' }}>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    User Values
                    {scenario.user_values && Object.keys(scenario.user_values).length > 0 && (
                      <Chip 
                        label={`${Object.keys(scenario.user_values).length} inputs`} 
                        size="small" 
                        sx={{ ml: 1 }} 
                      />
                    )}
                  </Typography>
                  {scenario.user_values && Object.keys(scenario.user_values).length > 0 ? (
                    <TableContainer sx={{ maxHeight: 400 }}>
                      <Table size="small" stickyHeader>
                        <TableHead>
                          <TableRow>
                            <TableCell sx={{ fontWeight: 600 }}>Input</TableCell>
                            <TableCell align="right" sx={{ fontWeight: 600 }}>Value</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {Object.entries(scenario.user_values).slice(0, 20).map(([key, value]) => (
                            <TableRow key={key} hover>
                              <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                                {key}
                              </TableCell>
                              <TableCell align="right" sx={{ fontFamily: 'monospace' }}>
                                {String(value)}
                              </TableCell>
                            </TableRow>
                          ))}
                          {Object.keys(scenario.user_values).length > 20 && (
                            <TableRow>
                              <TableCell colSpan={2} align="center">
                                <Typography variant="body2" color="text.secondary">
                                  ... and {Object.keys(scenario.user_values).length - 20} more inputs
                                </Typography>
                              </TableCell>
                            </TableRow>
                          )}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                      No user values set for this scenario.
                    </Typography>
                  )}
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default ScenarioDetail;
