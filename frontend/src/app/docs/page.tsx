import Header from '@/components/landing/Header'

export default function DocsPage() {
  return (
    <>
      <Header />
      <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-800 pt-16">
      <div className="mx-auto max-w-7xl px-6 lg:px-8 py-20 lg:py-24">
        {/* Header */}
        <div className="mb-16 text-center">
          <div className="inline-flex items-center gap-2 rounded-full bg-indigo-500/10 px-4 py-2 text-sm font-medium text-indigo-300 ring-1 ring-inset ring-indigo-500/20 backdrop-blur-sm mb-6">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            Documentation
          </div>
          <h1 className="text-5xl sm:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-white via-white to-slate-400 bg-clip-text text-transparent">
              Help & Documentation
            </span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            Everything you need to know about migrating SAP BusinessObjects universes to modern platforms
          </p>
        </div>

        {/* Content Grid */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {/* Quick Start */}
          <div className="lg:col-span-2 space-y-8">
            {/* Getting Started */}
            <div className="rounded-2xl bg-slate-900/50 p-8 ring-1 ring-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-white">Getting Started</h2>
              </div>
              <div className="space-y-4 text-slate-300">
                <div className="flex gap-3">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 text-sm font-semibold">1</span>
                  <div>
                    <h3 className="font-semibold text-white mb-1">Upload Universe Files</h3>
                    <p className="text-sm">Navigate to the app and upload your .unv or .unx universe files. The system automatically detects universe identity and structure.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 text-sm font-semibold">2</span>
                  <div>
                    <h3 className="font-semibold text-white mb-1">Run Migration</h3>
                    <p className="text-sm">Click "Run Migration" to execute the three-stage pipeline: Parser → Transform → Validation. Average processing time is ~3 minutes per universe.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 text-sm font-semibold">3</span>
                  <div>
                    <h3 className="font-semibold text-white mb-1">Review & Download</h3>
                    <p className="text-sm">Access validation reports, semantic diff analysis, and lineage graphs. Download generated SAC models, Datasphere views, or HANA schemas.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Pipeline Stages */}
            <div className="rounded-2xl bg-slate-900/50 p-8 ring-1 ring-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-white">Migration Pipeline</h2>
              </div>
              <div className="space-y-6">
                <div>
                  <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <span className="text-blue-400">01</span> Parser Engine
                  </h3>
                  <p className="text-sm text-slate-300 mb-2">Converts BusinessObjects universe files (.unv/.unx) into Common Information Model (CIM) format.</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Universe Detection</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Metadata Extraction</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">CIM Generation</span>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <span className="text-green-400">02</span> Transform Engine
                  </h3>
                  <p className="text-sm text-slate-300 mb-2">Generates platform-specific artifacts from CIM: SAC models, Datasphere calculation views, HANA schemas.</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">SAC Model</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Datasphere Views</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">HANA Schema</span>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2 flex items-center gap-2">
                    <span className="text-purple-400">03</span> Validation Engine
                  </h3>
                  <p className="text-sm text-slate-300 mb-2">Performs semantic validation, coverage analysis, and generates data lineage graphs.</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Coverage Report</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Semantic Diff</span>
                    <span className="px-2 py-1 text-xs rounded-md bg-slate-800 text-slate-400">Lineage Graph</span>
                  </div>
                </div>
              </div>
            </div>

            {/* FAQs */}
            <div className="rounded-2xl bg-slate-900/50 p-8 ring-1 ring-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-6">
                <div className="rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 p-3">
                  <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-white">Frequently Asked Questions</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-white mb-2">What file formats are supported?</h3>
                  <p className="text-sm text-slate-300">.unv (Universe files) and .unx (Universe XML) formats from SAP BusinessObjects.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">How long does migration take?</h3>
                  <p className="text-sm text-slate-300">Average processing time is approximately 3 minutes per universe, depending on complexity.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">What platforms are supported?</h3>
                  <p className="text-sm text-slate-300">SAP Analytics Cloud (SAC), SAP Datasphere, and SAP HANA Cloud.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">What is semantic validation?</h3>
                  <p className="text-sm text-slate-300">Automated verification that the migrated artifacts maintain semantic equivalence with the source universe, including field mappings, calculations, and relationships.</p>
                </div>
                <div>
                  <h3 className="font-semibold text-white mb-2">Can I preview before deploying?</h3>
                  <p className="text-sm text-slate-300">Yes, all artifacts can be downloaded and reviewed before deployment to your target system.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Links */}
            <div className="rounded-2xl bg-slate-900/50 p-6 ring-1 ring-white/10 backdrop-blur-sm">
              <h3 className="font-semibold text-white mb-4">Quick Links</h3>
              <div className="space-y-2">
                <a href="/app" className="flex items-center gap-2 text-sm text-slate-300 hover:text-indigo-400 transition-colors">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  Launch Studio
                </a>
                <a href="/#features" className="flex items-center gap-2 text-sm text-slate-300 hover:text-indigo-400 transition-colors">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  Features Overview
                </a>
                <a href="/#pricing" className="flex items-center gap-2 text-sm text-slate-300 hover:text-indigo-400 transition-colors">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                  Pricing
                </a>
              </div>
            </div>

            {/* Support */}
            <div className="rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 p-6 ring-1 ring-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-2 mb-2">
                <svg className="h-5 w-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <h3 className="font-semibold text-white">Need Help?</h3>
              </div>
              <p className="text-sm text-slate-300 mb-4">Our support team is here to assist you with any questions.</p>
              <button className="w-full px-4 py-2 text-sm font-medium rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors">
                Contact Support
              </button>
            </div>

            {/* Stats */}
            <div className="rounded-2xl bg-slate-900/50 p-6 ring-1 ring-white/10 backdrop-blur-sm">
              <h3 className="font-semibold text-white mb-4">Platform Statistics</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Universes Migrated</span>
                  <span className="text-sm font-semibold text-white">10,000+</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Accuracy Rate</span>
                  <span className="text-sm font-semibold text-green-400">99.8%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">Avg. Processing Time</span>
                  <span className="text-sm font-semibold text-white">3.2 min</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    </>
  )
}
