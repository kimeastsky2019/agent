import { createSlice } from '@reduxjs/toolkit'

interface DisasterState {
  disasters: any[]
  activeDisasters: any[]
  loading: boolean
}

const initialState: DisasterState = {
  disasters: [],
  activeDisasters: [],
  loading: false,
}

const disasterSlice = createSlice({
  name: 'disaster',
  initialState,
  reducers: {
    setDisasters: (state, action) => {
      state.disasters = action.payload
    },
    setActiveDisasters: (state, action) => {
      state.activeDisasters = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
  },
})

export const { setDisasters, setActiveDisasters, setLoading } = disasterSlice.actions
export default disasterSlice.reducer




