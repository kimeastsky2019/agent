import React, { useState } from 'react';
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
  SmartToy,
} from '@mui/icons-material';
import apiClient from '../services/api';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleRealTimeAnalysis = () => {
    // Navigate directly to Real-time Analysis page
    navigate('/rta');
  };

  const features = [
    {
      icon: <Public sx={{ fontSize: 60, color: 'primary.main' }} />,
      title: 'Global Scenarios',
      description: 'Create energy transition scenarios for any country or region',
      onClick: () => navigate('/studio'),
    },
    {
      icon: <TrendingUp sx={{ fontSize: 60, color: 'success.main' }} />,
      title: 'Real-time Analysis',
      description: 'See instant results as you adjust your energy mix',
      onClick: handleRealTimeAnalysis,
    },
    {
      icon: <EmojiObjects sx={{ fontSize: 60, color: 'warning.main' }} />,
      title: 'Renewable Integration',
      description: 'Optimize solar, wind, and other renewable energy sources',
      onClick: () => navigate('/renewable'),
    },
    {
      icon: <Assessment sx={{ fontSize: 60, color: 'info.main' }} />,
      title: 'Collaborative Ontology Building',
      description: 'Enable multiple stakeholders to co-create /shared knowledge',
      onClick: () => navigate('/otg'),
    },
    {
      icon: <SmartToy sx={{ fontSize: 60, color: 'secondary.main' }} />,
      title: 'AI Agent',
      description: 'Intelligent energy orchestration and optimization platform',
      onClick: () => window.open('http://agent.gngmeta.com/eop', '_blank'),
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
          onClick={() => window.open('http://agent.gngmeta.com/eop', '_blank')}
          sx={{ px: 4, py: 1.5, fontSize: '1.1rem', ml: 2 }}
        >
          AI Agent
        </Button>
      </Box>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(5, 1fr)',
          },
          gap: 4,
          mt: 4,
        }}
      >
        {features.map((feature, index) => (
          <Card
            key={index}
            onClick={feature.onClick}
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              p: 2,
              transition: 'transform 0.2s',
              cursor: 'pointer',
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
        ))}
      </Box>

      {/* G&G International Logo */}
      <Box
        sx={{
          mt: 8,
          mb: 4,
          textAlign: 'center',
          py: 6,
          borderTop: 1,
          borderColor: 'divider',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 1,
            mb: 1,
          }}
        >
          <Typography
            variant="h3"
            component="span"
            sx={{
              fontWeight: 'bold',
              color: '#212121',
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            G
          </Typography>
          <Typography
            variant="h3"
            component="span"
            sx={{
              fontWeight: 'bold',
              color: '#212121',
              fontSize: { xs: '1.5rem', md: '2.25rem' },
            }}
          >
            &
          </Typography>
          <Typography
            variant="h3"
            component="span"
            sx={{
              fontWeight: 'bold',
              color: '#1b5e20',
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            G
          </Typography>
          <Box
            sx={{
              position: 'relative',
              display: 'inline-flex',
              alignItems: 'center',
              ml: 1,
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                top: -8,
                left: 0,
                right: 0,
                height: 3,
                background: 'linear-gradient(90deg, transparent 0%, #ff9800 50%, transparent 100%)',
                borderRadius: 1,
                transform: 'skewY(-2deg)',
              }}
            />
            <Typography
              variant="h5"
              component="span"
              sx={{
                fontWeight: 500,
                color: '#000000',
                fontSize: { xs: '1rem', md: '1.5rem' },
                textTransform: 'none',
                letterSpacing: 0,
              }}
            >
              International
            </Typography>
          </Box>
        </Box>
        <Typography
          variant="body1"
          sx={{
            color: '#424242',
            fontWeight: 500,
            fontSize: { xs: '0.875rem', md: '1rem' },
            mt: 1,
            mb: 3,
          }}
        >
          Good People & Green Society
        </Typography>

        {/* Designed for GnG International Section */}
        <Typography
          variant="h5"
          sx={{
            color: '#212121',
            fontWeight: 600,
            fontSize: { xs: '1.25rem', md: '1.5rem' },
            mb: 1,
          }}
        >
          Designed for GnG International
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: '#424242',
            fontWeight: 500,
            fontSize: { xs: '0.875rem', md: '1rem' },
          }}
        >
          Integrated with SolarGuard AI and NanoGrid AI for comprehensive energy
          management solutions
        </Typography>
      </Box>
    </Container>
  );
};

export default Home;
