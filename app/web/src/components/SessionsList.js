import React, { useState, useEffect } from 'react';
import { apiClient } from '../api';
import './SessionsList.css';
import { 
  FiRefreshCw, FiClock, FiGlobe, FiPhone, 
  FiCheckCircle, FiXCircle, FiActivity 
} from 'react-icons/fi';

function SessionsList() {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    loadSessions();
    const interval = setInterval(loadSessions, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadSessions = async () => {
    try {
      if (!isLoading) setIsRefreshing(true);
      const response = await apiClient.getSessions(50);
      setSessions(response.data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="sessions-card card">
        <div className="loading-state">
          <div className="spinner-lg"></div>
          <p className="text-muted">Loading sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="sessions-container">
      <div className="sessions-card card">
        <div className="sessions-header">
          <div className="sessions-title">
            <FiActivity size={24} />
            <div>
              <h3>Active Sessions</h3>
              <p className="text-muted">Monitor ongoing and recent conversations</p>
            </div>
          </div>
          <button 
            className="btn btn-secondary"
            onClick={loadSessions}
            disabled={isRefreshing}
          >
            <FiRefreshCw className={isRefreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>

        {sessions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">
              <FiActivity />
            </div>
            <h4 className="empty-state-title">No Sessions Yet</h4>
            <p className="empty-state-description">
              Start a voice call to create your first session. Sessions will appear here in real-time.
            </p>
          </div>
        ) : (
          <div className="sessions-table-wrapper">
            <table className="sessions-table">
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Channel</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Duration</th>
                  <th>Room ID</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id} className="session-row">
                    <td>
                      <div className="agent-cell">
                        <div className="agent-avatar-small">
                          {session.agent_name.charAt(0)}
                        </div>
                        <span className="agent-name">{session.agent_name}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`channel-badge channel-${session.channel}`}>
                        {session.channel === 'web' ? <FiGlobe /> : <FiPhone />}
                        {session.channel}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge status-${session.status.toLowerCase()}`}>
                        {session.status === 'active' ? (
                          <FiCheckCircle />
                        ) : (
                          <FiXCircle />
                        )}
                        {session.status}
                      </span>
                    </td>
                    <td>
                      <div className="time-cell">
                        <FiClock size={14} />
                        {formatDateTime(session.started_at)}
                      </div>
                    </td>
                    <td>
                      <span className="duration-badge">
                        {formatDuration(session.duration)}
                      </span>
                    </td>
                    <td>
                      <code className="room-id">{session.room.substring(0, 16)}...</code>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {sessions.length > 0 && (
          <div className="sessions-footer">
            <p className="text-muted">
              Showing {sessions.length} session{sessions.length !== 1 ? 's' : ''} • Auto-refreshes every 10 seconds
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default SessionsList;
