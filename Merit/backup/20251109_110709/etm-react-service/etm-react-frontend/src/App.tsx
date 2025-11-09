import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { ScenarioProvider } from './contexts/ScenarioContext';
import Layout from './components/Layout';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import ScenarioBuilder from './pages/ScenarioBuilder';
import ScenarioDetail from './pages/ScenarioDetail';
import ScenarioList from './pages/ScenarioList';
import RealTimeAnalysis from './pages/RealTimeAnalysis';
import RenewableIntegration from './pages/RenewableIntegration';
import ComprehensiveReports from './pages/ComprehensiveReports';
import EnergyMixStudio from './pages/EnergyMixStudio';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#4caf50',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ScenarioProvider>
        <Router basename="/dt">
          <Routes>
            <Route path="/rta" element={<RealTimeAnalysis />} />
            <Route path="/renewable" element={<RenewableIntegration />} />
            <Route path="/otg" element={<ComprehensiveReports />} />
            <Route path="/studio" element={<EnergyMixStudio />} />
            <Route path="/" element={<Layout><Home /></Layout>} />
            <Route path="/scenario/new" element={<Layout><ScenarioBuilder /></Layout>} />
            <Route path="/scenario/:id" element={<Layout><ScenarioDetail /></Layout>} />
            <Route path="/scenarios" element={<Layout><ScenarioList /></Layout>} />
            <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
          </Routes>
        </Router>
      </ScenarioProvider>
    </ThemeProvider>
  );
};

export default App;
