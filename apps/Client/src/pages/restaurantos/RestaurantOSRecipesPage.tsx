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
  TableSortLabel,
  TablePagination,
} from '@mui/material'
import { Add, Edit, Delete, PlayArrow } from '@mui/icons-material'
import MenuBookIcon from '@mui/icons-material/MenuBook'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { useRestaurant } from '@/hooks/useRestaurant'
import { useRecipes } from '@/hooks/useRecipes'
import { useResources } from '@/hooks/useResources'
import { useSnackbar } from '@/hooks/useSnackbar'
import { useTableSort } from '@/hooks/useTableSort'
import { useTablePagination } from '@/hooks/useTablePagination'
import { TRRecipeForm } from '@/components/forms/TRRecipeForm'
import { TRProfitabilityBadge } from '@/components/ui/TRProfitabilityBadge'
import { TRBreadcrumbs } from '@/components/ui/TRBreadcrumbs'
import { TRTableSkeleton } from '@/components/ui/TRTableSkeleton'
import { TREmptyState } from '@/components/ui/TREmptyState'
import { TRProduceRecipeDialog } from '@/components/forms/TRProduceRecipeDialog'
import { TRNoRestaurantPrompt } from './TRNoRestaurantPrompt'
import type { Recipe, RecipeCreate, RecipeUpdate } from '@/types/recipe'

const formatCurrency = (value: number): string =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value)

const PIE_COLORS = ['#1976d2', '#2e7d32', '#7b1fa2', '#00796b', '#d32f2f', '#f57c00', '#0288d1', '#388e3c']

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
  const { showSnackbar } = useSnackbar()

  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)
  const [isProduceDialogOpen, setIsProduceDialogOpen] = useState(false)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [drawerRecipe, setDrawerRecipe] = useState<Recipe | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredRecipes = useMemo(() => {
    if (!searchQuery) return recipes
    return recipes.filter((r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
  }, [recipes, searchQuery])

  const { sorted, orderBy, order, onSort } = useTableSort<Recipe>(filteredRecipes)
  const { paginated, page, rowsPerPage, totalCount, onPageChange, onRowsPerPageChange } = useTablePagination(sorted)

  // Summary stats
  const profitableCount = recipes.filter((r) => r.is_profitable).length
  const unprofitableCount = recipes.filter((r) => !r.is_profitable).length
  const avgMargin = recipes.length > 0
    ? recipes.reduce((sum, r) => sum + Number(r.margin_percent), 0) / recipes.length
    : 0

  const resourceNameMap = useMemo(() => {
    const map: Record<string, { name: string; last_unit_cost: number }> = {}
    for (const r of resources) {
      map[r.id] = { name: r.name, last_unit_cost: r.last_unit_cost }
    }
    return map
  }, [resources])

  // Pie chart data for drawer
  const ingredientCostData = useMemo(() => {
    if (!drawerRecipe) return []
    return drawerRecipe.items.map((item) => {
      const resource = resourceNameMap[item.resource_id]
      const cost = (resource?.last_unit_cost ?? 0) * Number(item.quantity)
      return {
        name: resource?.name || item.resource_name || 'Desconocido',
        value: cost,
      }
    }).filter((d) => d.value > 0)
  }, [drawerRecipe, resourceNameMap])

  if (isLoading) {
    return (
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <CircularProgress size={24} />
        <Typography color="text.secondary">Cargando...</Typography>
      </Box>
    )
  }

  if (restaurants.length === 0) {
    return <TRNoRestaurantPrompt />
  }

  const handleCreateRecipe = async (data: RecipeCreate | RecipeUpdate) => {
    console.log('INFO [RestaurantOSRecipesPage]: Creating recipe')
    setIsSubmitting(true)
    try {
      await createRecipe(data as RecipeCreate)
      setIsAddDialogOpen(false)
      showSnackbar('Receta creada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to create recipe:', err)
      showSnackbar('Error al crear receta', 'error')
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
      setIsEditDialogOpen(false)
      setSelectedRecipe(null)
      showSnackbar('Receta actualizada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to update recipe:', err)
      showSnackbar('Error al actualizar receta', 'error')
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
      setIsDeleteDialogOpen(false)
      setSelectedRecipe(null)
      showSnackbar('Receta eliminada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to delete recipe:', err)
      showSnackbar('Error al eliminar receta', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleProduce = async (qty: number) => {
    if (!selectedRecipe) return
    console.log('INFO [RestaurantOSRecipesPage]: Producing recipe:', selectedRecipe.id, 'quantity:', qty)
    setIsSubmitting(true)
    try {
      await produceRecipe(selectedRecipe.id, qty)
      setIsProduceDialogOpen(false)
      setSelectedRecipe(null)
      showSnackbar('Produccion registrada', 'success')
    } catch (err) {
      console.error('ERROR [RestaurantOSRecipesPage]: Failed to produce recipe:', err)
      showSnackbar('Error al producir receta', 'error')
    } finally {
      setIsSubmitting(false)
    }
  }

  const sortableHeader = (label: string, column: keyof Recipe) => (
    <TableSortLabel
      active={orderBy === column}
      direction={orderBy === column ? order : 'asc'}
      onClick={() => onSort(column)}
    >
      {label}
    </TableSortLabel>
  )

  return (
    <Box sx={{ p: 3 }}>
      <TRBreadcrumbs
        module="RestaurantOS"
        moduleHref="/poc/restaurant-os"
        restaurantName={currentRestaurant?.name}
        currentPage="Recetas"
      />

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>
          Recetas
        </Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setIsAddDialogOpen(true)}>
          Agregar Receta
        </Button>
      </Box>

      {/* Summary Bar */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`${profitableCount} rentables`} color="success" variant="outlined" />
        <Chip label={`${unprofitableCount} no rentables`} color={unprofitableCount > 0 ? 'error' : 'default'} variant="outlined" />
        <Chip label={`Margen promedio: ${avgMargin.toFixed(1)}%`} variant="outlined" />
      </Box>

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

      {/* Table */}
      {recipesLoading ? (
        <TRTableSkeleton columns={7} />
      ) : filteredRecipes.length === 0 ? (
        <TREmptyState
          icon={<MenuBookIcon sx={{ fontSize: 64 }} />}
          title="No se encontraron recetas"
          description="Crea recetas con ingredientes para calcular costos y margenes"
          actionLabel="Agregar Receta"
          onAction={() => setIsAddDialogOpen(true)}
        />
      ) : (
        <>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{sortableHeader('Nombre', 'name')}</TableCell>
                  <TableCell>{sortableHeader('Precio Venta', 'sale_price')}</TableCell>
                  <TableCell>{sortableHeader('Costo Actual', 'current_cost')}</TableCell>
                  <TableCell>{sortableHeader('Margen %', 'margin_percent')}</TableCell>
                  <TableCell>Rentabilidad</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginated.map((recipe) => (
                  <TableRow
                    key={recipe.id}
                    hover
                    sx={{
                      cursor: 'pointer',
                      ...(!recipe.is_profitable && { backgroundColor: 'rgba(211, 47, 47, 0.04)' }),
                    }}
                    onClick={() => setDrawerRecipe(recipe)}
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
                        onClick={(e) => { e.stopPropagation(); setSelectedRecipe(recipe); setIsEditDialogOpen(true) }}
                        aria-label="edit"
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => { e.stopPropagation(); setSelectedRecipe(recipe); setIsDeleteDialogOpen(true) }}
                        aria-label="delete"
                        color="error"
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={(e) => { e.stopPropagation(); setSelectedRecipe(recipe); setIsProduceDialogOpen(true) }}
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
          <TablePagination
            component="div"
            count={totalCount}
            page={page}
            onPageChange={(_, p) => onPageChange(p)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => onRowsPerPageChange(parseInt(e.target.value, 10))}
            rowsPerPageOptions={[10, 25, 50]}
            labelRowsPerPage="Filas por pagina"
          />
        </>
      )}

      {/* Add Recipe Dialog */}
      <Dialog open={isAddDialogOpen} onClose={() => setIsAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Agregar Receta</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TRRecipeForm
              onSubmit={handleCreateRecipe}
              restaurantId={currentRestaurant?.id || ''}
              resources={resources}
              onCancel={() => setIsAddDialogOpen(false)}
              isSubmitting={isSubmitting}
            />
          </Box>
        </DialogContent>
      </Dialog>

      {/* Edit Recipe Dialog */}
      <Dialog open={isEditDialogOpen} onClose={() => { setIsEditDialogOpen(false); setSelectedRecipe(null) }} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Receta</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {selectedRecipe && (
              <TRRecipeForm
                onSubmit={handleUpdateRecipe}
                initialData={selectedRecipe}
                restaurantId={currentRestaurant?.id || ''}
                resources={resources}
                onCancel={() => { setIsEditDialogOpen(false); setSelectedRecipe(null) }}
                isSubmitting={isSubmitting}
              />
            )}
          </Box>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={isDeleteDialogOpen} onClose={() => { setIsDeleteDialogOpen(false); setSelectedRecipe(null) }}>
        <DialogTitle>Eliminar Receta</DialogTitle>
        <DialogContent>
          <Typography>
            ¿Esta seguro que desea eliminar esta receta?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setIsDeleteDialogOpen(false); setSelectedRecipe(null) }} disabled={isSubmitting}>
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

      {/* Enhanced Produce Dialog */}
      <TRProduceRecipeDialog
        open={isProduceDialogOpen}
        recipe={selectedRecipe}
        resources={resources}
        isSubmitting={isSubmitting}
        onClose={() => { setIsProduceDialogOpen(false); setSelectedRecipe(null) }}
        onProduce={handleProduce}
      />

      {/* Detail Drawer */}
      <Drawer
        anchor="right"
        open={!!drawerRecipe}
        onClose={() => setDrawerRecipe(null)}
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
              <TableContainer component={Paper} sx={{ mb: 3 }}>
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

            {/* Ingredient Cost Breakdown Chart */}
            {ingredientCostData.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Distribucion de Costos
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={ingredientCostData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={(entry) => entry.name}
                    >
                      {ingredientCostData.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            )}
          </Box>
        )}
      </Drawer>
    </Box>
  )
}

export default RestaurantOSRecipesPage
