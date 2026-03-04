import { Chip } from '@mui/material'

interface TRProfitabilityBadgeProps {
  marginPercent: number
  isProfitable: boolean
}

export const TRProfitabilityBadge: React.FC<TRProfitabilityBadgeProps> = ({
  marginPercent,
  isProfitable,
}) => {
  console.log('INFO [TRProfitabilityBadge]: Rendering margin:', marginPercent, 'profitable:', isProfitable)

  const label = isProfitable
    ? `Rentable (${marginPercent.toFixed(1)}%)`
    : `No Rentable (${marginPercent.toFixed(1)}%)`

  return (
    <Chip
      label={label}
      color={isProfitable ? 'success' : 'error'}
      size="small"
    />
  )
}

export default TRProfitabilityBadge
