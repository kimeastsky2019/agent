import { useParams } from 'react-router-dom'
import { Grid, Box, Typography, Card, CardContent, CircularProgress, Alert, Chip } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getSupplyAnalysis, getRealtimePower, getProductionForecast } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'

const SupplyAnalysis = () => {
  const { assetId } = useParams<{ assetId: string }>()
  
  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['supplyAnalysis', assetId],
    queryFn: () => getSupplyAnalysis(assetId!),
    enabled: !!assetId,
  })

  const { data: realtimeData } = useQuery({
    queryKey: ['realtimePower', assetId],
    queryFn: () => getRealtimePower(assetId!, 'hour'),
    enabled: !!assetId,
    refetchInterval: 30000, // 30초마다 갱신
  })

  const { data: forecast } = useQuery({
    queryKey: ['productionForecast', assetId],
    queryFn: () => getProductionForecast(assetId!, 7),
    enabled: !!assetId,
  })

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
        공급 분석 데이터를 불러오는 중 오류가 발생했습니다.
      </Alert>
    )
  }

  if (!analysis) {
    return (
      <Alert severity="info">분석 데이터가 없습니다.</Alert>
    )
  }

  // 실시간 차트 데이터 준비
  const chartData = realtimeData?.labels?.map((label: string, index: number) => ({
    time: label,
    power: realtimeData.values[index] || 0
  })) || []

  // 예측 차트 데이터 준비
  const forecastData = forecast?.predictions?.map((pred: any) => ({
    date: pred.date,
    predicted: pred.predicted_production,
    lower: pred.confidence_lower,
    upper: pred.confidence_upper
  })) || []

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        에너지 공급 분석 대시보드
      </Typography>

      <Grid container spacing={3}>
        {/* 통계 카드 */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                현재 전력
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="primary">
                {analysis.facility?.current_power?.toFixed(0) || 0} W
              </Typography>
              <Typography variant="body2" color="text.secondary">
                용량: {analysis.facility?.capacity?.toLocaleString() || 0} W
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                효율
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="success.main">
                {analysis.statistics?.efficiency?.toFixed(1) || 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                평균 전력
              </Typography>
              <Typography variant="h3" fontWeight="bold">
                {analysis.statistics?.average_power?.toFixed(1) || 0} W
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                이상 탐지
              </Typography>
              <Typography variant="h3" fontWeight="bold" color={analysis.anomalies?.count > 0 ? "error.main" : "success.main"}>
                {analysis.anomalies?.count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 실시간 전력 그래프 */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                실시간 전력 생산
              </Typography>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="power" stroke="#1976d2" strokeWidth={2} name="전력 (W)" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
                  <CircularProgress />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* 시설 정보 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                시설 정보
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    이름
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {analysis.facility?.name || 'N/A'}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    타입
                  </Typography>
                  <Chip label={analysis.facility?.type || 'N/A'} size="small" color="primary" />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    상태
                  </Typography>
                  <Chip
                    label={analysis.facility?.status || 'offline'}
                    size="small"
                    color={analysis.facility?.status === 'online' ? 'success' : 'error'}
                  />
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2" color="text.secondary">
                    용량
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {analysis.facility?.capacity?.toLocaleString() || 0} W
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* 생산량 예측 */}
        {forecastData.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  7일 생산량 예측
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={forecastData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="predicted" fill="#1976d2" name="예측 생산량" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 이상 탐지 결과 */}
        {analysis.anomalies && analysis.anomalies.anomalies && analysis.anomalies.anomalies.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  이상 탐지 결과
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  {analysis.anomalies.anomalies.slice(0, 5).map((anomaly: any, index: number) => (
                    <Box key={index} display="flex" justifyContent="space-between" alignItems="center" p={1} sx={{ backgroundColor: 'rgba(211, 47, 47, 0.1)', borderRadius: 1 }}>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {new Date(anomaly.timestamp).toLocaleString('ko-KR')}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {anomaly.description || `값: ${anomaly.value?.toFixed(2)}`}
                        </Typography>
                      </Box>
                      <Chip
                        label={anomaly.severity || 'high'}
                        size="small"
                        color="error"
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}

export default SupplyAnalysis




