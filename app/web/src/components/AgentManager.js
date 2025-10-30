/**
 * Agent Manager Component
 * Allows creating, viewing, editing, and deleting agents
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api';

function AgentManager() {
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    system_prompt: '',
  });

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await apiClient.getAgents();
      setAgents(response.data);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAgent) {
        await apiClient.updateAgent(editingAgent.id, formData);
      } else {
        await apiClient.createAgent(formData);
      }
      setShowForm(false);
      setEditingAgent(null);
      resetForm();
      loadAgents();
    } catch (error) {
      console.error('Failed to save agent:', error);
      alert('Failed to save agent. Please try again.');
    }
  };

  const handleEdit = (agent) => {
    setEditingAgent(agent);
    setFormData({
      name: agent.name,
      system_prompt: agent.system_prompt,
    });
    setShowForm(true);
  };

  const handleDelete = async (agent) => {
    if (!window.confirm(`Delete agent "${agent.name}"?`)) {
      return;
    }
    try {
      await apiClient.deleteAgent(agent.id);
      loadAgents();
    } catch (error) {
      console.error('Failed to delete agent:', error);
      alert('Failed to delete agent. Please try again.');
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      system_prompt: '',
    });
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingAgent(null);
    resetForm();
  };

  if (isLoading) {
    return <div className="card">Loading agents...</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>Agents</h2>
          {!showForm && (
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              + Create Agent
            </button>
          )}
        </div>

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginBottom: '2rem', padding: '1.5rem', background: '#f9fafb', borderRadius: '0.5rem' }}>
            <h3>{editingAgent ? 'Edit Agent' : 'Create New Agent'}</h3>
            
            <div className="form-group">
              <label>Agent Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Customer Support Agent"
              />
            </div>

            <div className="form-group">
              <label>System Prompt *</label>
              <textarea
                required
                value={formData.system_prompt}
                onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                placeholder="You are a helpful assistant that..."
              />
              <small style={{ color: '#6b7280' }}>
                This defines how your agent behaves and responds to users. The agent uses Gemini LLM, Whisper tiny for speech recognition, and SpeechT5 for text-to-speech.
              </small>
            </div>


            <div style={{ display: 'flex', gap: '1rem' }}>
              <button type="submit" className="btn btn-primary">
                {editingAgent ? 'Update Agent' : 'Create Agent'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        )}

        {agents.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
            <p>No agents yet. Create your first agent to get started!</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Model</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {agents.map((agent) => (
                <tr key={agent.id}>
                  <td style={{ fontWeight: 600, color: '#1f2937' }}>{agent.name}</td>
                  <td>{agent.llm_model}</td>
                  <td>
                    <span className={`status-badge ${agent.is_active ? 'active' : 'ended'}`}>
                      {agent.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>{new Date(agent.created_at).toLocaleDateString()}</td>
                  <td>
                    <button
                      className="btn btn-primary"
                      style={{ marginRight: '0.5rem', padding: '0.5rem 1rem' }}
                      onClick={() => handleEdit(agent)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '0.5rem 1rem' }}
                      onClick={() => handleDelete(agent)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default AgentManager;

