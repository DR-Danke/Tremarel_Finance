import { useState, useMemo } from 'react'

interface UseTablePaginationResult<T> {
  paginated: T[]
  page: number
  rowsPerPage: number
  totalCount: number
  onPageChange: (newPage: number) => void
  onRowsPerPageChange: (newRowsPerPage: number) => void
}

export function useTablePagination<T>(data: T[], defaultRowsPerPage = 10): UseTablePaginationResult<T> {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(defaultRowsPerPage)

  const paginated = useMemo(() => {
    const start = page * rowsPerPage
    return data.slice(start, start + rowsPerPage)
  }, [data, page, rowsPerPage])

  const onPageChange = (newPage: number) => setPage(newPage)

  const onRowsPerPageChange = (newRowsPerPage: number) => {
    setRowsPerPage(newRowsPerPage)
    setPage(0)
  }

  return {
    paginated,
    page,
    rowsPerPage,
    totalCount: data.length,
    onPageChange,
    onRowsPerPageChange,
  }
}
