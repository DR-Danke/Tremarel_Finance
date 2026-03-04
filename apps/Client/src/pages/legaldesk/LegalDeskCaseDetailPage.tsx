import React from 'react'
import { useParams } from 'react-router-dom'
import { Alert, Box, Button, Chip, CircularProgress, Typography } from '@mui/material'
import { useLegaldeskCaseDetail } from '@/hooks/useLegaldeskCaseDetail'
import { CASE_STATUS_LABELS, CASE_STATUS_COLORS } from '@/types/legaldesk'
import type { CaseStatus } from '@/types/legaldesk'

export const LegalDeskCaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const caseId = id ? parseInt(id, 10) : null
  const { caseDetail, loading, error, refreshCase } = useLegaldeskCaseDetail(
    caseId && !isNaN(caseId) ? caseId : null
  )

  if (!id) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">No case ID provided</Alert>
      </Box>
    )
  }

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
            <Button color="inherit" size="small" onClick={refreshCase}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    )
  }

  if (!caseDetail) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">Case not found</Alert>
      </Box>
    )
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {caseDetail.title}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip
          label={CASE_STATUS_LABELS[caseDetail.status as CaseStatus] || caseDetail.status}
          size="small"
          sx={{ backgroundColor: CASE_STATUS_COLORS[caseDetail.status as CaseStatus], color: '#000' }}
        />
        <Typography variant="body2" color="text.secondary">
          {caseDetail.case_number}
        </Typography>
      </Box>
      {caseDetail.description && (
        <Typography variant="body1" sx={{ mt: 1 }}>
          {caseDetail.description}
        </Typography>
      )}
    </Box>
  )
}

export default LegalDeskCaseDetailPage
