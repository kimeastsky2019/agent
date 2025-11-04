import { useEffect } from 'react'
import { Card, CardContent, Typography, Box, LinearProgress } from '@mui/material'
import { FlashOn, TrendingUp } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getEnergyBalance } from '../../services/api'

const EnergyBalanceCard = () => {
  const { data: balance, isLoading } = useQuery({
    queryKey: ['energyBalance'],
    queryFn: getEnergyBalance,
    refetchInterval: 5000,
  })

  if (isLoading || !balance) {
    return (
      <Card>
        <CardContent>
          <Typography>Loading...</Typography>
        </CardContent>
      </Card>
    )
  }

  const utilization = balance.total_production > 0
    ? (balance.total_consumption / balance.total_production) * 100
    : 0

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <FlashOn color="primary" />
          <Typography variant="h6">Energy Balance</Typography>
        </Box>

        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Production
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {balance.total_production?.toFixed(1) || 0} kW
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Consumption
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {balance.total_consumption?.toFixed(1) || 0} kW
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              Balance
            </Typography>
            <Typography
              variant="body2"
              fontWeight="bold"
              color={balance.balance >= 0 ? 'success.main' : 'error.main'}
            >
              {balance.balance >= 0 ? '+' : ''}{balance.balance?.toFixed(1) || 0} kW
            </Typography>
          </Box>
        </Box>

        <Box>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="caption" color="text.secondary">
              Utilization
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {utilization.toFixed(1)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(utilization, 100)}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Box>
      </CardContent>
    </Card>
  )
}

export default EnergyBalanceCard




