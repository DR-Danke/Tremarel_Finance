import { Paper, Typography, Box } from '@mui/material'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import type { CategoryBreakdown } from '@/types'

interface TRExpenseBreakdownChartProps {
  data: CategoryBreakdown[]
}

// Default color palette for pie chart segments
const COLORS = [
  '#f44336', // red
  '#e91e63', // pink
  '#9c27b0', // purple
  '#673ab7', // deep purple
  '#3f51b5', // indigo
  '#2196f3', // blue
  '#03a9f4', // light blue
  '#00bcd4', // cyan
  '#009688', // teal
  '#4caf50', // green
  '#8bc34a', // light green
  '#cddc39', // lime
  '#ffeb3b', // yellow
  '#ffc107', // amber
  '#ff9800', // orange
  '#ff5722', // deep orange
]

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

interface TooltipPayload {
  payload: {
    name: string
    value: number
    percentage: number
  }
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayload[]
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <Paper sx={{ p: 1.5 }}>
        <Typography variant="body2" fontWeight={600}>
          {data.name}
        </Typography>
        <Typography variant="body2">
          Amount: {formatCurrency(data.value)}
        </Typography>
        <Typography variant="body2">
          {data.percentage}% of total
        </Typography>
      </Paper>
    )
  }
  return null
}

/**
 * TRExpenseBreakdownChart displays a pie chart showing expense distribution by category.
 */
export const TRExpenseBreakdownChart: React.FC<TRExpenseBreakdownChartProps> = ({ data }) => {
  if (data.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>
          Expenses by Category
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
            No expense data available for this month.
          </Typography>
        </Box>
      </Paper>
    )
  }

  // Transform data for chart
  const chartData = data.map((item, index) => ({
    name: item.category_name,
    value: Number(item.amount),
    percentage: item.percentage,
    color: item.color || COLORS[index % COLORS.length],
  }))

  return (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Expenses by Category
      </Typography>
      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              outerRadius={100}
              innerRadius={40}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
              label={({ name, percentage }) => `${name}: ${percentage}%`}
              labelLine={false}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  )
}

export default TRExpenseBreakdownChart
