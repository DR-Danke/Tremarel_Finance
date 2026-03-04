import { useState, useEffect, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import {
  TextField,
  Button,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Typography,
  Switch,
  FormControlLabel,
  CircularProgress,
  Divider,
} from '@mui/material'
import { Add, Delete } from '@mui/icons-material'
import type { Recipe, RecipeCreate, RecipeUpdate } from '@/types/recipe'
import type { Resource } from '@/types/resource'

interface RecipeFormData {
  name: string
  sale_price: string
  is_active: boolean
}

interface IngredientRow {
  resource_id: string
  quantity: string
  unit: string
}

interface TRRecipeFormProps {
  onSubmit: (data: RecipeCreate | RecipeUpdate) => Promise<void>
  initialData?: Recipe
  restaurantId: string
  resources: Resource[]
  onCancel: () => void
  isSubmitting?: boolean
}

export const TRRecipeForm: React.FC<TRRecipeFormProps> = ({
  onSubmit,
  initialData,
  restaurantId,
  resources,
  onCancel,
  isSubmitting = false,
}) => {
  const isEditMode = !!initialData

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting: formSubmitting },
  } = useForm<RecipeFormData>({
    defaultValues: {
      name: initialData?.name || '',
      sale_price: initialData?.sale_price?.toString() || '',
      is_active: initialData?.is_active ?? true,
    },
  })

  const [ingredients, setIngredients] = useState<IngredientRow[]>(() => {
    if (initialData?.items && initialData.items.length > 0) {
      return initialData.items.map((item) => ({
        resource_id: item.resource_id,
        quantity: item.quantity.toString(),
        unit: item.unit,
      }))
    }
    return []
  })

  const [ingredientError, setIngredientError] = useState<string | null>(null)

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        sale_price: initialData.sale_price.toString(),
        is_active: initialData.is_active,
      })
      if (initialData.items && initialData.items.length > 0) {
        setIngredients(
          initialData.items.map((item) => ({
            resource_id: item.resource_id,
            quantity: item.quantity.toString(),
            unit: item.unit,
          }))
        )
      }
    }
  }, [initialData, reset])

  const watchSalePrice = watch('sale_price')

  const resourcesMap = useMemo(() => {
    const map: Record<string, Resource> = {}
    for (const r of resources) {
      map[r.id] = r
    }
    return map
  }, [resources])

  const estimatedCost = useMemo(() => {
    let total = 0
    for (const ing of ingredients) {
      const resource = resourcesMap[ing.resource_id]
      const qty = parseFloat(ing.quantity)
      if (resource && !isNaN(qty) && qty > 0) {
        total += qty * resource.last_unit_cost
      }
    }
    return total
  }, [ingredients, resourcesMap])

  const estimatedMargin = useMemo(() => {
    const salePrice = parseFloat(watchSalePrice)
    if (!salePrice || salePrice <= 0) return 0
    return ((salePrice - estimatedCost) / salePrice) * 100
  }, [watchSalePrice, estimatedCost])

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const handleAddIngredient = () => {
    console.log('INFO [TRRecipeForm]: Adding ingredient row')
    setIngredients([...ingredients, { resource_id: '', quantity: '', unit: '' }])
    setIngredientError(null)
  }

  const handleRemoveIngredient = (index: number) => {
    console.log('INFO [TRRecipeForm]: Removing ingredient row:', index)
    setIngredients(ingredients.filter((_, i) => i !== index))
  }

  const handleIngredientChange = (
    index: number,
    field: keyof IngredientRow,
    value: string
  ) => {
    const updated = [...ingredients]
    updated[index] = { ...updated[index], [field]: value }

    if (field === 'resource_id') {
      const resource = resourcesMap[value]
      if (resource) {
        updated[index].unit = resource.unit
      }
    }

    setIngredients(updated)
    setIngredientError(null)
  }

  const validateIngredients = (): boolean => {
    if (ingredients.length === 0) {
      setIngredientError('Debe agregar al menos un ingrediente')
      return false
    }
    for (let i = 0; i < ingredients.length; i++) {
      const ing = ingredients[i]
      if (!ing.resource_id) {
        setIngredientError(`Seleccione un recurso para el ingrediente ${i + 1}`)
        return false
      }
      const qty = parseFloat(ing.quantity)
      if (isNaN(qty) || qty <= 0) {
        setIngredientError(`La cantidad del ingrediente ${i + 1} debe ser mayor a 0`)
        return false
      }
    }
    return true
  }

  const handleFormSubmit = async (data: RecipeFormData) => {
    console.log('INFO [TRRecipeForm]: Submitting recipe form', data)

    if (!validateIngredients()) return

    try {
      const items = ingredients.map((ing) => ({
        resource_id: ing.resource_id,
        quantity: parseFloat(ing.quantity),
        unit: ing.unit,
      }))

      if (isEditMode) {
        const updateData: RecipeUpdate = {
          name: data.name,
          sale_price: parseFloat(data.sale_price),
          is_active: data.is_active,
          items,
        }
        await onSubmit(updateData)
      } else {
        const createData: RecipeCreate = {
          restaurant_id: restaurantId,
          name: data.name,
          sale_price: parseFloat(data.sale_price),
          is_active: data.is_active,
          items,
        }
        await onSubmit(createData)
      }
      console.log('INFO [TRRecipeForm]: Recipe submitted successfully')
      if (!isEditMode) {
        reset()
        setIngredients([])
      }
    } catch (error) {
      console.error('ERROR [TRRecipeForm]: Failed to submit recipe:', error)
    }
  }

  const isFormLoading = isSubmitting || formSubmitting

  return (
    <Box
      component="form"
      onSubmit={handleSubmit(handleFormSubmit)}
      noValidate
      sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
    >
      <TextField
        {...register('name', {
          required: 'El nombre es obligatorio',
          maxLength: { value: 255, message: 'Máximo 255 caracteres' },
        })}
        label="Nombre"
        fullWidth
        error={!!errors.name}
        helperText={errors.name?.message}
        disabled={isFormLoading}
      />

      <TextField
        {...register('sale_price', {
          required: 'El precio de venta es obligatorio',
          validate: (value) =>
            parseFloat(value) > 0 || 'El precio de venta debe ser mayor a 0',
        })}
        label="Precio de Venta"
        type="number"
        fullWidth
        error={!!errors.sale_price}
        helperText={errors.sale_price?.message}
        disabled={isFormLoading}
        inputProps={{ min: 0, step: 'any' }}
      />

      <FormControlLabel
        control={
          <Switch
            {...register('is_active')}
            defaultChecked={initialData?.is_active ?? true}
            disabled={isFormLoading}
          />
        }
        label="Activo"
      />

      <Divider />

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1" fontWeight="bold">
          Ingredientes
        </Typography>
        <Button
          size="small"
          startIcon={<Add />}
          onClick={handleAddIngredient}
          disabled={isFormLoading}
        >
          Agregar Ingrediente
        </Button>
      </Box>

      {ingredientError && (
        <Typography color="error" variant="body2">
          {ingredientError}
        </Typography>
      )}

      {ingredients.map((ing, index) => (
        <Box key={index} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 180, flex: 1 }}>
            <InputLabel id={`ingredient-resource-label-${index}`}>Recurso</InputLabel>
            <Select
              labelId={`ingredient-resource-label-${index}`}
              value={ing.resource_id}
              onChange={(e) =>
                handleIngredientChange(index, 'resource_id', e.target.value)
              }
              label="Recurso"
              disabled={isFormLoading}
            >
              {resources.map((r) => (
                <MenuItem key={r.id} value={r.id}>
                  {r.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Cantidad"
            type="number"
            size="small"
            value={ing.quantity}
            onChange={(e) =>
              handleIngredientChange(index, 'quantity', e.target.value)
            }
            disabled={isFormLoading}
            inputProps={{ min: 0, step: 'any' }}
            sx={{ width: 100 }}
          />

          <TextField
            label="Unidad"
            size="small"
            value={ing.unit}
            disabled
            sx={{ width: 80 }}
          />

          <IconButton
            size="small"
            color="error"
            onClick={() => handleRemoveIngredient(index)}
            disabled={isFormLoading}
          >
            <Delete fontSize="small" />
          </IconButton>
        </Box>
      ))}

      {ingredients.length > 0 && (
        <Box sx={{ mt: 1, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Costo Estimado: {formatCurrency(estimatedCost)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Margen Estimado: {estimatedMargin.toFixed(1)}%
          </Typography>
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 1 }}>
        <Button
          type="button"
          variant="outlined"
          onClick={onCancel}
          disabled={isFormLoading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="contained"
          disabled={isFormLoading}
        >
          {isFormLoading ? (
            <CircularProgress size={24} />
          ) : isEditMode ? (
            'Actualizar Receta'
          ) : (
            'Agregar Receta'
          )}
        </Button>
      </Box>
    </Box>
  )
}

export default TRRecipeForm
