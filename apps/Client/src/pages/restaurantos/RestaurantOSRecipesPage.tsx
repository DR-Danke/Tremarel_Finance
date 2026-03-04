import React, { useState, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  Alert,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  CircularProgress,
  Chip,
  Drawer,
} from '@mui/material'
import { Add, Edit, Delete, PlayArrow } from '@mui/icons-material'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useRecipes } from '@/hooks/useRecipes'
import { useResources } from '@/hooks/useResources'
import { TRRecipeForm } from '@/components/forms/TRRecipeForm'
import { TRProfitabilityBadge } from '@/components/ui/TRProfitabilityBadge'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Recipe, RecipeCreate, RecipeUpdate } from '@/types/recipe'

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)
}

export const RestaurantOSRecipesPage: React.FC = () => {
  const { currentRestaurant, restaurants, isLoading } = useRestaurant()
  const {
    recipes,
    isLoading: recipesLoading,
    error,
    createRecipe,
    updateRecipe,
    deleteRecipe,
    produceRecipe,
  } = useRecipes(currentRestaurant?.id ?? null)
  const { resources } = useResources(currentRestaurant?.id ?? null)

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isProduceDialogOpen, setIsProduceDialogOpen] = useState(false)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [drawerRecipe, setDrawerRecipe] = useState<Recipe | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [produceQuantity, setProduceQuantity] = useState('1')

  const filteredRecipes = useMemo(() => {
    if (!searchQuery) return recipes
    return recipes.filter((r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [recipes, searchQuery])

  // Loading state
  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  // No restaurants
  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  // --- Dialog handlers ---

  const handleOpenAddDialog = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Opening add recipe dialog')
    setIsAddDialogOpen(true)
  }

  const handleCloseAddDialog = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Closing add recipe dialog')
    setIsAddDialogOpen(false)
  }

  const handleOpenEditDialog = (recipe: Recipe) => {
    console.log('INFO [RestaurantOSRecipesPage]: Opening edit dialog for recipe:', recipe.id)
    setSelectedRecipe(recipe)
    setIsEditDialogOpen(true)
  }

  const handleCloseEditDialog = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Closing edit recipe dialog')
    setIsEditDialogOpen(false)
    setSelectedRecipe(null)
  }

  const handleOpenDeleteDialog = (recipe: Recipe) => {
    console.log('INFO [RestaurantOSRecipesPage]: Opening delete dialog for recipe:', recipe.id)
    setSelectedRecipe(recipe)
    setIsDeleteDialogOpen(true)
  }

  const handleCloseDeleteDialog = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Closing delete dialog')
    setIsDeleteDialogOpen(false)
    setSelectedRecipe(null)
  }

  const handleOpenProduceDialog = (recipe: Recipe) => {
    console.log('INFO [RestaurantOSRecipesPage]: Opening produce dialog for recipe:', recipe.id)
    setSelectedRecipe(recipe)
    setProduceQuantity('1')
    setIsProduceDialogOpen(true)
  }

  const handleCloseProduceDialog = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Closing produce dialog')
    setIsProduceDialogOpen(false)
    setSelectedRecipe(null)
  }

  // --- Detail drawer handlers ---

  const handleOpenDrawer = (recipe: Recipe) => {
    console.log('INFO [RestaurantOSRecipesPage]: Opening detail drawer for recipe:', recipe.id)
    setDrawerRecipe(recipe)
  }

  const handleCloseDrawer = () => {
    console.log('INFO [RestaurantOSRecipesPage]: Closing detail drawer')
    setDrawerRecipe(null)
  }

  // --- CRUD handlers ---

  const handleCreateRecipe = async (data: RecipeCreate | RecipeUpdate) => {
    console.log('INFO [RestaurantOSRecipesPage]: Creating recipe')
    setIsSubmitting(true)
    try {
      await createRecipe(data as RecipeCreate)
      handleCloseAddDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to create recipe:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleUpdateRecipe = async (data: RecipeCreate | RecipeUpdate) => {
    if (!selectedRecipe) return
    console.log('INFO [RestaurantOSRecipesPage]: Updating recipe:', selectedRecipe.id)
    setIsSubmitting(true)
    try {
      await updateRecipe(selectedRecipe.id, data as RecipeUpdate)
      handleCloseEditDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to update recipe:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteRecipe = async () => {
    if (!selectedRecipe) return
    console.log('INFO [RestaurantOSRecipesPage]: Deleting recipe:', selectedRecipe.id)
    setIsSubmitting(true)
    try {
      await deleteRecipe(selectedRecipe.id)
      handleCloseDeleteDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to delete recipe:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleProduce = async () => {
    if (!selectedRecipe) return
    const qty = parseInt(produceQuantity, 10)
    if (isNaN(qty) || qty < 1) return
    console.log('INFO [RestaurantOSRecipesPage]: Producing recipe:', selectedRecipe.id, 'quantity:', qty)
    setIsSubmitting(true)
    try {
      await produceRecipe(selectedRecipe.id, qty)
      handleCloseProduceDialog()
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to produce recipe:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  // --- Build resource name map for drawer ---
  const resourceNameMap = useMemo(() => {
    const map: Record<string, { name: string; last_unit_cost: number }> = {}
    for (const r of resources) {
      map[r.id] = { name: r.name, last_unit_cost: r.last_unit_cost }
    }
    return map
  }, [resources])

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Recetas
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {currentRestaurant?.name}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenAddDialog}
        >
          Agregar Receta
        </Button>
      </Box>

      {/* Error display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Search */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          label="Buscar por nombre"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{ minWidth: 250 }}
        />
      </Box>

      {/* Data table */}
      {recipesLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredRecipes.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron recetas
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nombre</TableCell>
                <TableCell>Precio Venta</TableCell>
                <TableCell>Costo Actual</TableCell>
                <TableCell>Margen %</TableCell>
                <TableCell>Rentabilidad</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredRecipes.map((recipe) => (
                <TableRow
                  key={recipe.id}
                  hover
                  sx={{
                    cursor: 'pointer',
                    ...(!recipe.is_profitable && {
                      backgroundColor: 'rgba(211, 47, 47, 0.04)',
                    }),
                  }}
                  onClick={() => handleOpenDrawer(recipe)}
                >
                  <TableCell>{recipe.name}</TableCell>
                  <TableCell>{formatCurrency(recipe.sale_price)}</TableCell>
                  <TableCell>{formatCurrency(recipe.current_cost)}</TableCell>
                  <TableCell>{Number(recipe.margin_percent).toFixed(1)}%</TableCell>
                  <TableCell>
                    <TRProfitabilityBadge
                      marginPercent={Number(recipe.margin_percent)}
                      isProfitable={recipe.is_profitable}
                    />
                  </TableCell>
                  <TableCell>
                    {recipe.is_active ? (
                      <Chip label="Activa" color="success" size="small" />
                    ) : (
                      <Chip label="Inactiva" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenEditDialog(recipe)
                      }}
                      aria-label="edit"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenDeleteDialog(recipe)
                      }}
                      aria-label="delete"
                      color="error"
                    >
                      <Delete fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleOpenProduceDialog(recipe)
                      }}
                      aria-label="produce"
                      color="primary"
                    >
                      <PlayArrow fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Add Recipe Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Receta</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRRecipeForm
              onSubmit={handleCreateRecipe}
              restaurantId={currentRestaurant?.id || ''}
              resources={resources}
              onCancel={handleCloseAddDialog}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Recipe Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Receta</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedRecipe && (
              <TRRecipeForm
                onSubmit={handleUpdateRecipe}
                initialData={selectedRecipe}
                restaurantId={currentRestaurant?.id || ''}
                resources={resources}
                onCancel={handleCloseEditDialog}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={handleCloseDeleteDialog}>
        <DialogTitle>Eliminar Receta</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Está seguro que desea eliminar esta receta?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleDeleteRecipe}
            color="error"
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Eliminar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Produce Dialog */}
      <Dialog open={isProduceDialogOpen} onClose={handleCloseProduceDialog}>
        <DialogTitle>Producir</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            ¿Cuántas porciones producir?
          </Typography>
          <TextField
            label="Cantidad"
            type="number"
            value={produceQuantity}
            onChange={(e) => setProduceQuantity(e.target.value)}
            fullWidth
            inputProps={{ min: 1, step: 1 }}
            disabled={isSubmitting}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseProduceDialog} disabled={isSubmitting}>
            Cancelar
          </Button>
          <Button
            onClick={handleProduce}
            variant="contained"
            disabled={isSubmitting}
          >
            {isSubmitting ? <CircularProgress size={24} /> : 'Producir'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail Drawer */}
      <Drawer
        anchor="right"
        open={!!drawerRecipe}
        onClose={handleCloseDrawer}
        PaperProps={{ sx: { width: { xs: '100%', sm: 500 } } }}
      >
        {drawerRecipe && (
          <Box sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              {drawerRecipe.name}
            </Typography>
            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Precio de Venta: {formatCurrency(drawerRecipe.sale_price)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Costo Actual: {formatCurrency(drawerRecipe.current_cost)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Margen: {Number(drawerRecipe.margin_percent).toFixed(1)}%
              </Typography>
              <Box sx={{ mt: 1 }}>
                <TRProfitabilityBadge
                  marginPercent={Number(drawerRecipe.margin_percent)}
                  isProfitable={drawerRecipe.is_profitable}
                />
              </Box>
            </Box>

            <Typography variant="h6" gutterBottom>
              Ingredientes
            </Typography>

            {drawerRecipe.items.length === 0 ? (
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography color="text.secondary">
                  No hay ingredientes registrados
                </Typography>
              </Paper>
            ) : (
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Ingrediente</TableCell>
                      <TableCell>Cantidad</TableCell>
                      <TableCell>Unidad</TableCell>
                      <TableCell>Costo Unitario</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {drawerRecipe.items.map((item) => {
                      const resourceInfo = resourceNameMap[item.resource_id]
                      return (
                        <TableRow key={item.id || item.resource_id}>
                          <TableCell>
                            {resourceInfo?.name || item.resource_name || item.resource_id}
                          </TableCell>
                          <TableCell>{Number(item.quantity)}</TableCell>
                          <TableCell>{item.unit}</TableCell>
                          <TableCell>
                            {resourceInfo
                              ? formatCurrency(resourceInfo.last_unit_cost)
                              : '—'}
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Box>
        )}
      </Drawer>
    </Box>
  )
}

export default RestaurantOSRecipesPage
