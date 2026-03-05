export default function Features() {
  const features = [
    {
      name: 'AI-Powered Intelligence',
      description: 'Claude analyzes every migration, optimizing queries up to 40%, refining schemas, and eliminating technical debt automatically.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      gradient: 'from-purple-400 to-indigo-500',
      bgGradient: 'from-purple-500/10 to-indigo-500/10',
      featured: true,
    },
    {
      name: 'Lightning Fast',
      description: 'Convert universes in minutes, not days. Automated parsing and transformation pipeline.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      gradient: 'from-yellow-400 to-orange-500',
      bgGradient: 'from-yellow-500/10 to-orange-500/10',
    },
    {
      name: 'Multi-Platform',
      description: 'Single click generates SAP Analytics Cloud, Datasphere, and HANA artifacts simultaneously.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
        </svg>
      ),
      gradient: 'from-blue-400 to-indigo-500',
      bgGradient: 'from-blue-500/10 to-indigo-500/10',
    },
    {
      name: 'Semantic Validation',
      description: 'Comprehensive quality checks ensure 100% semantic fidelity with full lineage tracking.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      ),
      gradient: 'from-emerald-400 to-green-500',
      bgGradient: 'from-emerald-500/10 to-green-500/10',
    },
    {
      name: 'Enterprise Scale',
      description: 'Handle thousands of universes with parallel processing and intelligent caching.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      ),
      gradient: 'from-cyan-400 to-blue-500',
      bgGradient: 'from-cyan-500/10 to-blue-500/10',
    },
    {
      name: 'Full Visibility',
      description: 'Real-time dashboards, detailed reports, and interactive lineage graphs for every migration.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      gradient: 'from-cyan-400 to-blue-500',
      bgGradient: 'from-cyan-500/10 to-blue-500/10',
    },
    {
      name: 'Zero Lock-in',
      description: 'Export to standard formats. Your data, your control. No proprietary dependencies.',
      icon: (
        <svg className="h-7 w-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
        </svg>
      ),
      gradient: 'from-rose-400 to-red-500',
      bgGradient: 'from-rose-500/10 to-red-500/10',
    },
  ]

  return (
    <section className="relative py-24 sm:py-32 bg-gradient-to-b from-white via-slate-50 to-white">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]" />

      <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">Everything you need</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Built for modern analytics teams
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Enterprise-grade migration platform with all the features you need to modernize your SAP landscape.
          </p>
        </div>

        {/* Feature grid */}
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <div
              key={feature.name}
              className={`group relative rounded-2xl border ${
                feature.featured
                  ? 'border-purple-300 ring-2 ring-purple-500/20'
                  : 'border-slate-200'
              } bg-white p-8 shadow-sm transition-all hover:shadow-xl hover:border-slate-300`}
            >
              {/* Featured badge */}
              {feature.featured && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1 rounded-full bg-gradient-to-r from-purple-500 to-indigo-500 px-3 py-1 text-xs font-semibold text-white shadow-lg">
                    <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    AI Powered
                  </span>
                </div>
              )}

              {/* Gradient background on hover */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.bgGradient} opacity-0 transition-opacity group-hover:opacity-100`} />

              {/* Content */}
              <div className="relative">
                <div className={`inline-flex rounded-xl bg-gradient-to-br ${feature.gradient} p-3 shadow-lg`}>
                  <div className="text-white">{feature.icon}</div>
                </div>
                <h3 className="mt-6 text-xl font-semibold text-slate-900 group-hover:text-slate-900">
                  {feature.name}
                </h3>
                <p className="mt-3 text-base leading-7 text-slate-600 group-hover:text-slate-700">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Stats section */}
        <div className="mx-auto mt-20 max-w-5xl">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                10k+
              </div>
              <div className="mt-2 text-sm font-medium text-slate-600">Universes Migrated</div>
            </div>
            <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">
                99.8%
              </div>
              <div className="mt-2 text-sm font-medium text-slate-600">Semantic Accuracy</div>
            </div>
            <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                85%
              </div>
              <div className="mt-2 text-sm font-medium text-slate-600">Time Savings</div>
            </div>
            <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <div className="text-4xl font-bold bg-gradient-to-r from-rose-600 to-red-600 bg-clip-text text-transparent">
                24/7
              </div>
              <div className="mt-2 text-sm font-medium text-slate-600">Expert Support</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
