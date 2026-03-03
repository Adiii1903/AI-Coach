import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#0f0f1a] flex flex-col items-center justify-center px-6 text-center">
      {/* Glow effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 max-w-2xl">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 bg-indigo-600/10 border border-indigo-500/30 rounded-full px-4 py-1.5 mb-6 text-sm text-indigo-400 font-medium">
          <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse" />
          AI-Powered Productivity
        </div>

        {/* Heading */}
        <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-4">
          AI Student
          <span className="block bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Dashboard
          </span>
        </h1>

        {/* Description */}
        <p className="text-lg text-slate-400 mb-10 max-w-xl mx-auto leading-relaxed">
          Your personal AI mentor for academic success. Track study sessions,
          manage habits, and receive intelligent coaching — all in one place.
        </p>

        {/* Features row */}
        <div className="flex flex-wrap justify-center gap-4 mb-10 text-sm text-slate-500">
          {["📚 Study Tracker", "✅ Task Manager", "🔥 Habit Streaks", "🤖 AI Coach"].map(
            (f) => (
              <span
                key={f}
                className="bg-white/5 border border-white/10 rounded-full px-4 py-1.5"
              >
                {f}
              </span>
            )
          )}
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signup"
            className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-indigo-900/50 hover:shadow-indigo-800/50"
          >
            Get Started Free
          </Link>
          <Link
            href="/login"
            className="px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold rounded-xl transition-all duration-200"
          >
            Log In
          </Link>
        </div>
      </div>
    </main>
  );
}
