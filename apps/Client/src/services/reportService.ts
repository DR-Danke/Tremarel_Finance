import { apiClient } from '@/api/clients'
import type { ReportData, ReportFilter } from '@/types'

/**
 * Report service for fetching report data and exporting CSV.
 */
export const reportService = {
  /**
   * Get report data for an entity within a date range.
   * @param entityId - Entity ID to get report data for
   * @param filters - Report filter parameters
   * @returns Report data including summary, comparison, and breakdown
   */
  async getReportData(entityId: string, filters: ReportFilter): Promise<ReportData> {
    console.log(
      `INFO [ReportService]: Fetching report data for entity ${entityId}`,
      filters
    )
    try {
      const params = new URLSearchParams({
        entity_id: entityId,
        start_date: filters.startDate,
        end_date: filters.endDate,
      })

      const response = await apiClient.get<ReportData>(`/reports/data?${params}`)
      console.log('INFO [ReportService]: Report data fetched successfully')
      return response.data
    } catch (error) {
      console.error('ERROR [ReportService]: Failed to fetch report data:', error)
      throw error
    }
  },

  /**
   * Export transactions to CSV file.
   * @param entityId - Entity ID to export data for
   * @param filters - Report filter parameters
   */
  async exportCsv(entityId: string, filters: ReportFilter): Promise<void> {
    console.log(
      `INFO [ReportService]: Exporting CSV for entity ${entityId}`,
      filters
    )
    try {
      const params = new URLSearchParams({
        entity_id: entityId,
        start_date: filters.startDate,
        end_date: filters.endDate,
      })

      const response = await apiClient.get(`/reports/export/csv?${params}`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.download = `transactions_${filters.startDate}_${filters.endDate}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      console.log('INFO [ReportService]: CSV export completed successfully')
    } catch (error) {
      console.error('ERROR [ReportService]: Failed to export CSV:', error)
      throw error
    }
  },
}

export default reportService
