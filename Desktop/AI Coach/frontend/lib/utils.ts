import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

export function formatHours(minutes: number): string {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    if (h === 0) return `${m}m`;
    if (m === 0) return `${h}h`;
    return `${h}h ${m}m`;
}

export function formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleDateString("en-US", {
        weekday: "short", month: "short", day: "numeric",
    });
}

export function getScoreColor(score: number): string {
    if (score >= 70) return "text-emerald-400";
    if (score >= 40) return "text-amber-400";
    return "text-rose-400";
}

export function getScoreGradient(score: number): string {
    if (score >= 70) return "from-emerald-500 to-teal-500";
    if (score >= 40) return "from-amber-500 to-orange-500";
    return "from-rose-500 to-pink-500";
}
