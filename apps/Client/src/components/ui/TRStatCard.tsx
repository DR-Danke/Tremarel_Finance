import { Paper, Typography, Box } from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'

interface TRStatCardProps {
  title: string
  value: number
  subtitle?: string
  variant: 'income' | 'expense' | 'balance'
}

const formatCurrency = (value: number): string => {
  const absValue = Math.abs(value)
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(absValue)
  return value < 0 ? `-${formatted}` : formatted
}

/**
 * TRStatCard displays a financial statistic with icon and color coding.
 */
export const TRStatCard: React.FC<TRStatCardProps> = ({ title, value, subtitle, variant }) => {
  const getVariantConfig = () => {
    switch (variant) {
      case 'income':
        return {
          icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
          color: 'success.main',
          bgColor: 'success.light',
        }
      case 'expense':
        return {
          icon: <TrendingDownIcon sx={{ fontSize: 40 }} />,
          color: 'error.main',
          bgColor: 'error.light',
        }
      case 'balance':
        return {
          icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />,
          color: value >= 0 ? 'primary.main' : 'error.main',
          bgColor: value >= 0 ? 'primary.light' : 'error.light',
        }
    }
  }

  const config = getVariantConfig()

  return (
    <Paper
      elevation={2}
      sx={{
        p: 3,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography
            variant="h4"
            component="div"
            sx={{
              fontWeight: 600,
              color: config.color,
            }}
          >
            {formatCurrency(value)}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {subtitle}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            p: 1.5,
            borderRadius: 2,
            backgroundColor: config.bgColor,
            color: config.color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {config.icon}
        </Box>
      </Box>
    </Paper>
  )
}

export default TRStatCard
