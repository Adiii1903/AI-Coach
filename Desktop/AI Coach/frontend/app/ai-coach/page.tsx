"use client";

import AppLayout from "@/components/AppLayout";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { aiCoachService, AIInsight } from "@/services/aiCoachService";
import { Card, CardHeader, CardTitle, CardSubtitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Brain, Sparkles, History, Quote } from "lucide-react";

const insightT: Record<string, "motivation" | "suggestion" | "warning"> = {
    motivation: "motivation", suggestion: "suggestion", warning: "warning",
};

function InsightCard({ insight, featured = false }: { insight: AIInsight; featured?: boolean }) {
    return (
        <motion.div whileHover={!featured ? { y: -1 } : undefined}>
            <Card padding="lg" className={featured ? "card-glow" : ""}>
                <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                            style={{ background: "var(--indigo-dim)" }}>
                            <Brain size={14} style={{ color: "#818cf8" }} />
                        </div>
                        <div>
                            <Badge insight={insightT[insight.insight_type] ?? "suggestion"} className="capitalize">
                                {insight.insight_type}
                            </Badge>
                        </div>
                    </div>
                    <time className="text-xs" style={{ color: "var(--t3)" }}>
                        {new Date(insight.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </time>
                </div>
                <div className="flex gap-2.5">
                    <Quote size={14} className="flex-shrink-0 mt-0.5" style={{ color: "var(--indigo)", opacity: 0.5 }} />
                    <p className={`leading-relaxed ${featured ? "text-base" : "text-sm"}`} style={{ color: "var(--t2)" }}>
                        {insight.insight_text}
                    </p>
                </div>
            </Card>
        </motion.div>
    );
}

export default function AICoachPage() {
    const qc = useQueryClient();
    const { data: latest, isLoading } = useQuery({ queryKey: ["ai-advice"], queryFn: aiCoachService.getLatest });
    const { data: history = [] } = useQuery({ queryKey: ["ai-history"], queryFn: aiCoachService.getHistory });

    const generateMut = useMutation({
        mutationFn: aiCoachService.generate,
        onSuccess: () => {
            qc.invalidateQueries({ queryKey: ["ai-advice"] });
            qc.invalidateQueries({ queryKey: ["ai-history"] });
        },
    });

    const pastHistory = history.length > 1 ? history.slice(1) : [];

    return (
        <AppLayout>
            <div className="max-w-2xl mx-auto space-y-6">
                {/* Generate button */}
                <div className="flex justify-end">
                    <Button onClick={() => generateMut.mutate()} loading={generateMut.isPending}
                        icon={<Sparkles size={13} />} size="lg">
                        {generateMut.isPending ? "Generating insight…" : "Generate new insight"}
                    </Button>
                </div>

                {/* Latest insight */}
                <div>
                    <p className="section-label mb-3">Latest Insight</p>
                    {isLoading ? (
                        <Card padding="lg" className="animate-fade-in">
                            <div className="flex items-center gap-3">
                                <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin"
                                    style={{ borderColor: "var(--indigo)", borderTopColor: "transparent" }} />
                                <p className="text-sm" style={{ color: "var(--t3)" }}>Loading…</p>
                            </div>
                        </Card>
                    ) : latest ? (
                        <InsightCard insight={latest} featured />
                    ) : (
                        <Card padding="lg">
                            <div className="empty-state py-8">
                                <Brain size={32} style={{ color: "var(--t4)" }} />
                                <p className="text-sm font-medium" style={{ color: "var(--t2)" }}>No insights yet</p>
                                <p className="text-xs" style={{ color: "var(--t3)" }}>Generate your first AI-powered insight</p>
                                <Button onClick={() => generateMut.mutate()} loading={generateMut.isPending} icon={<Sparkles size={12} />}>
                                    Get my first insight
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
                            <p className="section-label">Previous insights</p>
                        </div>
                        <div className="space-y-3">
                            {pastHistory.map(i => <InsightCard key={i.id} insight={i} />)}
                        </div>
                    </div>
                )}
            </div>
        </AppLayout>
    );
}
