import React, { useState } from 'react'
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Grid,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Checkbox,
  FormControlLabel,
  Chip,
  Snackbar,
  MenuItem,
} from '@mui/material'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useParams, useNavigate } from 'react-router-dom'
import { useLegaldeskCaseDetail } from '@/hooks/useLegaldeskCaseDetail'
import { useLegaldeskPricing } from '@/hooks/useLegaldeskPricing'
import { TRCaseStatusBadge } from '@/components/ui/TRCaseStatusBadge'
import { TRLegalDomainBadge } from '@/components/ui/TRLegalDomainBadge'
import { TRCasePriorityBadge } from '@/components/ui/TRCasePriorityBadge'
import { TRDeliverableChecklist } from '@/components/ui/TRDeliverableChecklist'
import { TRPricingTimeline } from '@/components/ui/TRPricingTimeline'
import type {
  CaseStatus,
  AssignmentRole,
  DeliverableStatus,
} from '@/types/legaldesk'
import {
  CASE_COMPLEXITY_LABELS,
  ASSIGNMENT_ROLE_LABELS,
  ASSIGNMENT_STATUS_LABELS,
} from '@/types/legaldesk'

const CASE_STATUS_TRANSITIONS: Record<CaseStatus, CaseStatus[]> = {
  new: ['classifying'],
  classifying: ['open'],
  open: ['assigning'],
  assigning: ['active'],
  active: ['in_progress'],
  in_progress: ['review'],
  review: ['negotiating', 'completed'],
  negotiating: ['completed'],
  completed: ['closed'],
  closed: ['archived'],
  archived: [],
}

export const LegalDeskCaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const caseId = id ? parseInt(id, 10) : null
  const navigate = useNavigate()

  const {
    caseDetail,
    loading,
    error,
    updateStatus,
    suggestSpecialists,
    candidates,
    assignSpecialist,
    addDeliverable,
    updateDeliverableStatus,
    addMessage,
    addDocument,
    refreshCase,
  } = useLegaldeskCaseDetail(caseId)

  const { history: pricingHistory, propose, counter, accept, reject } = useLegaldeskPricing(caseId)

  const [tabIndex, setTabIndex] = useState(0)
  const [snackbar, setSnackbar] = useState<string | null>(null)
  const [showInternal, setShowInternal] = useState(true)

  // Deliverable form state
  const [delivTitle, setDelivTitle] = useState('')
  const [delivDesc, setDelivDesc] = useState('')
  const [delivDue, setDelivDue] = useState('')

  // Message form state
  const [msgSenderType, setMsgSenderType] = useState('user')
  const [msgSenderName, setMsgSenderName] = useState('')
  const [msgText, setMsgText] = useState('')
  const [msgInternal, setMsgInternal] = useState(false)

  // Document form state
  const [docFileName, setDocFileName] = useState('')
  const [docFileUrl, setDocFileUrl] = useState('')
  const [docFileType, setDocFileType] = useState('')
  const [docUploadedBy, setDocUploadedBy] = useState('')

  // Pricing form state
  const [pricingAmount, setPricingAmount] = useState('')
  const [pricingNotes, setPricingNotes] = useState('')

  console.log('INFO [LegalDeskCaseDetailPage]: Rendering case detail for id:', caseId)

  if (!caseId || isNaN(caseId)) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Alert severity="error">Invalid case ID.</Alert>
        </Box>
      </Container>
    )
  }

  if (loading && !caseDetail) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
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
      </Container>
    )
  }

  if (!caseDetail) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Alert severity="warning">Case not found.</Alert>
        </Box>
      </Container>
    )
  }

  const validTransitions = CASE_STATUS_TRANSITIONS[caseDetail.status] || []

  const handleStatusChange = async (status: CaseStatus) => {
    try {
      await updateStatus(status)
      setSnackbar(`Status updated to ${status}`)
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Status update failed')
    }
  }

  const handleAddDeliverable = async () => {
    if (!delivTitle) return
    try {
      await addDeliverable({
        case_id: caseId,
        title: delivTitle,
        description: delivDesc || undefined,
        due_date: delivDue || undefined,
      })
      setDelivTitle('')
      setDelivDesc('')
      setDelivDue('')
      setSnackbar('Deliverable added')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to add deliverable')
    }
  }

  const handleDeliverableStatusChange = async (deliverableId: number, status: DeliverableStatus) => {
    try {
      await updateDeliverableStatus(deliverableId, status)
      setSnackbar('Deliverable updated')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to update deliverable')
    }
  }

  const handleAddMessage = async () => {
    if (!msgText) return
    try {
      await addMessage({
        case_id: caseId,
        sender_type: msgSenderType,
        sender_name: msgSenderName || undefined,
        message: msgText,
        is_internal: msgInternal,
      })
      setMsgText('')
      setMsgSenderName('')
      setMsgInternal(false)
      setSnackbar('Message sent')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to add message')
    }
  }

  const handleAddDocument = async () => {
    if (!docFileName || !docFileUrl) return
    try {
      await addDocument({
        case_id: caseId,
        file_name: docFileName,
        file_url: docFileUrl,
        file_type: docFileType || undefined,
        uploaded_by: docUploadedBy || undefined,
      })
      setDocFileName('')
      setDocFileUrl('')
      setDocFileType('')
      setDocUploadedBy('')
      setSnackbar('Document added')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to add document')
    }
  }

  const handlePropose = async () => {
    const amount = parseFloat(pricingAmount)
    if (isNaN(amount)) return
    try {
      await propose({ amount, notes: pricingNotes || undefined })
      setPricingAmount('')
      setPricingNotes('')
      setSnackbar('Proposal submitted')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to propose')
    }
  }

  const handleCounter = async () => {
    const amount = parseFloat(pricingAmount)
    if (isNaN(amount)) return
    try {
      await counter({ amount, notes: pricingNotes || undefined })
      setPricingAmount('')
      setPricingNotes('')
      setSnackbar('Counter submitted')
    } catch {
      console.error('ERROR [LegalDeskCaseDetailPage]: Failed to counter')
    }
  }

  const messages = caseDetail.messages ?? []
  const filteredMessages = showInternal
    ? messages
    : messages.filter((m) => !m.is_internal)
  const sortedMessages = [...filteredMessages].sort(
    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  )

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/poc/legal-desk/cases')}
          sx={{ mb: 2 }}
        >
          Back to Cases
        </Button>

        {/* Header */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Typography variant="h5" component="h1">
              {caseDetail.case_number} — {caseDetail.title}
            </Typography>
            <TRCaseStatusBadge status={caseDetail.status} size="medium" />
            <TRLegalDomainBadge domain={caseDetail.legal_domain} size="medium" />
            <TRCasePriorityBadge priority={caseDetail.priority} size="medium" />
          </Box>

          {/* Status Transitions */}
          {validTransitions.length > 0 && (
            <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
              <Typography variant="body2" color="text.secondary" sx={{ alignSelf: 'center' }}>
                Transition to:
              </Typography>
              {validTransitions.map((nextStatus) => (
                <Button
                  key={nextStatus}
                  variant="outlined"
                  size="small"
                  onClick={() => handleStatusChange(nextStatus)}
                >
                  {nextStatus.replace(/_/g, ' ')}
                </Button>
              ))}
            </Box>
          )}
        </Paper>

        {/* Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabIndex} onChange={(_, v) => setTabIndex(v)} variant="scrollable">
            <Tab label="Overview" />
            <Tab label="Specialists" />
            <Tab label="Deliverables" />
            <Tab label="Pricing" />
            <Tab label="Messages" />
            <Tab label="Documents" />
          </Tabs>
        </Paper>

        {/* Tab 0 — Overview */}
        {tabIndex === 0 && (
          <Paper sx={{ p: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                <Typography variant="body2">{caseDetail.description || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Case Type</Typography>
                <Typography variant="body2">{caseDetail.case_type || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Complexity</Typography>
                <Typography variant="body2">{CASE_COMPLEXITY_LABELS[caseDetail.complexity]}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Budget</Typography>
                <Typography variant="body2">{caseDetail.budget != null ? `$${caseDetail.budget.toLocaleString()}` : 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Estimated Cost</Typography>
                <Typography variant="body2">{caseDetail.estimated_cost != null ? `$${caseDetail.estimated_cost.toLocaleString()}` : 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Final Quote</Typography>
                <Typography variant="body2">{caseDetail.final_quote != null ? `$${caseDetail.final_quote.toLocaleString()}` : 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Margin %</Typography>
                <Typography variant="body2">{caseDetail.margin_percentage != null ? `${caseDetail.margin_percentage}%` : 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="subtitle2" color="text.secondary">Deadline</Typography>
                <Typography variant="body2">{caseDetail.deadline ? new Date(caseDetail.deadline).toLocaleDateString() : 'N/A'}</Typography>
              </Grid>

              {caseDetail.client && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>Client</Typography>
                  <Typography variant="body2">{caseDetail.client.name} ({caseDetail.client.client_type})</Typography>
                  {caseDetail.client.contact_email && (
                    <Typography variant="body2">{caseDetail.client.contact_email}</Typography>
                  )}
                </Grid>
              )}

              {caseDetail.ai_classification && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary" sx={{ mt: 1 }}>AI Classification</Typography>
                  <Paper variant="outlined" sx={{ p: 1, mt: 0.5 }}>
                    <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                      {JSON.stringify(caseDetail.ai_classification, null, 2)}
                    </Typography>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </Paper>
        )}

        {/* Tab 1 — Specialists */}
        {tabIndex === 1 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Assigned Specialists</Typography>
              <Button variant="outlined" onClick={() => suggestSpecialists()}>
                Suggest Specialists
              </Button>
            </Box>

            {(caseDetail.specialists ?? []).length === 0 ? (
              <Typography variant="body2" color="text.secondary">No specialists assigned yet.</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Specialist ID</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Proposed Fee</TableCell>
                      <TableCell>Agreed Fee</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(caseDetail.specialists ?? []).map((s) => (
                      <TableRow key={s.id}>
                        <TableCell>{s.specialist_id}</TableCell>
                        <TableCell>{ASSIGNMENT_ROLE_LABELS[s.role]}</TableCell>
                        <TableCell>{ASSIGNMENT_STATUS_LABELS[s.status]}</TableCell>
                        <TableCell>{s.proposed_fee != null ? `${s.fee_currency} ${s.proposed_fee}` : '-'}</TableCell>
                        <TableCell>{s.agreed_fee != null ? `${s.fee_currency} ${s.agreed_fee}` : '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}

            {candidates.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle1" gutterBottom>Suggested Candidates</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Match Score</TableCell>
                        <TableCell>Workload</TableCell>
                        <TableCell>Expertise</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {candidates.map((c) => (
                        <TableRow key={c.specialist_id}>
                          <TableCell>{c.full_name}</TableCell>
                          <TableCell>{`${(c.match_score * 100).toFixed(0)}%`}</TableCell>
                          <TableCell>{`${c.current_workload}/${c.max_concurrent_cases}`}</TableCell>
                          <TableCell>{c.expertise_match.join(', ')}</TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              variant="contained"
                              onClick={() =>
                                assignSpecialist({
                                  case_id: caseId,
                                  specialist_id: c.specialist_id,
                                  role: 'lead' as AssignmentRole,
                                })
                              }
                            >
                              Assign
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Paper>
        )}

        {/* Tab 2 — Deliverables */}
        {tabIndex === 2 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Deliverables</Typography>
            <TRDeliverableChecklist
              deliverables={(caseDetail.deliverables ?? [])}
              onStatusChange={handleDeliverableStatusChange}
            />

            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>Add Deliverable</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={5}>
                  <TextField
                    label="Title"
                    size="small"
                    fullWidth
                    value={delivTitle}
                    onChange={(e) => setDelivTitle(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Description"
                    size="small"
                    fullWidth
                    value={delivDesc}
                    onChange={(e) => setDelivDesc(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <TextField
                    label="Due Date"
                    type="date"
                    size="small"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    value={delivDue}
                    onChange={(e) => setDelivDue(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={1}>
                  <Button variant="contained" fullWidth onClick={handleAddDeliverable} disabled={!delivTitle}>
                    Add
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        )}

        {/* Tab 3 — Pricing */}
        {tabIndex === 3 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Pricing History</Typography>
            <TRPricingTimeline history={pricingHistory} />

            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>Pricing Actions</Typography>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={3}>
                  <TextField
                    label="Amount"
                    type="number"
                    size="small"
                    fullWidth
                    value={pricingAmount}
                    onChange={(e) => setPricingAmount(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Notes"
                    size="small"
                    fullWidth
                    value={pricingNotes}
                    onChange={(e) => setPricingNotes(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={5}>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button size="small" variant="contained" onClick={handlePropose} disabled={!pricingAmount}>
                      Propose
                    </Button>
                    <Button size="small" variant="outlined" onClick={handleCounter} disabled={!pricingAmount}>
                      Counter
                    </Button>
                    <Button size="small" variant="contained" color="success" onClick={() => accept()}>
                      Accept
                    </Button>
                    <Button size="small" variant="outlined" color="error" onClick={() => reject(pricingNotes || undefined)}>
                      Reject
                    </Button>
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        )}

        {/* Tab 4 — Messages */}
        {tabIndex === 4 && (
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Messages</Typography>
              <FormControlLabel
                control={<Checkbox checked={showInternal} onChange={(e) => setShowInternal(e.target.checked)} />}
                label="Show Internal"
              />
            </Box>

            {sortedMessages.length === 0 ? (
              <Typography variant="body2" color="text.secondary">No messages yet.</Typography>
            ) : (
              <Box sx={{ maxHeight: 400, overflowY: 'auto', mb: 2 }}>
                {sortedMessages.map((m) => (
                  <Paper key={m.id} variant="outlined" sx={{ p: 2, mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle2">{m.sender_name || m.sender_type}</Typography>
                      {m.is_internal && <Chip label="Internal" size="small" color="warning" />}
                      <Typography variant="caption" color="text.secondary">
                        {new Date(m.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                    <Typography variant="body2">{m.message}</Typography>
                  </Paper>
                ))}
              </Box>
            )}

            <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>Add Message</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={3}>
                  <TextField
                    select
                    label="Sender Type"
                    size="small"
                    fullWidth
                    value={msgSenderType}
                    onChange={(e) => setMsgSenderType(e.target.value)}
                  >
                    <MenuItem value="user">User</MenuItem>
                    <MenuItem value="specialist">Specialist</MenuItem>
                    <MenuItem value="system">System</MenuItem>
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField
                    label="Sender Name"
                    size="small"
                    fullWidth
                    value={msgSenderName}
                    onChange={(e) => setMsgSenderName(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Message"
                    size="small"
                    fullWidth
                    value={msgText}
                    onChange={(e) => setMsgText(e.target.value)}
                  />
                </Grid>
                <Grid item xs={6} sm={1}>
                  <FormControlLabel
                    control={<Checkbox checked={msgInternal} onChange={(e) => setMsgInternal(e.target.checked)} size="small" />}
                    label="Internal"
                  />
                </Grid>
                <Grid item xs={6} sm={1}>
                  <Button variant="contained" fullWidth onClick={handleAddMessage} disabled={!msgText}>
                    Send
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        )}

        {/* Tab 5 — Documents */}
        {tabIndex === 5 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Documents</Typography>
            {(caseDetail.documents ?? []).length === 0 ? (
              <Typography variant="body2" color="text.secondary">No documents yet.</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>File Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Size</TableCell>
                      <TableCell>Uploaded By</TableCell>
                      <TableCell>Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(caseDetail.documents ?? []).map((doc) => (
                      <TableRow key={doc.id}>
                        <TableCell>{doc.file_name}</TableCell>
                        <TableCell>{doc.file_type || '-'}</TableCell>
                        <TableCell>{doc.file_size_bytes != null ? `${(doc.file_size_bytes / 1024).toFixed(1)} KB` : '-'}</TableCell>
                        <TableCell>{doc.uploaded_by || '-'}</TableCell>
                        <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}

            <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom>Add Document</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={3}>
                  <TextField
                    label="File Name"
                    size="small"
                    fullWidth
                    value={docFileName}
                    onChange={(e) => setDocFileName(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="File URL"
                    size="small"
                    fullWidth
                    value={docFileUrl}
                    onChange={(e) => setDocFileUrl(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <TextField
                    label="File Type"
                    size="small"
                    fullWidth
                    value={docFileType}
                    onChange={(e) => setDocFileType(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <TextField
                    label="Uploaded By"
                    size="small"
                    fullWidth
                    value={docUploadedBy}
                    onChange={(e) => setDocUploadedBy(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} sm={1}>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleAddDocument}
                    disabled={!docFileName || !docFileUrl}
                  >
                    Add
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Paper>
        )}

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

export default LegalDeskCaseDetailPage
