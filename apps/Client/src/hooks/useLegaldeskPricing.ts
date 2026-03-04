import { useState, useEffect, useCallback } from 'react'
import { legaldeskService } from '@/services/legaldeskService'
import type { LdPricingHistory } from '@/types/legaldesk'

interface UseLegaldeskPricingResult {
  history: LdPricingHistory[]
  loading: boolean
  error: string | null
  propose: (data: { amount: number; currency?: string; notes?: string }) => Promise<void>
  counter: (data: { amount: number; currency?: string; notes?: string }) => Promise<void>
  accept: () => Promise<void>
  reject: (notes?: string) => Promise<void>
  refreshPricing: () => Promise<void>
}

export const useLegaldeskPricing = (caseId: number | null): UseLegaldeskPricingResult => {
  const [history, setHistory] = useState<LdPricingHistory[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshPricing = useCallback(async () => {
    if (!caseId) {
      console.log('INFO [useLegaldeskPricing]: No caseId provided, skipping fetch')
      return
    }

    console.log('INFO [useLegaldeskPricing]: Fetching pricing history for case:', caseId)
    setLoading(true)
    setError(null)

    try {
      const data = await legaldeskService.getPricingHistory(caseId)
      setHistory(data)
      console.log('INFO [useLegaldeskPricing]: Fetched', data.length, 'pricing records')
    } catch (err) {
      console.error('ERROR [useLegaldeskPricing]: Failed to fetch pricing history:', err)
      setError('Failed to load pricing history. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [caseId])

  const propose = useCallback(
    async (data: { amount: number; currency?: string; notes?: string }) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskPricing]: Creating proposal for case:', caseId)
      setError(null)

      try {
        await legaldeskService.createPricingProposal(caseId, data)
        console.log('INFO [useLegaldeskPricing]: Proposal created, refreshing')
        await refreshPricing()
      } catch (err) {
        console.error('ERROR [useLegaldeskPricing]: Failed to create proposal:', err)
        setError('Failed to create pricing proposal. Please try again.')
        throw err
      }
    },
    [caseId, refreshPricing]
  )

  const counter = useCallback(
    async (data: { amount: number; currency?: string; notes?: string }) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskPricing]: Submitting counter for case:', caseId)
      setError(null)

      try {
        await legaldeskService.submitCounter(caseId, data)
        console.log('INFO [useLegaldeskPricing]: Counter submitted, refreshing')
        await refreshPricing()
      } catch (err) {
        console.error('ERROR [useLegaldeskPricing]: Failed to submit counter:', err)
        setError('Failed to submit counter offer. Please try again.')
        throw err
      }
    },
    [caseId, refreshPricing]
  )

  const accept = useCallback(async () => {
    if (!caseId) return
    console.log('INFO [useLegaldeskPricing]: Accepting pricing for case:', caseId)
    setError(null)

    try {
      await legaldeskService.acceptPricing(caseId)
      console.log('INFO [useLegaldeskPricing]: Pricing accepted, refreshing')
      await refreshPricing()
    } catch (err) {
      console.error('ERROR [useLegaldeskPricing]: Failed to accept pricing:', err)
      setError('Failed to accept pricing. Please try again.')
      throw err
    }
  }, [caseId, refreshPricing])

  const reject = useCallback(
    async (notes?: string) => {
      if (!caseId) return
      console.log('INFO [useLegaldeskPricing]: Rejecting pricing for case:', caseId)
      setError(null)

      try {
        await legaldeskService.rejectPricing(caseId, notes)
        console.log('INFO [useLegaldeskPricing]: Pricing rejected, refreshing')
        await refreshPricing()
      } catch (err) {
        console.error('ERROR [useLegaldeskPricing]: Failed to reject pricing:', err)
        setError('Failed to reject pricing. Please try again.')
        throw err
      }
    },
    [caseId, refreshPricing]
  )

  useEffect(() => {
    refreshPricing()
  }, [refreshPricing])

  return {
    history,
    loading,
    error,
    propose,
    counter,
    accept,
    reject,
    refreshPricing,
  }
}

export default useLegaldeskPricing
