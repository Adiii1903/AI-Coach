import api from "./api";

export interface ProductivityScore {
    productivity_score: number;
    tasks_completed_today: number;
    study_hours_today: number;
    habits_completed_today: number;
}

export const productivityService = {
    async getScore(): Promise<ProductivityScore> {
        const res = await api.get("/productivity/score");
        return res.data.data ?? res.data;
    },
};
