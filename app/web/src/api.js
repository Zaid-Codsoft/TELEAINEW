/**
 * API Client for BrainCX Voice SaaS
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API functions
export const apiClient = {
    // Health check
    health: () => api.get('/health'),
    
    // Authentication
    login: (password) => api.post('/admin/login', { password }),
    logout: () => api.post('/admin/logout'),
    
    // Agents
    getAgents: () => api.get('/agents'),
    getAgent: (id) => api.get(`/agents/${id}`),
    createAgent: (data) => api.post('/agents', data),
    updateAgent: (id, data) => api.put(`/agents/${id}`, data),
    deleteAgent: (id) => api.delete(`/agents/${id}`),
    
    // Sessions
    createSession: (agentId, channel = 'web') => 
        api.post('/sessions', { agent_id: agentId, channel }),
    getSessions: (limit = 50) => api.get(`/sessions?limit=${limit}`),
    endSession: (sessionId) => api.post(`/sessions/${sessionId}/end`),
    
    // LiveKit token
    getToken: (room, identity) => 
        api.post('/token', { room, identity }),
};

export default api;

