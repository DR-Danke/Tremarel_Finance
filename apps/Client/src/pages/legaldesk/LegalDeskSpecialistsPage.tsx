import React from 'react'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material'
import { useLegaldeskSpecialists } from '@/hooks/useLegaldeskSpecialists'

export const LegalDeskSpecialistsPage: React.FC = () => {
  const { specialists, loading, error, refreshSpecialists } = useLegaldeskSpecialists()

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
            <Button color="inherit" size="small" onClick={refreshSpecialists}>
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
        Specialists
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Manage legal specialists and their expertise
      </Typography>

      {specialists.length === 0 ? (
        <Typography variant="body2" color="text.disabled" sx={{ mt: 2 }}>
          No specialists found
        </Typography>
      ) : (
        <TableContainer sx={{ mt: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Experience (years)</TableCell>
                <TableCell>Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {specialists.map((s) => (
                <TableRow key={s.id}>
                  <TableCell>{s.full_name}</TableCell>
                  <TableCell>{s.email}</TableCell>
                  <TableCell>{s.years_experience}</TableCell>
                  <TableCell>{s.overall_score}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  )
}

export default LegalDeskSpecialistsPage
