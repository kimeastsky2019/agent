import { Outlet, Link, useLocation } from 'react-router-dom'
import { Box, AppBar, Toolbar, Typography, Container, Tabs, Tab } from '@mui/material'
import { Dashboard, FlashOn, Warning, Analytics, Cloud } from '@mui/icons-material'

const Layout = () => {
  const location = useLocation()
  
  const getTabValue = () => {
    if (location.pathname === '/') return 0
    if (location.pathname === '/assets') return 1
    if (location.pathname === '/disasters') return 2
    if (location.pathname === '/analytics') return 3
    if (location.pathname === '/weather') return 4
    return 0
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static" elevation={2}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Energy Orchestrator Platform
          </Typography>
          <Tabs value={getTabValue()} textColor="inherit" indicatorColor="secondary">
            <Tab icon={<Dashboard />} label="Dashboard" component={Link} to="/" />
            <Tab icon={<FlashOn />} label="Assets" component={Link} to="/assets" />
            <Tab icon={<Warning />} label="Disasters" component={Link} to="/disasters" />
            <Tab icon={<Analytics />} label="Analytics" component={Link} to="/analytics" />
            <Tab icon={<Cloud />} label="Weather" component={Link} to="/weather" />
          </Tabs>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4, flex: 1 }}>
        <Outlet />
      </Container>
    </Box>
  )
}

export default Layout

