import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Weather API
export const getCurrentWeather = async (lat: number, lon: number) => {
  const response = await api.get('/api/v1/weather/current', {
    params: { lat, lon },
  })
  return response.data
}

export const getWeatherForecast = async (lat: number, lon: number, days: number = 5) => {
  const response = await api.get('/api/v1/weather/forecast', {
    params: { lat, lon, days },
  })
  return response.data
}

// Energy API
export const getEnergyBalance = async () => {
  const response = await api.get('/api/v1/energy/balance')
  return response.data
}

export const getAssets = async () => {
  const response = await api.get('/api/v1/assets')
  return response.data
}

// Disaster API
export const getDisasters = async () => {
  const response = await api.get('/api/v1/disasters')
  return response.data
}

export const getActiveDisasters = async () => {
  const response = await api.get('/api/v1/disasters/active')
  return response.data
}

// Asset API
export const createAsset = async (asset: any) => {
  const response = await api.post('/api/v1/assets', asset)
  return response.data
}

export const deleteAsset = async (assetId: string) => {
  const response = await api.delete(`/api/v1/assets/${assetId}`)
  return response.data
}

// Demand Analysis API
export const getDemandAnalysis = async (assetId: string) => {
  const response = await api.get(`/api/v1/demand/analysis/${assetId}`)
  return response.data
}

export const analyzeDemand = async (assetId: string, file?: File) => {
  const formData = new FormData()
  if (file) {
    formData.append('file', file)
  }
  const response = await api.post(`/api/v1/demand/analysis/${assetId}/analyze`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

// Supply Analysis API
export const getSupplyAnalysis = async (assetId: string) => {
  const response = await api.get(`/api/v1/supply/analysis/${assetId}`)
  return response.data
}

export const getRealtimePower = async (assetId: string, range: string = 'hour') => {
  const response = await api.get(`/api/v1/supply/realtime/${assetId}`, {
    params: { range },
  })
  return response.data
}

export const getProductionForecast = async (assetId: string, days: number = 7) => {
  const response = await api.get(`/api/v1/supply/forecast/${assetId}`, {
    params: { days },
  })
  return response.data
}

export const getAnomalies = async (assetId: string) => {
  const response = await api.get(`/api/v1/supply/anomalies/${assetId}`)
  return response.data
}

export const getFacilityInfo = async (assetId: string) => {
  const response = await api.get(`/api/v1/supply/facility/${assetId}`)
  return response.data
}

// Digital Twin API
export const getDigitalTwinState = async (assetId: string) => {
  const response = await api.get(`/api/v1/digitaltwin/state/${assetId}`)
  return response.data
}

export const initializeDigitalTwin = async (assetId: string) => {
  const response = await api.post(`/api/v1/digitaltwin/initialize/${assetId}`)
  return response.data
}

export const runControlCycle = async (assetId: string) => {
  const response = await api.post(`/api/v1/digitaltwin/cycle/${assetId}`)
  return response.data
}

export const getPerformanceMetrics = async (assetId: string) => {
  const response = await api.get(`/api/v1/digitaltwin/metrics/${assetId}`)
  return response.data
}

export const startSimulation = async (
  assetId: string,
  duration_hours: number = 24,
  time_step_minutes: number = 15
) => {
  const response = await api.get(`/api/v1/digitaltwin/simulation/${assetId}`, {
    params: { duration_hours, time_step_minutes },
  })
  return response.data
}

export default api

