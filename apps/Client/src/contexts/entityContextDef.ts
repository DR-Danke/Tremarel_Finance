import { createContext } from 'react'
import type { Entity, CreateEntityData, UpdateEntityData } from '@/types'

export interface EntityContextType {
  entities: Entity[]
  currentEntity: Entity | null
  isLoading: boolean
  switchEntity: (entityId: string) => void
  createEntity: (data: CreateEntityData) => Promise<Entity>
  updateEntity: (id: string, data: UpdateEntityData) => Promise<Entity>
  deleteEntity: (id: string) => Promise<void>
  refreshEntities: () => Promise<void>
}

export const EntityContext = createContext<EntityContextType | undefined>(undefined)
