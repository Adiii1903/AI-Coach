import api from "./api";

export interface Task {
    id: string;
    title: string;
    description?: string;
    priority: "low" | "medium" | "high";
    is_completed: boolean;
    deadline?: string;
    created_at: string;
}

export interface CreateTaskPayload {
    title: string;
    description?: string;
    priority?: "low" | "medium" | "high";
    deadline?: string;
}

export const taskService = {
    async getAll(): Promise<Task[]> {
        const res = await api.get("/tasks");
        return res.data.data ?? res.data;
    },

    async create(payload: CreateTaskPayload): Promise<Task> {
        const res = await api.post("/tasks", payload);
        return res.data.data ?? res.data;
    },

    async update(id: string, payload: Partial<CreateTaskPayload>): Promise<Task> {
        const res = await api.put(`/tasks/${id}`, payload);
        return res.data.data ?? res.data;
    },

    async complete(id: string): Promise<Task> {
        const res = await api.patch(`/tasks/${id}/complete`);
        return res.data.data ?? res.data;
    },

    async delete(id: string): Promise<void> {
        await api.delete(`/tasks/${id}`);
    },
};
