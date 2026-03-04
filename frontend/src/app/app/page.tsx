'use client'

import { useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'
import type { KPIStats, EventEntry } from '@/lib/types'
import KPICard from '@/components/dashboard/KPICard'
import EventFeed from '@/components/dashboard/EventFeed'

export default function DashboardPage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [kpis, setKpis] = useState<KPIStats | null>(null)
  const [events, setEvents] = useState<EventEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number } | null>(null)

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [kpisData, eventsData] = await Promise.all([
          api.getKPIs(),
          api.getEvents(10),
        ])
        setKpis(kpisData)
        setEvents(eventsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleNewMigration = () => {
    router.push('/app/runs')
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    // Limit to 20 files
    const filesToUpload = files.slice(0, 20)
    if (files.length > 20) {
      setError('Maximum 20 files allowed. Only first 20 will be uploaded.')
    }

    try {
      setUploading(true)
      setError(null)
      setUploadSuccess(null)
      setUploadProgress({ current: 0, total: filesToUpload.length })

      let successCount = 0
      let failCount = 0

      // Upload files sequentially with progress updates
      for (let i = 0; i < filesToUpload.length; i++) {
        const file = filesToUpload[i]
        setUploadProgress({ current: i + 1, total: filesToUpload.length })

        try {
          await api.uploadUniverse(file)
          successCount++
        } catch (err) {
          failCount++
          console.error(`Failed to upload ${file.name}:`, err)
        }
      }

      // Refresh data after all uploads
      const [kpisData, eventsData] = await Promise.all([
        api.getKPIs(),
        api.getEvents(10),
      ])
      setKpis(kpisData)
      setEvents(eventsData)

      // Show summary
      if (failCount === 0) {
        setUploadSuccess(`✅ ${successCount} of ${filesToUpload.length} files uploaded successfully!`)
      } else {
        setUploadSuccess(`⚠️ ${successCount} uploaded, ${failCount} failed`)
      }

      // Clear success message after 5 seconds
      setTimeout(() => {
        setUploadSuccess(null)
        setUploadProgress(null)
      }, 5000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload files')
    } finally {
      setUploading(false)
      setUploadProgress(null)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleViewReports = () => {
    router.push('/app/universes')
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900 mx-auto"></div>
          <p className="mt-4 text-sm text-slate-600">Loading dashboard...</p>
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
    <div className="space-y-8">
      {/* Success Message */}
      {uploadSuccess && (
        <div className="rounded-lg bg-green-50 border border-green-200 p-4">
          <p className="text-sm font-medium text-green-800">{uploadSuccess}</p>
        </div>
      )}

      {/* Hero Header with Gradient */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-900 to-purple-900 p-8 lg:p-12">
        <div className="absolute inset-0 bg-grid-white/5 [mask-image:linear-gradient(0deg,transparent,black)]" />
        <div className="relative">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl lg:text-5xl font-bold text-white mb-3">
                Pipeline Overview
              </h1>
              <p className="text-lg text-slate-300 max-w-2xl">
                Real-time monitoring of your universe migration pipeline
              </p>
            </div>
            <div className="hidden lg:block">
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 rounded-full bg-green-400 animate-pulse" />
                <span className="text-sm font-medium text-slate-300">System Active</span>
              </div>
            </div>
          </div>

          {/* Quick Stats Bar */}
          <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-blue-500/20 p-2.5">
                  <UniverseIcon />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-300">Total Universes</p>
                  <p className="text-3xl font-bold text-white mt-1">{kpis?.total_universes || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-green-500/20 p-2.5">
                  <CheckIcon />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-300">Parsed</p>
                  <p className="text-3xl font-bold text-white mt-1">{kpis?.parsed || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-purple-500/20 p-2.5">
                  <TransformIcon />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-300">Transformed</p>
                  <p className="text-3xl font-bold text-white mt-1">{kpis?.transformed || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-orange-500/20 p-2.5">
                  <ValidateIcon />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-300">Validated</p>
                  <p className="text-3xl font-bold text-white mt-1">{kpis?.validated || 0}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bento Grid Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Pipeline Stage Cards */}
        <div className="lg:col-span-2 grid sm:grid-cols-3 gap-4">
          <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 p-6 hover:scale-105 transition-transform duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-grid-white/10" />
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="rounded-xl bg-white/20 p-2.5">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <span className="text-xs font-bold text-white/60">01</span>
              </div>
              <h3 className="text-white font-semibold mb-1">Parser</h3>
              <p className="text-sm text-white/80">Universe detection & CIM generation</p>
              <div className="mt-4 flex items-center gap-2">
                <div className="h-2 flex-1 rounded-full bg-white/20 overflow-hidden">
                  <div className="h-full bg-white rounded-full" style={{ width: `${((kpis?.parsed || 0) / (kpis?.total_universes || 1)) * 100}%` }} />
                </div>
                <span className="text-xs font-semibold text-white">{kpis?.parsed || 0}/{kpis?.total_universes || 0}</span>
              </div>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 p-6 hover:scale-105 transition-transform duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-grid-white/10" />
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="rounded-xl bg-white/20 p-2.5">
                  <TransformIcon />
                </div>
                <span className="text-xs font-bold text-white/60">02</span>
              </div>
              <h3 className="text-white font-semibold mb-1">Transform</h3>
              <p className="text-sm text-white/80">SAC, Datasphere & HANA generation</p>
              <div className="mt-4 flex items-center gap-2">
                <div className="h-2 flex-1 rounded-full bg-white/20 overflow-hidden">
                  <div className="h-full bg-white rounded-full" style={{ width: `${((kpis?.transformed || 0) / (kpis?.total_universes || 1)) * 100}%` }} />
                </div>
                <span className="text-xs font-semibold text-white">{kpis?.transformed || 0}/{kpis?.total_universes || 0}</span>
              </div>
            </div>
          </div>

          <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 p-6 hover:scale-105 transition-transform duration-300 cursor-pointer">
            <div className="absolute inset-0 bg-grid-white/10" />
            <div className="relative">
              <div className="flex items-center justify-between mb-4">
                <div className="rounded-xl bg-white/20 p-2.5">
                  <ValidateIcon />
                </div>
                <span className="text-xs font-bold text-white/60">03</span>
              </div>
              <h3 className="text-white font-semibold mb-1">Validate</h3>
              <p className="text-sm text-white/80">Semantic validation & lineage</p>
              <div className="mt-4 flex items-center gap-2">
                <div className="h-2 flex-1 rounded-full bg-white/20 overflow-hidden">
                  <div className="h-full bg-white rounded-full" style={{ width: `${((kpis?.validated || 0) / (kpis?.total_universes || 1)) * 100}%` }} />
                </div>
                <span className="text-xs font-semibold text-white">{kpis?.validated || 0}/{kpis?.total_universes || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".unv,.unx"
                multiple
                className="hidden"
              />
              <button
                onClick={handleNewMigration}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-indigo-500 hover:bg-indigo-600 text-white transition-colors"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span className="text-sm font-medium">New Migration</span>
              </button>
              <button
                onClick={handleUploadClick}
                disabled={uploading}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-700 hover:bg-slate-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? (
                  <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                )}
                <span className="text-sm font-medium">
                  {uploading
                    ? uploadProgress
                      ? `Uploading ${uploadProgress.current} of ${uploadProgress.total}...`
                      : 'Uploading...'
                    : 'Upload Universe'
                  }
                </span>
              </button>
              <button
                onClick={handleViewReports}
                className="w-full flex items-center gap-3 p-3 rounded-xl bg-slate-700 hover:bg-slate-600 text-white transition-colors"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm font-medium">View Reports</span>
              </button>
            </div>
          </div>

          <div className="rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 p-6 border border-green-400">
            <div className="flex items-center gap-3 mb-2">
              <div className="rounded-lg bg-white/20 p-2">
                <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="text-white font-semibold">System Status</h4>
            </div>
            <p className="text-sm text-white/90">All engines operational</p>
          </div>
        </div>
      </div>

      {/* Events Feed - Full Width */}
      <EventFeed events={events} />
    </div>
  )
}

function UniverseIcon() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
    </svg>
  )
}

function TransformIcon() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  )
}

function ValidateIcon() {
  return (
    <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}
