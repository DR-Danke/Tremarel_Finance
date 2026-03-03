/**
 * Resource and InventoryMovement types for RestaurantOS resource/inventory management.
 * Matches backend ResourceResponseDTO, ResourceCreateDTO, ResourceUpdateDTO,
 * InventoryMovementResponseDTO, InventoryMovementCreateDTO.
 */

export type ResourceType = 'producto' | 'activo' | 'servicio'

export interface Resource {
  id: string
  restaurant_id: string
  type: ResourceType
  name: string
  unit: string
  current_stock: number
  minimum_stock: number
  last_unit_cost: number
  is_low_stock: boolean
  created_at: string
  updated_at: string | null
}

export interface ResourceCreate {
  restaurant_id: string
  type?: ResourceType
  name: string
  unit: string
  current_stock?: number
  minimum_stock?: number
  last_unit_cost?: number
}

export interface ResourceUpdate {
  type?: ResourceType
  name?: string
  unit?: string
  current_stock?: number
  minimum_stock?: number
  last_unit_cost?: number
}

export interface ResourceFilters {
  type?: ResourceType
}

export type MovementType = 'entry' | 'exit'

export type MovementReason = 'compra' | 'uso' | 'produccion' | 'merma' | 'receta' | 'ajuste'

export interface InventoryMovement {
  id: string
  resource_id: string
  type: MovementType
  quantity: number
  reason: MovementReason
  date: string | null
  person_id: string | null
  restaurant_id: string
  notes: string | null
  created_at: string
}

export interface InventoryMovementCreate {
  resource_id: string
  restaurant_id: string
  type: MovementType
  quantity: number
  reason: MovementReason
  date?: string
  person_id?: string
  notes?: string
}

export interface MovementFilters {
  date_from?: string
  date_to?: string
  reason?: MovementReason
}

export const RESOURCE_TYPE_LABELS: Record<ResourceType, string> = {
  producto: 'Producto',
  activo: 'Activo',
  servicio: 'Servicio',
}

export const MOVEMENT_TYPE_LABELS: Record<MovementType, string> = {
  entry: 'Entrada',
  exit: 'Salida',
}

export const MOVEMENT_REASON_LABELS: Record<MovementReason, string> = {
  compra: 'Compra',
  uso: 'Uso',
  produccion: 'Producción',
  merma: 'Merma',
  receta: 'Receta',
  ajuste: 'Ajuste',
}
