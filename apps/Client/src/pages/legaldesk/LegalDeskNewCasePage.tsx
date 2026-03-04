import React from 'react'
import { Box, Typography } from '@mui/material'

export const LegalDeskNewCasePage: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        New Case
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Create a new legal case. Full form implementation coming soon.
      </Typography>
    </Box>
  )
}

export default LegalDeskNewCasePage
