import Link from 'next/link'
import type { UniverseInfo } from '@/lib/types'
import UniverseStatusBadge from './UniverseStatusBadge'

interface UniverseRowProps {
  universe: UniverseInfo
}

export default function UniverseRow({ universe }: UniverseRowProps) {
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
    </tr>
  )
}
