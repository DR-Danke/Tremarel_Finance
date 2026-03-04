import React from 'react'
import { Box, Typography, LinearProgress } from '@mui/material'

interface TRSpecialistScoreDisplayProps {
  score: number
  maxScore?: number
}

export const TRSpecialistScoreDisplay: React.FC<TRSpecialistScoreDisplayProps> = ({
  score,
  maxScore = 10,
}) => {
  const percentage = Math.min((score / maxScore) * 100, 100)

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 32 }}>
        {score.toFixed(1)}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={percentage}
        sx={{ flex: 1, height: 8, borderRadius: 4 }}
      />
    </Box>
  )
}

export default TRSpecialistScoreDisplay
