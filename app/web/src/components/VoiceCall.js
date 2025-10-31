import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent } from 'livekit-client';
import { apiClient } from '../api';
import './VoiceCall.css';
import { 
  FiPhone, FiPhoneOff, FiMic, FiMicOff, FiVolume2, 
  FiVolumeX, FiAlertCircle, FiCheckCircle, FiLoader 
} from 'react-icons/fi';

function VoiceCall() {
  const [agents, setAgents] = useState([]);
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [agentSpeaking, setAgentSpeaking] = useState(false);
  
  const roomRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    loadAgents();
    
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
      const sessionResponse = await apiClient.createSession(selectedAgentId, 'web');
      const { session_id, room: roomName, url, token } = sessionResponse.data;
      
      setSessionId(session_id);

      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
      });

      roomRef.current = room;

      room.on(RoomEvent.TrackSubscribed, (track, publication, participant) => {
        console.log('🔊 Track subscribed:', track.kind);
        if (track.kind === 'audio') {
          const audioElement = track.attach();
          audioRef.current = audioElement;
          document.body.appendChild(audioElement);
          
          audioElement.addEventListener('play', () => {
            setAgentSpeaking(true);
          });
          
          audioElement.addEventListener('ended', () => {
            setAgentSpeaking(false);
          });
          
          audioElement.addEventListener('pause', () => {
            setAgentSpeaking(false);
          });
          
          audioElement.play().catch(err => {
            console.error('❌ Error playing audio:', err);
          });
        }
      });

      room.on(RoomEvent.Disconnected, () => {
        setIsConnected(false);
        setIsConnecting(false);
        if (audioRef.current) {
          audioRef.current.remove();
        }
      });

      await room.connect(url, token);
      
      try {
        await room.localParticipant.setMicrophoneEnabled(true);
        console.log('✅ Microphone enabled');
      } catch (micError) {
        console.error('❌ Microphone error:', micError);
        setError('Failed to enable microphone. Please grant permission.');
        throw micError;
      }
      
      setIsConnected(true);
      setIsConnecting(false);

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
    <div className="voice-call-container">
      <div className="voice-call-card card">
        {/* Error Alert */}
        {error && (
          <div className="alert alert-error">
            <FiAlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {/* Not Connected State */}
        {!isConnected && !isConnecting && (
          <div className="call-setup animate-fade-in">
            <div className="call-header">
              <div className="call-icon">
                <FiPhone />
              </div>
              <div>
                <h3 className="call-title">Voice Call Test</h3>
                <p className="call-description">Start a voice conversation with an AI agent</p>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label required">Select Agent</label>
              <select
                className="form-select"
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
              <div className="agent-preview">
                <div className="agent-preview-header">
                  <div className="agent-avatar">
                    {selectedAgent.name.charAt(0)}
                  </div>
                  <div className="agent-preview-info">
                    <h4>{selectedAgent.name}</h4>
                    <div className="agent-details">
                      <span className="text-muted">{selectedAgent.locale}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <button
              className="btn btn-primary btn-xl"
              onClick={startCall}
              disabled={agents.length === 0}
              style={{ width: '100%' }}
            >
              <FiPhone /> Start Voice Call
            </button>

            {agents.length === 0 && (
              <div className="empty-state-inline">
                <FiAlertCircle />
                <p>No active agents available. Please create an agent first.</p>
              </div>
            )}
          </div>
        )}

        {/* Connecting State */}
        {isConnecting && (
          <div className="call-connecting animate-scale-in">
            <div className="connecting-spinner">
              <FiLoader className="animate-spin" size={48} />
            </div>
            <h3>Connecting to agent...</h3>
            <p className="text-muted">Establishing voice connection</p>
          </div>
        )}

        {/* Connected State */}
        {isConnected && (
          <div className="call-active animate-scale-in">
            <div className="call-avatar-container">
              <div className="call-avatar-wrapper">
                <div className={`call-avatar ${agentSpeaking ? 'speaking' : ''}`}>
                  {selectedAgent?.name.charAt(0)}
                </div>
                {agentSpeaking && (
                  <div className="audio-wave">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="call-info">
              <h3 className="call-agent-name">{selectedAgent?.name}</h3>
              <div className="call-status">
                {agentSpeaking ? (
                  <div className="status-indicator speaking">
                    <FiVolume2 />
                    <span>Agent is speaking...</span>
                  </div>
                ) : (
                  <div className="status-indicator listening">
                    <FiMic />
                    <span>Listening... Speak now</span>
                  </div>
                )}
              </div>
            </div>

            <div className="call-controls">
              <button
                className="btn btn-danger btn-lg"
                onClick={endCall}
              >
                <FiPhoneOff /> End Call
              </button>
            </div>

            <div className="call-note">
              <FiAlertCircle size={16} />
              <span>Check the terminal for real-time transcriptions</span>
            </div>
          </div>
        )}
      </div>

      {/* Tips Card */}
      <div className="tips-card card">
        <div className="tips-header">
          <FiCheckCircle size={20} />
          <h4>Call Tips</h4>
        </div>
        <ul className="tips-list">
          <li>
            <FiCheckCircle />
            <span>Ensure your microphone is enabled and working properly</span>
          </li>
          <li>
            <FiCheckCircle />
            <span>Use headphones to prevent echo and improve audio quality</span>
          </li>
          <li>
            <FiCheckCircle />
            <span>Speak clearly and wait for the agent to finish responding</span>
          </li>
          <li>
            <FiCheckCircle />
            <span>Try asking questions or giving simple commands</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

export default VoiceCall;
