import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Typography,
} from '@mui/material'
import { useState } from 'react'

interface AddAssetDialogProps {
  open: boolean
  onClose: () => void
  onSave: (asset: {
    name: string
    type: string
    capacity_kw: number
    location?: { lat: number; lon: number }
  }) => void
}

const AddAssetDialog = ({ open, onClose, onSave }: AddAssetDialogProps) => {
  const [formData, setFormData] = useState({
    name: '',
    type: 'solar',
    capacity_kw: 0,
    lat: '',
    lon: '',
  })

  const handleSave = () => {
    const asset = {
      name: formData.name,
      type: formData.type,
      capacity_kw: parseFloat(formData.capacity_kw.toString()) || 0,
      location:
        formData.lat && formData.lon
          ? {
              lat: parseFloat(formData.lat),
              lon: parseFloat(formData.lon),
            }
          : undefined,
    }
    onSave(asset)
    setFormData({
      name: '',
      type: 'solar',
      capacity_kw: 0,
      lat: '',
      lon: '',
    })
    onClose()
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>자산 추가</DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column" gap={2} sx={{ mt: 1 }}>
          <TextField
            label="자산 이름"
            fullWidth
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <TextField
            label="자산 타입"
            select
            fullWidth
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            required
          >
            <MenuItem value="solar">태양광 (Solar)</MenuItem>
            <MenuItem value="wind">풍력 (Wind)</MenuItem>
            <MenuItem value="battery">배터리 (Battery)</MenuItem>
            <MenuItem value="demand">수요 부문 (Demand)</MenuItem>
            <MenuItem value="grid">전력망 (Grid)</MenuItem>
          </TextField>

          <TextField
            label="용량 (kW)"
            type="number"
            fullWidth
            value={formData.capacity_kw}
            onChange={(e) =>
              setFormData({ ...formData, capacity_kw: parseFloat(e.target.value) || 0 })
            }
          />

          <Typography variant="subtitle2" sx={{ mt: 1 }}>
            위치 (선택사항)
          </Typography>
          <Box display="flex" gap={2}>
            <TextField
              label="위도 (Latitude)"
              type="number"
              fullWidth
              value={formData.lat}
              onChange={(e) => setFormData({ ...formData, lat: e.target.value })}
            />
            <TextField
              label="경도 (Longitude)"
              type="number"
              fullWidth
              value={formData.lon}
              onChange={(e) => setFormData({ ...formData, lon: e.target.value })}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>취소</Button>
        <Button onClick={handleSave} variant="contained" disabled={!formData.name}>
          저장
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default AddAssetDialog




