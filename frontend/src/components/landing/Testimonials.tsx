export default function Testimonials() {
  const testimonials = [
    {
      content: "Universe Migration Studio reduced our migration timeline from 6 months to 3 weeks. The semantic validation caught issues we would have never found manually.",
      author: "Sarah Chen",
      role: "VP of Analytics",
      company: "Fortune 500 Retail",
      avatar: "SC",
    },
    {
      content: "We migrated 450+ universes with 99.9% semantic accuracy. The lineage tracking alone saved us months of documentation work.",
      author: "Michael Rodriguez",
      role: "Enterprise Architect",
      company: "Global Financial Services",
      avatar: "MR",
    },
    {
      content: "Best investment we made in our SAP modernization journey. The multi-platform output means we can gradually migrate users without disruption.",
      author: "Priya Patel",
      role: "Director of BI",
      company: "Healthcare Technology",
      avatar: "PP",
    },
  ]

  return (
    <section className="relative py-24 sm:py-32 bg-gradient-to-b from-white to-slate-50">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        {/* Section header */}
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-indigo-600">Testimonials</h2>
          <p className="mt-2 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Trusted by enterprise teams
          </p>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            Join hundreds of organizations modernizing their SAP analytics platforms.
          </p>
        </div>

        {/* Testimonial cards */}
        <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 lg:grid-cols-3">
          {testimonials.map((testimonial, idx) => (
            <div
              key={idx}
              className="relative rounded-2xl border border-slate-200 bg-white p-8 shadow-sm hover:shadow-lg transition-all"
            >
              {/* Quote icon */}
              <div className="mb-6">
                <svg className="h-8 w-8 text-indigo-500/20" fill="currentColor" viewBox="0 0 32 32">
                  <path d="M9.352 4C4.456 7.456 1 13.12 1 19.36c0 5.088 3.072 8.064 6.624 8.064 3.36 0 5.856-2.688 5.856-5.856 0-3.168-2.208-5.472-5.088-5.472-.576 0-1.344.096-1.536.192.48-3.264 3.552-7.104 6.624-9.024L9.352 4zm16.512 0c-4.8 3.456-8.256 9.12-8.256 15.36 0 5.088 3.072 8.064 6.624 8.064 3.264 0 5.856-2.688 5.856-5.856 0-3.168-2.304-5.472-5.184-5.472-.576 0-1.248.096-1.44.192.48-3.264 3.456-7.104 6.528-9.024L25.864 4z" />
                </svg>
              </div>

              {/* Content */}
              <p className="text-base leading-7 text-slate-700">{testimonial.content}</p>

              {/* Author */}
              <div className="mt-6 flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-semibold text-white">
                  {testimonial.avatar}
                </div>
                <div>
                  <div className="font-semibold text-slate-900">{testimonial.author}</div>
                  <div className="text-sm text-slate-600">
                    {testimonial.role}, {testimonial.company}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Logos */}
        <div className="mt-20">
          <p className="text-center text-sm font-semibold text-slate-500 uppercase tracking-wide">
            Trusted by leading enterprises
          </p>
          <div className="mt-8 grid grid-cols-2 gap-8 md:grid-cols-4 lg:grid-cols-6 items-center justify-items-center opacity-50">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="flex items-center justify-center">
                <div className="h-12 w-32 rounded bg-slate-200/50" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
