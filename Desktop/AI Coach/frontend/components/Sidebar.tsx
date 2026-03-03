"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { authService } from "@/services/authService";
import {
    LayoutDashboard, CheckSquare, Flame, BookOpen,
    Brain, CalendarDays, LogOut, Bot, X, Menu,
} from "lucide-react";

const NAV = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/tasks", label: "Tasks", icon: CheckSquare },
    { href: "/habits", label: "Habits", icon: Flame },
    { href: "/study", label: "Study Sessions", icon: BookOpen },
    { href: "/ai-coach", label: "AI Coach", icon: Brain },
    { href: "/study-plan", label: "Study Planner", icon: CalendarDays },
];

function NavItem({ href, label, icon: Icon, active }: { href: string; label: string; icon: any; active: boolean }) {
    return (
        <Link href={href}>
            <motion.div
                whileHover={{ x: 2 }}
                className={`nav-item ${active ? "active" : ""}`}>
                <Icon size={15} />
                <span>{label}</span>
                {active && (
                    <motion.div
                        layoutId="nav-indicator"
                        className="absolute right-2 w-1 h-4 rounded-full"
                        style={{ background: "var(--indigo)" }}
                    />
                )}
            </motion.div>
        </Link>
    );
}

export default function Sidebar() {
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);

    const sidebarContent = (
        <>
            {/* Logo */}
            <div className="flex items-center gap-2.5 px-4 py-4 border-b" style={{ borderColor: "var(--border)" }}>
                <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: "linear-gradient(135deg,#6366f1,#8b5cf6)" }}>
                    <Bot size={14} color="white" />
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold truncate" style={{ color: "var(--t1)" }}>AI Coach</p>
                    <p className="text-[11px]" style={{ color: "var(--t3)" }}>Productivity OS</p>
                </div>
                <button className="lg:hidden btn btn-ghost btn-icon" onClick={() => setMobileOpen(false)}>
                    <X size={14} />
                </button>
            </div>

            {/* Nav */}
            <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
                <p className="sidebar-section">Navigation</p>
                {NAV.map(({ href, label, icon }) => (
                    <NavItem
                        key={href}
                        href={href}
                        label={label}
                        icon={icon}
                        active={pathname === href || pathname.startsWith(href + "/")}
                    />
                ))}
            </nav>

            {/* Footer */}
            <div className="px-3 py-3 border-t" style={{ borderColor: "var(--border)" }}>
                <motion.button
                    whileHover={{ x: 2 }}
                    onClick={() => authService.logout()}
                    className="nav-item w-full">
                    <LogOut size={15} />
                    <span>Sign out</span>
                </motion.button>
            </div>
        </>
    );

    return (
        <>
            {/* Desktop Sidebar */}
            <aside className="sidebar hidden lg:flex">{sidebarContent}</aside>

            {/* Mobile Hamburger */}
            <button
                className="lg:hidden fixed top-3 left-3 z-[60] btn btn-secondary btn-icon"
                onClick={() => setMobileOpen(true)}>
                <Menu size={16} />
            </button>

            {/* Mobile Sidebar Drawer */}
            <AnimatePresence>
                {mobileOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            className="fixed inset-0 z-[55] bg-black/60 lg:hidden"
                            onClick={() => setMobileOpen(false)}
                        />
                        <motion.aside
                            initial={{ x: -260 }} animate={{ x: 0 }} exit={{ x: -260 }}
                            transition={{ type: "spring", damping: 25, stiffness: 300 }}
                            className="sidebar lg:hidden flex z-[60]" style={{ width: 240 }}>
                            {sidebarContent}
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>
        </>
    );
}
