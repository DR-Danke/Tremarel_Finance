import { useState, useMemo } from 'react'
import {
  Paper,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Tabs,
  Tab,
} from '@mui/material'
import type { CategorySummary, TransactionType } from '@/types'

interface TRCategoryBreakdownTableProps {
  data: CategorySummary[]
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel({ children, value, index }: TabPanelProps) {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  )
}

/**
 * TRCategoryBreakdownTable displays a table showing category breakdown with tabs for filtering.
 */
export const TRCategoryBreakdownTable: React.FC<TRCategoryBreakdownTableProps> = ({
  data,
}) => {
  const [tabValue, setTabValue] = useState(0)

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    const tabLabels = ['all', 'expense', 'income']
    console.log(`INFO [TRCategoryBreakdownTable]: Tab changed to ${tabLabels[newValue]}`)
    setTabValue(newValue)
  }

  // Filter and sort data based on selected tab
  const filteredData = useMemo(() => {
    let filtered: CategorySummary[]

    if (tabValue === 0) {
      // All categories
      filtered = [...data]
    } else if (tabValue === 1) {
      // Expenses only
      filtered = data.filter((item) => item.type === 'expense')
    } else {
      // Income only
      filtered = data.filter((item) => item.type === 'income')
    }

    // Sort by amount descending
    return filtered.sort((a, b) => Number(b.amount) - Number(a.amount))
  }, [data, tabValue])

  const getTypeChipColor = (type: TransactionType) => {
    return type === 'income' ? 'success' : 'error'
  }

  const renderTable = (tableData: CategorySummary[]) => {
    if (tableData.length === 0) {
      return (
        <Box
          sx={{
            py: 4,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography color="text.secondary">
            No category data available for the selected criteria.
          </Typography>
        </Box>
      )
    }

    return (
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell align="right">Percentage</TableCell>
              <TableCell align="center">Type</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((row) => (
              <TableRow key={row.category_id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {row.color && (
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: row.color,
                        }}
                      />
                    )}
                    {row.category_name}
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography
                    fontWeight={500}
                    color={row.type === 'income' ? 'success.main' : 'error.main'}
                  >
                    {formatCurrency(Number(row.amount))}
                  </Typography>
                </TableCell>
                <TableCell align="right">{row.percentage.toFixed(1)}%</TableCell>
                <TableCell align="center">
                  <Chip
                    label={row.type.charAt(0).toUpperCase() + row.type.slice(1)}
                    color={getTypeChipColor(row.type)}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  return (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Category Breakdown
      </Typography>

      <Tabs
        value={tabValue}
        onChange={handleTabChange}
        aria-label="category breakdown tabs"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="All" />
        <Tab label="Expenses" />
        <Tab label="Income" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        {renderTable(filteredData)}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        {renderTable(filteredData)}
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        {renderTable(filteredData)}
      </TabPanel>
    </Paper>
  )
}

export default TRCategoryBreakdownTable
