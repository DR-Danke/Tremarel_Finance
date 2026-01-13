import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Typography,
  Box,
  Skeleton,
} from '@mui/material'
import { Edit, Delete } from '@mui/icons-material'
import type { Transaction, Category } from '@/types'

interface TRTransactionTableProps {
  transactions: Transaction[]
  categories: Record<string, Category>
  onEdit: (transaction: Transaction) => void
  onDelete: (transactionId: string) => void
  isLoading?: boolean
  canDelete?: boolean
}

/**
 * Format a number as currency.
 */
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

/**
 * Format a date string to a readable format.
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

export const TRTransactionTable: React.FC<TRTransactionTableProps> = ({
  transactions,
  categories,
  onEdit,
  onDelete,
  isLoading = false,
  canDelete = true,
}) => {
  console.log('INFO [TRTransactionTable]: Rendering with', transactions.length, 'transactions')

  if (isLoading) {
    return (
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {[1, 2, 3].map((n) => (
              <TableRow key={n}>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" width={80} /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
                <TableCell><Skeleton variant="text" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  if (transactions.length === 0) {
    return (
      <Paper sx={{ p: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 4,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Transactions Found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Add your first transaction to start tracking your finances.
          </Typography>
        </Box>
      </Paper>
    )
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Category</TableCell>
            <TableCell align="right">Amount</TableCell>
            <TableCell>Description</TableCell>
            <TableCell align="center">Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map((transaction) => {
            const category = categories[transaction.category_id]
            return (
              <TableRow key={transaction.id} hover>
                <TableCell>{formatDate(transaction.date)}</TableCell>
                <TableCell>
                  <Chip
                    label={transaction.type.charAt(0).toUpperCase() + transaction.type.slice(1)}
                    color={transaction.type === 'income' ? 'success' : 'error'}
                    size="small"
                    variant="filled"
                  />
                </TableCell>
                <TableCell>{category?.name || 'Unknown'}</TableCell>
                <TableCell
                  align="right"
                  sx={{
                    fontWeight: 'medium',
                    color: transaction.type === 'income' ? 'success.main' : 'error.main',
                  }}
                >
                  {transaction.type === 'income' ? '+' : '-'}
                  {formatCurrency(transaction.amount)}
                </TableCell>
                <TableCell>
                  {transaction.description || (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      No description
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={() => onEdit(transaction)}
                      aria-label="edit transaction"
                    >
                      <Edit fontSize="small" />
                    </IconButton>
                    {canDelete && (
                      <IconButton
                        size="small"
                        onClick={() => onDelete(transaction.id)}
                        aria-label="delete transaction"
                        color="error"
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

export default TRTransactionTable
