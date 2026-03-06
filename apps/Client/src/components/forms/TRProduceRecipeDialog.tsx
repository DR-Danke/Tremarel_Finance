import React, { useMemo, useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Chip,
  Box,
  CircularProgress,
} from '@mui/material'
import type { Recipe } from '@/types/recipe'
import type { Resource } from '@/types/resource'

interface TRProduceRecipeDialogProps {
  open: boolean
  recipe: Recipe | null
  resources: Resource[]
  isSubmitting: boolean
  onClose: () => void
  onProduce: (quantity: number) => Promise<void>
}

const formatCurrency = (value: number): string =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)

export const TRProduceRecipeDialog: React.FC<TRProduceRecipeDialogProps> = ({
  open,
  recipe,
  resources,
  isSubmitting,
  onClose,
  onProduce,
}) => {
  const [quantity, setQuantity] = useState('1')

  const qty = parseInt(quantity, 10) || 0

  const resourceMap = useMemo(() => {
    const map: Record<string, Resource> = {}
    for (const r of resources) {
      map[r.id] = r
    }
    return map
  }, [resources])

  const ingredientStatus = useMemo(() => {
    if (!recipe) return []
    return recipe.items.map((item) => {
      const resource = resourceMap[item.resource_id]
      const requiredQty = Number(item.quantity) * qty
      const available = resource?.current_stock ?? 0
      const sufficient = available >= requiredQty
      const unitCost = resource?.last_unit_cost ?? 0
      return {
        name: resource?.name || item.resource_name || item.resource_id,
        unit: item.unit,
        requiredQty,
        available,
        sufficient,
        lineCost: unitCost * Number(item.quantity) * qty,
      }
    })
  }, [recipe, resourceMap, qty])

  const hasInsufficient = ingredientStatus.some((i) => !i.sufficient)
  const totalCost = ingredientStatus.reduce((sum, i) => sum + i.lineCost, 0)

  const handleProduce = async () => {
    if (qty < 1) return
    await onProduce(qty)
    setQuantity('1')
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Producir: {recipe?.name}</DialogTitle>
      <DialogContent>
        <TextField
          label="Cantidad de porciones"
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          fullWidth
          inputProps={{ min: 1, step: 1 }}
          disabled={isSubmitting}
          sx={{ mt: 1, mb: 2 }}
        />

        {recipe && recipe.items.length > 0 && (
          <>
            <Typography variant="subtitle2" gutterBottom>
              Ingredientes requeridos
            </Typography>
            <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Ingrediente</TableCell>
                    <TableCell align="right">Requerido</TableCell>
                    <TableCell align="right">Disponible</TableCell>
                    <TableCell align="center">Estado</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {ingredientStatus.map((item, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{item.name}</TableCell>
                      <TableCell align="right">
                        {item.requiredQty} {item.unit}
                      </TableCell>
                      <TableCell align="right">
                        {item.available} {item.unit}
                      </TableCell>
                      <TableCell align="center">
                        {item.sufficient ? (
                          <Chip label="OK" color="success" size="small" />
                        ) : (
                          <Chip label="Insuficiente" color="error" size="small" />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Costo total de produccion:
              </Typography>
              <Typography variant="subtitle1" fontWeight={600}>
                {formatCurrency(totalCost)}
              </Typography>
            </Box>
          </>
        )}

        {hasInsufficient && qty > 0 && (
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            No hay stock suficiente para todos los ingredientes.
          </Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>
          Cancelar
        </Button>
        <Button
          onClick={handleProduce}
          variant="contained"
          disabled={isSubmitting || hasInsufficient || qty < 1}
        >
          {isSubmitting ? <CircularProgress size={24} /> : 'Producir'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
