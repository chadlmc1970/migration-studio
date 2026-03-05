import Link from 'next/link'

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-slate-800 pt-16">
      {/* Animated gradient background */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(45rem_50rem_at_top,theme(colors.indigo.500/20),transparent)]" />
      <div className="absolute inset-y-0 right-1/2 -z-10 mr-16 w-[200%] origin-bottom-left skew-x-[-30deg] bg-white/[0.02] shadow-xl shadow-indigo-600/10 ring-1 ring-indigo-50/5 sm:mr-28 lg:mr-0 xl:mr-16 xl:origin-center" />

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-b from-transparent to-slate-800/50 pointer-events-none" />

      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="grid lg:grid-cols-[1fr_1.1fr] gap-20 xl:gap-24 items-center min-h-[85vh] py-16 lg:py-20">
          {/* Left: Content */}
          <div className="relative z-10 max-w-xl">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-purple-500/10 to-indigo-500/10 px-3 py-1 text-xs font-medium text-purple-300 ring-1 ring-inset ring-purple-500/20 backdrop-blur-sm mb-6">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-purple-500"></span>
              </span>
              AI-Powered SAP Analytics Modernization
            </div>

            {/* Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-6xl xl:text-7xl font-bold tracking-tight mb-8">
              <span className="bg-gradient-to-r from-white via-white to-slate-400 bg-clip-text text-transparent">
                Migrate
              </span>
              <br />
              <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                BusinessObjects
              </span>
              <br />
              <span className="text-white text-3xl sm:text-4xl lg:text-5xl xl:text-6xl">to Modern SAP</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-slate-300 mb-4 max-w-lg leading-relaxed">
              Automated universe conversion to SAC, Datasphere, and HANA with semantic validation. Minutes, not months.
            </p>

            {/* AI Value Prop */}
            <div className="mb-10 rounded-xl bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-blue-500/10 p-4 ring-1 ring-purple-500/20 backdrop-blur-sm">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  <svg className="h-5 w-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-200 mb-1">Claude AI Enhancements</p>
                  <p className="text-xs text-slate-400">
                    Every migration is analyzed and optimized by Claude - improving query performance up to 40%, refining schemas, and eliminating technical debt automatically.
                  </p>
                </div>
              </div>
            </div>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 mb-10">
              <Link
                href="/app"
                className="group inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 px-8 py-4 text-base font-semibold text-white shadow-lg shadow-indigo-500/50 transition-all hover:shadow-xl hover:shadow-indigo-500/60 hover:scale-105"
              >
                <span>Launch Studio</span>
                <svg className="h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <button className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/50 px-6 py-4 text-base font-semibold text-slate-200 backdrop-blur-sm transition-all hover:bg-slate-800 hover:border-slate-600">
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Watch Demo
              </button>
            </div>

            {/* Stats */}
            <div className="flex flex-wrap items-center gap-6 lg:gap-8 text-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>10k+ Universes</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>99.8% Accuracy</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <svg className="h-4 w-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Enterprise Ready</span>
              </div>
            </div>
          </div>

          {/* Right: Visual Pipeline - Bento Grid */}
          <div className="relative lg:h-full flex items-center">
            <div className="grid grid-cols-2 gap-4 w-full">
              {/* Upload - Large card */}
              <div className="group relative col-span-2">
                <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-600 opacity-25 blur transition duration-500 group-hover:opacity-50" />
                <div className="relative rounded-2xl bg-slate-900 p-6 ring-1 ring-white/10 transition-all hover:scale-105">
                  <div className="flex items-center gap-4">
                    <div className="inline-flex rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 p-3">
                      <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white">Upload</h3>
                      <p className="text-sm text-slate-400 mt-1">.unv / .unx universe files</p>
                    </div>
                    <div className="text-3xl font-bold text-slate-700">01</div>
                  </div>
                </div>
              </div>

              {/* Transform - Medium card */}
              <div className="group relative">
                <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-emerald-600 to-green-600 opacity-25 blur transition duration-500 group-hover:opacity-50" />
                <div className="relative rounded-2xl bg-slate-900 p-6 ring-1 ring-white/10 transition-all hover:scale-105 h-full">
                  <div className="flex flex-col h-full justify-between">
                    <div className="inline-flex rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 p-3 self-start">
                      <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">Transform</h3>
                      <p className="text-xs text-slate-400 mt-1">SAC/DS/HANA</p>
                      <div className="text-2xl font-bold text-slate-700 mt-2">02</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Validate - Medium card */}
              <div className="group relative">
                <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 opacity-25 blur transition duration-500 group-hover:opacity-50" />
                <div className="relative rounded-2xl bg-slate-900 p-6 ring-1 ring-white/10 transition-all hover:scale-105 h-full">
                  <div className="flex flex-col h-full justify-between">
                    <div className="inline-flex rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 p-3 self-start">
                      <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">Validate</h3>
                      <p className="text-xs text-slate-400 mt-1">Semantic checks</p>
                      <div className="text-2xl font-bold text-slate-700 mt-2">03</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Results - Full width status bar */}
              <div className="col-span-2 rounded-2xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 p-4 ring-1 ring-white/10 backdrop-blur-sm">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-slate-300">
                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                    <span className="font-medium">Migration Complete</span>
                  </div>
                  <div className="text-xs text-slate-500">3.2 minutes</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Platform Capabilities Bar - Integrated */}
        <div className="relative -mt-8 lg:-mt-12 pb-16 lg:pb-20">
          <div className="relative group">
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 opacity-15 blur-xl transition duration-500 group-hover:opacity-25" />
            <div className="relative rounded-2xl bg-slate-900/70 backdrop-blur-xl ring-1 ring-white/10 shadow-2xl border border-white/5">
              <div className="px-6 py-5 lg:px-10 lg:py-6">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  {/* Platform Support */}
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-slate-500">Platform Support</div>
                      <div className="text-sm font-semibold text-white">SAC · DS · HANA</div>
                    </div>
                  </div>

                  {/* Processing Speed */}
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-green-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-slate-500">Processing</div>
                      <div className="text-sm font-semibold text-white">~3 min average</div>
                    </div>
                  </div>

                  {/* Validation Coverage */}
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-slate-500">Validation</div>
                      <div className="text-sm font-semibold text-white">99.8% accurate</div>
                    </div>
                  </div>

                  {/* Format Support */}
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-xs font-medium text-slate-500">File Support</div>
                      <div className="text-sm font-semibold text-white">.unv · .unx</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Color Extension Gradient Below */}
          <div className="absolute bottom-0 left-0 right-0 h-32 pointer-events-none">
            <div className="h-full bg-gradient-to-b from-indigo-600/20 via-purple-600/10 to-transparent blur-2xl" />
          </div>
        </div>
      </div>
    </section>
  )
}
