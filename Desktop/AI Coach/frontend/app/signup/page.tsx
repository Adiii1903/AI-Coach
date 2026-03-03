"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { authService } from "@/services/authService";
import { Bot, User, Mail, Lock } from "lucide-react";

export default function SignupPage() {
    const router = useRouter();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setLoading(true);
        setError("");
        try {
            await authService.signup(name, email, password);
            const data = await authService.login(email, password);
            const token = (data as any).data?.access_token ?? (data as any).access_token;
            if (token) {
                localStorage.setItem("access_token", token);
                router.push("/dashboard");
            }
        } catch (err: any) {
            setError(err?.response?.data?.detail ?? "Signup failed. Try again.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center px-4"
            style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(99,102,241,0.1) 0%, var(--background) 60%)" }}>
            <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="w-full max-w-md">
                <div className="text-center mb-8">
                    <div className="w-14 h-14 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                        style={{ background: "linear-gradient(135deg, #6366f1, #8b5cf6)" }}>
                        <Bot size={28} color="white" />
                    </div>
                    <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>Create your account</h1>
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>Start your AI-powered productivity journey</p>
                </div>

                <div className="glass p-8 glow-indigo">
                    <form onSubmit={handleSubmit} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Name</label>
                            <div className="relative">
                                <User size={16} className="absolute left-3 top-3.5" style={{ color: "var(--text-muted)" }} />
                                <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Your name" required className="input pl-10" />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Email</label>
                            <div className="relative">
                                <Mail size={16} className="absolute left-3 top-3.5" style={{ color: "var(--text-muted)" }} />
                                <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required className="input pl-10" />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Password</label>
                            <div className="relative">
                                <Lock size={16} className="absolute left-3 top-3.5" style={{ color: "var(--text-muted)" }} />
                                <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required className="input pl-10" />
                            </div>
                        </div>
                        {error && (
                            <div className="rounded-xl p-3 text-sm" style={{ background: "rgba(239,68,68,0.1)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.2)" }}>
                                {error}
                            </div>
                        )}
                        <motion.button type="submit" whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }} disabled={loading} className="btn-primary w-full">
                            {loading ? "Creating account…" : "Create account →"}
                        </motion.button>
                    </form>
                    <p className="text-center text-sm mt-6" style={{ color: "var(--text-muted)" }}>
                        Already have an account?{" "}
                        <a href="/login" style={{ color: "var(--accent)" }} className="hover:underline">Sign in</a>
                    </p>
                </div>
            </motion.div>
        </div>
    );
}
