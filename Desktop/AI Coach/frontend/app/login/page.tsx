"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { authService } from "@/services/authService";
import { Button } from "@/components/ui/Button";
import { TrendingUp, Mail, Lock, Eye, EyeOff, Bot } from "lucide-react";

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPwd, setShowPwd] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            const data: any = await authService.login(email, password);
            const token = data?.data?.access_token ?? data?.access_token;
            if (token) {
                localStorage.setItem("access_token", token);
                router.push("/dashboard");
            } else {
                setError("Unexpected response. Please try again.");
            }
        } catch (err: any) {
            setError(err?.response?.data?.detail ?? "Login failed. Check your credentials.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex" style={{ background: "var(--bg)" }}>
            {/* Left branding panel */}
            <div className="hidden lg:flex lg:w-1/2 flex-col justify-between p-12"
                style={{ background: "var(--surface)", borderRight: "1px solid var(--border)" }}>
                <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)" }}>
                        <Bot size={16} color="white" />
                    </div>
                    <span className="font-bold text-sm" style={{ color: "var(--t1)" }}>AI Coach</span>
                </div>

                <div>
                    <h2 className="text-3xl font-bold leading-tight mb-4" style={{ color: "var(--t1)" }}>
                        Your AI-powered<br />productivity coach
                    </h2>
                    <p className="text-sm leading-relaxed mb-8" style={{ color: "var(--t3)" }}>
                        Track tasks, habits, and study sessions. Get personalized AI advice to stay productive every day.
                    </p>
                    <div className="grid grid-cols-3 gap-4">
                        {[
                            { v: "Tasks", l: "Completed" },
                            { v: "Habits", l: "Tracked" },
                            { v: "AI", l: "Insights" },
                        ].map(({ v, l }) => (
                            <div key={l} className="card p-4 text-center">
                                <p className="font-bold text-sm" style={{ color: "var(--indigo)" }}>{v}</p>
                                <p className="text-xs mt-0.5" style={{ color: "var(--t3)" }}>{l}</p>
                            </div>
                        ))}
                    </div>
                </div>

                <p className="text-xs" style={{ color: "var(--t3)" }}>© 2026 AI Coach. All rights reserved.</p>
            </div>

            {/* Right login panel */}
            <div className="flex-1 flex items-center justify-center px-6 py-12">
                <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="w-full max-w-sm">

                    <div className="mb-8">
                        <h1 className="text-2xl font-bold" style={{ color: "var(--t1)" }}>Sign in</h1>
                        <p className="text-sm mt-1" style={{ color: "var(--t3)" }}>Welcome back to your dashboard</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--t2)" }}>Email</label>
                            <div className="relative">
                                <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--t3)" }} />
                                <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                                    placeholder="you@example.com" required className="inp pl-9" />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium mb-1.5" style={{ color: "var(--t2)" }}>Password</label>
                            <div className="relative">
                                <Lock size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--t3)" }} />
                                <input type={showPwd ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)}
                                    placeholder="••••••••" required className="inp pl-9 pr-9" />
                                <button type="button" onClick={() => setShowPwd(!showPwd)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2" style={{ color: "var(--t3)" }}>
                                    {showPwd ? <EyeOff size={14} /> : <Eye size={14} />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="rounded-lg px-3 py-2.5 text-xs" style={{ background: "var(--rose-dim)", color: "var(--rose)", border: "1px solid rgba(244,63,94,0.2)" }}>
                                {error}
                            </div>
                        )}

                        <Button type="submit" loading={loading} className="w-full" size="lg">
                            {loading ? "Signing in…" : "Sign in"}
                        </Button>
                    </form>

                    <p className="text-center text-xs mt-6" style={{ color: "var(--t3)" }}>
                        Don&apos;t have an account?{" "}
                        <a href="/signup" style={{ color: "var(--indigo)" }} className="font-medium hover:underline">Create one</a>
                    </p>
                </motion.div>
            </div>
        </div>
    );
}
