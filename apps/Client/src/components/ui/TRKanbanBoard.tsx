import React, { useMemo } from 'react'
import { Box, Skeleton } from '@mui/material'
import { DragDropContext, type DropResult } from '@hello-pangea/dnd'
import { TRKanbanColumn } from '@/components/ui/TRKanbanColumn'
import type { PipelineStage, Prospect } from '@/types'

interface TRKanbanBoardProps {
  stages: PipelineStage[]
  prospects: Prospect[]
  isLoading: boolean
  onProspectClick?: (prospect: Prospect) => void
  onProspectEdit?: (prospect: Prospect) => void
  onDragEnd?: (result: DropResult) => void
}

export const TRKanbanBoard: React.FC<TRKanbanBoardProps> = ({
  stages,
  prospects,
  isLoading,
  onProspectClick,
  onProspectEdit,
  onDragEnd,
}) => {
  const prospectsByStage = useMemo(() => {
    const map = new Map<string, Prospect[]>()
    for (const stage of stages) {
      map.set(stage.name, [])
    }
    for (const prospect of prospects) {
      const list = map.get(prospect.stage)
      if (list) {
        list.push(prospect)
      }
    }
    return map
  }, [stages, prospects])

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2 }}>
        {Array.from({ length: 7 }).map((_, i) => (
          <Box key={i} sx={{ minWidth: 280 }}>
            <Skeleton variant="rectangular" height={44} sx={{ mb: 1, borderRadius: 1 }} />
            <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 1 }} />
          </Box>
        ))}
      </Box>
    )
  }

  const sortedStages = [...stages].sort((a, b) => a.order_index - b.order_index)

  return (
    <DragDropContext onDragEnd={onDragEnd || (() => {})}>
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2 }}>
        {sortedStages.map((stage) => (
          <TRKanbanColumn
            key={stage.id}
            stage={stage}
            prospects={prospectsByStage.get(stage.name) || []}
            onProspectClick={onProspectClick}
            onProspectEdit={onProspectEdit}
          />
        ))}
      </Box>
    </DragDropContext>
  )
}

export default TRKanbanBoard
