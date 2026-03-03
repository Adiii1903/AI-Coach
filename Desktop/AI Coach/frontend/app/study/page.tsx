"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { studyService, CreateStudySessionPayload } from "@/services/studyService";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/StatCard";
import { formatHours } from "@/lib/utils";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import { Plus, Trash2, BookOpen, Clock, TrendingUp, X } from "lucide-react";

export default function StudyPage() {
    const qc = useQueryClient();
    const [showForm, setShowForm] = useState(false);
    const [subject, setSubject] = useState("");
    const [topic, setTopic] = useState("");
    const [duration, setDuration] = useState("60");
    const [notes, setNotes] = useState("");

    const { data: sessions = [], isLoading } = useQuery({ queryKey: ["study-sessions"], queryFn: studyService.getAll });
    const { data: stats } = useQuery({ queryKey: ["study-stats"], queryFn: studyService.getStats });

    const createMut = useMutation({
        mutationFn: (p: CreateStudySessionPayload) => studyService.create(p),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["study-sessions"] });
            qc.invalidateQueries({ queryKey: ["study-stats"] });
            setSubject(""); setTopic(""); setDuration("60"); setNotes(""); setShowForm(false);
        },
    });

    const deleteMut = useMutation({
        mutationFn: (id: string) => studyService.delete(id),
        onSuccess: () => { qc.invalidateQueries({ queryKey: ["study-sessions"] }); qc.invalidateQueries({ queryKey: ["study-stats"] }); },
    });

    // Last 10 sessions for bar chart (reversed to show oldest → newest)
    const chartData = [...sessions].slice(0, 10).reverse().map((s, i) => ({
        name: s.subject.length > 8 ? s.subject.substring(0, 7) + "…" : s.subject,
        minutes: s.duration_minutes,
    }));

    return (
        <AppLayout>
            {/* Stats row */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <StatCard label="Total Study Time" value={stats ? formatHours(stats.total_minutes) : "—"} icon={<TrendingUp size={14} />} />
                <StatCard label="Today" value={stats ? formatHours(stats.today_minutes) : "—"} icon={<Clock size={14} />} iconColor="var(--emerald)" iconBg="var(--emerald-dim)" />
                <StatCard label="This Week" value={stats ? formatHours(stats.weekly_minutes) : "—"} icon={<BookOpen size={14} />} iconColor="var(--amber)" iconBg="var(--amber-dim)" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Left: Form + List */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex justify-end">
                        <Button onClick={() => setShowForm(!showForm)} icon={<Plus size={13} />}>Log session</Button>
                    </div>

                    {/* Create form */}
                    <AnimatePresence>
                        {showForm && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}>
                                <Card padding="lg">
                                    <div className="flex items-center justify-between mb-4">
                                        <p className="text-sm font-semibold" style={{ color: "var(--t1)" }}>Log study session</p>
                                        <button onClick={() => setShowForm(false)} className="btn btn-ghost btn-icon"><X size={13} /></button>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="grid grid-cols-2 gap-3">
                                            <input className="inp" placeholder="Subject *" value={subject} onChange={e => setSubject(e.target.value)} />
                                            <input className="inp" placeholder="Topic (optional)" value={topic} onChange={e => setTopic(e.target.value)} />
                                        </div>
                                        <input className="inp" type="number" placeholder="Duration (minutes)" value={duration} onChange={e => setDuration(e.target.value)} min="1" />
                                        <textarea className="inp" rows={2} placeholder="Notes (optional)" value={notes} onChange={e => setNotes(e.target.value)} style={{ resize: "none" }} />
                                        <Button
                                            onClick={() => subject && createMut.mutate({ subject, topic: topic || undefined, duration_minutes: parseInt(duration) || 60, notes: notes || undefined })}
                                            disabled={!subject} loading={createMut.isPending}>
                                            Save session
                                        </Button>
                                    </div>
                                </Card>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Session list */}
                    <Card padding="none">
                        {isLoading && <div className="empty-state"><p>Loading…</p></div>}
                        <AnimatePresence mode="popLayout">
                            {sessions.map((s, idx) => (
                                <motion.div
                                    key={s.id} layout
                                    initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -16 }}
                                    className="flex items-center gap-3 px-5 py-3.5 group"
                                    style={{ borderBottom: idx < sessions.length - 1 ? "1px solid var(--border)" : "none" }}>
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                                        style={{ background: "var(--emerald-dim)" }}>
                                        <BookOpen size={13} style={{ color: "var(--emerald)" }} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium truncate" style={{ color: "var(--t1)" }}>{s.subject}</p>
                                        {s.topic && <p className="text-xs truncate" style={{ color: "var(--t3)" }}>{s.topic}</p>}
                                    </div>
                                    <div className="text-right flex-shrink-0">
                                        <p className="text-sm font-semibold" style={{ color: "var(--emerald)" }}>{s.duration_minutes}m</p>
                                        <p className="text-xs" style={{ color: "var(--t3)" }}>{new Date(s.session_date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</p>
                                    </div>
                                    <button onClick={() => deleteMut.mutate(s.id)}
                                        className="btn btn-ghost btn-icon opacity-0 group-hover:opacity-100 transition-opacity"
                                        style={{ color: "var(--rose)" }}>
                                        <Trash2 size={12} />
                                    </button>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        {!isLoading && sessions.length === 0 && (
                            <div className="empty-state">
                                <BookOpen size={28} style={{ color: "var(--t4)" }} />
                                <p className="text-sm">No sessions yet</p>
                                <Button size="sm" onClick={() => setShowForm(true)} icon={<Plus size={12} />}>Log your first session</Button>
                            </div>
                        )}
                    </Card>
                </div>

                {/* Right: Chart */}
                <div className="space-y-4">
                    <Card padding="lg">
                        <CardHeader>
                            <CardTitle>Session History</CardTitle>
                        </CardHeader>
                        {sessions.length > 0 ? (
                            <ResponsiveContainer width="100%" height={220}>
                                <BarChart data={chartData} barSize={20} margin={{ left: -20 }}>
                                    <CartesianGrid vertical={false} stroke="var(--border)" />
                                    <XAxis dataKey="name" tick={{ fill: "var(--t3)", fontSize: 10 }} axisLine={false} tickLine={false} />
                                    <YAxis tick={{ fill: "var(--t3)", fontSize: 10 }} axisLine={false} tickLine={false} />
                                    <Tooltip
                                        cursor={{ fill: "rgba(16,185,129,0.06)" }}
                                        contentStyle={{ background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                                        formatter={(v: any) => [`${v}m`, "Duration"]}
                                    />
                                    <Bar dataKey="minutes" fill="var(--emerald)" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="empty-state py-8">
                                <p className="text-xs">Chart appears after sessions are logged</p>
                            </div>
                        )}
                    </Card>
                </div>
            </div>
        </AppLayout>
    );
}
