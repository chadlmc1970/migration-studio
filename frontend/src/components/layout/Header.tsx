import Link from 'next/link'

export default function Header() {
  return (
    <header className="h-16 border-b border-slate-200 bg-white px-6">
      <div className="flex h-full items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Universe Migration</h2>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-slate-900"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Back to Home
          </Link>
          <span className="text-sm text-slate-400">|</span>
          <span className="text-sm text-slate-600">Development Mode</span>
        </div>
      </div>
    </header>
  )
}
