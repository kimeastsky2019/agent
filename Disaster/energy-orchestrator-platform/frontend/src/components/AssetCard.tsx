import { Card, CardContent, CardActions, Typography, Box, Button, Chip, IconButton } from '@mui/material'
import { OpenInNew, Edit, Delete, BarChart } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'

interface AssetCardProps {
  asset: {
    id: string
    name: string
    type: string
    capacity_kw: number
    status: string
    service_type?: string
    created_at?: string
  }
  onEdit?: (asset: any) => void
  onDelete?: (assetId: string) => void
}

const AssetCard = ({ asset, onEdit, onDelete }: AssetCardProps) => {
  const navigate = useNavigate()

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'solar':
        return '☀️'
      case 'wind':
        return '💨'
      case 'battery':
        return '🔋'
      case 'demand':
        return '📊'
      default:
        return '⚡'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'solar':
        return '#FFD700'
      case 'wind':
        return '#87CEEB'
      case 'battery':
        return '#32CD32'
      case 'demand':
        return '#667eea'
      default:
        return '#9e9e9e'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'online':
        return 'success'
      case 'offline':
        return 'error'
      case 'maintenance':
        return 'warning'
      default:
        return 'default'
    }
  }

  const handleOpenService = () => {
    if (asset.service_type === 'demand') {
      // Demand 분석 서비스로 이동
      navigate(`/demand-analysis/${asset.id}`)
    } else if (asset.service_type === 'supply') {
      // Supply 분석 서비스로 이동
      navigate(`/supply-analysis/${asset.id}`)
    } else {
      // 기본적으로 supply로 이동
      navigate(`/supply-analysis/${asset.id}`)
    }
  }

  const handleOpenDigitalTwin = () => {
    navigate(`/digital-twin/${asset.id}`)
  }

  return (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Typography variant="h4">{getTypeIcon(asset.type)}</Typography>
          <Box flex={1}>
            <Typography variant="h6" fontWeight="bold">
              {asset.name}
            </Typography>
            <Chip
              label={asset.type.toUpperCase()}
              size="small"
              sx={{
                backgroundColor: getTypeColor(asset.type),
                color: 'white',
                fontSize: '0.7rem',
                mt: 0.5,
              }}
            />
          </Box>
        </Box>

        <Box display="flex" flexDirection="column" gap={1} mb={2}>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              용량
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {asset.capacity_kw > 0 ? `${asset.capacity_kw} kW` : '-'}
            </Typography>
          </Box>
          <Box display="flex" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary">
              상태
            </Typography>
            <Chip
              label={asset.status}
              size="small"
              color={getStatusColor(asset.status) as any}
            />
          </Box>
          {asset.created_at && (
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                생성일
              </Typography>
              <Typography variant="body2">
                {new Date(asset.created_at).toLocaleDateString('ko-KR')}
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2, flexDirection: 'column', gap: 1 }}>
        <Box display="flex" justifyContent="space-between" width="100%">
          <Box>
            {onEdit && (
              <IconButton
                size="small"
                color="primary"
                onClick={() => onEdit(asset)}
              >
                <Edit fontSize="small" />
              </IconButton>
            )}
            {onDelete && (
              <IconButton
                size="small"
                color="error"
                onClick={() => onDelete(asset.id)}
              >
                <Delete fontSize="small" />
              </IconButton>
            )}
          </Box>
        </Box>
        <Box display="flex" gap={1} width="100%">
          {asset.service_type && (
            <Button
              variant="contained"
              size="small"
              startIcon={<OpenInNew />}
              onClick={handleOpenService}
              sx={{
                flex: 1,
                backgroundColor: asset.service_type === 'demand' ? '#667eea' : '#ff9800',
                '&:hover': {
                  backgroundColor: asset.service_type === 'demand' ? '#5568d3' : '#f57c00',
                },
              }}
            >
              분석
            </Button>
          )}
          <Button
            variant="outlined"
            size="small"
            startIcon={<OpenInNew />}
            onClick={handleOpenDigitalTwin}
            sx={{
              flex: 1,
              borderColor: '#00bcd4',
              color: '#00bcd4',
              '&:hover': {
                borderColor: '#0097a7',
                backgroundColor: 'rgba(0, 188, 212, 0.1)',
              },
            }}
          >
            디지털 트윈
          </Button>
        </Box>
      </CardActions>
    </Card>
  )
}

export default AssetCard

