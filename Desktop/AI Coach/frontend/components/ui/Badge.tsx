import React from "react";
import { cn } from "@/lib/utils";

type BadgeVariant = "indigo" | "emerald" | "amber" | "rose" | "violet";
type PriorityVariant = "high" | "medium" | "low";
type InsightVariant = "motivation" | "suggestion" | "warning";

interface BadgeProps {
    children: React.ReactNode;
    variant?: BadgeVariant;
    priority?: PriorityVariant;
    insight?: InsightVariant;
    className?: string;
}

const priorityMap: Record<PriorityVariant, string> = {
    high: "priority-high",
    medium: "priority-medium",
    low: "priority-low",
};

const insightMap: Record<InsightVariant, string> = {
    motivation: "insight-motivation",
    suggestion: "insight-suggestion",
    warning: "insight-warning",
};

const variantMap: Record<BadgeVariant, string> = {
    indigo: "badge-indigo",
    emerald: "badge-emerald",
    amber: "badge-amber",
    rose: "badge-rose",
    violet: "badge-violet",
};

export function Badge({ children, variant, priority, insight, className }: BadgeProps) {
    const cls = priority
        ? priorityMap[priority]
        : insight
            ? insightMap[insight]
            : variant
                ? variantMap[variant]
                : "badge-indigo";

    return <span className={cn("badge", cls, className)}>{children}</span>;
}
