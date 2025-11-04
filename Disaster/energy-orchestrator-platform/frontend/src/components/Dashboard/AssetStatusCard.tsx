import { Card, CardContent, Typography, Box, Chip } from '@mui/material'
import { Dashboard, CheckCircle, Error, Warning } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getAssets } from '../../services/api'

const AssetStatusCard = () => {
  const { data: assets, isLoading } = useQuery({
    queryKey: ['assets'],
    queryFn: getAssets,
    refetchInterval: 10000,
  })

  const assetList = assets || []
  const onlineCount = assetList.filter((a: any) => a.status === 'online').length
  const offlineCount = assetList.filter((a: any) => a.status === 'offline').length
  const maintenanceCount = assetList.filter((a: any) => a.status === 'maintenance').length

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Dashboard color="primary" />
          <Typography variant="h6">Asset Status</Typography>
        </Box>

        <Box display="flex" flexDirection="column" gap={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <CheckCircle color="success" fontSize="small" />
              <Typography variant="body2">Online</Typography>
            </Box>
            <Chip label={onlineCount} size="small" color="success" />
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <Error color="error" fontSize="small" />
              <Typography variant="body2">Offline</Typography>
            </Box>
            <Chip label={offlineCount} size="small" color="error" />
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <Warning color="warning" fontSize="small" />
              <Typography variant="body2">Maintenance</Typography>
            </Box>
            <Chip label={maintenanceCount} size="small" color="warning" />
          </Box>

          <Box mt={1}>
            <Typography variant="caption" color="text.secondary">
              Total Assets: {assetList.length}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default AssetStatusCard




