import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  MenuItem,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useScenario } from '../contexts/ScenarioContext';
import apiClient, { Area } from '../services/api';

const ScenarioBuilder: React.FC = () => {
  const navigate = useNavigate();
  const { createScenario, loading, error, clearScenario } = useScenario();
  
  const [areaCode, setAreaCode] = useState('nl');
  const [endYear, setEndYear] = useState(2050);
  const [title, setTitle] = useState('');
  const [areas, setAreas] = useState<Area[]>([]);
  const [loadingAreas, setLoadingAreas] = useState(true);

  // Clear any previous errors when component mounts
  useEffect(() => {
    clearScenario();
  }, [clearScenario]);

  useEffect(() => {
    const fetchAreas = async () => {
      setLoadingAreas(true);
      try {
        const fetchedAreas = await apiClient.getAreas();
        if (fetchedAreas && fetchedAreas.length > 0) {
          // Transform API response to match expected format
          const transformedAreas = fetchedAreas.map((area: any) => ({
            code: area.area || area.code || area.id,
            name: area.name || area.area || area.code || `Area ${area.id}`,
          }));
          setAreas(transformedAreas);
          if (!transformedAreas.find((a: any) => a.code === areaCode)) {
            setAreaCode(transformedAreas[0].code);
          }
        } else {
          // Fallback to default list if API returns empty
          setAreas([
            { code: 'nl', name: 'Netherlands' },
            { code: 'de', name: 'Germany' },
            { code: 'uk', name: 'United Kingdom' },
            { code: 'fr', name: 'France' },
          ]);
        }
      } catch (err: any) {
        console.error('Failed to fetch areas:', err);
        // Fallback to default list if API fails
        setAreas([
          { code: 'nl', name: 'Netherlands' },
          { code: 'de', name: 'Germany' },
          { code: 'uk', name: 'United Kingdom' },
          { code: 'fr', name: 'France' },
        ]);
      } finally {
        setLoadingAreas(false);
      }
    };
    fetchAreas();
  }, []);

  const years = Array.from({ length: 8 }, (_, i) => 2030 + i * 5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createScenario(areaCode, endYear, title);
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to create scenario:', err);
      // Error is already set in context, will be displayed
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Scenario
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Build your energy transition scenario by selecting a region and target year
        </Typography>

        {error && !error.includes('404') && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Scenario Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            margin="normal"
            placeholder="e.g., Korea 2050 Carbon Neutral"
          />

          <TextField
            fullWidth
            select
            label="Country/Region"
            value={areaCode}
            onChange={(e) => setAreaCode(e.target.value)}
            margin="normal"
            required
            disabled={loadingAreas}
          >
            {areas.map((area) => (
              <MenuItem key={area.code} value={area.code}>
                {area.name || area.code}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            select
            label="Target Year"
            value={endYear}
            onChange={(e) => setEndYear(Number(e.target.value))}
            margin="normal"
            required
          >
            {years.map((year) => (
              <MenuItem key={year} value={year}>
                {year}
              </MenuItem>
            ))}
          </TextField>

          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/')}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={loading}
              sx={{ flexGrow: 1 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Create Scenario'}
            </Button>
          </Box>
        </form>
      </Paper>
    </Box>
  );
};

export default ScenarioBuilder;
