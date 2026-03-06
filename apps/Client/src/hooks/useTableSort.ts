import { useState, useMemo } from 'react'

type Order = 'asc' | 'desc'

interface UseTableSortResult<T> {
  sorted: T[]
  orderBy: keyof T | null
  order: Order
  onSort: (column: keyof T) => void
}

function getComparator<T>(orderBy: keyof T, order: Order) {
  return (a: T, b: T): number => {
    const aVal = a[orderBy]
    const bVal = b[orderBy]
    if (aVal == null && bVal == null) return 0
    if (aVal == null) return 1
    if (bVal == null) return -1
    if (aVal < bVal) return order === 'asc' ? -1 : 1
    if (aVal > bVal) return order === 'asc' ? 1 : -1
    return 0
  }
}

export function useTableSort<T>(data: T[], defaultOrderBy?: keyof T): UseTableSortResult<T> {
  const [orderBy, setOrderBy] = useState<keyof T | null>(defaultOrderBy ?? null)
  const [order, setOrder] = useState<Order>('asc')

  const onSort = (column: keyof T) => {
    if (orderBy === column) {
      setOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setOrderBy(column)
      setOrder('asc')
    }
  }

  const sorted = useMemo(() => {
    if (!orderBy) return data
    return [...data].sort(getComparator(orderBy, order))
  }, [data, orderBy, order])

  return { sorted, orderBy, order, onSort }
}
