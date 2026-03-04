import type { UniverseInfo } from '@/lib/types'
import UniverseRow from './UniverseRow'

interface UniverseTableProps {
  universes: UniverseInfo[]
}

export default function UniverseTable({ universes }: UniverseTableProps) {
  if (universes.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-12 text-center">
        <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <h3 className="mt-4 text-sm font-medium text-slate-900">No universes found</h3>
        <p className="mt-2 text-sm text-slate-500">Upload a universe file to get started</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th scope="col" className="py-3.5 pl-6 pr-3 text-left text-sm font-semibold text-slate-900">
              Universe ID
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
              Parsed
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
              Transformed
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
              Validated
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
              Coverage
            </th>
            <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">
              Last Updated
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white">
          {universes.map((universe) => (
            <UniverseRow key={universe.id} universe={universe} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
