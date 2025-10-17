/**
 * Sessions List Component
 * Displays recent voice call sessions
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api';

function SessionsList() {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSessions();
    // Refresh every 10 seconds
    const interval = setInterval(loadSessions, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadSessions = async () => {
    try {
      const response = await apiClient.getSessions(50);
      setSessions(response.data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return <div className="card">Loading sessions...</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>Recent Sessions</h2>
          <button className="btn btn-secondary" onClick={loadSessions}>
            🔄 Refresh
          </button>
        </div>

        {sessions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#6b7280' }}>
            <p>No sessions yet. Start a voice call to create your first session!</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>Channel</th>
                <th>Status</th>
                <th>Started</th>
                <th>Duration</th>
                <th>Room</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id}>
                  <td style={{ fontWeight: 600, color: '#1f2937' }}>
                    {session.agent_name}
                  </td>
                  <td>
                    <span style={{ 
                      textTransform: 'capitalize',
                      padding: '0.25rem 0.5rem',
                      background: session.channel === 'web' ? '#dbeafe' : '#fce7f3',
                      color: session.channel === 'web' ? '#1e40af' : '#9f1239',
                      borderRadius: '0.25rem',
                      fontSize: '0.875rem'
                    }}>
                      {session.channel}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${session.status.toLowerCase()}`}>
                      {session.status}
                    </span>
                  </td>
                  <td>{new Date(session.started_at).toLocaleString()}</td>
                  <td>{formatDuration(session.duration)}</td>
                  <td style={{ fontSize: '0.875rem', color: '#6b7280', fontFamily: 'monospace' }}>
                    {session.room.substring(0, 20)}...
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

export default SessionsList;

