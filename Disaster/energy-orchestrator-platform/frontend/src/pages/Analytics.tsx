import { Box, Typography, Card, CardContent } from '@mui/material'

const Analytics = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Analytics
      </Typography>
      
      <Card>
        <CardContent>
          <Typography variant="h6">Analytics Dashboard</Typography>
          <Typography variant="body2" color="text.secondary">
            Analytics features will be implemented here.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  )
}

export default Analytics




