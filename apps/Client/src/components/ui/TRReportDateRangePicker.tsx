import { useState } from 'react'
import {
  Box,
  Button,
  Paper,
  TextField,
  Typography,
  Stack,
  Chip,
} from '@mui/material'
import type { ReportFilter } from '@/types'

interface TRReportDateRangePickerProps {
  filters: ReportFilter
  onChange: (filters: ReportFilter) => void
}

/**
 * Get date range for "This Month".
 */
function getThisMonthRange(): { startDate: string; endDate: string } {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()

  const startDate = new Date(year, month, 1)
  const endDate = new Date(year, month + 1, 0)

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}

/**
 * Get date range for "Last N Months".
 */
function getLastNMonthsRange(months: number): { startDate: string; endDate: string } {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()

  const endDate = new Date(year, month + 1, 0)
  const startDate = new Date(year, month - months + 1, 1)

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}

/**
 * Get date range for "This Year".
 */
function getThisYearRange(): { startDate: string; endDate: string } {
  const now = new Date()
  const year = now.getFullYear()

  const startDate = new Date(year, 0, 1)
  const endDate = new Date(year, 11, 31)

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}

/**
 * TRReportDateRangePicker component for selecting report date ranges.
 */
export const TRReportDateRangePicker: React.FC<TRReportDateRangePickerProps> = ({
  filters,
  onChange,
}) => {
  const [localStartDate, setLocalStartDate] = useState(filters.startDate)
  const [localEndDate, setLocalEndDate] = useState(filters.endDate)

  const handleQuickSelect = (range: { startDate: string; endDate: string }) => {
    console.log('INFO [TRReportDateRangePicker]: Quick select applied', range)
    setLocalStartDate(range.startDate)
    setLocalEndDate(range.endDate)
    onChange({
      ...filters,
      startDate: range.startDate,
      endDate: range.endDate,
    })
  }

  const handleApply = () => {
    console.log('INFO [TRReportDateRangePicker]: Custom range applied', {
      startDate: localStartDate,
      endDate: localEndDate,
    })
    onChange({
      ...filters,
      startDate: localStartDate,
      endDate: localEndDate,
    })
  }

  const handleClear = () => {
    const defaultRange = getThisMonthRange()
    console.log('INFO [TRReportDateRangePicker]: Range cleared to default', defaultRange)
    setLocalStartDate(defaultRange.startDate)
    setLocalEndDate(defaultRange.endDate)
    onChange({
      ...filters,
      startDate: defaultRange.startDate,
      endDate: defaultRange.endDate,
    })
  }

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Date Range
      </Typography>

      {/* Quick Select Buttons */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Quick Select:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <Chip
            label="This Month"
            onClick={() => handleQuickSelect(getThisMonthRange())}
            color="primary"
            variant="outlined"
            clickable
          />
          <Chip
            label="Last 3 Months"
            onClick={() => handleQuickSelect(getLastNMonthsRange(3))}
            color="primary"
            variant="outlined"
            clickable
          />
          <Chip
            label="Last 6 Months"
            onClick={() => handleQuickSelect(getLastNMonthsRange(6))}
            color="primary"
            variant="outlined"
            clickable
          />
          <Chip
            label="This Year"
            onClick={() => handleQuickSelect(getThisYearRange())}
            color="primary"
            variant="outlined"
            clickable
          />
        </Stack>
      </Box>

      {/* Date Inputs */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <TextField
          label="Start Date"
          type="date"
          value={localStartDate}
          onChange={(e) => setLocalStartDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          size="small"
          sx={{ minWidth: 150 }}
        />
        <Typography variant="body2" color="text.secondary">
          to
        </Typography>
        <TextField
          label="End Date"
          type="date"
          value={localEndDate}
          onChange={(e) => setLocalEndDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          size="small"
          sx={{ minWidth: 150 }}
        />
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="contained"
            size="small"
            onClick={handleApply}
            disabled={!localStartDate || !localEndDate}
          >
            Apply
          </Button>
          <Button
            variant="outlined"
            size="small"
            onClick={handleClear}
          >
            Clear
          </Button>
        </Box>
      </Box>
    </Paper>
  )
}

export default TRReportDateRangePicker
