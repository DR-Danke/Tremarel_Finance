/**
 * Dashboard types for RestaurantOS operations dashboard.
 * Matches backend restaurant_dashboard_routes overview response.
 */

import type { Document } from './document'
import type { Event } from './event'
import type { InventoryMovement, Resource } from './resource'

export interface DashboardStats {
  total_employees: number
  total_resources: number
  active_documents: number
  tasks_completed_today: number
}

export interface DashboardOverview {
  today_tasks: Event[]
  upcoming_expirations: Document[]
  low_stock_items: Resource[]
  recent_movements: InventoryMovement[]
  pending_alerts: Event[]
  stats: DashboardStats
}
