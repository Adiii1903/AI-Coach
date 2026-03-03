"use client";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import React from "react";

interface CardProps {
    children: React.ReactNode;
    className?: string;
    glow?: boolean;
    padding?: "sm" | "md" | "lg" | "none";
    onClick?: () => void;
    hover?: boolean;
}

export function Card({ children, className, glow, padding = "md", onClick, hover = true }: CardProps) {
    const padMap = { none: "", sm: "p-4", md: "p-5", lg: "p-6" };
    return (
        <motion.div
            whileHover={hover && !onClick ? { y: -1 } : undefined}
            onClick={onClick}
            className={cn("card", padMap[padding], glow && "card-glow", onClick && "cursor-pointer", className)}>
            {children}
        </motion.div>
    );
}

export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
    return <div className={cn("flex items-center justify-between mb-4", className)}>{children}</div>;
}

export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
    return (
        <p className={cn("text-sm font-semibold", className)} style={{ color: "var(--t1)" }}>
            {children}
        </p>
    );
}

export function CardSubtitle({ children, className }: { children: React.ReactNode; className?: string }) {
    return (
        <p className={cn("text-xs mt-0.5", className)} style={{ color: "var(--t3)" }}>
            {children}
        </p>
    );
}
