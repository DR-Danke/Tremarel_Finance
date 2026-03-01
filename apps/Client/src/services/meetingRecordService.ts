import { apiClient } from '@/api/clients'
import type {
  MeetingRecord,
  MeetingRecordCreate,
  MeetingRecordUpdate,
  MeetingRecordFilters,
  MeetingRecordListResponse,
} from '@/types'

export const meetingRecordService = {
  async create(data: MeetingRecordCreate): Promise<MeetingRecord> {
    console.log('INFO [MeetingRecordService]: Creating meeting record for entity:', data.entity_id)
    try {
      const response = await apiClient.post<MeetingRecord>('/meeting-records/', data)
      console.log('INFO [MeetingRecordService]: Meeting record created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to create meeting record:', error)
      throw error
    }
  },

  async list(
    entityId: string,
    filters?: MeetingRecordFilters,
    skip = 0,
    limit = 100
  ): Promise<MeetingRecordListResponse> {
    console.log('INFO [MeetingRecordService]: Listing meeting records for entity:', entityId)
    try {
      const params = new URLSearchParams()
      params.append('entity_id', entityId)
      params.append('skip', skip.toString())
      params.append('limit', limit.toString())

      if (filters?.prospect_id) {
        params.append('prospect_id', filters.prospect_id)
      }
      if (filters?.is_active !== undefined) {
        params.append('is_active', filters.is_active.toString())
      }
      if (filters?.meeting_date_from) {
        params.append('meeting_date_from', filters.meeting_date_from)
      }
      if (filters?.meeting_date_to) {
        params.append('meeting_date_to', filters.meeting_date_to)
      }

      const response = await apiClient.get<MeetingRecordListResponse>(
        `/meeting-records/?${params.toString()}`
      )
      console.log(
        'INFO [MeetingRecordService]: Fetched',
        response.data.meeting_records.length,
        'meeting records (total:',
        response.data.total,
        ')'
      )
      return response.data
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to list meeting records:', error)
      throw error
    }
  },

  async get(recordId: string, entityId: string): Promise<MeetingRecord> {
    console.log('INFO [MeetingRecordService]: Getting meeting record:', recordId)
    try {
      const response = await apiClient.get<MeetingRecord>(
        `/meeting-records/${recordId}?entity_id=${entityId}`
      )
      console.log('INFO [MeetingRecordService]: Meeting record fetched:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to get meeting record:', error)
      throw error
    }
  },

  async getHtml(recordId: string, entityId: string): Promise<string> {
    console.log('INFO [MeetingRecordService]: Getting HTML for meeting record:', recordId)
    try {
      const response = await apiClient.get<string>(
        `/meeting-records/${recordId}/html?entity_id=${entityId}`,
        { responseType: 'text' as never }
      )
      console.log('INFO [MeetingRecordService]: HTML fetched for meeting record:', recordId)
      return response.data
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to get meeting record HTML:', error)
      throw error
    }
  },

  async update(
    recordId: string,
    entityId: string,
    data: MeetingRecordUpdate
  ): Promise<MeetingRecord> {
    console.log('INFO [MeetingRecordService]: Updating meeting record:', recordId)
    try {
      const response = await apiClient.put<MeetingRecord>(
        `/meeting-records/${recordId}?entity_id=${entityId}`,
        data
      )
      console.log('INFO [MeetingRecordService]: Meeting record updated:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to update meeting record:', error)
      throw error
    }
  },

  async delete(recordId: string, entityId: string): Promise<void> {
    console.log('INFO [MeetingRecordService]: Deleting meeting record:', recordId)
    try {
      await apiClient.delete(`/meeting-records/${recordId}?entity_id=${entityId}`)
      console.log('INFO [MeetingRecordService]: Meeting record deleted:', recordId)
    } catch (error) {
      console.error('ERROR [MeetingRecordService]: Failed to delete meeting record:', error)
      throw error
    }
  },
}

export default meetingRecordService
