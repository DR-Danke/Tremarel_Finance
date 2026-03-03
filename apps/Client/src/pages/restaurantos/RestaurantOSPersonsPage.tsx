import React from 'react'
import { Box, Typography } from '@mui/material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'

export const RestaurantOSPersonsPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Personas
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {currentRestaurant?.name}
      </Typography>
      <Typography variant="body1" color="text.disabled">
        Próximamente
      </Typography>
    </Box>
  )
}

export default RestaurantOSPersonsPage
