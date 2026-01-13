import { createContext } from 'react'
import type { Entity } from '@/types'

export interface EntityContextType {
  currentEntity: Entity | null
  entities: Entity[]
  switchEntity: (entityId: string) => void
  isLoading: boolean
}

export const EntityContext = createContext<EntityContextType | null>(null)
