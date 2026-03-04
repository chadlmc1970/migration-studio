import type { EventEntry } from '@/lib/types'

interface EventFeedProps {
  events: EventEntry[]
}

export default function EventFeed({ events }: EventFeedProps) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 shadow-xl border border-slate-700 overflow-hidden">
      <div className="border-b border-slate-700 px-6 py-5 bg-slate-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-indigo-500/20 p-2">
              <svg className="h-5 w-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-white">Recent Events</h3>
          </div>
          <span className="text-sm text-slate-400">{events.length} events</span>
        </div>
      </div>
      <div className="divide-y divide-slate-700/50">
        {events.length === 0 ? (
          <div className="px-6 py-12 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-4">
              <svg className="h-8 w-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <p className="text-sm text-slate-400 font-medium">No events yet</p>
            <p className="text-xs text-slate-500 mt-1">Events will appear here as migrations are processed</p>
          </div>
        ) : (
          events.map((event, idx) => (
            <div key={idx} className="px-6 py-4 hover:bg-slate-800/50 transition-colors group">
              <div className="flex items-start gap-4">
                <div className={`flex-shrink-0 w-2 h-2 rounded-full mt-1.5 ${
                  event.level === 'ERROR' ? 'bg-red-400' :
                  event.level === 'WARNING' ? 'bg-yellow-400' :
                  'bg-green-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm font-medium text-white group-hover:text-indigo-300 transition-colors">
                        {event.message}
                      </p>
                      {event.universe_id && (
                        <p className="mt-1 text-xs text-slate-400">
                          Universe: <span className="font-mono text-indigo-400">{event.universe_id}</span>
                        </p>
                      )}
                      <p className="mt-1 text-xs text-slate-500">{event.timestamp}</p>
                    </div>
                    <span className={`flex-shrink-0 inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium ${
                      event.level === 'ERROR' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                      event.level === 'WARNING' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
                      'bg-green-500/20 text-green-300 border border-green-500/30'
                    }`}>
                      <div className={`w-1.5 h-1.5 rounded-full ${
                        event.level === 'ERROR' ? 'bg-red-400' :
                        event.level === 'WARNING' ? 'bg-yellow-400' :
                        'bg-green-400'
                      }`} />
                      {event.level}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
