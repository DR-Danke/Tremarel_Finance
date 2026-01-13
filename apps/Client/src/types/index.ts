// Base API response interface
export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

// User interface matching backend UserResponseDTO
export interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  is_active: boolean
  createdAt?: string
  updatedAt?: string
}

// Login credentials for authentication
export interface LoginCredentials {
  email: string
  password: string
}

// Registration data for new users
export interface RegisterData {
  email: string
  password: string
  first_name?: string
  last_name?: string
}

// Authentication response from backend
export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// Authentication state placeholder
export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

// Entity interface matching backend EntityResponseDTO
export interface Entity {
  id: string
  name: string
  type: 'family' | 'startup'
  description?: string
  created_at: string
  updated_at?: string
}

// Data for creating a new entity
export interface CreateEntityData {
  name: string
  type: 'family' | 'startup'
  description?: string
}

// Data for updating an entity
export interface UpdateEntityData {
  name?: string
  description?: string
}

// User-Entity membership interface
export interface UserEntity {
  id: string
  user_id: string
  entity_id: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  created_at: string
}

// Entity member with user details
export interface EntityMember {
  id: string
  user_id: string
  email: string
  first_name?: string
  last_name?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  created_at: string
}

// Transaction types
export type TransactionType = 'income' | 'expense'

export interface Transaction {
  id: string
  entity_id: string
  category_id: string
  user_id?: string
  recurring_template_id?: string
  type: TransactionType
  amount: number
  description?: string
  date: string
  notes?: string
  created_at: string
  updated_at?: string
}

export interface TransactionCreate {
  entity_id: string
  category_id: string
  amount: number
  type: TransactionType
  description?: string
  date: string
  notes?: string
}

export interface TransactionUpdate {
  category_id?: string
  amount?: number
  type?: TransactionType
  description?: string
  date?: string
  notes?: string
}

export interface TransactionFilters {
  start_date?: string
  end_date?: string
  category_id?: string
  type?: TransactionType
}

export interface TransactionListResponse {
  transactions: Transaction[]
  total: number
}

// Category type alias
export type CategoryType = 'income' | 'expense'

// Category interface matching backend CategoryResponseDTO
export interface Category {
  id: string
  entity_id: string
  name: string
  type: CategoryType
  parent_id?: string | null
  description?: string | null
  color?: string | null
  icon?: string | null
  is_active: boolean
  created_at: string
  updated_at?: string | null
}

// Category with nested children for tree display
export interface CategoryTree extends Category {
  children: CategoryTree[]
}

// Input for creating a category
export interface CategoryCreateInput {
  entity_id: string
  name: string
  type: CategoryType
  parent_id?: string | null
  description?: string | null
  color?: string | null
  icon?: string | null
}

// Input for updating a category
export interface CategoryUpdateInput {
  name?: string
  parent_id?: string | null
  description?: string | null
  color?: string | null
  icon?: string | null
  is_active?: boolean
}

// Dashboard types
export interface CurrentMonthSummary {
  total_income: number
  total_expenses: number
  net_balance: number
}

export interface MonthlyTotal {
  month: string
  year: number
  month_number: number
  income: number
  expenses: number
}

export interface CategoryBreakdown {
  category_id: string
  category_name: string
  amount: number
  percentage: number
  color: string | null
}

export interface DashboardStats {
  current_month_summary: CurrentMonthSummary
  monthly_trends: MonthlyTotal[]
  expense_breakdown: CategoryBreakdown[]
}

// Budget types
export type BudgetPeriodType = 'monthly' | 'quarterly' | 'yearly'

export interface Budget {
  id: string
  entity_id: string
  category_id: string
  amount: number
  period_type: BudgetPeriodType
  start_date: string
  end_date?: string | null
  is_active: boolean
  created_at: string
  updated_at?: string | null
}

export interface BudgetWithSpending extends Budget {
  category_name?: string | null
  spent_amount: number
  spent_percentage: number
}

export interface BudgetCreate {
  entity_id: string
  category_id: string
  amount: number
  period_type: BudgetPeriodType
  start_date: string
}

export interface BudgetUpdate {
  amount?: number
  period_type?: BudgetPeriodType
  start_date?: string
  is_active?: boolean
}

export interface BudgetListResponse {
  budgets: BudgetWithSpending[]
  total: number
}

// Report types
export interface ReportFilter {
  startDate: string
  endDate: string
  type?: TransactionType
  categoryIds?: string[]
}

export interface IncomeExpenseComparison {
  period: string
  month: number
  year: number
  income: number
  expenses: number
}

export interface CategorySummary {
  category_id: string
  category_name: string
  amount: number
  percentage: number
  type: TransactionType
  color: string | null
}

export interface ReportSummary {
  total_income: number
  total_expenses: number
  net_balance: number
  transaction_count: number
}

export interface ReportData {
  summary: ReportSummary
  income_expense_comparison: IncomeExpenseComparison[]
  category_breakdown: CategorySummary[]
}

// Recurring template types
export type RecurrenceFrequency = 'daily' | 'weekly' | 'monthly' | 'yearly'

export interface RecurringTemplate {
  id: string
  entity_id: string
  category_id: string
  name: string
  amount: number
  type: TransactionType
  description?: string
  notes?: string
  frequency: RecurrenceFrequency
  start_date: string
  end_date?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface RecurringTemplateCreate {
  entity_id: string
  category_id: string
  name: string
  amount: number
  type: TransactionType
  description?: string
  notes?: string
  frequency: RecurrenceFrequency
  start_date: string
  end_date?: string
}

export interface RecurringTemplateUpdate {
  category_id?: string
  name?: string
  amount?: number
  type?: TransactionType
  description?: string
  notes?: string
  frequency?: RecurrenceFrequency
  start_date?: string
  end_date?: string
  is_active?: boolean
}

export interface RecurringTemplateListResponse {
  templates: RecurringTemplate[]
  total: number
}
