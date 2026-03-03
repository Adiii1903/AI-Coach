"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { habitService } from "@/services/habitService";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatCard } from "@/components/ui/StatCard";
import { Plus, Trash2, Flame, CheckCircle2, X, Zap } from "lucide-react";

export default function HabitsPage() {
    const qc = useQueryClient();
    const [showForm, setShowForm] = useState(false);
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [justLogged, setJustLogged] = useState<Set<string>>(new Set());

    const { data: habits = [], isLoading } = useQuery({ queryKey: ["habits"], queryFn: habitService.getAll });

    const createMut = useMutation({
        mutationFn: () => habitService.create({ name, description: description || undefined }),
        onSuccess: () => { qc.invalidateQueries({ queryKey: ["habits"] }); setName(""); setDescription(""); setShowForm(false); },
    });

    const logMut = useMutation({
        mutationFn: (id: string) => habitService.log(id),
        onSuccess: (_, id) => {
            qc.invalidateQueries({ queryKey: ["habits"] });
            setJustLogged(prev => new Set(prev).add(id));
            setTimeout(() => setJustLogged(prev => { const s = new Set(prev); s.delete(id); return s; }), 2000);
        },
    });

    const deleteMut = useMutation({
        mutationFn: (id: string) => habitService.delete(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["habits"] }),
    });

    const totalStreak = habits.reduce((s, h) => s + h.current_streak, 0);
    const maxStreak = habits.reduce((m, h) => Math.max(m, h.longest_streak), 0);

    return (
        <AppLayout>
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <StatCard label="Active Habits" value={habits.length} icon={<Flame size={14} />} iconColor="var(--amber)" iconBg="var(--amber-dim)" />
                <StatCard label="Total Streak Days" value={totalStreak} icon={<Zap size={14} />} iconColor="var(--indigo)" iconBg="var(--indigo-dim)" />
                <StatCard label="Longest Streak" value={`${maxStreak}d`} icon={<CheckCircle2 size={14} />} iconColor="var(--emerald)" iconBg="var(--emerald-dim)" />
            </div>

            {/* Toolbar */}
            <div className="flex justify-end mb-4">
                <Button onClick={() => setShowForm(!showForm)} icon={<Plus size={13} />}>New habit</Button>
            </div>

            {/* Create form */}
            <AnimatePresence>
                {showForm && (
                    <motion.div
                        initial={{ opacity: 0, height: 0, marginBottom: 0 }}
                        animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
                        exit={{ opacity: 0, height: 0, marginBottom: 0 }}>
                        <Card padding="lg">
                            <div className="flex items-center justify-between mb-4">
                                <p className="text-sm font-semibold" style={{ color: "var(--t1)" }}>New habit</p>
                                <button onClick={() => setShowForm(false)} className="btn btn-ghost btn-icon"><X size={13} /></button>
                            </div>
                            <div className="space-y-3">
                                <input className="inp" placeholder="Habit name *" value={name} onChange={e => setName(e.target.value)} />
                                <input className="inp" placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} />
                                <Button onClick={() => name && createMut.mutate()} disabled={!name} loading={createMut.isPending}>
                                    Create habit
                                </Button>
                            </div>
                        </Card>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Habit Grid */}
            {isLoading && <div className="empty-state"><p>Loading…</p></div>}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <AnimatePresence>
                    {habits.map((habit, idx) => (
                        <motion.div
                            key={habit.id} layout
                            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }}
                            transition={{ delay: idx * 0.04 }}>
                            <Card padding="lg" className="group flex flex-col h-full">
                                {/* Top row */}
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1 min-w-0 pr-2">
                                        <p className="font-semibold text-sm truncate" style={{ color: "var(--t1)" }}>{habit.name}</p>
                                        {habit.description && (
                                            <p className="text-xs mt-0.5 line-clamp-1" style={{ color: "var(--t3)" }}>{habit.description}</p>
                                        )}
                                    </div>
                                    <button onClick={() => deleteMut.mutate(habit.id)}
                                        className="btn btn-ghost btn-icon opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0"
                                        style={{ color: "var(--rose)" }}>
                                        <Trash2 size={12} />
                                    </button>
                                </div>

                                {/* Streak */}
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full"
                                        style={{ background: "var(--amber-dim)" }}>
                                        <Flame size={12} style={{ color: "var(--amber)" }} />
                                        <span className="text-xs font-bold" style={{ color: "var(--amber)" }}>
                                            {habit.current_streak}
                                        </span>
                                    </div>
                                    <span className="text-xs" style={{ color: "var(--t3)" }}>
                                        current · best {habit.longest_streak}d
                                    </span>
                                </div>

                                {/* Log button */}
                                <div className="mt-auto">
                                    <AnimatePresence mode="wait">
                                        {justLogged.has(habit.id) ? (
                                            <motion.div
                                                key="success"
                                                initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ opacity: 0 }}
                                                className="flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold"
                                                style={{ background: "var(--emerald-dim)", color: "var(--emerald)" }}>
                                                <CheckCircle2 size={13} /> Logged!
                                            </motion.div>
                                        ) : (
                                            <Button
                                                key="log"
                                                variant="secondary"
                                                className="w-full text-xs"
                                                onClick={() => logMut.mutate(habit.id)}
                                                loading={logMut.isPending && logMut.variables === habit.id}
                                                icon={<CheckCircle2 size={12} />}>
                                                Log today
                                            </Button>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </Card>
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {!isLoading && habits.length === 0 && (
                <div className="empty-state mt-8">
                    <Flame size={28} style={{ color: "var(--t4)" }} />
                    <p className="text-sm">No habits yet. Start your streak!</p>
                    <Button size="sm" onClick={() => setShowForm(true)} icon={<Plus size={12} />}>Create habit</Button>
                </div>
            )}
        </AppLayout>
    );
}
