// Type definitions

export interface Asset {
  id: string
  name: string
  type: string
  capacity_kw: number
  location: {
    lat: number
    lon: number
  }
  status: string
}

export interface Disaster {
  id: string
  event_type: string
  severity: number
  location: {
    lat: number
    lon: number
  }
  affected_radius_km?: number
  status: string
}

export interface Weather {
  location: {
    lat: number
    lon: number
    name: string
  }
  weather: {
    id: number
    main: string
    description: string
    icon: string
  }
  main: {
    temp: number
    feels_like: number
    temp_min: number
    temp_max: number
    pressure: number
    humidity: number
  }
  wind?: {
    speed: number
    deg: number
  }
  dt: Date
}




