import React, { useState } from 'react'
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
  Dialog,
  DialogTitle,
  DialogContent,
  Snackbar,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import { useLegaldeskClients } from '@/hooks/useLegaldeskClients'
import { TRLegalClientForm } from '@/components/forms/TRLegalClientForm'
import { CLIENT_TYPE_LABELS } from '@/types/legaldesk'
import type { LdClientCreate } from '@/types/legaldesk'

export const LegalDeskClientsPage: React.FC = () => {
  const { clients, loading, error, createClient, refreshClients } = useLegaldeskClients()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [snackbar, setSnackbar] = useState<string | null>(null)

  console.log('INFO [LegalDeskClientsPage]: Rendering clients page')

  const handleCreateClient = async (data: LdClientCreate) => {
    setSubmitting(true)
    try {
      await createClient(data)
      setDialogOpen(false)
      setSnackbar('Client created successfully')
      console.log('INFO [LegalDeskClientsPage]: Client created')
    } catch {
      console.error('ERROR [LegalDeskClientsPage]: Failed to create client')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading && clients.length === 0) {
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
            Legal Desk Clients
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Add Client
          </Button>
        </Box>

        {error && (
          <Alert
            severity="error"
            sx={{ mb: 2 }}
            action={
              <Button color="inherit" size="small" onClick={refreshClients}>
                Retry
              </Button>
            }
          >
            {error}
          </Alert>
        )}

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Industry</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {clients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      No clients yet. Click "Add Client" to create one.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                clients.map((client) => (
                  <TableRow key={client.id}>
                    <TableCell>{client.name}</TableCell>
                    <TableCell>{CLIENT_TYPE_LABELS[client.client_type]}</TableCell>
                    <TableCell>{client.contact_email || '-'}</TableCell>
                    <TableCell>{client.country || '-'}</TableCell>
                    <TableCell>{client.industry || '-'}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add Client</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <TRLegalClientForm onSubmit={handleCreateClient} loading={submitting} />
          </DialogContent>
        </Dialog>

        <Snackbar
          open={!!snackbar}
          autoHideDuration={3000}
          onClose={() => setSnackbar(null)}
          message={snackbar}
        />
      </Box>
    </Container>
  )
}

export default LegalDeskClientsPage
