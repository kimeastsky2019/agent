import { createSlice } from '@reduxjs/toolkit'

interface EnergyState {
  assets: any[]
  balance: any | null
  loading: boolean
}

const initialState: EnergyState = {
  assets: [],
  balance: null,
  loading: false,
}

const energySlice = createSlice({
  name: 'energy',
  initialState,
  reducers: {
    setAssets: (state, action) => {
      state.assets = action.payload
    },
    setBalance: (state, action) => {
      state.balance = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
  },
})

export const { setAssets, setBalance, setLoading } = energySlice.actions
export default energySlice.reducer




