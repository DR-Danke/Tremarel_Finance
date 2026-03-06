import React from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'
import InboxIcon from '@mui/icons-material/Inbox'

interface TREmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  actionLabel?: string
  onAction?: () => void
}

export const TREmptyState: React.FC<TREmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <Paper sx={{ p: 6, textAlign: 'center' }}>
      <Box sx={{ color: 'text.disabled', mb: 2 }}>
        {icon || <InboxIcon sx={{ fontSize: 64 }} />}
      </Box>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      {description && (
        <Typography variant="body2" color="text.disabled" sx={{ mb: 2 }}>
          {description}
        </Typography>
      )}
      {actionLabel && onAction && (
        <Button variant="contained" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </Paper>
  )
}
