import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material'
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu'
import { useForm } from 'react-hook-form'
import { useRestaurant } from '@/hooks/useRestaurant'
import type { CreateRestaurantData } from '@/types/restaurant'

export const TRNoRestaurantPrompt: React.FC = () => {
  const { createRestaurant } = useRestaurant()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateRestaurantData>()

  const onSubmit = async (data: CreateRestaurantData) => {
    setIsSubmitting(true)
    try {
      await createRestaurant(data)
      setDialogOpen(false)
      reset()
    } catch (error) {
      console.error('ERROR [TRNoRestaurantPrompt]: Failed to create restaurant:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '50vh',
          textAlign: 'center',
          gap: 2,
        }}
      >
        <RestaurantMenuIcon sx={{ fontSize: 64, color: 'text.disabled' }} />
        <Typography variant="h5" color="text.secondary">
          No tienes restaurantes
        </Typography>
        <Typography variant="body1" color="text.disabled">
          Crea tu primer restaurante para comenzar
        </Typography>
        <Button
          variant="contained"
          onClick={() => setDialogOpen(true)}
          sx={{ mt: 2 }}
        >
          Crear Restaurante
        </Button>
      </Box>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Crear Restaurante</DialogTitle>
          <DialogContent>
            <TextField
              {...register('name', { required: 'El nombre es requerido' })}
              label="Nombre"
              fullWidth
              margin="normal"
              error={!!errors.name}
              helperText={errors.name?.message}
              autoFocus
            />
            <TextField
              {...register('address')}
              label="Dirección (opcional)"
              fullWidth
              margin="normal"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} disabled={isSubmitting}>
              Cancelar
            </Button>
            <Button type="submit" variant="contained" disabled={isSubmitting}>
              {isSubmitting ? 'Creando...' : 'Crear'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </>
  )
}

export default TRNoRestaurantPrompt
