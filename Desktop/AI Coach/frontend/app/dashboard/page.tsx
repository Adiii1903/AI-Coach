"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { User } from "@/types/auth";

export default function DashboardPage() {
    const { logout, getProfile } = useAuth();
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        getProfile().then(setUser);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return (
        <main className="min-h-screen bg-[#0f0f1a] text-white">
            {/* Navbar */}
            <nav className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-sm font-bold">
                        AI
                    </div>
                    <span className="font-semibold text-white">AI Student Dashboard</span>
                </div>
                <button
                    onClick={logout}
                    className="text-sm text-slate-400 hover:text-white transition-colors px-4 py-2 bg-white/5 rounded-lg border border-white/10"
                >
                    Log Out
                </button>
            </nav>

            {/* Content */}
            <div className="max-w-5xl mx-auto px-6 py-12">
                {/* Welcome */}
                <div className="mb-10">
                    <h1 className="text-4xl font-bold text-white mb-2">
                        Welcome back{user ? `, ${user.name.split(" ")[0]}` : ""}! 👋
                    </h1>
                    <p className="text-slate-400">
                        Your AI-powered productivity hub. More features coming in Phase 2.
                    </p>
                </div>

                {/* Placeholder cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
                    {[
                        { label: "Productivity Score", value: "—", icon: "🏆", color: "indigo" },
                        { label: "Tasks Today", value: "—", icon: "✅", color: "purple" },
                        { label: "Study Hours", value: "—", icon: "📚", color: "blue" },
                        { label: "Habit Streak", value: "—", icon: "🔥", color: "orange" },
                    ].map((card) => (
                        <div
                            key={card.label}
                            className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:bg-white/8 transition-colors"
                        >
                            <div className="text-2xl mb-3">{card.icon}</div>
                            <div className="text-2xl font-bold text-white mb-1">{card.value}</div>
                            <div className="text-sm text-slate-500">{card.label}</div>
                        </div>
                    ))}
                </div>

                {/* AI Coach placeholder */}
                <div className="bg-gradient-to-br from-indigo-900/40 to-purple-900/40 border border-indigo-500/20 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center text-lg">
                            🤖
                        </div>
                        <div>
                            <h2 className="font-semibold text-white">AI Coach</h2>
                            <p className="text-xs text-indigo-400">Your personal mentor</p>
                        </div>
                    </div>
                    <p className="text-slate-400 text-sm italic">
                        &quot;Your AI Coach will analyze your habits and study sessions to provide personalized advice. Complete your profile and start logging sessions to unlock insights.&quot;
                    </p>
                </div>

                {user && (
                    <div className="mt-8 text-xs text-slate-600 text-center">
                        Logged in as <span className="text-slate-500">{user.email}</span> · Member since{" "}
                        {new Date(user.created_at).toLocaleDateString()}
                    </div>
                )}
            </div>
        </main>
    );
}
