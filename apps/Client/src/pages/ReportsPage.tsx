import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Grid,
  Alert,
  Skeleton,
  CircularProgress,
} from '@mui/material'
import DownloadIcon from '@mui/icons-material/Download'
import ReceiptIcon from '@mui/icons-material/Receipt'
import { useEntity } from '@/hooks/useEntity'
import { useReports } from '@/hooks/useReports'
import { TRReportDateRangePicker } from '@/components/ui/TRReportDateRangePicker'
import { TRIncomeExpenseChart } from '@/components/ui/TRIncomeExpenseChart'
import { TRCategoryBreakdownTable } from '@/components/ui/TRCategoryBreakdownTable'
import { TRStatCard } from '@/components/ui/TRStatCard'

/**
 * Reports page displaying financial reports with date range filtering.
 */
export const ReportsPage: React.FC = () => {
  const { currentEntity } = useEntity()
  const {
    reportData,
    filters,
    isLoading,
    error,
    setFilters,
    exportToCsv,
    isExporting,
  } = useReports(currentEntity?.id)

  // Render loading skeleton for stat cards
  const renderStatCardSkeleton = () => (
    <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Box sx={{ flex: 1 }}>
          <Skeleton width={100} height={20} />
          <Skeleton width={150} height={40} sx={{ mt: 1 }} />
        </Box>
        <Skeleton variant="circular" width={60} height={60} />
      </Box>
    </Paper>
  )

  // No entity selected state
  if (!currentEntity) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              No Entity Selected
            </Typography>
            <Typography color="text.secondary">
              Please select an entity to view reports.
            </Typography>
          </Paper>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Reports
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Financial reports for {currentEntity.name}
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={isExporting ? <CircularProgress size={20} color="inherit" /> : <DownloadIcon />}
            onClick={exportToCsv}
            disabled={isExporting || isLoading || !reportData}
          >
            {isExporting ? 'Exporting...' : 'Export CSV'}
          </Button>
        </Box>

        {/* Date Range Picker */}
        <TRReportDateRangePicker filters={filters} onChange={setFilters} />

        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading State for Stat Cards */}
        {isLoading ? (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              {renderStatCardSkeleton()}
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              {renderStatCardSkeleton()}
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              {renderStatCardSkeleton()}
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              {renderStatCardSkeleton()}
            </Grid>
          </Grid>
        ) : reportData ? (
          <>
            {/* Summary Cards */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={12} sm={6} md={3}>
                <TRStatCard
                  title="Total Income"
                  value={Number(reportData.summary.total_income)}
                  subtitle={`${filters.startDate} - ${filters.endDate}`}
                  variant="income"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TRStatCard
                  title="Total Expenses"
                  value={Number(reportData.summary.total_expenses)}
                  subtitle={`${filters.startDate} - ${filters.endDate}`}
                  variant="expense"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <TRStatCard
                  title="Net Balance"
                  value={Number(reportData.summary.net_balance)}
                  subtitle={`${filters.startDate} - ${filters.endDate}`}
                  variant="balance"
                />
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper
                  elevation={2}
                  sx={{
                    p: 3,
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary">
                        Transactions
                      </Typography>
                      <Typography variant="h4" fontWeight={600} sx={{ mt: 1 }}>
                        {reportData.summary.transaction_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                        {filters.startDate} - {filters.endDate}
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        backgroundColor: 'grey.100',
                      }}
                    >
                      <ReceiptIcon sx={{ fontSize: 32, color: 'grey.600' }} />
                    </Box>
                  </Box>
                </Paper>
              </Grid>
            </Grid>

            {/* Charts and Tables */}
            <Grid container spacing={3}>
              {/* Income vs Expense Chart */}
              <Grid item xs={12} md={7}>
                <TRIncomeExpenseChart data={reportData.income_expense_comparison} />
              </Grid>

              {/* Category Breakdown Table */}
              <Grid item xs={12} md={5}>
                <TRCategoryBreakdownTable data={reportData.category_breakdown} />
              </Grid>
            </Grid>
          </>
        ) : null}
      </Box>
    </Container>
  )
}

export default ReportsPage
