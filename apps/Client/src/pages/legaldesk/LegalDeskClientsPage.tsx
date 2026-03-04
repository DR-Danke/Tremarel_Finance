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
import { useLegaldeskClients } from '@/hooks/useLegaldeskClients'
import { CLIENT_TYPE_LABELS } from '@/types/legaldesk'
import type { ClientType } from '@/types/legaldesk'

export const LegalDeskClientsPage: React.FC = () => {
  const { clients, loading, error, refreshClients } = useLegaldeskClients()

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
            <Button color="inherit" size="small" onClick={refreshClients}>
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
        Clients
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage legal desk clients
      </Typography>

      {clients.length === 0 ? (
        <Typography variant="body2" color="text.disabled" sx={{ mt: 2 }}>
          No clients found
        </Typography>
      ) : (
        <TableContainer sx={{ mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Country</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.map((c) => (
                <TableRow key={c.id}>
                  <TableCell>{c.name}</TableCell>
                  <TableCell>
                    <Chip
                      label={CLIENT_TYPE_LABELS[c.client_type as ClientType] || c.client_type}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{c.contact_email || '-'}</TableCell>
                  <TableCell>{c.country || '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

export default LegalDeskClientsPage
