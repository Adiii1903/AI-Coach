import api from "./api";

export interface StudySession {
    id: string;
    subject: string;
    topic?: string;
    duration_minutes: number;
    session_date: string;
    notes?: string;
    created_at: string;
}

export interface StudyStats {
    total_minutes: number;
    today_minutes: number;
    weekly_minutes: number;
}

export interface CreateStudySessionPayload {
    subject: string;
    topic?: string;
    duration_minutes: number;
    session_date?: string;
    notes?: string;
}

export const studyService = {
    async getAll(): Promise<StudySession[]> {
        const res = await api.get("/study-sessions");
        return res.data.data ?? res.data;
    },

    async getStats(): Promise<StudyStats> {
        const res = await api.get("/study-sessions/stats");
        return res.data.data ?? res.data;
    },

    async create(payload: CreateStudySessionPayload): Promise<StudySession> {
        const res = await api.post("/study-sessions", payload);
        return res.data.data ?? res.data;
    },

    async update(id: string, payload: Partial<CreateStudySessionPayload>): Promise<StudySession> {
        const res = await api.put(`/study-sessions/${id}`, payload);
        return res.data.data ?? res.data;
    },

    async delete(id: string): Promise<void> {
        await api.delete(`/study-sessions/${id}`);
    },
};
