/**
 * Person types for RestaurantOS person management.
 * Matches backend PersonResponseDTO, PersonCreateDTO, PersonUpdateDTO.
 */

export type PersonType = 'employee' | 'supplier' | 'owner'

export interface Person {
  id: string
  restaurant_id: string
  name: string
  role: string
  email: string | null
  whatsapp: string | null
  push_token: string | null
  type: PersonType
  created_at: string
  updated_at: string | null
}

export interface PersonCreate {
  restaurant_id: string
  name: string
  role: string
  email?: string
  whatsapp?: string
  push_token?: string
  type?: PersonType
}

export interface PersonUpdate {
  name?: string
  role?: string
  email?: string
  whatsapp?: string
  push_token?: string
  type?: PersonType
}

export interface PersonFilters {
  type?: PersonType
}
