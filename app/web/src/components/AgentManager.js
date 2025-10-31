import React, { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './AgentManager.css';
import { 
  FiPlus, FiEdit2, FiTrash2, FiSave, FiX, 
  FiCheckCircle, FiXCircle, FiCpu, FiCalendar
} from 'react-icons/fi';

function AgentManager({ showCreateForm = false, onCreateFormClose = () => {} }) {
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

  useEffect(() => {
    if (showCreateForm) {
      setShowForm(true);
      setEditingAgent(null);
      resetForm();
    }
  }, [showCreateForm]);

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
    onCreateFormClose();
  };

  if (isLoading) {
    return (
      <div className="agent-manager-card card">
        <div className="loading-state">
          <div className="spinner-lg"></div>
          <p className="text-muted">Loading agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="agent-manager-container">
      <div className="agent-manager-card card">
        <div className="agent-manager-header">
          <div className="agent-manager-title">
            <FiCpu size={24} />
            <div>
              <h3>Agent Management</h3>
              <p className="text-muted">Create and configure AI voice agents</p>
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <FiPlus /> Create Agent
          </button>
        </div>

        {/* Agent Form */}
        {showForm && (
          <div className="agent-form-overlay" onClick={(e) => {
            if (e.target.className === 'agent-form-overlay') {
              handleCancel();
            }
          }}>
            <div className="agent-form-container animate-scale-in">
              <form onSubmit={handleSubmit} className="agent-form">
                <div className="form-header">
                  <h4>{editingAgent ? 'Edit Agent' : 'Create New Agent'}</h4>
                  <button 
                    type="button" 
                    className="btn btn-ghost btn-sm"
                    onClick={handleCancel}
                  >
                    <FiX />
                  </button>
                </div>
              
              <div className="form-group">
                <label className="form-label required">Agent Name</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Customer Support Agent"
                />
                <span className="form-helper">
                  Choose a descriptive name for your AI agent
                </span>
              </div>

              <div className="form-group">
                <label className="form-label required">System Prompt</label>
                <textarea
                  className="form-textarea"
                  required
                  value={formData.system_prompt}
                  onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                  placeholder="You are a helpful assistant that..."
                  rows="6"
                />
                <span className="form-helper">
                  Define your agent's behavior and personality using natural language instructions.
                </span>
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-success">
                  <FiSave /> {editingAgent ? 'Update Agent' : 'Create Agent'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                  <FiX /> Cancel
                </button>
              </div>
            </form>
          </div>
          </div>
        )}

        {/* Agents List */}
        <>
            {agents.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">
                  <FiCpu />
                </div>
                <h4 className="empty-state-title">No Agents Yet</h4>
                <p className="empty-state-description">
                  Create your first AI agent to start testing voice interactions. Agents can be customized with different personalities and behaviors.
                </p>
                <button className="btn btn-primary mt-4" onClick={() => setShowForm(true)}>
                  <FiPlus /> Create Your First Agent
                </button>
              </div>
            ) : (
              <div className="agents-grid animate-fade-in">
                {agents.map((agent) => (
                  <div key={agent.id} className="agent-card">
                    <div className="agent-card-header">
                      <div className="agent-card-avatar">
                        {agent.name.charAt(0)}
                      </div>
                      <div className="agent-card-status">
                        {agent.is_active ? (
                          <span className="status-dot active"></span>
                        ) : (
                          <span className="status-dot inactive"></span>
                        )}
                      </div>
                    </div>
                    
                    <div className="agent-card-body">
                      <h4 className="agent-card-name">{agent.name}</h4>
                      
                      <div className="agent-card-meta">
                        <div className="meta-item">
                          <FiCalendar size={14} />
                          <span>{new Date(agent.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>

                      <div className="agent-card-prompt">
                        {agent.system_prompt.length > 120
                          ? agent.system_prompt.substring(0, 120) + '...'
                          : agent.system_prompt}
                      </div>

                      <div className="agent-card-badge">
                        {agent.is_active ? (
                          <span className="badge badge-success">
                            <FiCheckCircle /> Active
                          </span>
                        ) : (
                          <span className="badge badge-neutral">
                            <FiXCircle /> Inactive
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="agent-card-actions">
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEdit(agent)}
                      >
                        <FiEdit2 /> Edit
                      </button>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => handleDelete(agent)}
                      >
                        <FiTrash2 /> Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
      </div>
    </div>
  );
}

export default AgentManager;
