import { Rating, Box, Typography } from '@mui/material'

interface TRSpecialistScoreDisplayProps {
  score: number
  showNumeric?: boolean
}

export const TRSpecialistScoreDisplay: React.FC<TRSpecialistScoreDisplayProps> = ({
  score,
  showNumeric = true,
}) => {
  console.log('INFO [TRSpecialistScoreDisplay]: Rendering score:', score)

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Rating value={score} precision={0.5} readOnly max={5} />
      {showNumeric && (
        <Typography variant="body2" color="text.secondary">
          {score.toFixed(1)}
        </Typography>
      )}
    </Box>
  )
}

export default TRSpecialistScoreDisplay
