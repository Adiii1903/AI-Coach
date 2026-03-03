"use client";

import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { productivityService } from "@/services/productivityService";
import { aiCoachService } from "@/services/aiCoachService";
import { studyPlanService } from "@/services/studyPlanService";
import { studyService } from "@/services/studyService";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from "recharts";
import {
    CheckCircle2, Flame, Clock, Brain, CalendarDays,
    RefreshCw, TrendingUp, Sparkles
} from "lucide-react";

/* ── Score Ring ────────────────────────────────────────────── */
function ScoreRing({ score }: { score: number }) {
    const r = 52, size = 128, cx = 64, cy = 64;
    const circ = 2 * Math.PI * r;
    const offset = circ * (1 - score / 100);
    const color = score >= 70 ? "#10b981" : score >= 40 ? "#f59e0b" : "#f43f5e";

    return (
        <div className="flex flex-col items-center">
            <div className="relative">
                <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
                    <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="9" />
                    <motion.circle
                        cx={cx} cy={cy} r={r} fill="none"
                        stroke={color} strokeWidth="9" strokeLinecap="round"
                        strokeDasharray={circ}
                        initial={{ strokeDashoffset: circ }}
                        animate={{ strokeDashoffset: offset }}
                        transition={{ duration: 1.4, ease: [0.4, 0, 0.2, 1] }}
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.span
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
                        className="text-3xl font-bold" style={{ color }}>
                        {score}
                    </motion.span>
                    <span className="text-[10px]" style={{ color: "var(--t3)" }}>/ 100</span>
                </div>
            </div>
            <p className="text-xs mt-2 font-medium" style={{ color: "var(--t2)" }}>Productivity Score</p>
        </div>
    );
}

/* ── Score breakdown bar ───────────────────────────────────── */
function MicroBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
    const pct = Math.min(value / max, 1) * 100;
    return (
        <div>
            <div className="flex justify-between mb-1">
                <span className="text-xs" style={{ color: "var(--t3)" }}>{label}</span>
                <span className="text-xs font-semibold" style={{ color }}>{value} pts</span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--surface-3)" }}>
                <motion.div
                    initial={{ width: 0 }} animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.9, delay: 0.3 }}
                    className="h-full rounded-full" style={{ background: color }} />
            </div>
        </div>
    );
}

const insightMap: Record<string, "motivation" | "suggestion" | "warning"> = {
    motivation: "motivation", suggestion: "suggestion", warning: "warning",
};

export default function DashboardPage() {
    const qc = useQueryClient();

    const { data: score } = useQuery({ queryKey: ["productivity"], queryFn: productivityService.getScore });
    const { data: advice } = useQuery({ queryKey: ["ai-advice"], queryFn: aiCoachService.getLatest });
    const { data: todayPlan } = useQuery({ queryKey: ["study-plan-today"], queryFn: studyPlanService.getToday });
    const { data: sessions = [] } = useQuery({ queryKey: ["study-sessions"], queryFn: studyService.getAll });

    const genAdvice = useMutation({
        mutationFn: aiCoachService.generate,
        onSuccess: () => qc.invalidateQueries({ queryKey: ["ai-advice"] }),
    });
    const genPlan = useMutation({
        mutationFn: studyPlanService.generate,
        onSuccess: () => qc.invalidateQueries({ queryKey: ["study-plan-today"] }),
    });

    const s = score ?? { productivity_score: 0, tasks_completed_today: 0, habits_completed_today: 0, study_hours_today: 0 };

    // Weekly bar chart data
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const weeklyMap: Record<string, number> = {};
    sessions.forEach(sess => {
        const d = new Date(sess.session_date);
        const idx = d.getDay() === 0 ? 6 : d.getDay() - 1;
        weeklyMap[days[idx]] = (weeklyMap[days[idx]] ?? 0) + sess.duration_minutes / 60;
    });
    const weeklyData = days.map(d => ({ day: d, hours: +(weeklyMap[d] ?? 0).toFixed(1) }));

    return (
        <AppLayout>
            {/* Row 1: Score + Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {/* Score card spans 1 col on lg */}
                <Card className="flex flex-col items-center justify-center py-6" glow>
                    <ScoreRing score={s.productivity_score} />
                    <div className="w-full mt-5 space-y-2.5 px-2">
                        <MicroBar label="Tasks (max 40)" value={Math.min(s.tasks_completed_today * 10, 40)} max={40} color="var(--indigo)" />
                        <MicroBar label="Study (max 30)" value={Math.min(Math.round(s.study_hours_today * 10), 30)} max={30} color="var(--emerald)" />
                        <MicroBar label="Habits (max 30)" value={Math.min(s.habits_completed_today * 10, 30)} max={30} color="var(--amber)" />
                    </div>
                </Card>

                <StatCard
                    label="Tasks Completed"
                    value={s.tasks_completed_today}
                    subtext="today"
                    icon={<CheckCircle2 size={15} />}
                    iconColor="var(--indigo)" iconBg="var(--indigo-dim)"
                />
                <StatCard
                    label="Study Hours"
                    value={`${s.study_hours_today}h`}
                    subtext="logged today"
                    icon={<Clock size={15} />}
                    iconColor="var(--emerald)" iconBg="var(--emerald-dim)"
                />
                <StatCard
                    label="Habits Done"
                    value={s.habits_completed_today}
                    subtext="today"
                    icon={<Flame size={15} />}
                    iconColor="var(--amber)" iconBg="var(--amber-dim)"
                />
            </div>

            {/* Row 2: Study Chart */}
            <div className="mb-6">
                <Card padding="lg">
                    <CardHeader>
                        <div>
                            <CardTitle>Weekly Study Hours</CardTitle>
                            <p className="text-xs mt-0.5" style={{ color: "var(--t3)" }}>Hours studied per day this week</p>
                        </div>
                        <TrendingUp size={15} style={{ color: "var(--t3)" }} />
                    </CardHeader>
                    <ResponsiveContainer width="100%" height={180}>
                        <BarChart data={weeklyData} barSize={28} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                            <CartesianGrid vertical={false} stroke="var(--border)" />
                            <XAxis dataKey="day" tick={{ fill: "var(--t3)", fontSize: 11 }} axisLine={false} tickLine={false} />
                            <YAxis tick={{ fill: "var(--t3)", fontSize: 11 }} axisLine={false} tickLine={false} />
                            <Tooltip
                                cursor={{ fill: "rgba(99,102,241,0.06)" }}
                                contentStyle={{ background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--t1)", fontSize: 12 }}
                                formatter={(v: any) => [`${v}h`, "Study"]}
                            />
                            <Bar dataKey="hours" fill="var(--indigo)" radius={[5, 5, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </Card>
            </div>

            {/* Row 3: AI Coach + Study Plan */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* AI Coach */}
                <Card padding="lg">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Brain size={15} style={{ color: "var(--indigo)" }} />
                            <CardTitle>AI Coach</CardTitle>
                        </div>
                        <Button variant="secondary" size="sm" icon={<RefreshCw size={12} />}
                            loading={genAdvice.isPending} onClick={() => genAdvice.mutate()}>
                            {genAdvice.isPending ? "Generating…" : "Generate"}
                        </Button>
                    </CardHeader>

                    {advice ? (
                        <div className="space-y-3">
                            <Badge insight={insightMap[advice.insight_type] ?? "suggestion"}>
                                {advice.insight_type}
                            </Badge>
                            <p className="text-sm leading-relaxed" style={{ color: "var(--t2)" }}>
                                &ldquo;{advice.insight_text}&rdquo;
                            </p>
                        </div>
                    ) : (
                        <div className="empty-state py-8">
                            <Brain size={28} style={{ color: "var(--t4)" }} />
                            <p className="text-sm">No advice yet</p>
                            <Button variant="primary" size="sm" onClick={() => genAdvice.mutate()} loading={genAdvice.isPending}>
                                <Sparkles size={12} /> Get advice
                            </Button>
                        </div>
                    )}
                </Card>

                {/* Study Plan */}
                <Card padding="lg">
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <CalendarDays size={15} style={{ color: "var(--emerald)" }} />
                            <CardTitle>Today&apos;s Study Plan</CardTitle>
                        </div>
                        <Button variant="secondary" size="sm" icon={<RefreshCw size={12} />}
                            loading={genPlan.isPending} onClick={() => genPlan.mutate()}>
                            {genPlan.isPending ? "Generating…" : "Generate"}
                        </Button>
                    </CardHeader>
                    {todayPlan ? (
                        <p className="text-sm leading-relaxed" style={{ color: "var(--t2)", whiteSpace: "pre-wrap" }}>
                            {todayPlan.plan_text.substring(0, 350)}{todayPlan.plan_text.length > 350 ? "…" : ""}
                        </p>
                    ) : (
                        <div className="empty-state py-8">
                            <CalendarDays size={28} style={{ color: "var(--t4)" }} />
                            <p className="text-sm">No plan for today</p>
                            <Button variant="primary" size="sm" onClick={() => genPlan.mutate()} loading={genPlan.isPending}>
                                <Sparkles size={12} /> Generate plan
                            </Button>
                        </div>
                    )}
                </Card>
            </div>
        </AppLayout>
    );
}
