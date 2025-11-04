import { useEffect, useState } from 'react'
import { Card, CardContent, Typography, Box, Chip, CircularProgress } from '@mui/material'
import { Cloud, WbSunny, AcUnit, WaterDrop, Air } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getCurrentWeather, getWeatherForecast } from '../services/api'

interface WeatherCardProps {
  lat: number
  lon: number
}

const WeatherCard = ({ lat, lon }: WeatherCardProps) => {
  const { data: weather, isLoading } = useQuery({
    queryKey: ['weather', lat, lon],
    queryFn: () => getCurrentWeather(lat, lon),
    refetchInterval: 300000, // 5분마다 갱신
  })

  const { data: forecast } = useQuery({
    queryKey: ['weatherForecast', lat, lon],
    queryFn: () => getWeatherForecast(lat, lon, 3),
  })

  const getWeatherIcon = (main: string) => {
    switch (main.toLowerCase()) {
      case 'clear':
        return <WbSunny sx={{ fontSize: 40, color: '#FFD700' }} />
      case 'clouds':
        return <Cloud sx={{ fontSize: 40, color: '#87CEEB' }} />
      case 'rain':
        return <WaterDrop sx={{ fontSize: 40, color: '#4169E1' }} />
      case 'snow':
        return <AcUnit sx={{ fontSize: 40, color: '#E0E0E0' }} />
      default:
        return <Cloud sx={{ fontSize: 40 }} />
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    )
  }

  if (!weather) {
    return (
      <Card>
        <CardContent>
          <Typography>Weather data not available</Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Weather Information
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          {getWeatherIcon(weather.weather?.main || 'clear')}
          <Box>
            <Typography variant="h4" fontWeight="bold">
              {Math.round(weather.main?.temp || 0)}°C
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {weather.weather?.description || 'N/A'}
            </Typography>
          </Box>
        </Box>

        <Box display="flex" flexDirection="column" gap={1}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <Air fontSize="small" />
              <Typography variant="body2">Wind</Typography>
            </Box>
            <Typography variant="body2" fontWeight="bold">
              {weather.wind?.speed?.toFixed(1) || 0} m/s
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box display="flex" alignItems="center" gap={1}>
              <WaterDrop fontSize="small" />
              <Typography variant="body2">Humidity</Typography>
            </Box>
            <Typography variant="body2" fontWeight="bold">
              {weather.main?.humidity || 0}%
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">Pressure</Typography>
            <Typography variant="body2" fontWeight="bold">
              {weather.main?.pressure || 0} hPa
            </Typography>
          </Box>

          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2">Feels like</Typography>
            <Typography variant="body2" fontWeight="bold">
              {Math.round(weather.main?.feels_like || 0)}°C
            </Typography>
          </Box>
        </Box>

        {forecast && forecast.forecast && forecast.forecast.length > 0 && (
          <Box mt={2}>
            <Typography variant="subtitle2" gutterBottom>
              3-Day Forecast
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {forecast.forecast.slice(0, 3).map((item: any, index: number) => (
                <Chip
                  key={index}
                  label={`${Math.round(item.temp)}°C`}
                  size="small"
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default WeatherCard




