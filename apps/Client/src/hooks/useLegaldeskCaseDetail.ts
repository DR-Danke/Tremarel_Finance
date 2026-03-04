import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type {
  LdCaseDetail,
  LdCaseUpdate,
  LdCaseSpecialistCreate,
  LdCaseDeliverableCreate,
  LdCaseMessageCreate,
  LdCaseDocumentCreate,
  LdSpecialistCandidate,
  CaseStatus,
  DeliverableStatus,
  AssignmentStatus,
} from '@/types/legaldesk'

interface UseLegaldeskCaseDetailResult {
  caseDetail: LdCaseDetail | null
  loading: boolean
  error: string | null
  updateCase: (data: LdCaseUpdate) => Promise<void>
  updateStatus: (status: CaseStatus) => Promise<void>
  classifyCase: () => Promise<Record<string, unknown>>
  assignSpecialist: (data: LdCaseSpecialistCreate) => Promise<void>
  suggestSpecialists: () => Promise<LdSpecialistCandidate[]>
  candidates: LdSpecialistCandidate[]
  updateAssignmentStatus: (assignmentId: number, status: AssignmentStatus) => Promise<void>
  addDeliverable: (data: LdCaseDeliverableCreate) => Promise<void>
  updateDeliverableStatus: (deliverableId: number, status: DeliverableStatus) => Promise<void>
  addMessage: (data: LdCaseMessageCreate) => Promise<void>
  addDocument: (data: LdCaseDocumentCreate) => Promise<void>
  refreshCase: () => Promise<void>
}

export const useLegaldeskCaseDetail = (caseId: number | null): UseLegaldeskCaseDetailResult => {
  const [caseDetail, setCaseDetail] = useState<LdCaseDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [candidates, setCandidates] = useState<LdSpecialistCandidate[]>([])

  const refreshCase = useCallback(async () => {
    if (!caseId) {
      console.log('INFO [useLegaldeskCaseDetail]: No caseId provided, skipping fetch')
      return
    }

    console.log('INFO [useLegaldeskCaseDetail]: Fetching case detail:', caseId)
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.getCase(caseId)
      setCaseDetail(data)
      console.log('INFO [useLegaldeskCaseDetail]: Case detail fetched:', data.case_number)
    } catch (err) {
      console.error('ERROR [useLegaldeskCaseDetail]: Failed to fetch case detail:', err)
      setError('Failed to load case details. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [caseId])

  const updateCase = useCallback(
    async (data: LdCaseUpdate) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Updating case:', caseId)
      setError(null)

      try {
        await legaldeskService.updateCase(caseId, data)
        console.log('INFO [useLegaldeskCaseDetail]: Case updated, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to update case:', err)
        setError('Failed to update case. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const updateStatus = useCallback(
    async (status: CaseStatus) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Updating case status:', caseId, '->', status)
      setError(null)

      try {
        await legaldeskService.updateCaseStatus(caseId, status)
        console.log('INFO [useLegaldeskCaseDetail]: Status updated, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to update status:', err)
        setError('Failed to update case status. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const classifyCase = useCallback(async (): Promise<Record<string, unknown>> => {
    if (!caseId) throw new Error('No case ID')
    console.log('INFO [useLegaldeskCaseDetail]: Classifying case:', caseId)
    setError(null)

    try {
      const result = await legaldeskService.classifyCase(caseId)
      console.log('INFO [useLegaldeskCaseDetail]: Case classified, refreshing')
      await refreshCase()
      return result
    } catch (err) {
      console.error('ERROR [useLegaldeskCaseDetail]: Failed to classify case:', err)
      setError('Failed to classify case. Please try again.')
      throw err
    }
  }, [caseId, refreshCase])

  const assignSpecialist = useCallback(
    async (data: LdCaseSpecialistCreate) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Assigning specialist to case:', caseId)
      setError(null)

      try {
        await legaldeskService.assignSpecialist(caseId, data)
        console.log('INFO [useLegaldeskCaseDetail]: Specialist assigned, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to assign specialist:', err)
        setError('Failed to assign specialist. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const suggestSpecialists = useCallback(async (): Promise<LdSpecialistCandidate[]> => {
    if (!caseId) return []
    console.log('INFO [useLegaldeskCaseDetail]: Suggesting specialists for case:', caseId)
    setError(null)

    try {
      const results = await legaldeskService.suggestSpecialists(caseId)
      setCandidates(results)
      console.log('INFO [useLegaldeskCaseDetail]: Got', results.length, 'candidates')
      return results
    } catch (err) {
      console.error('ERROR [useLegaldeskCaseDetail]: Failed to suggest specialists:', err)
      setError('Failed to get specialist suggestions. Please try again.')
      throw err
    }
  }, [caseId])

  const updateAssignmentStatus = useCallback(
    async (assignmentId: number, status: AssignmentStatus) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Updating assignment status:', assignmentId)
      setError(null)

      try {
        await legaldeskService.updateAssignmentStatus(caseId, assignmentId, status)
        console.log('INFO [useLegaldeskCaseDetail]: Assignment status updated, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to update assignment status:', err)
        setError('Failed to update assignment status. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const addDeliverable = useCallback(
    async (data: LdCaseDeliverableCreate) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Adding deliverable to case:', caseId)
      setError(null)

      try {
        await legaldeskService.createDeliverable(caseId, data)
        console.log('INFO [useLegaldeskCaseDetail]: Deliverable added, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to add deliverable:', err)
        setError('Failed to add deliverable. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const updateDeliverableStatus = useCallback(
    async (deliverableId: number, status: DeliverableStatus) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Updating deliverable status:', deliverableId)
      setError(null)

      try {
        await legaldeskService.updateDeliverableStatus(caseId, deliverableId, status)
        console.log('INFO [useLegaldeskCaseDetail]: Deliverable status updated, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to update deliverable status:', err)
        setError('Failed to update deliverable status. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const addMessage = useCallback(
    async (data: LdCaseMessageCreate) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Adding message to case:', caseId)
      setError(null)

      try {
        await legaldeskService.createMessage(caseId, data)
        console.log('INFO [useLegaldeskCaseDetail]: Message added, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to add message:', err)
        setError('Failed to add message. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  const addDocument = useCallback(
    async (data: LdCaseDocumentCreate) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskCaseDetail]: Adding document to case:', caseId)
      setError(null)

      try {
        await legaldeskService.addDocument(caseId, data)
        console.log('INFO [useLegaldeskCaseDetail]: Document added, refreshing')
        await refreshCase()
      } catch (err) {
        console.error('ERROR [useLegaldeskCaseDetail]: Failed to add document:', err)
        setError('Failed to add document. Please try again.')
        throw err
      }
    },
    [caseId, refreshCase]
  )

  useEffect(() => {
    refreshCase()
  }, [refreshCase])

  return {
    caseDetail,
    loading,
    error,
    updateCase,
    updateStatus,
    classifyCase,
    assignSpecialist,
    suggestSpecialists,
    candidates,
    updateAssignmentStatus,
    addDeliverable,
    updateDeliverableStatus,
    addMessage,
    addDocument,
    refreshCase,
  }
}

export default useLegaldeskCaseDetail
