"use client";
import React from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "ghost" | "danger";
    size?: "sm" | "md" | "lg" | "icon";
    loading?: boolean;
    icon?: React.ReactNode;
}

export function Button({
    children, variant = "primary", size = "md",
    loading, icon, className, disabled, ...props
}: ButtonProps) {
    const variantMap = {
        primary: "btn-primary",
        secondary: "btn-secondary",
        ghost: "btn-ghost",
        danger: "btn-danger",
    };
    const sizeMap = { sm: "btn-sm", md: "", lg: "btn-lg", icon: "btn-icon" };

    return (
        <motion.button
            whileHover={!disabled && !loading ? { scale: 1.01 } : undefined}
            whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
            disabled={disabled || loading}
            className={cn("btn", variantMap[variant], sizeMap[size], className)}
            {...(props as any)}>
            {loading ? <Loader2 size={13} className="animate-spin" /> : icon}
            {children}
        </motion.button>
    );
}
