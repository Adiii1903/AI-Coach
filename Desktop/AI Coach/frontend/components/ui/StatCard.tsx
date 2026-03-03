"use client";
import React from "react";
import { motion } from "framer-motion";
import { Card } from "./Card";

interface StatCardProps {
    label: string;
    value: string | number;
    subtext?: string;
    icon: React.ReactNode;
    iconColor?: string;
    iconBg?: string;
    trend?: "up" | "down" | "neutral";
}

export function StatCard({ label, value, subtext, icon, iconColor, iconBg }: StatCardProps) {
    return (
        <Card>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <p className="text-xs font-medium mb-3" style={{ color: "var(--t3)" }}>{label}</p>
                    <p className="text-2xl font-bold tracking-tight" style={{ color: "var(--t1)" }}>{value}</p>
                    {subtext && <p className="text-xs mt-1" style={{ color: "var(--t3)" }}>{subtext}</p>}
                </div>
                <div className="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: iconBg ?? "var(--indigo-dim)", color: iconColor ?? "var(--indigo)" }}>
                    {icon}
                </div>
            </div>
        </Card>
    );
}
