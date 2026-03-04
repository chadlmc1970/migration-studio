'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { UniverseInfo } from '@/lib/types'
import UniverseTable from '@/components/universes/UniverseTable'

export default function UniversesPage() {
  const [universes, setUniverses] = useState<UniverseInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadUniverses() {
      try {
        setLoading(true)
        const data = await api.getUniverses()
        setUniverses(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load universes')
      } finally {
        setLoading(false)
      }
    }
    loadUniverses()
  }, [])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900 mx-auto"></div>
          <p className="mt-4 text-sm text-slate-600">Loading universes...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-lg bg-red-50 p-6">
        <p className="text-sm text-red-800">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Universes</h1>
          <p className="mt-1 text-sm text-slate-600">
            View and manage your migrated universes
          </p>
        </div>
      </div>

      <UniverseTable universes={universes} />
    </div>
  )
}
