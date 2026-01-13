import React, { useState, useEffect, useCallback, useMemo } from 'react'
import type { Entity, CreateEntityData, UpdateEntityData } from '@/types'
import { entityService } from '@/services/entityService'
import { EntityContext, type EntityContextType } from './entityContextDef'
import { useAuth } from '@/hooks/useAuth'

const ENTITY_KEY = 'currentEntityId'

interface EntityProviderProps {
  children: React.ReactNode
}

export const EntityProvider: React.FC<EntityProviderProps> = ({ children }) => {
  const { isAuthenticated } = useAuth()
  const [entities, setEntities] = useState<Entity[]>([])
  const [currentEntity, setCurrentEntity] = useState<Entity | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Fetch entities when user is authenticated
  useEffect(() => {
    const fetchEntities = async () => {
      if (!isAuthenticated) {
        console.log('INFO [EntityContext]: User not authenticated, clearing entities')
        setEntities([])
        setCurrentEntity(null)
        setIsLoading(false)
        return
      }

      console.log('INFO [EntityContext]: Fetching entities for user')
      setIsLoading(true)

      try {
        const userEntities = await entityService.getEntities()
        setEntities(userEntities)
        console.log('INFO [EntityContext]: Entities loaded successfully:', userEntities.length)

        // Restore current entity from localStorage or select first entity
        const storedEntityId = localStorage.getItem(ENTITY_KEY)
        if (storedEntityId) {
          const storedEntity = userEntities.find((e) => e.id === storedEntityId)
          if (storedEntity) {
            setCurrentEntity(storedEntity)
            console.log('INFO [EntityContext]: Restored entity from storage:', storedEntity.name)
          } else if (userEntities.length > 0) {
            setCurrentEntity(userEntities[0])
            localStorage.setItem(ENTITY_KEY, userEntities[0].id)
            console.log('INFO [EntityContext]: Stored entity not found, selecting first:', userEntities[0].name)
          }
        } else if (userEntities.length > 0) {
          setCurrentEntity(userEntities[0])
          localStorage.setItem(ENTITY_KEY, userEntities[0].id)
          console.log('INFO [EntityContext]: No stored entity, selecting first:', userEntities[0].name)
        }
      } catch (error) {
        console.error('ERROR [EntityContext]: Failed to fetch entities:', error)
        setEntities([])
        setCurrentEntity(null)
      } finally {
        setIsLoading(false)
      }
    }

    fetchEntities()
  }, [isAuthenticated])

  const switchEntity = useCallback(
    (entityId: string) => {
      console.log('INFO [EntityContext]: Switching to entity:', entityId)
      const entity = entities.find((e) => e.id === entityId)
      if (entity) {
        setCurrentEntity(entity)
        localStorage.setItem(ENTITY_KEY, entityId)
        console.log('INFO [EntityContext]: Switched to entity:', entity.name)
      } else {
        console.error('ERROR [EntityContext]: Entity not found:', entityId)
      }
    },
    [entities]
  )

  const createEntity = useCallback(async (data: CreateEntityData): Promise<Entity> => {
    console.log('INFO [EntityContext]: Creating entity:', data.name)
    const newEntity = await entityService.createEntity(data)
    setEntities((prev) => [...prev, newEntity])

    // Set as current entity if it's the first one
    if (entities.length === 0) {
      setCurrentEntity(newEntity)
      localStorage.setItem(ENTITY_KEY, newEntity.id)
      console.log('INFO [EntityContext]: Set new entity as current:', newEntity.name)
    }

    console.log('INFO [EntityContext]: Entity created:', newEntity.name)
    return newEntity
  }, [entities.length])

  const updateEntity = useCallback(
    async (id: string, data: UpdateEntityData): Promise<Entity> => {
      console.log('INFO [EntityContext]: Updating entity:', id)
      const updatedEntity = await entityService.updateEntity(id, data)
      setEntities((prev) => prev.map((e) => (e.id === id ? updatedEntity : e)))

      // Update current entity if it was the one updated
      if (currentEntity?.id === id) {
        setCurrentEntity(updatedEntity)
      }

      console.log('INFO [EntityContext]: Entity updated:', updatedEntity.name)
      return updatedEntity
    },
    [currentEntity?.id]
  )

  const deleteEntity = useCallback(
    async (id: string): Promise<void> => {
      console.log('INFO [EntityContext]: Deleting entity:', id)
      await entityService.deleteEntity(id)
      setEntities((prev) => prev.filter((e) => e.id !== id))

      // If deleted entity was current, switch to first remaining entity
      if (currentEntity?.id === id) {
        const remaining = entities.filter((e) => e.id !== id)
        if (remaining.length > 0) {
          setCurrentEntity(remaining[0])
          localStorage.setItem(ENTITY_KEY, remaining[0].id)
          console.log('INFO [EntityContext]: Switched to entity after deletion:', remaining[0].name)
        } else {
          setCurrentEntity(null)
          localStorage.removeItem(ENTITY_KEY)
          console.log('INFO [EntityContext]: No entities remaining after deletion')
        }
      }

      console.log('INFO [EntityContext]: Entity deleted:', id)
    },
    [currentEntity?.id, entities]
  )

  const refreshEntities = useCallback(async (): Promise<void> => {
    console.log('INFO [EntityContext]: Refreshing entities')
    setIsLoading(true)
    try {
      const userEntities = await entityService.getEntities()
      setEntities(userEntities)

      // Update current entity reference if it still exists
      if (currentEntity) {
        const updated = userEntities.find((e) => e.id === currentEntity.id)
        if (updated) {
          setCurrentEntity(updated)
        } else if (userEntities.length > 0) {
          setCurrentEntity(userEntities[0])
          localStorage.setItem(ENTITY_KEY, userEntities[0].id)
        } else {
          setCurrentEntity(null)
          localStorage.removeItem(ENTITY_KEY)
        }
      }

      console.log('INFO [EntityContext]: Entities refreshed:', userEntities.length)
    } catch (error) {
      console.error('ERROR [EntityContext]: Failed to refresh entities:', error)
    } finally {
      setIsLoading(false)
    }
  }, [currentEntity])

  const value = useMemo<EntityContextType>(
    () => ({
      entities,
      currentEntity,
      isLoading,
      switchEntity,
      createEntity,
      updateEntity,
      deleteEntity,
      refreshEntities,
    }),
    [entities, currentEntity, isLoading, switchEntity, createEntity, updateEntity, deleteEntity, refreshEntities]
  )

  return <EntityContext.Provider value={value}>{children}</EntityContext.Provider>
}

export default EntityProvider
