import React from 'react'
import { Card, CardContent, Typography, Chip, Box } from '@mui/material'
import type { DraggableProvidedDragHandleProps, DraggableProvidedDraggableProps } from '@hello-pangea/dnd'
import type { Prospect } from '@/types'

interface TRProspectCardProps {
  prospect: Prospect
  onEdit?: (prospect: Prospect) => void
  onClick?: (prospect: Prospect) => void
  dragHandleProps?: DraggableProvidedDragHandleProps | null
  draggableProps?: DraggableProvidedDraggableProps
  innerRef?: (element: HTMLElement | null) => void
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

export const TRProspectCard: React.FC<TRProspectCardProps> = ({
  prospect,
  onEdit,
  onClick,
  dragHandleProps,
  draggableProps,
  innerRef,
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(prospect)
    } else if (onEdit) {
      onEdit(prospect)
    }
  }

  return (
    <Card
      ref={innerRef}
      {...draggableProps}
      {...dragHandleProps}
      sx={{
        cursor: 'pointer',
        transition: 'box-shadow 0.2s',
        '&:hover': {
          boxShadow: 3,
        },
      }}
      onClick={handleClick}
    >
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontWeight: 600,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {prospect.company_name}
        </Typography>

        {prospect.contact_name && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25 }}>
            {prospect.contact_name}
          </Typography>
        )}

        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
          {prospect.estimated_value != null && (
            <Chip
              label={formatCurrency(prospect.estimated_value)}
              size="small"
              color="primary"
              variant="outlined"
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          )}
          {prospect.source && (
            <Chip
              label={prospect.source}
              size="small"
              variant="outlined"
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          )}
        </Box>

        <Typography
          variant="caption"
          color="text.disabled"
          sx={{ display: 'block', mt: 0.5 }}
        >
          {formatDate(prospect.created_at)}
        </Typography>
      </CardContent>
    </Card>
  )
}

export default TRProspectCard
