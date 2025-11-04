import { useState, useEffect } from 'react'
import { Grid, Box, Typography, Card, CardContent, CircularProgress, Alert, Chip, Button } from '@mui/material'
import { Refresh, Cloud, WbSunny, Air, WaterDrop, Visibility, Thermostat } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { getCurrentWeather, getWeatherForecast } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const Weather = () => {
  const [location, setLocation] = useState({ lat: 37.5665, lon: 126.9780 }) // 서울 기본값
  const [selectedRange, setSelectedRange] = useState<'hour' | 'day'>('hour')

  const { data: weather, isLoading, error, refetch } = useQuery({
    queryKey: ['weather', location.lat, location.lon],
    queryFn: () => getCurrentWeather(location.lat, location.lon),
    refetchInterval: 300000, // 5분마다 갱신
  })

  const { data: forecast } = useQuery({
    queryKey: ['weatherForecast', location.lat, location.lon],
    queryFn: () => getWeatherForecast(location.lat, location.lon, 7),
    enabled: !!location,
  })

  // 현재 위치 가져오기
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          })
        },
        (error) => {
          console.warn('위치 정보를 가져올 수 없습니다:', error)
        }
      )
    }
  }, [])

  const handleRefresh = () => {
    refetch()
  }

  const getWeatherIcon = (main?: string) => {
    if (!main) return <Cloud sx={{ fontSize: 60, color: '#87CEEB' }} />
    
    switch (main.toLowerCase()) {
      case 'clear':
        return <WbSunny sx={{ fontSize: 60, color: '#FFD700' }} />
      case 'clouds':
        return <Cloud sx={{ fontSize: 60, color: '#87CEEB' }} />
      case 'rain':
        return <WaterDrop sx={{ fontSize: 60, color: '#4169E1' }} />
      default:
        return <Cloud sx={{ fontSize: 60, color: '#87CEEB' }} />
    }
  }

  // 예보 데이터를 차트용으로 변환
  const forecastChartData = forecast?.forecast?.map((item: any) => ({
    date: new Date(item.dt).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
    temp: Math.round(item.temp || 0),
    feels_like: Math.round(item.feels_like || 0),
    humidity: item.humidity || 0,
  })) || []

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error">
        날씨 데이터를 불러오는 중 오류가 발생했습니다.
      </Alert>
    )
  }

  if (!weather) {
    return (
      <Alert severity="info">날씨 데이터가 없습니다.</Alert>
    )
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          날씨 분석 대시보드
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={handleRefresh}
        >
          새로고침
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* 현재 날씨 카드 */}
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {weather.location?.name || '현재 위치'}
                  </Typography>
                  <Typography variant="h2" fontWeight="bold">
                    {Math.round(weather.main?.temp || 0)}°C
                  </Typography>
                  <Typography variant="body1" sx={{ opacity: 0.9 }}>
                    {weather.weather?.description || 'N/A'}
                  </Typography>
                </Box>
                <Box>
                  {getWeatherIcon(weather.weather?.main)}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 날씨 통계 카드들 */}
        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Thermostat color="primary" />
                <Typography variant="body2" color="text.secondary">
                  체감온도
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {Math.round(weather.main?.feels_like || 0)}°C
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <WaterDrop color="primary" />
                <Typography variant="body2" color="text.secondary">
                  습도
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {weather.main?.humidity || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Air color="primary" />
                <Typography variant="body2" color="text.secondary">
                  풍속
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {weather.wind?.speed?.toFixed(1) || 0} m/s
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Visibility color="primary" />
                <Typography variant="body2" color="text.secondary">
                  기압
                </Typography>
              </Box>
              <Typography variant="h5" fontWeight="bold">
                {weather.main?.pressure || 0} hPa
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 온도 범위 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                온도 범위
              </Typography>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    최저
                  </Typography>
                  <Typography variant="h6" fontWeight="bold" color="primary">
                    {Math.round(weather.main?.temp_min || 0)}°C
                  </Typography>
                </Box>
                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary">
                    현재
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {Math.round(weather.main?.temp || 0)}°C
                  </Typography>
                </Box>
                <Box textAlign="right">
                  <Typography variant="body2" color="text.secondary">
                    최고
                  </Typography>
                  <Typography variant="h6" fontWeight="bold" color="error">
                    {Math.round(weather.main?.temp_max || 0)}°C
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 7일 예보 차트 */}
        {forecastChartData.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  7일 예보
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={forecastChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="temp"
                      stroke="#1976d2"
                      strokeWidth={2}
                      name="온도 (°C)"
                    />
                    <Line
                      type="monotone"
                      dataKey="feels_like"
                      stroke="#ff9800"
                      strokeWidth={2}
                      name="체감온도 (°C)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 상세 예보 */}
        {forecast && forecast.forecast && forecast.forecast.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  상세 예보
                </Typography>
                <Grid container spacing={2}>
                  {forecast.forecast.slice(0, 7).map((item: any, index: number) => (
                    <Grid item xs={12} sm={6} md={4} lg={12/7} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {new Date(item.dt).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
                          </Typography>
                          <Typography variant="h6" fontWeight="bold">
                            {Math.round(item.temp || 0)}°C
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {item.weather?.description || 'N/A'}
                          </Typography>
                          <Box display="flex" gap={1} mt={1}>
                            <Chip
                              label={`습도 ${item.humidity || 0}%`}
                              size="small"
                              variant="outlined"
                            />
                            {item.wind && (
                              <Chip
                                label={`풍속 ${item.wind.speed?.toFixed(1) || 0}m/s`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}

export default Weather




