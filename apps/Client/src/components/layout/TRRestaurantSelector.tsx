import React from 'react'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
} from '@mui/material'
import type { SelectChangeEvent } from '@mui/material'
import { useRestaurant } from '@/hooks/useRestaurant'

interface TRRestaurantSelectorProps {
  open: boolean
}

export const TRRestaurantSelector: React.FC<TRRestaurantSelectorProps> = ({ open }) => {
  const { currentRestaurant, restaurants, switchRestaurant } = useRestaurant()

  const handleRestaurantChange = (event: SelectChangeEvent) => {
    switchRestaurant(event.target.value)
  }

  if (restaurants.length === 0) {
    return null
  }

  if (open) {
    return (
      <Box sx={{ p: 2 }}>
        <FormControl fullWidth size="small">
          <InputLabel id="restaurant-select-label">Restaurante</InputLabel>
          <Select
            labelId="restaurant-select-label"
            id="restaurant-select"
            value={currentRestaurant?.id || ''}
            label="Restaurante"
            onChange={handleRestaurantChange}
          >
            {restaurants.map((restaurant) => (
              <MenuItem key={restaurant.id} value={restaurant.id}>
                {restaurant.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>
    )
  }

  // Collapsed mode: show first letter of current restaurant
  if (currentRestaurant) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          py: 1,
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
          {currentRestaurant.name.charAt(0)}
        </Typography>
      </Box>
    )
  }

  return null
}

export default TRRestaurantSelector
