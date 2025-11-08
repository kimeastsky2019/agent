import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material';
import {
  LocationOn,
  CalendarToday,
  Visibility,
  Delete,
  Add,
} from '@mui/icons-material';
import apiClient from '../services/api';
import { Scenario } from '../services/api';

const ScenarioList: React.FC = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.listScenarios();
      setScenarios(data);
    } catch (err: any) {
      setError(
        err instanceof Error ? err.message : 'Failed to load scenarios'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this scenario?')) {
      return;
    }

    try {
      await apiClient.deleteScenario(id);
      loadScenarios();
    } catch (err) {
      console.error('Failed to delete scenario:', err);
      alert('Failed to delete scenario');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Scenarios
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => navigate('/scenario/new')}
          >
            Create New Scenario
          </Button>
        </Box>

        {scenarios.length === 0 ? (
          <Alert severity="info" sx={{ mt: 4 }}>
            No scenarios found. Create your first scenario to get started!
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {scenarios.map((scenario) => (
              <Grid item xs={12} sm={6} md={4} key={scenario.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    cursor: 'pointer',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                  onClick={() => navigate(`/scenario/${scenario.id}`)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2" gutterBottom>
                      {scenario.title || `${scenario.area_code} ${scenario.end_year} Scenario`}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                      <Chip
                        icon={<LocationOn />}
                        label={scenario.area_code}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        icon={<CalendarToday />}
                        label={`${scenario.end_year}`}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                      {scenario.private && (
                        <Chip label="Private" size="small" color="warning" />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Created: {formatDate(scenario.created_at)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Updated: {formatDate(scenario.updated_at)}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                    <Button
                      size="small"
                      startIcon={<Visibility />}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/scenario/${scenario.id}`);
                      }}
                    >
                      View
                    </Button>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={(e) => handleDelete(scenario.id, e)}
                    >
                      <Delete />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default ScenarioList;

