import Link from 'next/link'
import type { UniverseInfo } from '@/lib/types'
import UniverseStatusBadge from './UniverseStatusBadge'

interface UniverseRowProps {
  universe: UniverseInfo
  onDelete: (universeId: string) => void
  isDeleting: boolean
}

export default function UniverseRow({ universe, onDelete, isDeleting }: UniverseRowProps) {
  return (
    <tr className="hover:bg-slate-50">
      <td className="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium text-slate-900">
        <Link href={`/app/universes/${universe.id}`} className="hover:text-blue-600">
          {universe.id}
        </Link>
      </td>
      <td className="whitespace-nowrap px-3 py-4 text-sm">
        <UniverseStatusBadge status={universe.parsed} label="Parsed" />
      </td>
      <td className="whitespace-nowrap px-3 py-4 text-sm">
        <UniverseStatusBadge status={universe.transformed} label="Transformed" />
      </td>
      <td className="whitespace-nowrap px-3 py-4 text-sm">
        <UniverseStatusBadge status={universe.validated} label="Validated" />
      </td>
      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-600">
        {universe.coverage ? `${Math.round(universe.coverage * 100)}%` : '-'}
      </td>
      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-600">
        {universe.last_updated || '-'}
      </td>
      <td className="relative whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm">
        <button
          onClick={() => onDelete(universe.id)}
          disabled={isDeleting}
          className="text-slate-400 hover:text-red-600 disabled:opacity-50 transition-colors"
          title="Delete universe and all files"
        >
          {isDeleting ? (
            <svg className="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          )}
        </button>
      </td>
    </tr>
  )
}
