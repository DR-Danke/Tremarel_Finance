import React from 'react'
import { Box, Typography } from '@mui/material'

export const LegalDeskAnalyticsPage: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Analytics
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Legal Desk analytics and reporting. Full implementation coming soon.
      </Typography>
    </Box>
  )
}

export default LegalDeskAnalyticsPage
