import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Container,
} from '@mui/material';
import {
  TrendingUp,
  EmojiObjects,
  Assessment,
  Public,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Public sx={{ fontSize: 60, color: 'primary.main' }} />,
      title: 'Global Scenarios',
      description: 'Create energy transition scenarios for any country or region',
    },
    {
      icon: <TrendingUp sx={{ fontSize: 60, color: 'success.main' }} />,
      title: 'Real-time Analysis',
      description: 'See instant results as you adjust your energy mix',
    },
    {
      icon: <EmojiObjects sx={{ fontSize: 60, color: 'warning.main' }} />,
      title: 'Renewable Integration',
      description: 'Optimize solar, wind, and other renewable energy sources',
    },
    {
      icon: <Assessment sx={{ fontSize: 60, color: 'info.main' }} />,
      title: 'Comprehensive Reports',
      description: 'Generate detailed CO2, cost, and energy mix reports',
    },
  ];

  return (
    <Container maxWidth="lg">
      <Box
        sx={{
          textAlign: 'center',
          py: 8,
        }}
      >
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 'bold', mb: 2 }}
        >
          Energy Transition Model
        </Typography>
        <Typography
          variant="h5"
          component="h2"
          color="text.secondary"
          paragraph
          sx={{ mb: 4 }}
        >
          Design the future of energy - Model scenarios, analyze impacts, and
          optimize renewable integration
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/scenario/new')}
          sx={{ mr: 2, px: 4, py: 1.5, fontSize: '1.1rem' }}
        >
          Create New Scenario
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/dashboard')}
          sx={{ px: 4, py: 1.5, fontSize: '1.1rem' }}
        >
          View Dashboard
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/scenarios')}
          sx={{ px: 4, py: 1.5, fontSize: '1.1rem', ml: 2 }}
        >
          Browse Scenarios
        </Button>
      </Box>

      <Grid container spacing={4} sx={{ mt: 4 }}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                p: 2,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent>
                <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                <Typography variant="h6" component="h3" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 8, textAlign: 'center', py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Designed for GnG International
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Integrated with SolarGuard AI and NanoGrid AI for comprehensive energy
          management solutions
        </Typography>
      </Box>
    </Container>
  );
};

export default Home;
