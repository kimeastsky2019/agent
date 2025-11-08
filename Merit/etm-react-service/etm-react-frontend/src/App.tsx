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
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/scenario/new" element={<ScenarioBuilder />} />
              <Route path="/scenario/:id" element={<ScenarioDetail />} />
              <Route path="/scenarios" element={<ScenarioList />} />
              <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
          </Layout>
        </Router>
      </ScenarioProvider>
    </ThemeProvider>
  );
};

export default App;
