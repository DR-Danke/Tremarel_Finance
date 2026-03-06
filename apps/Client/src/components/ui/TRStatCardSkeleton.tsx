import React from 'react'
import { Paper, Box, Skeleton } from '@mui/material'

export const TRStatCardSkeleton: React.FC = () => {
  return (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Skeleton variant="text" width={100} height={20} />
          <Skeleton variant="text" width={60} height={40} sx={{ mt: 0.5 }} />
          <Skeleton variant="text" width={120} height={16} sx={{ mt: 0.5 }} />
        </Box>
        <Skeleton variant="rounded" width={56} height={56} />
      </Box>
    </Paper>
  )
}
