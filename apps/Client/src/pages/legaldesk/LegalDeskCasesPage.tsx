import React from 'react'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { useLegaldeskCases } from '@/hooks/useLegaldeskCases'
import { CASE_STATUS_LABELS, CASE_STATUS_COLORS } from '@/types/legaldesk'
import type { CaseStatus } from '@/types/legaldesk'

export const LegalDeskCasesPage: React.FC = () => {
  const { cases, loading, error, refreshCases } = useLegaldeskCases()

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 300 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refreshCases}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Cases
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage legal cases and their status
      </Typography>

      {cases.length === 0 ? (
        <Typography variant="body2" color="text.disabled" sx={{ mt: 2 }}>
          No cases found
        </Typography>
      ) : (
        <TableContainer sx={{ mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Case Number</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {cases.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>{c.case_number}</TableCell>
                  <TableCell>{c.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={CASE_STATUS_LABELS[c.status as CaseStatus] || c.status}
                      size="small"
                      sx={{ backgroundColor: CASE_STATUS_COLORS[c.status as CaseStatus], color: '#000' }}
                    />
                  </TableCell>
                  <TableCell>{c.priority}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

export default LegalDeskCasesPage
