"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import TopNav from "@/components/TopNav";
import { motion } from "framer-motion";

export default function AppLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [ready, setReady] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            router.push("/login");
        } else {
            setReady(true);
        }
    }, [router]);

    if (!ready) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg)" }}>
                <div className="flex items-center gap-3">
                    <div className="w-4 h-4 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: "var(--indigo)", borderTopColor: "transparent" }} />
                    <span className="text-sm" style={{ color: "var(--t3)" }}>Loading…</span>
                </div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen" style={{ background: "var(--bg)" }}>
            <Sidebar />
            <div className="flex-1 flex flex-col min-h-screen lg:ml-[240px]">
                <TopNav />
                <motion.main
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="flex-1 overflow-y-auto">
                    <div className="page-container">
                        {children}
                    </div>
                </motion.main>
            </div>
        </div>
    );
}
