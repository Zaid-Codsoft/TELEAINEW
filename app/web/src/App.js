import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import AgentManager from './components/AgentManager';
import SessionsList from './components/SessionsList';
import VoiceCall from './components/VoiceCall';
import { FiArrowLeft, FiZap, FiPlus } from 'react-icons/fi';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [selectedModule, setSelectedModule] = useState('test');
  const [showCreateAgent, setShowCreateAgent] = useState(false);

  const renderContent = () => {
    if (currentView === 'dashboard') {
      return <Dashboard onModuleSelect={setSelectedModule} onViewChange={setCurrentView} />;
    }

    switch (selectedModule) {
      case 'test':
        return (
          <div className="module-view">
            {/* Module Header */}
            <header className="module-header">
              <div className="container">
                <button className="back-button" onClick={() => setCurrentView('dashboard')}>
                  <FiArrowLeft />
                  <span>Back to Dashboard</span>
                </button>
                <div className="module-header-content">
                  <div className="module-header-icon">
                    <FiZap />
                  </div>
                  <div className="module-header-info">
                    <h1>Test Module</h1>
                    <p>Voice call testing, session monitoring, and agent management</p>
                  </div>
                  <button 
                    className="btn btn-success btn-lg"
                    onClick={() => setShowCreateAgent(true)}
                    style={{ marginLeft: 'auto' }}
                  >
                    <FiPlus /> Create Agent
                  </button>
                </div>
              </div>
            </header>

            {/* Module Content */}
            <main className="module-content">
              <div className="container">
                <div className="module-grid">
                  <div className="module-column">
                    <VoiceCall />
                  </div>
                  <div className="module-column">
                    <SessionsList />
                  </div>
                  <div className="module-column-full">
                    <AgentManager showCreateForm={showCreateAgent} onCreateFormClose={() => setShowCreateAgent(false)} />
                  </div>
                </div>
              </div>
            </main>

            {/* Floating Action Button */}
            <button 
              className="fab-button"
              onClick={() => setShowCreateAgent(true)}
              title="Create New Agent"
            >
              <FiPlus size={24} />
            </button>
          </div>
        );
      default:
        return (
          <div className="module-view">
            <header className="module-header">
              <div className="container">
                <button className="back-button" onClick={() => setCurrentView('dashboard')}>
                  <FiArrowLeft />
                  <span>Back to Dashboard</span>
                </button>
                <div className="module-header-content">
                  <h1>{selectedModule.toUpperCase()} Module</h1>
                  <p>This module is coming soon</p>
                </div>
              </div>
            </header>

            <main className="module-content">
              <div className="container">
                <div className="coming-soon-view">
                  <div className="coming-soon-icon">🚧</div>
                  <h2>Coming Soon</h2>
                  <p>This module is currently under development and will be available in future iterations.</p>
                  <button 
                    className="btn btn-primary mt-5"
                    onClick={() => setCurrentView('dashboard')}
                  >
                    <FiArrowLeft /> Back to Dashboard
                  </button>
                </div>
              </div>
            </main>
          </div>
        );
    }
  };

  return (
    <div className="App">
      {renderContent()}
    </div>
  );
}

export default App;
