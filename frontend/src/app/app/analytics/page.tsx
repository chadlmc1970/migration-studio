'use client'

import { useEffect, useState } from 'react'

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')

  // Mock data - will be replaced with real API calls
  const migrationStats = {
    successRate: 94.8,
    avgProcessingTime: 3.2,
    totalProcessed: 247,
    activeProjects: 12
  }

  const pipelinePerformance = [
    { stage: 'Parser', success: 98, time: 45 },
    { stage: 'Transform', success: 95, time: 82 },
    { stage: 'Validate', success: 92, time: 38 }
  ]

  const weeklyTrend = [
    { week: 'Week 1', migrations: 42, errors: 3 },
    { week: 'Week 2', migrations: 58, errors: 2 },
    { week: 'Week 3', migrations: 65, errors: 5 },
    { week: 'Week 4', migrations: 82, errors: 4 }
  ]

  const universeTypes = [
    { type: 'Sales', count: 89, percentage: 36 },
    { type: 'Finance', count: 67, percentage: 27 },
    { type: 'Operations', count: 54, percentage: 22 },
    { type: 'HR', count: 37, percentage: 15 }
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Analytics</h1>
          <p className="mt-2 text-slate-600">
            Track migration performance and project insights
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-slate-100 p-1">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                timeRange === range
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {range === '7d' ? '7 Days' : range === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Top KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-500 p-6 text-white">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-white/10" />
          <div className="relative">
            <p className="text-sm font-medium text-white/80">Success Rate</p>
            <p className="mt-2 text-4xl font-bold">{migrationStats.successRate}%</p>
            <div className="mt-4 flex items-center gap-1 text-xs">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span>+2.4% from last period</span>
            </div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 p-6 text-white">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-white/10" />
          <div className="relative">
            <p className="text-sm font-medium text-white/80">Avg Processing Time</p>
            <p className="mt-2 text-4xl font-bold">{migrationStats.avgProcessingTime}<span className="text-2xl">min</span></p>
            <div className="mt-4 flex items-center gap-1 text-xs">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
              <span>-0.8min improvement</span>
            </div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 to-red-500 p-6 text-white">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-white/10" />
          <div className="relative">
            <p className="text-sm font-medium text-white/80">Total Processed</p>
            <p className="mt-2 text-4xl font-bold">{migrationStats.totalProcessed}</p>
            <div className="mt-4 flex items-center gap-1 text-xs">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <span>+18 this week</span>
            </div>
          </div>
        </div>

        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 to-green-500 p-6 text-white">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-white/10" />
          <div className="relative">
            <p className="text-sm font-medium text-white/80">Active Projects</p>
            <p className="mt-2 text-4xl font-bold">{migrationStats.activeProjects}</p>
            <div className="mt-4 flex items-center gap-1 text-xs">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <span>3 new this month</span>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Migration Trend */}
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-900">Migration Trend</h3>
            <div className="flex items-center gap-3 text-xs">
              <div className="flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full bg-indigo-500" />
                <span className="text-slate-600">Migrations</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="h-2.5 w-2.5 rounded-full bg-red-500" />
                <span className="text-slate-600">Errors</span>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            {weeklyTrend.map((week, idx) => {
              const maxMigrations = Math.max(...weeklyTrend.map(w => w.migrations))
              const migrationWidth = (week.migrations / maxMigrations) * 100
              const errorWidth = (week.errors / week.migrations) * 100

              return (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-slate-700">{week.week}</span>
                    <span className="text-sm text-slate-500">{week.migrations} migrations</span>
                  </div>
                  <div className="relative h-8 rounded-lg bg-slate-100 overflow-hidden">
                    <div
                      className="absolute h-full bg-gradient-to-r from-indigo-500 to-indigo-400 rounded-lg transition-all"
                      style={{ width: `${migrationWidth}%` }}
                    />
                    <div
                      className="absolute right-0 h-full bg-gradient-to-r from-red-500 to-red-400 rounded-r-lg"
                      style={{ width: `${errorWidth}%` }}
                    />
                    <div className="absolute inset-0 flex items-center justify-between px-3">
                      <span className="text-xs font-semibold text-white">{week.migrations}</span>
                      {week.errors > 0 && (
                        <span className="text-xs font-semibold text-white">{week.errors}</span>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Pipeline Performance */}
        <div className="rounded-2xl bg-white p-6 shadow-sm border border-slate-200 overflow-hidden">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">Pipeline Performance</h3>
          <div className="space-y-6">
            {pipelinePerformance.map((stage, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between gap-6 mb-2">
                  <div className="flex items-baseline gap-2 flex-1 min-w-0">
                    <span className="text-sm font-medium text-slate-900">{stage.stage}</span>
                    <span className="text-xs text-slate-500">{stage.time}s</span>
                  </div>
                  <span className="text-sm font-semibold text-slate-900 flex-shrink-0">{stage.success}%</span>
                </div>
                <div className="h-3 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      idx === 0 ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
                      idx === 1 ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                      'bg-gradient-to-r from-orange-500 to-red-500'
                    }`}
                    style={{ width: `${stage.success}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Universe Distribution */}
        <div className="lg:col-span-2 rounded-2xl bg-white p-6 shadow-sm border border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900 mb-6">Universe Distribution</h3>
          <div className="flex items-center gap-8">
            {/* Donut Chart */}
            <div className="relative flex-shrink-0">
              <svg className="w-40 h-40 transform -rotate-90">
                <circle
                  cx="80"
                  cy="80"
                  r="60"
                  fill="none"
                  stroke="#f1f5f9"
                  strokeWidth="20"
                />
                {universeTypes.map((type, idx) => {
                  const colors = ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981']
                  const totalPercentage = universeTypes.slice(0, idx).reduce((sum, t) => sum + t.percentage, 0)
                  const circumference = 2 * Math.PI * 60
                  const offset = (totalPercentage / 100) * circumference
                  const dashArray = `${(type.percentage / 100) * circumference} ${circumference}`

                  return (
                    <circle
                      key={idx}
                      cx="80"
                      cy="80"
                      r="60"
                      fill="none"
                      stroke={colors[idx]}
                      strokeWidth="20"
                      strokeDasharray={dashArray}
                      strokeDashoffset={-offset}
                      className="transition-all duration-300"
                    />
                  )
                })}
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-2xl font-bold text-slate-900">{universeTypes.reduce((sum, t) => sum + t.count, 0)}</p>
                  <p className="text-xs text-slate-500">Total</p>
                </div>
              </div>
            </div>

            {/* Legend */}
            <div className="flex-1 space-y-3">
              {universeTypes.map((type, idx) => {
                const colors = ['bg-blue-500', 'bg-purple-500', 'bg-orange-500', 'bg-emerald-500']
                return (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`h-3 w-3 rounded-full ${colors[idx]}`} />
                      <span className="text-sm font-medium text-slate-700">{type.type}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-slate-900">{type.count}</span>
                      <span className="ml-2 text-xs text-slate-500">{type.percentage}%</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Quick Insights */}
        <div className="space-y-4">
          <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-6 border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="rounded-lg bg-green-500/20 p-2">
                <svg className="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="text-white font-semibold">Top Performer</h4>
            </div>
            <p className="text-sm text-slate-300 mb-2">Parser Engine</p>
            <p className="text-xs text-slate-400">98% success rate with 45s avg time</p>
          </div>

          <div className="rounded-2xl bg-gradient-to-br from-amber-500/10 to-orange-500/10 p-6 border border-amber-500/20">
            <div className="flex items-center gap-3 mb-4">
              <div className="rounded-lg bg-amber-500/20 p-2">
                <svg className="h-5 w-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h4 className="text-slate-900 font-semibold">Needs Attention</h4>
            </div>
            <p className="text-sm text-slate-700 mb-2">Validation Stage</p>
            <p className="text-xs text-slate-600">92% success rate - investigate errors</p>
          </div>
        </div>
      </div>
    </div>
  )
}
