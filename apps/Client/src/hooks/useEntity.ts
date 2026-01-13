import { useContext } from 'react'
import { EntityContext, type EntityContextType } from '@/contexts/entityContextDef'

/**
 * Custom hook for accessing entity context.
 * @throws Error if used outside of EntityProvider
 * @returns EntityContextType with currentEntity, entities, switchEntity, isLoading
 */
export const useEntity = (): EntityContextType => {
  const context = useContext(EntityContext)

  if (context === null) {
    throw new Error('useEntity must be used within an EntityProvider')
  }

  return context
}

export default useEntity
