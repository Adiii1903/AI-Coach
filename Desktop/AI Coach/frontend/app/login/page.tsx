import { Suspense } from "react";
import LoginForm from "./LoginForm";

export default function LoginPage() {
    return (
        <Suspense
            fallback={
                <main className="min-h-screen bg-[#0f0f1a] flex items-center justify-center">
                    <div className="text-slate-400 animate-pulse">Loading...</div>
                </main>
            }
        >
            <LoginForm />
        </Suspense>
    );
}
