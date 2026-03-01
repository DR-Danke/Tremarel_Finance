import React from 'react'
import { Paper, Typography, Box, Chip } from '@mui/material'
import { Droppable, Draggable } from '@hello-pangea/dnd'
import { TRProspectCard } from '@/components/ui/TRProspectCard'
import type { PipelineStage, Prospect } from '@/types'

interface TRKanbanColumnProps {
  stage: PipelineStage
  prospects: Prospect[]
  onProspectClick?: (prospect: Prospect) => void
  onProspectEdit?: (prospect: Prospect) => void
}

export const TRKanbanColumn: React.FC<TRKanbanColumnProps> = ({
  stage,
  prospects,
  onProspectClick,
  onProspectEdit,
}) => {
  const stageColor = stage.color || '#9e9e9e'

  return (
    <Box
      sx={{
        minWidth: 280,
        maxWidth: 280,
        display: 'flex',
        flexDirection: 'column',
        maxHeight: 'calc(100vh - 220px)',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          p: 1.5,
          mb: 1,
          borderLeft: `4px solid ${stageColor}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'grey.50',
        }}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          {stage.display_name}
        </Typography>
        <Chip
          label={prospects.length}
          size="small"
          sx={{
            height: 22,
            minWidth: 22,
            backgroundColor: stageColor,
            color: '#fff',
            fontWeight: 600,
            fontSize: '0.75rem',
          }}
        />
      </Paper>

      <Droppable droppableId={stage.name}>
        {(provided) => (
          <Box
            ref={provided.innerRef}
            {...provided.droppableProps}
            sx={{
              flex: 1,
              overflowY: 'auto',
              backgroundColor: 'grey.100',
              borderRadius: 1,
              p: 1,
              minHeight: 100,
            }}
          >
            {prospects.length === 0 ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: 'center', py: 2 }}
              >
                No prospects
              </Typography>
            ) : (
              prospects.map((prospect, index) => (
                <Draggable key={prospect.id} draggableId={prospect.id} index={index}>
                  {(draggableProvided) => (
                    <Box sx={{ mb: 1 }}>
                      <TRProspectCard
                        prospect={prospect}
                        onClick={onProspectClick}
                        onEdit={onProspectEdit}
                        innerRef={draggableProvided.innerRef}
                        draggableProps={draggableProvided.draggableProps}
                        dragHandleProps={draggableProvided.dragHandleProps}
                      />
                    </Box>
                  )}
                </Draggable>
              ))
            )}
            {provided.placeholder}
          </Box>
        )}
      </Droppable>
    </Box>
  )
}

export default TRKanbanColumn
