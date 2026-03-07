/**
 * Legal Desk TypeScript types for the frontend application.
 * Matches the 11 ld_* database tables from create_legaldesk_tables.sql.
 */

// ============================================================================
// String Literal Union Types (14)
// ============================================================================

export type CaseStatus =
  | 'new'
  | 'classifying'
  | 'open'
  | 'assigning'
  | 'active'
  | 'in_progress'
  | 'review'
  | 'negotiating'
  | 'completed'
  | 'closed'
  | 'archived'

export type CaseType = 'advisory' | 'litigation'

export type LegalDomain =
  | 'corporate'
  | 'ip'
  | 'labor'
  | 'tax'
  | 'litigation'
  | 'real_estate'
  | 'immigration'
  | 'regulatory'
  | 'data_privacy'
  | 'commercial'

export type CaseComplexity = 'low' | 'medium' | 'high' | 'critical'

export type CasePriority = 'low' | 'medium' | 'high' | 'urgent'

export type OriginationChannel = 'direct' | 'referral'

export type SpecialistStatus = 'active' | 'inactive' | 'on_leave'

export type SpecialistType = 'individual' | 'boutique_firm'

export type ProficiencyLevel = 'junior' | 'intermediate' | 'expert'

export type AssignmentRole = 'lead' | 'support' | 'reviewer' | 'consultant'

export type AssignmentStatus = 'proposed' | 'accepted' | 'rejected' | 'active' | 'completed'

export type DeliverableStatus = 'pending' | 'in_progress' | 'review' | 'completed' | 'cancelled'

export type PricingAction = 'proposal' | 'counter' | 'accept' | 'reject' | 'adjust' | 'final'

export type ClientType = 'company' | 'individual'

// ============================================================================
// Entity Interfaces (matching ld_* tables)
// ============================================================================

export interface LdClient {
  id: number
  name: string
  client_type: ClientType
  contact_email: string | null
  contact_phone: string | null
  country: string | null
  industry: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LdSpecialist {
  id: number
  full_name: string
  email: string
  phone: string | null
  years_experience: number
  hourly_rate: number | null
  currency: string
  max_concurrent_cases: number
  current_workload: number
  overall_score: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LdSpecialistExpertise {
  id: number
  specialist_id: number
  legal_domain: LegalDomain
  proficiency_level: ProficiencyLevel
  years_in_domain: number
  created_at: string
}

export interface LdSpecialistJurisdiction {
  id: number
  specialist_id: number
  country: string
  region: string | null
  is_primary: boolean
  created_at: string
}

export interface LdCase {
  id: number
  case_number: string
  title: string
  description: string | null
  client_id: number
  legal_domain: LegalDomain
  complexity: CaseComplexity
  priority: CasePriority
  status: CaseStatus
  case_type?: CaseType
  budget: number | null
  estimated_cost: number | null
  final_quote: number | null
  margin_percentage: number | null
  deadline: string | null
  ai_classification: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface LdCaseSpecialist {
  id: number
  case_id: number
  specialist_id: number
  role: AssignmentRole
  status: AssignmentStatus
  proposed_fee: number | null
  agreed_fee: number | null
  fee_currency: string
  assigned_at: string
  responded_at: string | null
}

export interface LdCaseDeliverable {
  id: number
  case_id: number
  specialist_id: number | null
  title: string
  description: string | null
  status: DeliverableStatus
  due_date: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface LdCaseMessage {
  id: number
  case_id: number
  sender_type: string
  sender_name: string | null
  message: string
  is_internal: boolean
  created_at: string
}

export interface LdCaseDocument {
  id: number
  case_id: number
  file_name: string
  file_url: string
  file_type: string | null
  file_size_bytes: number | null
  uploaded_by: string | null
  created_at: string
}

export interface LdPricingHistory {
  id: number
  case_id: number
  action: PricingAction
  previous_amount: number | null
  new_amount: number | null
  currency: string
  changed_by: string | null
  notes: string | null
  created_at: string
}

export interface LdSpecialistScore {
  id: number
  specialist_id: number
  case_id: number
  quality_score: number | null
  teamwork_score: number | null
  delivery_score: number | null
  satisfaction_score: number | null
  overall_score: number | null
  feedback: string | null
  scored_at: string
}

// ============================================================================
// Detail/Extended Interfaces
// ============================================================================

export interface LdCaseDetail extends LdCase {
  client?: LdClient
  specialists: LdCaseSpecialist[]
  deliverables: LdCaseDeliverable[]
  messages: LdCaseMessage[]
  documents: LdCaseDocument[]
  pricing_history: LdPricingHistory[]
}

export interface LdSpecialistDetail extends LdSpecialist {
  expertise: LdSpecialistExpertise[]
  jurisdictions: LdSpecialistJurisdiction[]
  scores: LdSpecialistScore[]
}

// ============================================================================
// Create/Update Interfaces
// ============================================================================

export interface LdClientCreate {
  name: string
  client_type?: ClientType
  contact_email?: string
  contact_phone?: string
  country?: string
  industry?: string
  notes?: string
}

export interface LdClientUpdate {
  name?: string
  client_type?: ClientType
  contact_email?: string
  contact_phone?: string
  country?: string
  industry?: string
  notes?: string
  is_active?: boolean
}

export interface LdSpecialistCreate {
  full_name: string
  email: string
  phone?: string
  years_experience?: number
  hourly_rate?: number
  currency?: string
  max_concurrent_cases?: number
}

export interface LdSpecialistUpdate {
  full_name?: string
  email?: string
  phone?: string
  years_experience?: number
  hourly_rate?: number
  currency?: string
  max_concurrent_cases?: number
  is_active?: boolean
}

export interface LdCaseCreate {
  title: string
  client_id: number
  legal_domain: LegalDomain
  description?: string
  complexity?: CaseComplexity
  priority?: CasePriority
  budget?: number
  estimated_cost?: number
  deadline?: string
}

export interface LdCaseUpdate {
  title?: string
  description?: string
  legal_domain?: LegalDomain
  complexity?: CaseComplexity
  priority?: CasePriority
  status?: CaseStatus
  budget?: number
  estimated_cost?: number
  final_quote?: number
  margin_percentage?: number
  deadline?: string
}

export interface LdCaseSpecialistCreate {
  case_id: number
  specialist_id: number
  role?: AssignmentRole
  proposed_fee?: number
  fee_currency?: string
}

export interface LdCaseSpecialistUpdate {
  role?: AssignmentRole
  status?: AssignmentStatus
  proposed_fee?: number
  agreed_fee?: number
  fee_currency?: string
}

export interface LdCaseDeliverableCreate {
  case_id: number
  title: string
  specialist_id?: number
  description?: string
  due_date?: string
}

export interface LdCaseDeliverableUpdate {
  title?: string
  description?: string
  status?: DeliverableStatus
  specialist_id?: number
  due_date?: string
}

export interface LdCaseMessageCreate {
  case_id: number
  sender_type: string
  message: string
  sender_name?: string
  is_internal?: boolean
}

export interface LdCaseDocumentCreate {
  case_id: number
  file_name: string
  file_url: string
  file_type?: string
  file_size_bytes?: number
  uploaded_by?: string
}

export interface LdPricingHistoryCreate {
  case_id: number
  action: PricingAction
  new_amount: number
  previous_amount?: number
  currency?: string
  changed_by?: string
  notes?: string
}

export interface LdSpecialistScoreCreate {
  specialist_id: number
  case_id: number
  quality_score?: number
  teamwork_score?: number
  delivery_score?: number
  satisfaction_score?: number
  overall_score?: number
  feedback?: string
}

export interface LdSpecialistExpertiseCreate {
  specialist_id: number
  legal_domain: LegalDomain
  proficiency_level?: ProficiencyLevel
  years_in_domain?: number
}

export interface LdSpecialistJurisdictionCreate {
  specialist_id: number
  country: string
  region?: string
  is_primary?: boolean
}

// ============================================================================
// Filter Interfaces
// ============================================================================

export interface LdCaseFilters {
  status?: CaseStatus
  legal_domain?: LegalDomain
  priority?: CasePriority
  complexity?: CaseComplexity
  client_id?: number
}

export interface LdSpecialistFilters {
  is_active?: boolean
  legal_domain?: LegalDomain
}

export interface LdClientFilters {
  client_type?: ClientType
  is_active?: boolean
  country?: string
}

// ============================================================================
// List Response Interfaces
// ============================================================================

export interface LdCaseListResponse {
  cases: LdCase[]
  total: number
}

export interface LdSpecialistListResponse {
  specialists: LdSpecialist[]
  total: number
}

export interface LdClientListResponse {
  clients: LdClient[]
  total: number
}

// ============================================================================
// Dashboard/Specialized Interfaces
// ============================================================================

export interface LdDashboardStats {
  total_cases: number
  active_cases: number
  total_specialists: number
  total_clients: number
  cases_by_status: Record<CaseStatus, number>
  cases_by_domain: Record<LegalDomain, number>
}

export interface LdSpecialistCandidate {
  specialist_id: number
  full_name: string
  email: string
  match_score: number
  hourly_rate: number | null
  currency: string
  current_workload: number
  max_concurrent_cases: number
  expertise_match: string[]
  jurisdiction_match: string[]
  match_reasons: string[]
}

// ============================================================================
// Label and Color Constant Maps
// ============================================================================

export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  new: 'New',
  classifying: 'Classifying',
  open: 'Open',
  assigning: 'Assigning',
  active: 'Active',
  in_progress: 'In Progress',
  review: 'Review',
  negotiating: 'Negotiating',
  completed: 'Completed',
  closed: 'Closed',
  archived: 'Archived',
}

export const CASE_STATUS_COLORS: Record<CaseStatus, string> = {
  new: '#90CAF9',
  classifying: '#CE93D8',
  open: '#80DEEA',
  assigning: '#FFF59D',
  active: '#A5D6A7',
  in_progress: '#81C784',
  review: '#FFB74D',
  negotiating: '#FFAB91',
  completed: '#66BB6A',
  closed: '#BDBDBD',
  archived: '#9E9E9E',
}

export const LEGAL_DOMAIN_LABELS: Record<LegalDomain, string> = {
  corporate: 'Corporate',
  ip: 'Intellectual Property',
  labor: 'Labor',
  tax: 'Tax',
  litigation: 'Litigation',
  real_estate: 'Real Estate',
  immigration: 'Immigration',
  regulatory: 'Regulatory',
  data_privacy: 'Data Privacy',
  commercial: 'Commercial',
}

export const LEGAL_DOMAIN_COLORS: Record<LegalDomain, string> = {
  corporate: '#1565C0',
  ip: '#6A1B9A',
  labor: '#2E7D32',
  tax: '#E65100',
  litigation: '#C62828',
  real_estate: '#4E342E',
  immigration: '#00838F',
  regulatory: '#AD1457',
  data_privacy: '#283593',
  commercial: '#F9A825',
}

export const CASE_PRIORITY_LABELS: Record<CasePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent',
}

export const CASE_PRIORITY_COLORS: Record<CasePriority, string> = {
  low: '#4CAF50',
  medium: '#FFC107',
  high: '#FF9800',
  urgent: '#F44336',
}

export const CASE_COMPLEXITY_LABELS: Record<CaseComplexity, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
}

export const CASE_COMPLEXITY_COLORS: Record<CaseComplexity, string> = {
  low: '#2196F3',
  medium: '#FFC107',
  high: '#FF9800',
  critical: '#F44336',
}

export const SPECIALIST_STATUS_LABELS: Record<SpecialistStatus, string> = {
  active: 'Active',
  inactive: 'Inactive',
  on_leave: 'On Leave',
}

export const SPECIALIST_STATUS_COLORS: Record<SpecialistStatus, string> = {
  active: '#4CAF50',
  inactive: '#9E9E9E',
  on_leave: '#FF9800',
}

export const ASSIGNMENT_STATUS_LABELS: Record<AssignmentStatus, string> = {
  proposed: 'Proposed',
  accepted: 'Accepted',
  rejected: 'Rejected',
  active: 'Active',
  completed: 'Completed',
}

export const ASSIGNMENT_STATUS_COLORS: Record<AssignmentStatus, string> = {
  proposed: '#90CAF9',
  accepted: '#A5D6A7',
  rejected: '#EF9A9A',
  active: '#4CAF50',
  completed: '#66BB6A',
}

export const DELIVERABLE_STATUS_LABELS: Record<DeliverableStatus, string> = {
  pending: 'Pending',
  in_progress: 'In Progress',
  review: 'Review',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

export const DELIVERABLE_STATUS_COLORS: Record<DeliverableStatus, string> = {
  pending: '#90CAF9',
  in_progress: '#FFC107',
  review: '#FF9800',
  completed: '#4CAF50',
  cancelled: '#9E9E9E',
}

export const PROFICIENCY_LEVEL_LABELS: Record<ProficiencyLevel, string> = {
  junior: 'Junior',
  intermediate: 'Intermediate',
  expert: 'Expert',
}

export const ASSIGNMENT_ROLE_LABELS: Record<AssignmentRole, string> = {
  lead: 'Lead',
  support: 'Support',
  reviewer: 'Reviewer',
  consultant: 'Consultant',
}

export const CASE_TYPE_LABELS: Record<CaseType, string> = {
  advisory: 'Advisory',
  litigation: 'Litigation',
}

export const CLIENT_TYPE_LABELS: Record<ClientType, string> = {
  company: 'Company',
  individual: 'Individual',
}

export const PRICING_ACTION_LABELS: Record<PricingAction, string> = {
  proposal: 'Proposal',
  counter: 'Counter',
  accept: 'Accept',
  reject: 'Reject',
  adjust: 'Adjust',
  final: 'Final',
}
