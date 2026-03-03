import api from "./api";

export interface AIInsight {
    id: string;
    insight_text: string;
    insight_type: "motivation" | "suggestion" | "warning";
    created_at: string;
}

export const aiCoachService = {
    async generate(): Promise<AIInsight> {
        const res = await api.post("/ai-coach/generate");
        return res.data.data ?? res.data;
    },

    async getLatest(): Promise<AIInsight | null> {
        const res = await api.get("/ai-coach/advice");
        return res.data.data ?? null;
    },

    async getHistory(): Promise<AIInsight[]> {
        const res = await api.get("/ai-coach/history");
        return res.data.data ?? res.data;
    },
};
