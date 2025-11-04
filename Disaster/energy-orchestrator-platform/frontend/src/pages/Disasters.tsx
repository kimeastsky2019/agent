import { Grid, Box, Typography, Card, CardContent, Chip, Alert } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getDisasters } from '../services/api'

const Disasters = () => {
  const { data: disasters, isLoading } = useQuery({
    queryKey: ['disasters'],
    queryFn: getDisasters,
  })

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Disaster Events
      </Typography>
      
      <Grid container spacing={3}>
        {isLoading ? (
          <Grid item xs={12}>
            <Typography>Loading...</Typography>
          </Grid>
        ) : (
          (disasters || []).map((disaster: any) => (
            <Grid item xs={12} sm={6} md={4} key={disaster.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="h6">{disaster.event_type}</Typography>
                    <Chip
                      label={`Severity ${disaster.severity}`}
                      color={disaster.severity >= 4 ? 'error' : disaster.severity >= 3 ? 'warning' : 'info'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Status: {disaster.status}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Location: {disaster.location?.lat?.toFixed(4)}, {disaster.location?.lon?.toFixed(4)}
                  </Typography>
                  {disaster.affected_radius_km && (
                    <Typography variant="body2" color="text.secondary">
                      Affected Radius: {disaster.affected_radius_km} km
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  )
}

export default Disasters




