import { configureStore } from '@reduxjs/toolkit'
import authSlice from './slices/authSlice'
import energySlice from './slices/energySlice'
import disasterSlice from './slices/disasterSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    energy: energySlice,
    disaster: disasterSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch




