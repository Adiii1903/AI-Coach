"use client";

import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { studyPlanService, StudyPlan } from "@/services/studyPlanService";
import { Card, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { CalendarDays, Sparkles, History, Sun, CloudSun, Moon } from "lucide-react";

function parsePlanSections(text: string) {
    const sections: { icon: any; label: string; content: string }[] = [];
    const timeBlocks = [
        { keys: ["morning", "am", "early"], icon: Sun, label: "Morning" },
        { keys: ["afternoon", "midday", "noon"], icon: CloudSun, label: "Afternoon" },
        { keys: ["evening", "night", "pm"], icon: Moon, label: "Evening" },
    ];

    const lines = text.split("\n").map(l => l.trim()).filter(Boolean);
    let current: string[] = [];
    let currentLabel = "";
    let currentIcon: any = Sun;

    for (const line of lines) {
        const lower = line.toLowerCase();
        const match = timeBlocks.find(b => b.keys.some(k => lower.includes(k)));
        if (match) {
            if (current.length > 0) sections.push({ icon: currentIcon, label: currentLabel, content: current.join("\n") });
            currentLabel = match.label; currentIcon = match.icon; current = [];
        } else {
            current.push(line);
        }
    }
    if (current.length > 0) sections.push({ icon: currentIcon, label: currentLabel || "Plan", content: current.join("\n") });
    return sections.length ? sections : [{ icon: Sun, label: "Study Plan", content: text }];
}

function PlanCard({ plan, isToday }: { plan: StudyPlan; isToday?: boolean }) {
    const sections = parsePlanSections(plan.plan_text);

    return (
        <Card padding="lg" glow={isToday}>
            <CardHeader>
                <div className="flex items-center gap-2">
                    {isToday && <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: "var(--indigo)" }} />}
                    <CardTitle>
                        {isToday ? "Today's Plan" : new Date(plan.plan_date).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
                    </CardTitle>
                    {isToday && <Badge variant="indigo">Today</Badge>}
                </div>
                <time className="text-xs" style={{ color: "var(--t3)" }}>
                    {new Date(plan.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" })}
                </time>
            </CardHeader>

            {sections.length > 1 ? (
                <div className="space-y-4">
                    {sections.map(({ icon: Icon, label, content }) => (
                        <div key={label}>
                            <div className="flex items-center gap-2 mb-2">
                                <div className="w-6 h-6 rounded-md flex items-center justify-center"
                                    style={{ background: "var(--indigo-dim)" }}>
                                    <Icon size={12} style={{ color: "#818cf8" }} />
                                </div>
                                <p className="text-xs font-semibold" style={{ color: "var(--t2)" }}>{label}</p>
                            </div>
                            <p className="text-sm leading-relaxed pl-8" style={{ color: "var(--t2)", whiteSpace: "pre-wrap" }}>{content}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-sm leading-relaxed" style={{ color: "var(--t2)", whiteSpace: "pre-wrap" }}>
                    {plan.plan_text}
                </p>
            )}
        </Card>
    );
}

export default function StudyPlanPage() {
    const qc = useQueryClient();
    const { data: today, isLoading } = useQuery({ queryKey: ["study-plan-today"], queryFn: studyPlanService.getToday });
    const { data: history = [] } = useQuery({ queryKey: ["study-plan-history"], queryFn: studyPlanService.getHistory });

    const generateMut = useMutation({
        mutationFn: studyPlanService.generate,
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["study-plan-today"] });
            qc.invalidateQueries({ queryKey: ["study-plan-history"] });
        },
    });

    const pastHistory = history.length > 1 ? history.slice(1) : [];

    return (
        <AppLayout>
            <div className="max-w-2xl mx-auto space-y-6">
                <div className="flex justify-end">
                    <Button onClick={() => generateMut.mutate()} loading={generateMut.isPending}
                        icon={<Sparkles size={13} />} size="lg">
                        {generateMut.isPending ? "Generating plan…" : "Generate today's plan"}
                    </Button>
                </div>

                {/* Today's plan */}
                <div>
                    <div className="flex items-center gap-2 mb-3">
                        <CalendarDays size={13} style={{ color: "var(--t3)" }} />
                        <p className="section-label">Today</p>
                    </div>

                    {isLoading ? (
                        <Card padding="lg">
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
                                    style={{ borderColor: "var(--indigo)", borderTopColor: "transparent" }} />
                                <p className="text-sm" style={{ color: "var(--t3)" }}>Loading…</p>
                            </div>
                        </Card>
                    ) : today ? (
                        <PlanCard plan={today} isToday />
                    ) : (
                        <Card padding="lg">
                            <div className="empty-state py-10">
                                <CalendarDays size={32} style={{ color: "var(--t4)" }} />
                                <p className="text-sm font-medium" style={{ color: "var(--t2)" }}>No plan for today</p>
                                <p className="text-xs" style={{ color: "var(--t3)" }}>Generate a personalized AI study plan based on your activity</p>
                                <Button onClick={() => generateMut.mutate()} loading={generateMut.isPending} icon={<Sparkles size={12} />}>
                                    Generate today's plan
                                </Button>
                            </div>
                        </Card>
                    )}
                </div>

                {/* History */}
                {pastHistory.length > 0 && (
                    <div>
                        <div className="flex items-center gap-2 mb-3">
                            <History size={13} style={{ color: "var(--t3)" }} />
                            <p className="section-label">Previous plans</p>
                        </div>
                        <div className="space-y-4">
                            {pastHistory.map(p => <PlanCard key={p.id} plan={p} />)}
                        </div>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
