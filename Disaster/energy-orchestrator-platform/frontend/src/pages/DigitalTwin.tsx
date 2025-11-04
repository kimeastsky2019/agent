import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import {
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Paper,
  LinearProgress,
} from '@mui/material'
import {
  PlayArrow,
  Stop,
  Refresh,
  TrendingUp,
  BatteryChargingFull,
  Bolt,
  Power,
  SolarPower,
  WindPower,
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getDigitalTwinState,
  runControlCycle,
  getPerformanceMetrics,
  startSimulation,
} from '../services/api'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const DigitalTwin = () => {
  const { assetId } = useParams<{ assetId: string }>()
  const [isRunning, setIsRunning] = useState(false)
  const [simulationData, setSimulationData] = useState<any[]>([])
  const queryClient = useQueryClient()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const { data: state, isLoading, error, refetch } = useQuery({
    queryKey: ['digitalTwinState', assetId],
    queryFn: () => getDigitalTwinState(assetId!),
    enabled: !!assetId,
    refetchInterval: isRunning ? 2000 : false, // 2초마다 갱신
  })

  const { data: metrics } = useQuery({
    queryKey: ['digitalTwinMetrics', assetId],
    queryFn: () => getPerformanceMetrics(assetId!),
    enabled: !!assetId,
    refetchInterval: isRunning ? 5000 : false,
  })

  const cycleMutation = useMutation({
    mutationFn: () => runControlCycle(assetId!),
    onSuccess: (data) => {
      // 시뮬레이션 데이터에 추가
      setSimulationData((prev) => {
        const newData = [...prev, data]
        // 최근 100개만 유지
        return newData.slice(-100)
      })
      queryClient.invalidateQueries({ queryKey: ['digitalTwinState', assetId] })
      queryClient.invalidateQueries({ queryKey: ['digitalTwinMetrics', assetId] })
    },
  })

  const startMutation = useMutation({
    mutationFn: () => startSimulation(assetId!, 24, 15),
    onSuccess: () => {
      setIsRunning(true)
    },
  })

  // 초기화
  useEffect(() => {
    if (assetId) {
      initializeDigitalTwin(assetId)
    }
  }, [assetId])

  // 실시간 업데이트
  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        cycleMutation.mutate()
      }, 2000) // 2초마다 사이클 실행
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isRunning])

  const handleStart = async () => {
    try {
      // 먼저 초기화
      await initializeDigitalTwin(assetId!)
      // 시뮬레이션 시작
      startMutation.mutate()
      setIsRunning(true)
    } catch (error) {
      console.error('Failed to start simulation:', error)
    }
  }

  const handleStop = () => {
    setIsRunning(false)
  }

  const handleRefresh = () => {
    refetch()
    queryClient.invalidateQueries({ queryKey: ['digitalTwinMetrics', assetId] })
  }

  // 차트 데이터 준비
  const powerChartData = simulationData.map((data, index) => ({
    time: new Date(data.timestamp).toLocaleTimeString('ko-KR'),
    demand: data.power?.total_demand || 0,
    supply: data.power?.total_supply || 0,
    balance: data.power?.balance || 0,
    ess_soc: data.power?.ess_soc || 0,
  }))

  const metricsChartData = simulationData.map((data, index) => ({
    time: new Date(data.timestamp).toLocaleTimeString('ko-KR'),
    renewable: data.performance_metrics?.renewable_ratio || 0,
    stability: data.performance_metrics?.stability_score || 0,
    costEfficiency: data.performance_metrics?.cost_efficiency || 0,
    overall: data.performance_metrics?.overall_score || 0,
  }))

  if (isLoading && !state) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error">
        디지털 트윈 데이터를 불러오는 중 오류가 발생했습니다.
      </Alert>
    )
  }

  if (!state) {
    return (
      <Alert severity="info">디지털 트윈 상태 데이터가 없습니다.</Alert>
    )
  }

  return (
    <Box>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          디지털 트윈 실시간 모니터링
        </Typography>
        <Box display="flex" gap={2}>
          {!isRunning ? (
            <Button
              variant="contained"
              color="success"
              startIcon={<PlayArrow />}
              onClick={handleStart}
            >
              시뮬레이션 시작
            </Button>
          ) : (
            <Button
              variant="contained"
              color="error"
              startIcon={<Stop />}
              onClick={handleStop}
            >
              시뮬레이션 중지
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            새로고침
          </Button>
        </Box>
      </Box>

      {/* 상태 표시 */}
      {isRunning && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'success.light', color: 'white' }}>
          <Box display="flex" alignItems="center" gap={2}>
            <CircularProgress size={20} sx={{ color: 'white' }} />
            <Typography variant="body1" fontWeight="bold">
              시뮬레이션 실행 중... (2초 간격 업데이트)
            </Typography>
          </Box>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* 전력 메트릭 카드 */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Bolt color="primary" />
                <Typography variant="h6">전력 수요</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color="primary">
                {state.power?.total_demand?.toFixed(1) || 0} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Power color="success" />
                <Typography variant="h6">전력 공급</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color="success.main">
                {state.power?.total_supply?.toFixed(1) || 0} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <TrendingUp color="warning" />
                <Typography variant="h6">전력 균형</Typography>
              </Box>
              <Typography
                variant="h3"
                fontWeight="bold"
                color={state.power?.balance >= 0 ? 'success.main' : 'error.main'}
              >
                {state.power?.balance >= 0 ? '+' : ''}
                {state.power?.balance?.toFixed(1) || 0} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <BatteryChargingFull color="info" />
                <Typography variant="h6">ESS SOC</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold" color="info.main">
                {state.power?.ess_soc?.toFixed(1) || 0}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={state.power?.ess_soc || 0}
                sx={{ mt: 1, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* 환경 데이터 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                환경 데이터
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    온도
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {state.environment?.temperature?.toFixed(1) || 0}°C
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    습도
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {state.environment?.humidity?.toFixed(1) || 0}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    일사량
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {state.environment?.solar_radiation?.toFixed(0) || 0} W/m²
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    풍속
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {state.environment?.wind_speed?.toFixed(1) || 0} m/s
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    재실 인원
                  </Typography>
                  <Typography variant="h6" fontWeight="bold">
                    {state.environment?.occupancy || 0}명
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* 공급원 상태 */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                공급원 상태
              </Typography>
              {state.supplies?.map((supply: any, index: number) => (
                <Box key={index} mb={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {supply.source_type === '태양광' && <SolarPower color="warning" />}
                      {supply.source_type === '풍력' && <WindPower color="info" />}
                      {supply.source_type === '전력망' && <Power color="primary" />}
                      <Typography variant="body1" fontWeight="bold">
                        {supply.source_type}
                      </Typography>
                    </Box>
                    <Chip
                      label={`${supply.current_output?.toFixed(1) || 0} / ${supply.capacity?.toFixed(0) || 0} kW`}
                      size="small"
                      color="primary"
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(supply.current_output / supply.capacity) * 100 || 0}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* 전력 수요-공급 차트 */}
        {powerChartData.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  전력 수요-공급 추이
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={powerChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="demand"
                      stackId="1"
                      stroke="#1976d2"
                      fill="#1976d2"
                      name="수요 (kW)"
                    />
                    <Area
                      type="monotone"
                      dataKey="supply"
                      stackId="1"
                      stroke="#2e7d32"
                      fill="#2e7d32"
                      name="공급 (kW)"
                    />
                    <Line
                      type="monotone"
                      dataKey="balance"
                      stroke="#ff9800"
                      strokeWidth={2}
                      name="균형 (kW)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 성능 지표 차트 */}
        {metricsChartData.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  성능 지표 추이
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={metricsChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="renewable"
                      stroke="#ff9800"
                      strokeWidth={2}
                      name="재생에너지 비율 (%)"
                    />
                    <Line
                      type="monotone"
                      dataKey="stability"
                      stroke="#1976d2"
                      strokeWidth={2}
                      name="안정성 점수 (%)"
                    />
                    <Line
                      type="monotone"
                      dataKey="costEfficiency"
                      stroke="#2e7d32"
                      strokeWidth={2}
                      name="비용 효율성 (%)"
                    />
                    <Line
                      type="monotone"
                      dataKey="overall"
                      stroke="#9c27b0"
                      strokeWidth={2}
                      name="종합 점수 (%)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* 성능 메트릭 카드 */}
        {metrics && (
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  재생에너지 비율
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="warning.main">
                  {metrics.renewable_ratio_avg?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {metrics && (
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  안정성 점수
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="primary">
                  {metrics.stability_score_avg?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {metrics && (
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  비용 효율성
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="success.main">
                  {metrics.cost_efficiency_avg?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}

        {metrics && (
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  종합 점수
                </Typography>
                <Typography variant="h3" fontWeight="bold" color="secondary">
                  {metrics.overall_score_avg?.toFixed(1) || 0}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}

export default DigitalTwin

