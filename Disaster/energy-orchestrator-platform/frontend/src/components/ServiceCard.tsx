import { Card, CardContent, Typography, Box, Button, Chip } from '@mui/material'
import { OpenInNew, TrendingUp, SolarPower } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

interface ServiceCardProps {
  assetId: string
  title: string
  subtitle: string
  value: string | number
  gradient: string
  icon: React.ReactNode
  serviceType: 'demand' | 'supply' | 'digitaltwin'
}

const ServiceCard = ({
  assetId,
  title,
  subtitle,
  value,
  gradient,
  icon,
  serviceType,
}: ServiceCardProps) => {
  const navigate = useNavigate()

  const handleOpen = () => {
    if (serviceType === 'demand') {
      navigate(`/demand-analysis/${assetId}`)
    } else if (serviceType === 'supply') {
      navigate(`/supply-analysis/${assetId}`)
    } else if (serviceType === 'digitaltwin') {
      navigate(`/digital-twin/${assetId}`)
    }
  }

  return (
    <Card
      sx={{
        background: gradient,
        color: 'white',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 6,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Box sx={{ fontSize: '3rem' }}>{icon}</Box>
          <Box>
            <Typography variant="h2" fontWeight="bold" sx={{ mb: 0.5 }}>
              {value}
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {title}
            </Typography>
          </Box>
        </Box>

        <Typography variant="body2" sx={{ opacity: 0.9, mb: 2 }}>
          {subtitle}
        </Typography>

        <Box sx={{ mt: 'auto' }}>
          <Button
            variant="contained"
            fullWidth
            endIcon={<OpenInNew />}
            onClick={handleOpen}
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
              },
            }}
          >
            열기
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}

export default ServiceCard

