import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Slider,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useScenario } from '../contexts/ScenarioContext';

const Dashboard: React.FC = () => {
  const { scenario, loading, error, updateInputs, fetchResults, results } = useScenario();
  
  const [solarCapacity, setSolarCapacity] = useState(50);
  const [windCapacity, setWindCapacity] = useState(30);
  const [nuclearCapacity, setNuclearCapacity] = useState(10);

  useEffect(() => {
    if (scenario) {
      // Fetch initial results
      fetchResults([
        'co2',
        'renewability',
        'total_costs',
        'final_demand_electricity',
      ]);
    }
  }, [scenario, fetchResults]);

  const handleSliderChange = async () => {
    if (!scenario) return;
    
    try {
      await updateInputs({
        'capacity_of_energy_power_solar_pv_solar_radiation': solarCapacity * 1000,
        'capacity_of_energy_power_wind_turbine_offshore': windCapacity * 1000,
        'number_of_energy_power_nuclear_gen3_uranium_oxide': nuclearCapacity,
      });
      
      // Refresh results after updating inputs
      await fetchResults([
        'co2_emissions_of_used_electricity',
        'renewability',
        'total_costs',
        'final_demand_electricity',
      ]);
    } catch (err) {
      console.error('Failed to update:', err);
    }
  };

  if (!scenario) {
    return (
      <Alert severity="info">
        No active scenario. Please create a new scenario first.
      </Alert>
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  // Validate energy mix data
  const totalEnergy = solarCapacity + windCapacity + nuclearCapacity;
  const otherEnergy = Math.max(0, 100 - totalEnergy);

  const energyMixData = [
    { name: 'Solar', value: solarCapacity },
    { name: 'Wind', value: windCapacity },
    { name: 'Nuclear', value: nuclearCapacity },
    { name: 'Other', value: otherEnergy },
  ].filter(item => item.value > 0); // Only show non-zero values

  const co2Data = results['co2_emissions_of_used_electricity'] || results['co2'] || results['co2_emissions_total'];
  const renewable = results['renewability'] || results['dashboard_renewability'];
  const cost = results['total_costs'] || results['dashboard_total_costs'];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {scenario.title}
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Region: {scenario.area_code.toUpperCase()} | Target Year: {scenario.end_year}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Input Controls */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Energy Mix Controls
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Typography gutterBottom>
                Solar PV Capacity: {solarCapacity} GW
              </Typography>
              <Slider
                value={solarCapacity}
                onChange={(_, value) => setSolarCapacity(value as number)}
                onChangeCommitted={handleSliderChange}
                min={0}
                max={150}
                valueLabelDisplay="auto"
                disabled={loading}
              />
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography gutterBottom>
                Offshore Wind Capacity: {windCapacity} GW
              </Typography>
              <Slider
                value={windCapacity}
                onChange={(_, value) => setWindCapacity(value as number)}
                onChangeCommitted={handleSliderChange}
                min={0}
                max={100}
                valueLabelDisplay="auto"
                disabled={loading}
              />
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography gutterBottom>
                Nuclear Plants: {nuclearCapacity}
              </Typography>
              <Slider
                value={nuclearCapacity}
                onChange={(_, value) => setNuclearCapacity(value as number)}
                onChangeCommitted={handleSliderChange}
                min={0}
                max={30}
                valueLabelDisplay="auto"
                disabled={loading}
              />
            </Box>

            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <CircularProgress size={24} />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Key Metrics */}
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    CO2 Emissions
                  </Typography>
                  <Typography variant="h4">
                    {co2Data ? co2Data.future.toFixed(1) : '-'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Mton / year
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Renewable Share
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {renewable ? renewable.future.toFixed(1) : '-'}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    of total energy
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Cost
                  </Typography>
                  <Typography variant="h4">
                    {cost ? cost.future.toFixed(0) : '-'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    billion EUR
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Energy Mix Pie Chart */}
          <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Energy Mix Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={energyMixData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {energyMixData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>

          {/* CO2 Comparison */}
          {co2Data && (
            <Paper sx={{ p: 3, mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                CO2 Emissions Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={[
                    { name: 'Present', value: co2Data.present },
                    { name: 'Future', value: co2Data.future },
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8" name="CO2 (Mton)" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
