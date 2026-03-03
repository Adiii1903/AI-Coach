"use client";

import { useState } from "react";
import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { taskService, CreateTaskPayload } from "@/services/taskService";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { StatCard } from "@/components/ui/StatCard";
import { Plus, Trash2, CheckCircle2, Circle, X, CheckSquare } from "lucide-react";

const PRIORITIES = ["low", "medium", "high"] as const;

export default function TasksPage() {
    const qc = useQueryClient();
    const [showForm, setShowForm] = useState(false);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState<"low" | "medium" | "high">("medium");
    const [filter, setFilter] = useState<"all" | "active" | "done">("all");

    const { data: tasks = [], isLoading } = useQuery({ queryKey: ["tasks"], queryFn: taskService.getAll });

    const createMut = useMutation({
        mutationFn: (p: CreateTaskPayload) => taskService.create(p),
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["tasks"] });
            setTitle(""); setDescription(""); setShowForm(false);
        },
    });
    const completeMut = useMutation({
        mutationFn: (id: string) => taskService.complete(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
    });
    const deleteMut = useMutation({
        mutationFn: (id: string) => taskService.delete(id),
        onSuccess: () => qc.invalidateQueries({ queryKey: ["tasks"] }),
    });

    const done = tasks.filter(t => t.is_completed).length;
    const active = tasks.filter(t => !t.is_completed).length;
    const filtered = tasks.filter(t =>
        filter === "all" ? true : filter === "done" ? t.is_completed : !t.is_completed
    );

    return (
        <AppLayout>
            {/* Stats row */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                <StatCard label="Total Tasks" value={tasks.length} icon={<CheckSquare size={14} />} />
                <StatCard label="Active" value={active} icon={<Circle size={14} />} iconColor="var(--amber)" iconBg="var(--amber-dim)" />
                <StatCard label="Completed" value={done} icon={<CheckCircle2 size={14} />} iconColor="var(--emerald)" iconBg="var(--emerald-dim)" />
            </div>

            {/* Controls row */}
            <div className="flex items-center justify-between gap-3 mb-4 flex-wrap">
                <div className="flex gap-1">
                    {(["all", "active", "done"] as const).map(f => (
                        <button key={f} onClick={() => setFilter(f)}
                            className={`btn btn-sm capitalize ${filter === f ? "btn-primary" : "btn-ghost"}`}>
                            {f}
                        </button>
                    ))}
                </div>
                <Button onClick={() => setShowForm(!showForm)} icon={<Plus size={13} />}>
                    New task
                </Button>
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
                                <p className="text-sm font-semibold" style={{ color: "var(--t1)" }}>New task</p>
                                <button onClick={() => setShowForm(false)} className="btn btn-ghost btn-icon">
                                    <X size={13} />
                                </button>
                            </div>
                            <div className="space-y-3">
                                <input className="inp" placeholder="Task title *" value={title} onChange={e => setTitle(e.target.value)} />
                                <input className="inp" placeholder="Description (optional)" value={description} onChange={e => setDescription(e.target.value)} />
                                <div className="flex gap-3">
                                    <select className="inp" value={priority} onChange={e => setPriority(e.target.value as any)}>
                                        {PRIORITIES.map(p => <option key={p} value={p} className="capitalize">{p}</option>)}
                                    </select>
                                    <Button onClick={() => title && createMut.mutate({ title, description: description || undefined, priority })}
                                        disabled={!title} loading={createMut.isPending}>
                                        Add task
                                    </Button>
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Task list */}
            <Card padding="none">
                {isLoading && (
                    <div className="empty-state"><p>Loading…</p></div>
                )}
                <AnimatePresence mode="popLayout">
                    {filtered.map((task, idx) => (
                        <motion.div
                            key={task.id}
                            layout
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            transition={{ delay: idx * 0.03 }}
                            className="flex items-center gap-3 px-5 py-3.5 group"
                            style={{ borderBottom: idx < filtered.length - 1 ? "1px solid var(--border)" : "none" }}>

                            {/* Complete toggle */}
                            <button onClick={() => !task.is_completed && completeMut.mutate(task.id)}
                                className="flex-shrink-0 transition-all">
                                {task.is_completed
                                    ? <CheckCircle2 size={17} style={{ color: "var(--emerald)" }} />
                                    : <Circle size={17} style={{ color: "var(--t3)" }} className="group-hover:text-white transition-colors" />}
                            </button>

                            {/* Title + desc */}
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate"
                                    style={{ color: task.is_completed ? "var(--t3)" : "var(--t1)", textDecoration: task.is_completed ? "line-through" : "none" }}>
                                    {task.title}
                                </p>
                                {task.description && (
                                    <p className="text-xs truncate mt-0.5" style={{ color: "var(--t3)" }}>{task.description}</p>
                                )}
                            </div>

                            {/* Priority badge */}
                            <Badge priority={task.priority as any} className="hidden sm:inline-flex capitalize">
                                {task.priority}
                            </Badge>

                            {/* Delete */}
                            <button onClick={() => deleteMut.mutate(task.id)}
                                className="btn btn-ghost btn-icon opacity-0 group-hover:opacity-100 transition-opacity"
                                style={{ color: "var(--rose)" }}>
                                <Trash2 size={13} />
                            </button>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {!isLoading && filtered.length === 0 && (
                    <div className="empty-state">
                        <CheckSquare size={28} style={{ color: "var(--t4)" }} />
                        <p className="text-sm">No tasks here</p>
                        <Button size="sm" onClick={() => setShowForm(true)} icon={<Plus size={12} />}>
                            Add your first task
                        </Button>
                    </div>
                )}
            </Card>
        </AppLayout>
    );
}
