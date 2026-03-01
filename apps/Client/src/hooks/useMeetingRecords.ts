import { useState, useEffect, useCallback } from 'react'
import { meetingRecordService } from '@/services/meetingRecordService'
import type {
  MeetingRecord,
  MeetingRecordCreate,
  MeetingRecordUpdate,
  MeetingRecordFilters,
} from '@/types'

interface UseMeetingRecordsResult {
  meetingRecords: MeetingRecord[]
  total: number
  isLoading: boolean
  error: string | null
  filters: MeetingRecordFilters
  fetchMeetingRecords: () => Promise<void>
  createMeetingRecord: (data: MeetingRecordCreate) => Promise<void>
  updateMeetingRecord: (id: string, data: MeetingRecordUpdate) => Promise<void>
  deleteMeetingRecord: (id: string) => Promise<void>
  getMeetingRecordHtml: (id: string) => Promise<string>
  setFilters: (filters: MeetingRecordFilters) => void
}

export const useMeetingRecords = (
  entityId: string | null,
  prospectId?: string
): UseMeetingRecordsResult => {
  const [meetingRecords, setMeetingRecords] = useState<MeetingRecord[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState<MeetingRecordFilters>({})

  const fetchMeetingRecords = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useMeetingRecords]: No entityId provided, skipping fetch')
      return
    }

    console.log('INFO [useMeetingRecords]: Fetching meeting records for entity:', entityId)
    setIsLoading(true)
    setError(null)

    try {
      const mergedFilters: MeetingRecordFilters = { ...filters }
      if (prospectId) {
        mergedFilters.prospect_id = prospectId
      }

      const response = await meetingRecordService.list(entityId, mergedFilters)
      setMeetingRecords(response.meeting_records)
      setTotal(response.total)
      console.log('INFO [useMeetingRecords]: Fetched', response.meeting_records.length, 'meeting records')
    } catch (err) {
      console.error('ERROR [useMeetingRecords]: Failed to fetch meeting records:', err)
      setError('Failed to load meeting records. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId, filters, prospectId])

  const createMeetingRecord = useCallback(
    async (data: MeetingRecordCreate) => {
      console.log('INFO [useMeetingRecords]: Creating meeting record')
      setError(null)

      try {
        await meetingRecordService.create(data)
        console.log('INFO [useMeetingRecords]: Meeting record created, refreshing list')
        await fetchMeetingRecords()
      } catch (err) {
        console.error('ERROR [useMeetingRecords]: Failed to create meeting record:', err)
        setError('Failed to create meeting record. Please try again.')
        throw err
      }
    },
    [fetchMeetingRecords]
  )

  const updateMeetingRecord = useCallback(
    async (id: string, data: MeetingRecordUpdate) => {
      if (!entityId) return
      console.log('INFO [useMeetingRecords]: Updating meeting record:', id)
      setError(null)

      try {
        await meetingRecordService.update(id, entityId, data)
        console.log('INFO [useMeetingRecords]: Meeting record updated, refreshing list')
        await fetchMeetingRecords()
      } catch (err) {
        console.error('ERROR [useMeetingRecords]: Failed to update meeting record:', err)
        setError('Failed to update meeting record. Please try again.')
        throw err
      }
    },
    [entityId, fetchMeetingRecords]
  )

  const deleteMeetingRecord = useCallback(
    async (id: string) => {
      if (!entityId) return
      console.log('INFO [useMeetingRecords]: Deleting meeting record:', id)
      setError(null)

      try {
        await meetingRecordService.delete(id, entityId)
        console.log('INFO [useMeetingRecords]: Meeting record deleted, refreshing list')
        await fetchMeetingRecords()
      } catch (err) {
        console.error('ERROR [useMeetingRecords]: Failed to delete meeting record:', err)
        setError('Failed to delete meeting record. Please try again.')
        throw err
      }
    },
    [entityId, fetchMeetingRecords]
  )

  const getMeetingRecordHtml = useCallback(
    async (id: string): Promise<string> => {
      if (!entityId) {
        console.log('INFO [useMeetingRecords]: No entityId provided, skipping HTML fetch')
        return ''
      }
      console.log('INFO [useMeetingRecords]: Getting HTML for meeting record:', id)

      try {
        const html = await meetingRecordService.getHtml(id, entityId)
        console.log('INFO [useMeetingRecords]: HTML fetched for meeting record:', id)
        return html
      } catch (err) {
        console.error('ERROR [useMeetingRecords]: Failed to get meeting record HTML:', err)
        setError('Failed to load meeting record HTML. Please try again.')
        throw err
      }
    },
    [entityId]
  )

  useEffect(() => {
    fetchMeetingRecords()
  }, [fetchMeetingRecords])

  return {
    meetingRecords,
    total,
    isLoading,
    error,
    filters,
    fetchMeetingRecords,
    createMeetingRecord,
    updateMeetingRecord,
    deleteMeetingRecord,
    getMeetingRecordHtml,
    setFilters,
  }
}

export default useMeetingRecords
