"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function LoginForm() {
    const { login, loading, error } = useAuth();
    const [form, setForm] = useState({ email: "", password: "" });
    const searchParams = useSearchParams();
    const registered = searchParams.get("registered") === "true";

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        login(form);
    };

    return (
        <main className="min-h-screen bg-[#0f0f1a] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-8 shadow-2xl backdrop-blur-sm">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
                        <p className="text-slate-400 text-sm">Log in to your AI Student Dashboard</p>
                    </div>

                    {/* Registration success */}
                    {registered && (
                        <div className="mb-5 bg-green-500/10 border border-green-500/30 rounded-lg p-3 text-sm text-green-400">
                            Account created successfully! Please log in.
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div className="mb-5 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-sm text-red-400">
                            {error}
                        </div>
                    )}

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1.5" htmlFor="email">
                                Email Address
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                placeholder="john@university.edu"
                                value={form.email}
                                onChange={(e) => setForm({ ...form, email: e.target.value })}
                                className="w-full bg-white/5 border border-white/10 focus:border-indigo-500 rounded-xl px-4 py-3 text-white placeholder:text-slate-600 outline-none transition-colors"
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-slate-400 mb-1.5" htmlFor="password">
                                Password
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                placeholder="Your password"
                                value={form.password}
                                onChange={(e) => setForm({ ...form, password: e.target.value })}
                                className="w-full bg-white/5 border border-white/10 focus:border-indigo-500 rounded-xl px-4 py-3 text-white placeholder:text-slate-600 outline-none transition-colors"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-all duration-200 shadow-lg shadow-indigo-900/40"
                        >
                            {loading ? "Signing In..." : "Sign In"}
                        </button>
                    </form>

                    {/* Footer */}
                    <p className="text-center text-sm text-slate-500 mt-6">
                        Don&apos;t have an account?{" "}
                        <Link href="/signup" className="text-indigo-400 hover:text-indigo-300 font-medium">
                            Sign up free
                        </Link>
                    </p>
                </div>
            </div>
        </main>
    );
}
