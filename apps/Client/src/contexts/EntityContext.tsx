import React, { useState, useEffect, useCallback, useMemo } from 'react'
import type { Entity } from '@/types'
import { EntityContext, type EntityContextType } from './entityContextDef'

const SELECTED_ENTITY_KEY = 'selectedEntityId'

// Mock entities for development (will be replaced with API fetch later)
const MOCK_ENTITIES: Entity[] = [
  {
    id: 'entity-family-001',
    name: 'Family',
    type: 'family',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: 'entity-startup-001',
    name: 'Startup',
    type: 'startup',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
]

interface EntityProviderProps {
  children: React.ReactNode
}

export const EntityProvider: React.FC<EntityProviderProps> = ({ children }) => {
  const [currentEntity, setCurrentEntity] = useState<Entity | null>(null)
  const [entities, setEntities] = useState<Entity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Initialize entities and restore selected entity from localStorage
  useEffect(() => {
    const initializeEntities = () => {
      console.log('INFO [EntityContext]: Initializing entity context')

      // Use mock entities for now (will fetch from API later)
      setEntities(MOCK_ENTITIES)
      console.log('INFO [EntityContext]: Loaded entities:', MOCK_ENTITIES.map(e => e.name).join(', '))

      // Restore selected entity from localStorage
      const storedEntityId = localStorage.getItem(SELECTED_ENTITY_KEY)

      if (storedEntityId) {
        const storedEntity = MOCK_ENTITIES.find(e => e.id === storedEntityId)
        if (storedEntity) {
          setCurrentEntity(storedEntity)
          console.log('INFO [EntityContext]: Restored entity from storage:', storedEntity.name)
        } else {
          // Stored entity not found, select first entity
          setCurrentEntity(MOCK_ENTITIES[0])
          localStorage.setItem(SELECTED_ENTITY_KEY, MOCK_ENTITIES[0].id)
          console.log('INFO [EntityContext]: Stored entity not found, selecting default:', MOCK_ENTITIES[0].name)
        }
      } else {
        // No stored entity, select first entity
        setCurrentEntity(MOCK_ENTITIES[0])
        localStorage.setItem(SELECTED_ENTITY_KEY, MOCK_ENTITIES[0].id)
        console.log('INFO [EntityContext]: No stored entity, selecting default:', MOCK_ENTITIES[0].name)
      }

      setIsLoading(false)
    }

    initializeEntities()
  }, [])

  const switchEntity = useCallback((entityId: string) => {
    console.log('INFO [EntityContext]: Switching to entity:', entityId)

    const entity = entities.find(e => e.id === entityId)

    if (entity) {
      setCurrentEntity(entity)
      localStorage.setItem(SELECTED_ENTITY_KEY, entityId)
      console.log('INFO [EntityContext]: Entity selected:', entity.name)
    } else {
      console.error('ERROR [EntityContext]: Entity not found:', entityId)
    }
  }, [entities])

  const value = useMemo<EntityContextType>(
    () => ({
      currentEntity,
      entities,
      switchEntity,
      isLoading,
    }),
    [currentEntity, entities, switchEntity, isLoading]
  )

  return <EntityContext.Provider value={value}>{children}</EntityContext.Provider>
}

export default EntityProvider
