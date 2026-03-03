import api from "./api";

export interface Habit {
    id: string;
    name: string;
    description?: string;
    target_frequency: string;
    current_streak: number;
    longest_streak: number;
    created_at: string;
}

export interface CreateHabitPayload {
    name: string;
    description?: string;
    target_frequency?: string;
}

export const habitService = {
    async getAll(): Promise<Habit[]> {
        const res = await api.get("/habits");
        return res.data.data ?? res.data;
    },

    async create(payload: CreateHabitPayload): Promise<Habit> {
        const res = await api.post("/habits", payload);
        return res.data.data ?? res.data;
    },

    async update(id: string, payload: Partial<CreateHabitPayload>): Promise<Habit> {
        const res = await api.put(`/habits/${id}`, payload);
        return res.data.data ?? res.data;
    },

    async log(id: string): Promise<void> {
        await api.post(`/habits/${id}/log`);
    },

    async delete(id: string): Promise<void> {
        await api.delete(`/habits/${id}`);
    },
};
