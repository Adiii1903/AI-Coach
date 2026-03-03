"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { SignupPayload, LoginPayload, TokenResponse, User } from "@/types/auth";

export function useAuth() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const signup = async (payload: SignupPayload) => {
        setLoading(true);
        setError(null);
        try {
            await api.post("/auth/signup", payload);
            router.push("/login?registered=true");
        } catch (err: any) {
            setError(err.response?.data?.error ?? err.response?.data?.detail ?? "Signup failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const login = async (payload: LoginPayload) => {
        setLoading(true);
        setError(null);
        try {
            const { data } = await api.post<TokenResponse>("/auth/login", payload);
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("refresh_token", data.refresh_token);
            // Also store in cookie so Next.js middleware can read it (localStorage is not
            // accessible in server-side middleware).
            document.cookie = `access_token=${data.access_token}; path=/; SameSite=Lax`;
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.response?.data?.error ?? err.response?.data?.detail ?? "Invalid email or password.");
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        // Clear the auth cookie so middleware correctly redirects to /login
        document.cookie = "access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
        router.push("/login");
    };

    const getProfile = async (): Promise<User | null> => {
        try {
            const { data } = await api.get<User>("/users/me");
            return data;
        } catch {
            return null;
        }
    };

    return { signup, login, logout, getProfile, loading, error };
}
