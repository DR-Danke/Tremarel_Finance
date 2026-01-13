import { useContext } from 'react'
import { EntityContext, type EntityContextType } from '@/contexts/entityContextDef'

/**
 * Custom hook for accessing entity context.
 * @throws Error if used outside of EntityProvider
 * @returns EntityContextType with entities, currentEntity, isLoading, and CRUD operations
 */
export const useEntity = (): EntityContextType => {
  const context = useContext(EntityContext)

  if (context === undefined) {
    throw new Error('useEntity must be used within an EntityProvider')
  }

  return context
}

export default useEntity
