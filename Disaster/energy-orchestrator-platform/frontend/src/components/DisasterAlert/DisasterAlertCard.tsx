import { Card, CardContent, Typography, Box, Chip, Alert } from '@mui/material'
import { Warning, CheckCircle } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getActiveDisasters } from '../../services/api'

const DisasterAlertCard = () => {
  const { data: activeDisasters, isLoading } = useQuery({
    queryKey: ['activeDisasters'],
    queryFn: getActiveDisasters,
    refetchInterval: 30000,
  })

  const disasters = activeDisasters || []
  const highSeverity = disasters.filter((d: any) => d.severity >= 4).length
  const mediumSeverity = disasters.filter((d: any) => d.severity >= 3 && d.severity < 4).length

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Warning color="warning" />
          <Typography variant="h6">Disaster Alerts</Typography>
        </Box>

        {disasters.length === 0 ? (
          <Box display="flex" alignItems="center" gap={1}>
            <CheckCircle color="success" />
            <Typography variant="body2" color="text.secondary">
              No active disasters
            </Typography>
          </Box>
        ) : (
          <Box display="flex" flexDirection="column" gap={2}>
            {highSeverity > 0 && (
              <Alert severity="error">
                {highSeverity} High Severity Disaster{highSeverity > 1 ? 's' : ''}
              </Alert>
            )}
            {mediumSeverity > 0 && (
              <Alert severity="warning">
                {mediumSeverity} Medium Severity Disaster{mediumSeverity > 1 ? 's' : ''}
              </Alert>
            )}
            
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Active Disasters: {disasters.length}
              </Typography>
              {disasters.slice(0, 3).map((disaster: any) => (
                <Chip
                  key={disaster.id}
                  label={disaster.event_type}
                  size="small"
                  color={disaster.severity >= 4 ? 'error' : 'warning'}
                  sx={{ mr: 0.5, mb: 0.5 }}
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default DisasterAlertCard




