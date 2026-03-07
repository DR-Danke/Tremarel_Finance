import { apiClient } from '@/api/clients'
import type {
  LdCase,
  LdCaseDetail,
  LdCaseCreate,
  LdCaseUpdate,
  LdCaseFilters,
  LdCaseSpecialist,
  LdCaseSpecialistCreate,
  LdCaseDeliverable,
  LdCaseDeliverableCreate,
  LdCaseDeliverableUpdate,
  LdCaseMessage,
  LdCaseMessageCreate,
  LdCaseDocument,
  LdCaseDocumentCreate,
  LdPricingHistory,
  LdSpecialist,
  LdSpecialistDetail,
  LdSpecialistCreate,
  LdSpecialistUpdate,
  LdSpecialistExpertiseCreate,
  LdSpecialistJurisdictionCreate,
  LdSpecialistScoreCreate,
  LdSpecialistCandidate,
  LdClient,
  LdClientCreate,
  LdClientUpdate,
  LdDashboardStats,
  CaseStatus,
  DeliverableStatus,
  AssignmentStatus,
} from '@/types/legaldesk'

const BASE = '/legaldesk'

export const legaldeskService = {
  // ── Cases ──────────────────────────────────────────────────────────────

  async createCase(data: LdCaseCreate): Promise<LdCase> {
    console.log('INFO [LegaldeskService]: Creating case:', data.title)
    try {
      const response = await apiClient.post<LdCase>(`${BASE}/cases`, data)
      console.log('INFO [LegaldeskService]: Case created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create case:', error)
      throw error
    }
  },

  async listCases(filters?: LdCaseFilters): Promise<LdCase[]> {
    console.log('INFO [LegaldeskService]: Fetching cases with filters:', filters)
    try {
      const response = await apiClient.get<LdCase[]>(`${BASE}/cases`, { params: filters })
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'cases')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch cases:', error)
      throw error
    }
  },

  async getCase(id: number): Promise<LdCaseDetail> {
    console.log('INFO [LegaldeskService]: Fetching case:', id)
    try {
      const response = await apiClient.get<LdCaseDetail>(`${BASE}/cases/${id}`)
      console.log('INFO [LegaldeskService]: Case fetched:', response.data.case_number)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch case:', error)
      throw error
    }
  },

  async updateCase(id: number, data: LdCaseUpdate): Promise<LdCase> {
    console.log('INFO [LegaldeskService]: Updating case:', id)
    try {
      const response = await apiClient.put<LdCase>(`${BASE}/cases/${id}`, data)
      console.log('INFO [LegaldeskService]: Case updated:', id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update case:', error)
      throw error
    }
  },

  async updateCaseStatus(id: number, status: CaseStatus): Promise<void> {
    console.log('INFO [LegaldeskService]: Updating case status:', id, '->', status)
    try {
      await apiClient.patch(`${BASE}/cases/${id}/status`, { status })
      console.log('INFO [LegaldeskService]: Case status updated:', id)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update case status:', error)
      throw error
    }
  },

  async classifyCase(id: number): Promise<Record<string, unknown>> {
    console.log('INFO [LegaldeskService]: Classifying case:', id)
    try {
      const response = await apiClient.post<Record<string, unknown>>(`${BASE}/cases/${id}/classify`)
      console.log('INFO [LegaldeskService]: Case classified:', id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to classify case:', error)
      throw error
    }
  },

  // ── Assignments ────────────────────────────────────────────────────────

  async getCaseSpecialists(caseId: number): Promise<LdCaseSpecialist[]> {
    console.log('INFO [LegaldeskService]: Fetching specialists for case:', caseId)
    try {
      const response = await apiClient.get<LdCaseSpecialist[]>(`${BASE}/cases/${caseId}/specialists`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'specialists for case', caseId)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch case specialists:', error)
      throw error
    }
  },

  async assignSpecialist(caseId: number, data: LdCaseSpecialistCreate): Promise<LdCaseSpecialist> {
    console.log('INFO [LegaldeskService]: Assigning specialist to case:', caseId)
    try {
      const response = await apiClient.post<LdCaseSpecialist>(`${BASE}/cases/${caseId}/specialists`, data)
      console.log('INFO [LegaldeskService]: Specialist assigned to case:', caseId)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to assign specialist:', error)
      throw error
    }
  },

  async suggestSpecialists(caseId: number): Promise<LdSpecialistCandidate[]> {
    console.log('INFO [LegaldeskService]: Suggesting specialists for case:', caseId)
    try {
      const response = await apiClient.get<{ case_id: number; legal_domain: string; candidates: LdSpecialistCandidate[]; generated_at: string }>(`${BASE}/cases/${caseId}/specialists/suggest`)
      const candidates = response.data.candidates ?? []
      console.log('INFO [LegaldeskService]: Got', candidates.length, 'suggestions for case', caseId)
      return candidates
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to suggest specialists:', error)
      throw error
    }
  },

  async updateAssignmentStatus(caseId: number, assignmentId: number, status: AssignmentStatus): Promise<void> {
    console.log('INFO [LegaldeskService]: Updating assignment status:', assignmentId, '->', status)
    try {
      await apiClient.patch(`${BASE}/cases/${caseId}/specialists/${assignmentId}/status`, { status })
      console.log('INFO [LegaldeskService]: Assignment status updated:', assignmentId)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update assignment status:', error)
      throw error
    }
  },

  // ── Deliverables ───────────────────────────────────────────────────────

  async getDeliverables(caseId: number): Promise<LdCaseDeliverable[]> {
    console.log('INFO [LegaldeskService]: Fetching deliverables for case:', caseId)
    try {
      const response = await apiClient.get<LdCaseDeliverable[]>(`${BASE}/cases/${caseId}/deliverables`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'deliverables')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch deliverables:', error)
      throw error
    }
  },

  async createDeliverable(caseId: number, data: LdCaseDeliverableCreate): Promise<LdCaseDeliverable> {
    console.log('INFO [LegaldeskService]: Creating deliverable for case:', caseId)
    try {
      const response = await apiClient.post<LdCaseDeliverable>(`${BASE}/cases/${caseId}/deliverables`, data)
      console.log('INFO [LegaldeskService]: Deliverable created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create deliverable:', error)
      throw error
    }
  },

  async updateDeliverable(caseId: number, deliverableId: number, data: LdCaseDeliverableUpdate): Promise<LdCaseDeliverable> {
    console.log('INFO [LegaldeskService]: Updating deliverable:', deliverableId)
    try {
      const response = await apiClient.put<LdCaseDeliverable>(`${BASE}/cases/${caseId}/deliverables/${deliverableId}`, data)
      console.log('INFO [LegaldeskService]: Deliverable updated:', deliverableId)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update deliverable:', error)
      throw error
    }
  },

  async updateDeliverableStatus(caseId: number, deliverableId: number, status: DeliverableStatus): Promise<void> {
    console.log('INFO [LegaldeskService]: Updating deliverable status:', deliverableId, '->', status)
    try {
      await apiClient.patch(`${BASE}/cases/${caseId}/deliverables/${deliverableId}/status`, { status })
      console.log('INFO [LegaldeskService]: Deliverable status updated:', deliverableId)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update deliverable status:', error)
      throw error
    }
  },

  // ── Messages ───────────────────────────────────────────────────────────

  async getMessages(caseId: number, includeInternal?: boolean): Promise<LdCaseMessage[]> {
    console.log('INFO [LegaldeskService]: Fetching messages for case:', caseId)
    try {
      const response = await apiClient.get<LdCaseMessage[]>(`${BASE}/cases/${caseId}/messages`, {
        params: { include_internal: includeInternal },
      })
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'messages')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch messages:', error)
      throw error
    }
  },

  async createMessage(caseId: number, data: LdCaseMessageCreate): Promise<LdCaseMessage> {
    console.log('INFO [LegaldeskService]: Creating message for case:', caseId)
    try {
      const response = await apiClient.post<LdCaseMessage>(`${BASE}/cases/${caseId}/messages`, data)
      console.log('INFO [LegaldeskService]: Message created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create message:', error)
      throw error
    }
  },

  // ── Documents ──────────────────────────────────────────────────────────

  async getDocuments(caseId: number): Promise<LdCaseDocument[]> {
    console.log('INFO [LegaldeskService]: Fetching documents for case:', caseId)
    try {
      const response = await apiClient.get<LdCaseDocument[]>(`${BASE}/cases/${caseId}/documents`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'documents')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch documents:', error)
      throw error
    }
  },

  async addDocument(caseId: number, data: LdCaseDocumentCreate): Promise<LdCaseDocument> {
    console.log('INFO [LegaldeskService]: Adding document to case:', caseId)
    try {
      const response = await apiClient.post<LdCaseDocument>(`${BASE}/cases/${caseId}/documents`, data)
      console.log('INFO [LegaldeskService]: Document added:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to add document:', error)
      throw error
    }
  },

  // ── Pricing ────────────────────────────────────────────────────────────

  async getPricingHistory(caseId: number): Promise<LdPricingHistory[]> {
    console.log('INFO [LegaldeskService]: Fetching pricing history for case:', caseId)
    try {
      const response = await apiClient.get<LdPricingHistory[]>(`${BASE}/cases/${caseId}/pricing`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'pricing records')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch pricing history:', error)
      throw error
    }
  },

  async createPricingProposal(caseId: number, data: { amount: number; currency?: string; notes?: string }): Promise<LdPricingHistory> {
    console.log('INFO [LegaldeskService]: Creating pricing proposal for case:', caseId)
    try {
      const response = await apiClient.post<LdPricingHistory>(`${BASE}/cases/${caseId}/pricing/propose`, data)
      console.log('INFO [LegaldeskService]: Pricing proposal created')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create pricing proposal:', error)
      throw error
    }
  },

  async submitCounter(caseId: number, data: { amount: number; currency?: string; notes?: string }): Promise<LdPricingHistory> {
    console.log('INFO [LegaldeskService]: Submitting counter for case:', caseId)
    try {
      const response = await apiClient.post<LdPricingHistory>(`${BASE}/cases/${caseId}/pricing/counter`, data)
      console.log('INFO [LegaldeskService]: Counter submitted')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to submit counter:', error)
      throw error
    }
  },

  async acceptPricing(caseId: number): Promise<LdPricingHistory> {
    console.log('INFO [LegaldeskService]: Accepting pricing for case:', caseId)
    try {
      const response = await apiClient.post<LdPricingHistory>(`${BASE}/cases/${caseId}/pricing/accept`)
      console.log('INFO [LegaldeskService]: Pricing accepted')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to accept pricing:', error)
      throw error
    }
  },

  async rejectPricing(caseId: number, notes?: string): Promise<LdPricingHistory> {
    console.log('INFO [LegaldeskService]: Rejecting pricing for case:', caseId)
    try {
      const response = await apiClient.post<LdPricingHistory>(`${BASE}/cases/${caseId}/pricing/reject`, { notes })
      console.log('INFO [LegaldeskService]: Pricing rejected')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to reject pricing:', error)
      throw error
    }
  },

  // ── Specialists ────────────────────────────────────────────────────────

  async listSpecialists(): Promise<LdSpecialist[]> {
    console.log('INFO [LegaldeskService]: Fetching specialists')
    try {
      const response = await apiClient.get<LdSpecialist[]>(`${BASE}/specialists`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'specialists')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch specialists:', error)
      throw error
    }
  },

  async createSpecialist(data: LdSpecialistCreate): Promise<LdSpecialist> {
    console.log('INFO [LegaldeskService]: Creating specialist:', data.full_name)
    try {
      const response = await apiClient.post<LdSpecialist>(`${BASE}/specialists`, data)
      console.log('INFO [LegaldeskService]: Specialist created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create specialist:', error)
      throw error
    }
  },

  async getSpecialist(id: number): Promise<LdSpecialistDetail> {
    console.log('INFO [LegaldeskService]: Fetching specialist:', id)
    try {
      const response = await apiClient.get<LdSpecialistDetail>(`${BASE}/specialists/${id}`)
      console.log('INFO [LegaldeskService]: Specialist fetched:', response.data.full_name)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch specialist:', error)
      throw error
    }
  },

  async updateSpecialist(id: number, data: LdSpecialistUpdate): Promise<LdSpecialist> {
    console.log('INFO [LegaldeskService]: Updating specialist:', id)
    try {
      const response = await apiClient.put<LdSpecialist>(`${BASE}/specialists/${id}`, data)
      console.log('INFO [LegaldeskService]: Specialist updated:', id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update specialist:', error)
      throw error
    }
  },

  async addExpertise(id: number, data: LdSpecialistExpertiseCreate): Promise<void> {
    console.log('INFO [LegaldeskService]: Adding expertise for specialist:', id)
    try {
      await apiClient.post(`${BASE}/specialists/${id}/expertise`, data)
      console.log('INFO [LegaldeskService]: Expertise added for specialist:', id)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to add expertise:', error)
      throw error
    }
  },

  async addJurisdiction(id: number, data: LdSpecialistJurisdictionCreate): Promise<void> {
    console.log('INFO [LegaldeskService]: Adding jurisdiction for specialist:', id)
    try {
      await apiClient.post(`${BASE}/specialists/${id}/jurisdictions`, data)
      console.log('INFO [LegaldeskService]: Jurisdiction added for specialist:', id)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to add jurisdiction:', error)
      throw error
    }
  },

  async submitScore(id: number, data: LdSpecialistScoreCreate): Promise<void> {
    console.log('INFO [LegaldeskService]: Submitting score for specialist:', id)
    try {
      await apiClient.post(`${BASE}/specialists/${id}/scores`, data)
      console.log('INFO [LegaldeskService]: Score submitted for specialist:', id)
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to submit score:', error)
      throw error
    }
  },

  // ── Clients ────────────────────────────────────────────────────────────

  async listClients(): Promise<LdClient[]> {
    console.log('INFO [LegaldeskService]: Fetching clients')
    try {
      const response = await apiClient.get<LdClient[]>(`${BASE}/clients`)
      console.log('INFO [LegaldeskService]: Fetched', response.data.length, 'clients')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch clients:', error)
      throw error
    }
  },

  async createClient(data: LdClientCreate): Promise<LdClient> {
    console.log('INFO [LegaldeskService]: Creating client:', data.name)
    try {
      const response = await apiClient.post<LdClient>(`${BASE}/clients`, data)
      console.log('INFO [LegaldeskService]: Client created:', response.data.id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to create client:', error)
      throw error
    }
  },

  async getClient(id: number): Promise<LdClient> {
    console.log('INFO [LegaldeskService]: Fetching client:', id)
    try {
      const response = await apiClient.get<LdClient>(`${BASE}/clients/${id}`)
      console.log('INFO [LegaldeskService]: Client fetched:', response.data.name)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch client:', error)
      throw error
    }
  },

  async updateClient(id: number, data: LdClientUpdate): Promise<LdClient> {
    console.log('INFO [LegaldeskService]: Updating client:', id)
    try {
      const response = await apiClient.put<LdClient>(`${BASE}/clients/${id}`, data)
      console.log('INFO [LegaldeskService]: Client updated:', id)
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to update client:', error)
      throw error
    }
  },

  // ── Analytics ──────────────────────────────────────────────────────────

  async getDashboardStats(): Promise<LdDashboardStats> {
    console.log('INFO [LegaldeskService]: Fetching dashboard stats')
    try {
      const response = await apiClient.get<LdDashboardStats>(`${BASE}/analytics/dashboard`)
      console.log('INFO [LegaldeskService]: Dashboard stats fetched')
      return response.data
    } catch (error) {
      console.error('ERROR [LegaldeskService]: Failed to fetch dashboard stats:', error)
      throw error
    }
  },
}

export default legaldeskService
