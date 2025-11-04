import { Grid, Box, Typography } from '@mui/material'
import EnergyMap from '../components/EnergyMap'
import WeatherCard from '../components/WeatherCard'
import EnergyBalanceCard from '../components/Dashboard/EnergyBalanceCard'
import DisasterAlertCard from '../components/DisasterAlert/DisasterAlertCard'
import AssetStatusCard from '../components/Dashboard/AssetStatusCard'

const Home = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* 지도 영역 - 전체 너비 */}
        <Grid item xs={12}>
          <EnergyMap />
        </Grid>
        
        {/* 카드들 */}
        <Grid item xs={12} md={6} lg={3}>
          <EnergyBalanceCard />
        </Grid>
        
        <Grid item xs={12} md={6} lg={3}>
          <AssetStatusCard />
        </Grid>
        
        <Grid item xs={12} md={6} lg={3}>
          <DisasterAlertCard />
        </Grid>
        
        <Grid item xs={12} md={6} lg={3}>
          <WeatherCard lat={35.6762} lon={139.6503} />
        </Grid>
      </Grid>
    </Box>
  )
}

export default Home




