import { useState, useEffect, useCallback } from 'react'
import { reportService } from '@/services/reportService'
import type { ReportData, ReportFilter } from '@/types'

interface UseReportsResult {
  reportData: ReportData | null
  filters: ReportFilter
  isLoading: boolean
  error: string | null
  setFilters: (filters: ReportFilter) => void
  refresh: () => Promise<void>
  exportToCsv: () => Promise<void>
  isExporting: boolean
}

/**
 * Get default filters for "This Month".
 */
function getDefaultFilters(): ReportFilter {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()

  const startDate = new Date(year, month, 1)
  const endDate = new Date(year, month + 1, 0)

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  }
}

export const useReports = (entityId: string | undefined): UseReportsResult => {
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [filters, setFilters] = useState<ReportFilter>(getDefaultFilters())
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isExporting, setIsExporting] = useState(false)

  const fetchReportData = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useReports]: No entityId provided, skipping fetch')
      return
    }

    console.log(
      `INFO [useReports]: Fetching report data for entity ${entityId}`,
      filters
    )
    setIsLoading(true)
    setError(null)

    try {
      const data = await reportService.getReportData(entityId, filters)
      setReportData(data)
      console.log(`INFO [useReports]: Reports loaded for entity ${entityId}`)
    } catch (err) {
      console.error('ERROR [useReports]: Failed to fetch report data:', err)
      setError('Failed to load report data. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [entityId, filters])

  const exportToCsv = useCallback(async () => {
    if (!entityId) {
      console.log('INFO [useReports]: No entityId provided, skipping export')
      return
    }

    console.log(`INFO [useReports]: Exporting CSV for entity ${entityId}`)
    setIsExporting(true)

    try {
      await reportService.exportCsv(entityId, filters)
      console.log('INFO [useReports]: CSV export completed')
    } catch (err) {
      console.error('ERROR [useReports]: Failed to export CSV:', err)
      setError('Failed to export CSV. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }, [entityId, filters])

  // Fetch report data when entityId or filters change
  useEffect(() => {
    fetchReportData()
  }, [fetchReportData])

  return {
    reportData,
    filters,
    isLoading,
    error,
    setFilters,
    refresh: fetchReportData,
    exportToCsv,
    isExporting,
  }
}

export default useReports
