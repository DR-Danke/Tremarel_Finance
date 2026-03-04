import React from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Grid,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useNavigate } from 'react-router-dom'
import { useLegaldeskCases } from '@/hooks/useLegaldeskCases'
import { TRCaseStatusBadge } from '@/components/ui/TRCaseStatusBadge'
import { TRLegalDomainBadge } from '@/components/ui/TRLegalDomainBadge'
import { TRCasePriorityBadge } from '@/components/ui/TRCasePriorityBadge'
import {
  CASE_STATUS_LABELS,
  LEGAL_DOMAIN_LABELS,
  CASE_PRIORITY_LABELS,
  CASE_TYPE_LABELS,
} from '@/types/legaldesk'
import type { CaseStatus, LegalDomain, CasePriority } from '@/types/legaldesk'

export const LegalDeskCasesPage: React.FC = () => {
  const { cases, loading, error, filters, setFilters, refreshCases } = useLegaldeskCases()
  const navigate = useNavigate()

  console.log('INFO [LegalDeskCasesPage]: Rendering cases page')

  if (loading && cases.length === 0) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Legal Desk Cases
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/poc/legal-desk/cases/new')}
          >
            New Case
          </Button>
        </Box>

        {error && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            action={
              <Button color="inherit" size="small" onClick={refreshCases}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        {/* Filters */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                label="Status"
                fullWidth
                size="small"
                value={filters.status || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    status: (e.target.value || undefined) as CaseStatus | undefined,
                  })
                }
              >
                <MenuItem value="">All</MenuItem>
                {Object.entries(CASE_STATUS_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                label="Domain"
                fullWidth
                size="small"
                value={filters.legal_domain || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    legal_domain: (e.target.value || undefined) as LegalDomain | undefined,
                  })
                }
              >
                <MenuItem value="">All</MenuItem>
                {Object.entries(LEGAL_DOMAIN_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                label="Priority"
                fullWidth
                size="small"
                value={filters.priority || ''}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    priority: (e.target.value || undefined) as CasePriority | undefined,
                  })
                }
              >
                <MenuItem value="">All</MenuItem>
                {Object.entries(CASE_PRIORITY_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                label="Type"
                fullWidth
                size="small"
                value=""
                onChange={() => {
                  // case_type not in LdCaseFilters — filter placeholder
                }}
              >
                <MenuItem value="">All</MenuItem>
                {Object.entries(CASE_TYPE_LABELS).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
              </TextField>
            </Grid>
          </Grid>
        </Paper>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Case #</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Client</TableCell>
                <TableCell>Domain</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Priority</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {cases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      No cases found. Click "New Case" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                cases.map((c) => (
                  <TableRow
                    key={c.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/poc/legal-desk/cases/${c.id}`)}
                  >
                    <TableCell>{c.case_number}</TableCell>
                    <TableCell>{c.title}</TableCell>
                    <TableCell>{c.client_id}</TableCell>
                    <TableCell>
                      <TRLegalDomainBadge domain={c.legal_domain} />
                    </TableCell>
                    <TableCell>
                      <TRCaseStatusBadge status={c.status} />
                    </TableCell>
                    <TableCell>
                      <TRCasePriorityBadge priority={c.priority} />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  )
}

export default LegalDeskCasesPage
