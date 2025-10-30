/**
 * Voice Call Component
 * Allows users to start a voice call with an agent
 */
import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { apiClient } from '../api';

function VoiceCall() {
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  
  const roomRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    loadAgents();
    
    // Cleanup on unmount
    return () => {
      if (roomRef.current) {
        roomRef.current.disconnect();
      }
    };
  }, []);

  const loadAgents = async () => {
    try {
      const response = await apiClient.getAgents();
      const activeAgents = response.data.filter(a => a.is_active);
      setAgents(activeAgents);
      if (activeAgents.length > 0) {
        setSelectedAgentId(activeAgents[0].id);
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      setError('Failed to load agents. Please refresh the page.');
    }
  };

  const startCall = async () => {
    if (!selectedAgentId) {
      setError('Please select an agent');
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      // Create session
      const sessionResponse = await apiClient.createSession(selectedAgentId, 'web');
      const { session_id, room: roomName, url, token } = sessionResponse.data;
      
      setSessionId(session_id);

      // Connect to LiveKit room
      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      roomRef.current = room;

      // Set up event handlers
      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        if (track.kind === 'audio') {
          const audioElement = track.attach();
          audioRef.current = audioElement;
          document.body.appendChild(audioElement);
          audioElement.play();
        }
      });

      room.on(RoomEvent.Disconnected, () => {
        setIsConnected(false);
        setIsConnecting(false);
        if (audioRef.current) {
          audioRef.current.remove();
        }
      });

      // Connect to room
      await room.connect(url, token);
      setIsConnected(true);
      setIsConnecting(false);

      console.log('✓ Connected to room:', room.name);

    } catch (error) {
      console.error('Failed to start call:', error);
      setError('Failed to start call. Please try again.');
      setIsConnecting(false);
    }
  };

  const endCall = async () => {
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }

    if (audioRef.current) {
      audioRef.current.remove();
      audioRef.current = null;
    }

    if (sessionId) {
      try {
        await apiClient.endSession(sessionId);
      } catch (error) {
        console.error('Failed to end session:', error);
      }
      setSessionId(null);
    }

    setIsConnected(false);
    setIsConnecting(false);
  };

  const selectedAgent = agents.find(a => a.id === selectedAgentId);

  return (
    <div>
      <div className="card">
        <h2>Voice Call</h2>

        {error && (
          <div style={{
            padding: '1rem',
            background: '#fee2e2',
            color: '#991b1b',
            borderRadius: '0.5rem',
            marginBottom: '1.5rem'
          }}>
            {error}
          </div>
        )}

        {!isConnected && !isConnecting && (
          <div>
            <div className="form-group">
              <label>Select Agent</label>
              <select
                value={selectedAgentId}
                onChange={(e) => setSelectedAgentId(e.target.value)}
                disabled={agents.length === 0}
              >
                {agents.length === 0 && (
                  <option value="">No agents available</option>
                )}
                {agents.map(agent => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </select>
            </div>

            {selectedAgent && (
              <div style={{
                padding: '1rem',
                background: '#f9fafb',
                borderRadius: '0.5rem',
                marginBottom: '1.5rem'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '0.5rem', fontSize: '1.125rem' }}>
                  {selectedAgent.name}
                </h3>
                <p style={{ color: '#6b7280', margin: 0, fontSize: '0.875rem' }}>
                  Model: {selectedAgent.llm_model} | Locale: {selectedAgent.locale}
                </p>
              </div>
            )}

            <button
              className="btn btn-primary btn-large"
              onClick={startCall}
              disabled={agents.length === 0}
              style={{ width: '100%' }}
            >
              🎤 Start Voice Call
            </button>

            {agents.length === 0 && (
              <p style={{ textAlign: 'center', color: '#6b7280', marginTop: '1rem' }}>
                No active agents available. Please create an agent first.
              </p>
            )}
          </div>
        )}

        {isConnecting && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div className="loading-spinner" style={{ margin: '0 auto 1rem' }}></div>
            <p>Connecting to agent...</p>
          </div>
        )}

        {isConnected && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <div style={{
              width: '120px',
              height: '120px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              margin: '0 auto 2rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '3rem',
              animation: 'pulse 2s ease-in-out infinite'
            }}>
              🎤
            </div>
            
            <h3 style={{ marginBottom: '0.5rem' }}>
              Connected to {selectedAgent?.name}
            </h3>
            <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
              Start speaking...
            </p>

            <button
              className="btn btn-secondary btn-large"
              onClick={endCall}
              style={{ background: '#ef4444' }}
            >
              📞 End Call
            </button>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Tips for a Great Call</h3>
        <ul style={{ color: '#6b7280', lineHeight: '1.8' }}>
          <li>Make sure your microphone is enabled and working</li>
          <li>Use headphones to avoid echo</li>
          <li>Speak clearly and wait for the agent to finish speaking</li>
          <li>Try asking the agent to check the weather or perform calculations</li>
        </ul>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
          }
          50% {
            transform: scale(1.05);
            box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
          }
        }
      `}</style>
    </div>
  );
}

export default VoiceCall;

