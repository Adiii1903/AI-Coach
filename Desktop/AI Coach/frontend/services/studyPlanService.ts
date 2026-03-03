import api from "./api";

export interface StudyPlan {
    id: string;
    plan_text: string;
    plan_date: string;
    created_at: string;
}

export const studyPlanService = {
    async generate(): Promise<StudyPlan> {
        const res = await api.post("/study-plan/generate");
        return res.data.data ?? res.data;
    },

    async getToday(): Promise<StudyPlan | null> {
        const res = await api.get("/study-plan/today");
        return res.data.data ?? null;
    },

    async getHistory(): Promise<StudyPlan[]> {
        const res = await api.get("/study-plan/history");
        return res.data.data ?? res.data;
    },
};
