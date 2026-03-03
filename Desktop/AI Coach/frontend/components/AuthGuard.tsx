"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const [mounted, setMounted] = useState(false);
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            router.push("/login");
        } else {
            setAuthorized(true);
        }
        setMounted(true);
    }, [router]);

    // Don't render anything until client-side check is done
    // This prevents SSR/client tree mismatch
    if (!mounted) return null;
    if (!authorized) return null;

    return <>{children}</>;
}
