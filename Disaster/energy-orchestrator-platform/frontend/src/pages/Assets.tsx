import { useState } from 'react'
import {
  Grid,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Add, TrendingUp, SolarPower } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAssets, createAsset, deleteAsset } from '../services/api'
import AssetCard from '../components/AssetCard'
import ServiceCard from '../components/ServiceCard'
import AddAssetDialog from '../components/AddAssetDialog'

const Assets = () => {
  const [openDialog, setOpenDialog] = useState(false)
  const queryClient = useQueryClient()

  const { data: assets, isLoading, error } = useQuery({
    queryKey: ['assets'],
    queryFn: getAssets,
  })

  const createMutation = useMutation({
    mutationFn: createAsset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
      setOpenDialog(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteAsset,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assets'] })
    },
  })

  const handleAddAsset = (assetData: any) => {
    createMutation.mutate(assetData)
  }

  const handleDeleteAsset = (assetId: string) => {
    if (window.confirm('정말 이 자산을 삭제하시겠습니까?')) {
      deleteMutation.mutate(assetId)
    }
  }

  // 서비스 카드를 위한 데이터 분리
  const demandAssets = (assets || []).filter((a: any) => a.service_type === 'demand')
  const supplyAssets = (assets || []).filter((a: any) => a.service_type === 'supply')

  // 통계 계산
  const totalAssets = (assets || []).length
  const onlineAssets = (assets || []).filter((a: any) => a.status === 'online').length
  const totalCapacity = (assets || []).reduce(
    (sum: number, a: any) => sum + (a.capacity_kw || 0),
    0
  )
  const avgCapacity = totalAssets > 0 ? totalCapacity / totalAssets : 0

  return (
    <Box>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" fontWeight="bold">
          에너지 자산 관리
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
          sx={{ px: 3 }}
        >
          + 자산 추가
        </Button>
      </Box>

      {/* 통계 카드 */}
      <Grid container spacing={2} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                총 자산
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {totalAssets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                운영 중
              </Typography>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {onlineAssets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                총 용량
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {totalCapacity.toFixed(1)} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                평균 용량
              </Typography>
              <Typography variant="h4" fontWeight="bold">
                {avgCapacity.toFixed(1)} kW
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 서비스 대시보드 카드 */}
      {demandAssets.length > 0 || supplyAssets.length > 0 ? (
        <Grid container spacing={3} mb={4}>
          {demandAssets.map((asset: any) => (
            <Grid item xs={12} md={6} key={asset.id}>
              <ServiceCard
                assetId={asset.id}
                title="에너지 수요 분석 대시보드"
                subtitle="AI 기반 예측 · 이상 탐지 · 데이터 품질 검증"
                value={asset.name}
                gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                icon={<TrendingUp />}
                serviceType="demand"
              />
            </Grid>
          ))}
          {supplyAssets.map((asset: any) => (
            <Grid item xs={12} md={6} key={asset.id}>
              <ServiceCard
                assetId={asset.id}
                title="에너지 공급 분석 대시보드"
                subtitle="태양광 · 실시간 모니터링 · AI 이상 탐지"
                value={asset.name}
                gradient="linear-gradient(135deg, #ff9800 0%, #f57c00 100%)"
                icon={<SolarPower />}
                serviceType="supply"
              />
            </Grid>
          ))}
          {/* 디지털 트윈 카드 - 모든 자산에 대해 표시 */}
          {(assets || []).map((asset: any) => (
            <Grid item xs={12} md={6} key={`twin-${asset.id}`}>
              <ServiceCard
                assetId={asset.id}
                title="디지털 트윈 실시간 모니터링"
                subtitle="수요-공급 매칭 · AI 에이전트 제어 · 실시간 시뮬레이션"
                value={asset.name}
                gradient="linear-gradient(135deg, #00bcd4 0%, #0097a7 100%)"
                icon={<TrendingUp />}
                serviceType="digitaltwin"
              />
            </Grid>
          ))}
        </Grid>
      ) : null}

      {/* 자산 목록 */}
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        자산 목록
      </Typography>

      {isLoading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">자산을 불러오는 중 오류가 발생했습니다.</Alert>
      ) : (
        <Grid container spacing={3}>
          {(assets || []).map((asset: any) => (
            <Grid item xs={12} sm={6} md={4} key={asset.id}>
              <AssetCard
                asset={asset}
                onDelete={handleDeleteAsset}
              />
            </Grid>
          ))}
          {(assets || []).length === 0 && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography align="center" color="text.secondary">
                    등록된 자산이 없습니다. + 자산 추가 버튼을 클릭하여 자산을 추가하세요.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* 자산 추가 다이얼로그 */}
      <AddAssetDialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        onSave={handleAddAsset}
      />
    </Box>
  )
}

export default Assets

