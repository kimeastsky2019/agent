import { useEffect, useState } from 'react'
import { Box, Card, CardContent, Typography } from '@mui/material'
import Map, { Marker, Popup } from 'react-map-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { LocationOn } from '@mui/icons-material'

// Mapbox 토큰은 환경변수에서 가져오거나 공개 토큰 사용
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoidGVzdCIsImEiOiJjbGV4YW1wbGUifQ.test'

interface Asset {
  id: string
  name: string
  type: string
  location: { lat: number; lon: number }
  capacity_kw: number
  status: string
}

const EnergyMap = () => {
  const [viewport, setViewport] = useState({
    latitude: 35.6762,
    longitude: 139.6503,
    zoom: 10,
  })
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [assets, setAssets] = useState<Asset[]>([])

  useEffect(() => {
    // Mock 데이터 - 실제로는 API에서 가져옴
    setAssets([
      {
        id: '1',
        name: 'Solar Farm Tokyo',
        type: 'solar',
        location: { lat: 35.6762, lon: 139.6503 },
        capacity_kw: 1000,
        status: 'online',
      },
      {
        id: '2',
        name: 'Wind Farm Yokohama',
        type: 'wind',
        location: { lat: 35.4437, lon: 139.6380 },
        capacity_kw: 500,
        status: 'online',
      },
      {
        id: '3',
        name: 'Battery Storage Osaka',
        type: 'battery',
        location: { lat: 34.6937, lon: 135.5023 },
        capacity_kw: 200,
        status: 'online',
      },
    ])
  }, [])

  const getMarkerColor = (type: string) => {
    switch (type) {
      case 'solar':
        return '#FFD700'
      case 'wind':
        return '#87CEEB'
      case 'battery':
        return '#32CD32'
      default:
        return '#FF0000'
    }
  }

  return (
    <Card sx={{ height: '600px', mb: 3 }}>
      <CardContent sx={{ height: '100%', p: 0 }}>
        <Box sx={{ position: 'relative', height: '100%' }}>
          <Typography variant="h6" sx={{ p: 2, pb: 0 }}>
            Energy Assets Map
          </Typography>
          <Map
            {...viewport}
            onMove={evt => setViewport(evt.viewState)}
            style={{ width: '100%', height: 'calc(100% - 56px)' }}
            mapStyle="mapbox://styles/mapbox/streets-v12"
            mapboxAccessToken={MAPBOX_TOKEN}
          >
            {assets.map((asset) => (
              <Marker
                key={asset.id}
                latitude={asset.location.lat}
                longitude={asset.location.lon}
                anchor="bottom"
                onClick={() => setSelectedAsset(asset)}
              >
                <LocationOn
                  sx={{
                    color: getMarkerColor(asset.type),
                    fontSize: 40,
                    cursor: 'pointer',
                  }}
                />
              </Marker>
            ))}
            
            {selectedAsset && (
              <Popup
                latitude={selectedAsset.location.lat}
                longitude={selectedAsset.location.lon}
                anchor="bottom"
                onClose={() => setSelectedAsset(null)}
                closeOnClick={false}
              >
                <Box sx={{ p: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold">
                    {selectedAsset.name}
                  </Typography>
                  <Typography variant="body2">Type: {selectedAsset.type}</Typography>
                  <Typography variant="body2">Capacity: {selectedAsset.capacity_kw} kW</Typography>
                  <Typography variant="body2">Status: {selectedAsset.status}</Typography>
                </Box>
              </Popup>
            )}
          </Map>
        </Box>
      </CardContent>
    </Card>
  )
}

export default EnergyMap




