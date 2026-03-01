import React, { useState, useEffect, useCallback } from 'react'
import {
  Drawer,
  Box,
  Typography,
  IconButton,
  Chip,
  Divider,
  CircularProgress,
  Paper,
  Link as MuiLink,
} from '@mui/material'
import { Close, Edit, Download, ArrowForward } from '@mui/icons-material'
import type { Prospect, PipelineStage, StageTransition } from '@/types'
import { pipelineStageService } from '@/services/pipelineStageService'
import { useMeetingRecords } from '@/hooks/useMeetingRecords'
import { meetingRecordService } from '@/services/meetingRecordService'

interface TRProspectDetailDrawerProps {
  prospect: Prospect | null
  open: boolean
  onClose: () => void
  onEdit: (prospect: Prospect) => void
  entityId: string
  stages: PipelineStage[]
}

const DRAWER_WIDTH = 520

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

const formatDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const formatDateTime = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export const TRProspectDetailDrawer: React.FC<TRProspectDetailDrawerProps> = ({
  prospect,
  open,
  onClose,
  onEdit,
  entityId,
  stages,
}) => {
  const [transitions, setTransitions] = useState<StageTransition[]>([])
  const [transitionsLoading, setTransitionsLoading] = useState(false)
  const [downloadingId, setDownloadingId] = useState<string | null>(null)

  const {
    meetingRecords,
    isLoading: meetingsLoading,
  } = useMeetingRecords(open ? entityId : null, prospect?.id)

  const resolveStageName = useCallback(
    (stageId: string | null): string => {
      if (!stageId) return 'Unknown'
      const stage = stages.find((s) => s.id === stageId)
      return stage?.display_name || 'Unknown'
    },
    [stages]
  )

  const getStageColor = useCallback(
    (stageName: string): string | undefined => {
      const stage = stages.find((s) => s.name === stageName)
      return stage?.color || undefined
    },
    [stages]
  )

  useEffect(() => {
    if (!open || !prospect) {
      setTransitions([])
      return
    }

    const fetchTransitions = async () => {
      console.log('INFO [TRProspectDetailDrawer]: Fetching transitions for prospect:', prospect.id)
      setTransitionsLoading(true)
      try {
        const response = await pipelineStageService.getTransitions(prospect.id, entityId)
        setTransitions(response.transitions)
        console.log('INFO [TRProspectDetailDrawer]: Loaded', response.transitions.length, 'transitions')
      } catch (err) {
        console.error('ERROR [TRProspectDetailDrawer]: Failed to fetch transitions:', err)
        setTransitions([])
      } finally {
        setTransitionsLoading(false)
      }
    }

    fetchTransitions()
  }, [open, prospect?.id, entityId, prospect])

  const handleDownloadHtml = async (meetingId: string, title: string) => {
    console.log('INFO [TRProspectDetailDrawer]: Downloading HTML for meeting:', meetingId)
    setDownloadingId(meetingId)
    try {
      const html = await meetingRecordService.getHtml(meetingId, entityId)
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = url
      anchor.download = `${title}.html`
      document.body.appendChild(anchor)
      anchor.click()
      document.body.removeChild(anchor)
      URL.revokeObjectURL(url)
      console.log('INFO [TRProspectDetailDrawer]: HTML downloaded for meeting:', meetingId)
    } catch (err) {
      console.error('ERROR [TRProspectDetailDrawer]: Failed to download HTML:', err)
    } finally {
      setDownloadingId(null)
    }
  }

  const sortedMeetings = [...meetingRecords].sort((a, b) => {
    const dateA = a.meeting_date || a.created_at
    const dateB = b.meeting_date || b.created_at
    return new Date(dateB).getTime() - new Date(dateA).getTime()
  })

  const parseJsonSafe = (jsonStr: string | undefined): string[] => {
    if (!jsonStr) return []
    try {
      const parsed: unknown = JSON.parse(jsonStr)
      if (Array.isArray(parsed)) return parsed as string[]
      return []
    } catch {
      return []
    }
  }

  if (!prospect) return null

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{
        sx: { width: DRAWER_WIDTH, maxWidth: '100vw' },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Typography variant="h6" noWrap sx={{ flex: 1 }}>
          {prospect.company_name}
        </Typography>
        <IconButton onClick={() => onEdit(prospect)} size="small" sx={{ mr: 0.5 }}>
          <Edit />
        </IconButton>
        <IconButton onClick={onClose} size="small">
          <Close />
        </IconButton>
      </Box>

      <Box sx={{ overflow: 'auto', flex: 1 }}>
        {/* Prospect Info Section */}
        <Box sx={{ p: 2 }}>
          <Chip
            label={stages.find((s) => s.name === prospect.stage)?.display_name || prospect.stage}
            size="small"
            sx={{
              backgroundColor: getStageColor(prospect.stage) || 'grey.300',
              color: 'white',
              fontWeight: 600,
              mb: 2,
            }}
          />

          {prospect.contact_name && (
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Contact:</strong> {prospect.contact_name}
            </Typography>
          )}

          {prospect.contact_email && (
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Email:</strong>{' '}
              <MuiLink href={`mailto:${prospect.contact_email}`}>
                {prospect.contact_email}
              </MuiLink>
            </Typography>
          )}

          {prospect.contact_phone && (
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Phone:</strong> {prospect.contact_phone}
            </Typography>
          )}

          {prospect.estimated_value != null && (
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Estimated Value:</strong> {formatCurrency(prospect.estimated_value)}
            </Typography>
          )}

          {prospect.source && (
            <Typography variant="body2" sx={{ mb: 0.5 }}>
              <strong>Source:</strong> {prospect.source}
            </Typography>
          )}

          {prospect.notes && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {prospect.notes}
            </Typography>
          )}
        </Box>

        <Divider />

        {/* Stage History Section */}
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
            Stage History
          </Typography>

          {transitionsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : transitions.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No stage transitions yet
            </Typography>
          ) : (
            <Box>
              {transitions.map((transition) => (
                <Box
                  key={transition.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    mb: 1.5,
                    pl: 2,
                    borderLeft: 2,
                    borderColor: 'primary.main',
                  }}
                >
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {transition.from_stage_id === null ? (
                        <Typography variant="body2">
                          <strong>Initial</strong> <ArrowForward sx={{ fontSize: 14, verticalAlign: 'middle' }} />{' '}
                          {resolveStageName(transition.to_stage_id)}
                        </Typography>
                      ) : (
                        <Typography variant="body2">
                          {resolveStageName(transition.from_stage_id)}{' '}
                          <ArrowForward sx={{ fontSize: 14, verticalAlign: 'middle' }} />{' '}
                          {resolveStageName(transition.to_stage_id)}
                        </Typography>
                      )}
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      {formatDateTime(transition.created_at)}
                    </Typography>
                    {transition.notes && (
                      <Typography variant="caption" display="block" color="text.secondary">
                        {transition.notes}
                      </Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </Box>
          )}
        </Box>

        <Divider />

        {/* Meeting History Section */}
        <Box sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1.5 }}>
            Meeting History
          </Typography>

          {meetingsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : sortedMeetings.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No meetings recorded yet
            </Typography>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {sortedMeetings.map((meeting) => {
                const participants = parseJsonSafe(meeting.participants)

                return (
                  <Paper key={meeting.id} variant="outlined" sx={{ p: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {meeting.title}
                      </Typography>
                      {meeting.html_output && (
                        <IconButton
                          size="small"
                          onClick={() => handleDownloadHtml(meeting.id, meeting.title)}
                          disabled={downloadingId === meeting.id}
                        >
                          {downloadingId === meeting.id ? (
                            <CircularProgress size={16} />
                          ) : (
                            <Download fontSize="small" />
                          )}
                        </IconButton>
                      )}
                    </Box>

                    <Typography variant="caption" color="text.secondary" display="block">
                      {meeting.meeting_date ? formatDate(meeting.meeting_date) : 'Date not set'}
                    </Typography>

                    {meeting.summary && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          mt: 0.5,
                          display: '-webkit-box',
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {meeting.summary}
                      </Typography>
                    )}

                    {participants.length > 0 && (
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
                        {participants.map((p, idx) => (
                          <Chip key={idx} label={p} size="small" variant="outlined" sx={{ height: 20, fontSize: '0.7rem' }} />
                        ))}
                      </Box>
                    )}
                  </Paper>
                )
              })}
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  )
}

export default TRProspectDetailDrawer
