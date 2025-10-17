/**
 * BrainCX Voice SaaS - Main Application
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import './App.css';
import { apiClient } from './api';

// Import components
import AgentManager from './components/AgentManager';
import SessionsList from './components/SessionsList';
import VoiceCall from './components/VoiceCall';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check API connection on startup
    apiClient.health()
      .then(() => {
        setIsConnected(true);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error('Failed to connect to API:', error);
        setIsConnected(false);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading BrainCX Voice...</p>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="error-screen">
        <div className="error-content">
          <h1>⚠️ Connection Error</h1>
          <p>Unable to connect to the API server.</p>
          <p>Make sure the API is running at: {process.env.REACT_APP_API_URL || 'http://localhost:8000'}</p>
          <button onClick={() => window.location.reload()}>
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/agents" element={<AgentManager />} />
            <Route path="/sessions" element={<SessionsList />} />
            <Route path="/call" element={<VoiceCall />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function Navigation() {
  return (
    <nav className="navigation">
      <div className="nav-container">
        <Link to="/" className="nav-brand">
          🧠 BrainCX Voice
        </Link>
        <div className="nav-links">
          <Link to="/agents" className="nav-link">Agents</Link>
          <Link to="/sessions" className="nav-link">Sessions</Link>
          <Link to="/call" className="nav-link nav-link-primary">Start Call</Link>
        </div>
      </div>
    </nav>
  );
}

function HomePage() {
  const [stats, setStats] = useState({
    agentCount: 0,
    sessionCount: 0,
  });

  useEffect(() => {
    // Load stats
    Promise.all([
      apiClient.getAgents(),
      apiClient.getSessions(10)
    ]).then(([agentsRes, sessionsRes]) => {
      setStats({
        agentCount: agentsRes.data.length,
        sessionCount: sessionsRes.data.length,
      });
    }).catch(err => {
      console.error('Failed to load stats:', err);
    });
  }, []);

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Welcome to BrainCX Voice SaaS</h1>
        <p className="subtitle">
          Build and deploy AI-powered voice agents with ease
        </p>
        
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-value">{stats.agentCount}</div>
            <div className="stat-label">Active Agents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.sessionCount}</div>
            <div className="stat-label">Recent Sessions</div>
          </div>
        </div>

        <div className="quick-actions">
          <Link to="/call" className="btn btn-primary btn-large">
            🎤 Start Voice Call
          </Link>
          <Link to="/agents" className="btn btn-secondary btn-large">
            ⚙️ Manage Agents
          </Link>
        </div>
      </div>

      <div className="features-section">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Agents</h3>
            <p>Create intelligent voice agents with custom behaviors</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Function Tools</h3>
            <p>Extend agents with custom functions and integrations</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Session Tracking</h3>
            <p>Monitor and analyze all voice conversations</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">☁️</div>
            <h3>Cloud Ready</h3>
            <p>Deploy easily with Docker and Kubernetes</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

