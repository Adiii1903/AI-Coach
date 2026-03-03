"use client";

import { usePathname } from "next/navigation";

const TITLES: Record<string, { title: string; subtitle: string }> = {
    "/dashboard": { title: "Dashboard", subtitle: "Your daily productivity at a glance" },
    "/tasks": { title: "Tasks", subtitle: "Manage and track your work" },
    "/habits": { title: "Habits", subtitle: "Build consistent daily habits" },
    "/study": { title: "Study Sessions", subtitle: "Log and review your learning time" },
    "/ai-coach": { title: "AI Coach", subtitle: "Personalized AI-generated insights" },
    "/study-plan": { title: "Study Planner", subtitle: "AI-generated structured study plans" },
};

export default function TopNav() {
    const pathname = usePathname();
    const info = TITLES[pathname] ?? { title: "AI Coach", subtitle: "" };
    const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "short", day: "numeric" });

    return (
        <header className="topnav">
            <div className="flex-1">
                <h1 className="text-base font-semibold" style={{ color: "var(--t1)" }}>{info.title}</h1>
                {info.subtitle && <p className="text-xs" style={{ color: "var(--t3)" }}>{info.subtitle}</p>}
            </div>
            <div className="flex items-center gap-3">
                <p className="text-xs hidden sm:block" style={{ color: "var(--t3)" }}>{today}</p>
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
                    style={{ background: "var(--indigo-dim)", color: "#818cf8" }}>
                    A
                </div>
            </div>
        </header>
    );
}
