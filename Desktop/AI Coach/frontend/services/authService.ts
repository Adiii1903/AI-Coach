import api from "./api";

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

export const authService = {
    async login(email: string, password: string): Promise<LoginResponse> {
        const res = await api.post("/auth/login", { email, password });
        return res.data;
    },

    async signup(name: string, email: string, password: string): Promise<void> {
        await api.post("/auth/signup", { name, email, password });
    },

    logout() {
        if (typeof window !== "undefined") {
            localStorage.removeItem("access_token");
            window.location.href = "/login";
        }
    },

    isAuthenticated(): boolean {
        if (typeof window === "undefined") return false;
        return !!localStorage.getItem("access_token");
    },
};
