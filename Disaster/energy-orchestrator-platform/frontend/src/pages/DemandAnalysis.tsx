import { useParams } from 'react-router-dom'
import { Grid, Box, Typography, Card, CardContent, CircularProgress, Alert } from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { getDemandAnalysis } from '../services/api'

const DemandAnalysis = () => {
  const { assetId } = useParams<{ assetId: string }>()
  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['demandAnalysis', assetId],
    queryFn: () => getDemandAnalysis(assetId!),
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
        수요 분석 데이터를 불러오는 중 오류가 발생했습니다.
      </Alert>
    )
  }

  if (!analysis) {
    return (
      <Alert severity="info">분석 데이터가 없습니다.</Alert>
    )
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        에너지 수요 분석 대시보드
      </Typography>

      <Grid container spacing={3}>
        {/* 품질 점수 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                데이터 품질 점수
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="primary">
                {analysis.quality_report?.quality_score?.toFixed(1) || 0}/100
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 이상 탐지 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                이상 탐지
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="error">
                {analysis.anomalies?.count || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                ({analysis.anomalies?.percentage?.toFixed(2) || 0}%)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 통계 */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                총 에너지
              </Typography>
              <Typography variant="h3" fontWeight="bold" color="success.main">
                {analysis.statistics?.total_energy?.toFixed(1) || 0} kWh
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* 예측 */}
        {analysis.predictions && analysis.predictions.predictions && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  7일 예측
                </Typography>
                <Box display="flex" gap={2} flexWrap="wrap">
                  {analysis.predictions.predictions.slice(0, 7).map((pred: any, index: number) => (
                    <Card key={index} variant="outlined">
                      <CardContent>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(pred.date).toLocaleDateString('ko-KR')}
                        </Typography>
                        <Typography variant="h6">
                          {pred.predicted_kwh?.toFixed(1)} kWh
                        </Typography>
                      </CardContent>
                    </Card>
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

export default DemandAnalysis

