import React from 'react'
import { Paper, Typography, Box } from '@mui/material'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import TrendingDownIcon from '@mui/icons-material/TrendingDown'
import AccountBalanceIcon from '@mui/icons-material/AccountBalance'

interface TRStatCardFinancialProps {
  title: string
  value: number
  subtitle?: string
  variant: 'income' | 'expense' | 'balance'
  icon?: never
  color?: never
}

interface TRStatCardGenericProps {
  title: string
  value: number | string
  subtitle?: string
  variant?: never
  icon: React.ReactNode
  color: string
}

type TRStatCardProps = TRStatCardFinancialProps | TRStatCardGenericProps

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
 * TRStatCard displays a statistic with icon and color coding.
 * Supports financial variants (income/expense/balance) and generic mode (custom icon + color).
 */
export const TRStatCard: React.FC<TRStatCardProps> = (props) => {
  const { title, value, subtitle } = props

  const isGeneric = 'icon' in props && props.icon !== undefined

  const getConfig = () => {
    if (isGeneric) {
      return {
        icon: props.icon,
        color: props.color,
        bgColor: `${props.color}22`,
        displayValue: String(value),
      }
    }

    const financialProps = props as TRStatCardFinancialProps
    switch (financialProps.variant) {
      case 'income':
        return {
          icon: <TrendingUpIcon sx={{ fontSize: 40 }} />,
          color: 'success.main',
          bgColor: 'success.light',
          displayValue: formatCurrency(value as number),
        }
      case 'expense':
        return {
          icon: <TrendingDownIcon sx={{ fontSize: 40 }} />,
          color: 'error.main',
          bgColor: 'error.light',
          displayValue: formatCurrency(value as number),
        }
      case 'balance':
        return {
          icon: <AccountBalanceIcon sx={{ fontSize: 40 }} />,
          color: (value as number) >= 0 ? 'primary.main' : 'error.main',
          bgColor: (value as number) >= 0 ? 'primary.light' : 'error.light',
          displayValue: formatCurrency(value as number),
        }
    }
  }

  const config = getConfig()

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
            {config.displayValue}
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
