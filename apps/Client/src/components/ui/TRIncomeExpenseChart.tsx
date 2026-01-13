import { Paper, Typography, Box } from '@mui/material'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { IncomeExpenseComparison } from '@/types'

interface TRIncomeExpenseChartProps {
  data: IncomeExpenseComparison[]
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface TooltipPayload {
  color: string
  name: string
  value: number
  dataKey: string
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayload[]
  label?: string
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Paper sx={{ p: 1.5 }}>
        <Typography variant="body2" fontWeight={600}>
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Typography
            key={index}
            variant="body2"
            sx={{ color: entry.color }}
          >
            {entry.name}: {formatCurrency(entry.value)}
          </Typography>
        ))}
      </Paper>
    )
  }
  return null
}

/**
 * TRIncomeExpenseChart displays a line chart comparing income vs expenses over time.
 */
export const TRIncomeExpenseChart: React.FC<TRIncomeExpenseChartProps> = ({ data }) => {
  if (data.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>
          Income vs Expenses
        </Typography>
        <Box
          sx={{
            height: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="text.secondary">
            No data available for the selected date range.
          </Typography>
        </Box>
      </Paper>
    )
  }

  // Transform data for chart
  const chartData = data.map((item) => ({
    name: item.period,
    income: Number(item.income),
    expenses: Number(item.expenses),
  }))

  return (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Income vs Expenses
      </Typography>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(value: number) => formatCurrency(value)} tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey="income"
              name="Income"
              stroke="#4caf50"
              strokeWidth={2}
              dot={{ fill: '#4caf50', strokeWidth: 2 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="expenses"
              name="Expenses"
              stroke="#f44336"
              strokeWidth={2}
              dot={{ fill: '#f44336', strokeWidth: 2 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  )
}

export default TRIncomeExpenseChart
