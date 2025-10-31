import React from 'react';
import './Dashboard.css';
import { 
  FiZap, FiUsers, FiActivity, FiDatabase, 
  FiGitBranch, FiLink, FiShield, FiTrendingUp,
  FiCheckCircle, FiClock, FiArrowRight
} from 'react-icons/fi';

function Dashboard({ onModuleSelect, onViewChange }) {
  const modules = [
    // Iteration 1 - Available
    {
      id: 'test',
      name: 'Test Module',
      description: 'Test voice calls, monitor sessions, and manage agents in real-time',
      icon: <FiActivity />,
      status: 'available',
      iteration: 1,
      gradient: 'from-blue-500 to-blue-700'
    },
    // Future Iterations - Coming Soon
    {
      id: 'agents',
      name: 'Agent Hub',
      description: 'Advanced AI agent configuration and performance analytics',
      icon: <FiZap />,
      status: 'coming-soon',
      iteration: 2,
      gradient: 'from-blue-400 to-blue-600'
    },
    {
      id: 'analytics',
      name: 'Analytics',
      description: 'Deep insights into call quality, user satisfaction, and metrics',
      icon: <FiTrendingUp />,
      status: 'coming-soon',
      iteration: 2,
      gradient: 'from-cyan-500 to-blue-600'
    },
    {
      id: 'knowledge',
      name: 'Knowledge Base',
      description: 'AI training data management and contextual learning',
      icon: <FiDatabase />,
      status: 'coming-soon',
      iteration: 2,
      gradient: 'from-blue-500 to-indigo-600'
    },
    {
      id: 'workflow',
      name: 'Workflows',
      description: 'Automation rules, triggers, and intelligent routing',
      icon: <FiGitBranch />,
      status: 'coming-soon',
      iteration: 3,
      gradient: 'from-blue-600 to-blue-800'
    },
    {
      id: 'crm',
      name: 'CRM Integration',
      description: 'Seamless integration with Salesforce, HubSpot, and more',
      icon: <FiUsers />,
      status: 'coming-soon',
      iteration: 3,
      gradient: 'from-indigo-500 to-blue-700'
    },
    {
      id: 'webhook',
      name: 'Webhooks',
      description: 'External API integrations and real-time event streaming',
      icon: <FiLink />,
      status: 'coming-soon',
      iteration: 3,
      gradient: 'from-blue-400 to-indigo-600'
    },
    {
      id: 'permissions',
      name: 'Permissions',
      description: 'Role-based access control and team management',
      icon: <FiShield />,
      status: 'coming-soon',
      iteration: 3,
      gradient: 'from-sky-500 to-blue-700'
    },
  ];

  const handleModuleClick = (module) => {
    if (module.status === 'available') {
      onModuleSelect(module.id);
      onViewChange('module');
    }
  };

  const stats = [
    { label: 'Active Agents', value: '1', change: '+0%', icon: <FiZap /> },
    { label: 'Sessions Today', value: '0', change: '-', icon: <FiActivity /> },
    { label: 'Uptime', value: '99.9%', change: '+0.1%', icon: <FiCheckCircle /> },
  ];

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <div className="logo-section">
              <div className="logo-icon">
                <FiZap />
              </div>
              <div className="logo-text">
                <h1>Tele-AI</h1>
                <p>Voice AI Agent Platform</p>
              </div>
            </div>
            <div className="header-actions">
              <div className="user-menu">
                <div className="user-avatar">
                  <span>A</span>
                </div>
                <span className="user-name">Admin</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        <div className="container">
          {/* Welcome Section */}
          <section className="welcome-section animate-fade-in">
            <div className="welcome-content">
              <h2>Welcome back, Admin</h2>
              <p>Monitor your AI agents, analyze performance, and manage voice interactions</p>
            </div>
            
            {/* Stats Grid */}
            <div className="stats-grid">
              {stats.map((stat, index) => (
                <div key={index} className="stat-card">
                  <div className="stat-icon">{stat.icon}</div>
                  <div className="stat-details">
                    <p className="stat-label">{stat.label}</p>
                    <div className="stat-value-row">
                      <h3 className="stat-value">{stat.value}</h3>
                      {stat.change !== '-' && (
                        <span className="stat-change">{stat.change}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Iteration 1 Section */}
          <section className="modules-section animate-fade-in" style={{ animationDelay: '100ms' }}>
            <div className="section-header">
              <div className="section-title">
                <span className="iteration-badge iteration-1">
                  <FiCheckCircle /> Iteration 1
                </span>
                <h3>Available Now</h3>
              </div>
              <p className="section-description">Start testing with our core features</p>
            </div>
            <div className="modules-grid">
              {modules
                .filter(m => m.iteration === 1)
                .map(module => (
                  <div
                    key={module.id}
                    className={`module-card module-${module.status}`}
                    onClick={() => handleModuleClick(module)}
                  >
                    <div className={`module-gradient ${module.gradient}`}></div>
                    <div className="module-content">
                      <div className="module-icon-wrapper">
                        <div className="module-icon">{module.icon}</div>
                      </div>
                      <div className="module-info">
                        <h4>{module.name}</h4>
                        <p>{module.description}</p>
                      </div>
                      <div className="module-footer">
                        <span className="module-status-badge available">
                          <FiCheckCircle /> Active
                        </span>
                        <FiArrowRight className="module-arrow" />
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </section>

          {/* Iteration 2 Section */}
          <section className="modules-section animate-fade-in" style={{ animationDelay: '200ms' }}>
            <div className="section-header">
              <div className="section-title">
                <span className="iteration-badge iteration-2">
                  <FiClock /> Iteration 2
                </span>
                <h3>Coming Soon</h3>
              </div>
              <p className="section-description">Advanced features in development</p>
            </div>
            <div className="modules-grid">
              {modules
                .filter(m => m.iteration === 2)
                .map(module => (
                  <div
                    key={module.id}
                    className="module-card module-coming-soon"
                  >
                    <div className={`module-gradient ${module.gradient} grayscale`}></div>
                    <div className="module-content">
                      <div className="module-icon-wrapper locked">
                        <div className="module-icon">{module.icon}</div>
                      </div>
                      <div className="module-info">
                        <h4>{module.name}</h4>
                        <p>{module.description}</p>
                      </div>
                      <div className="module-footer">
                        <span className="module-status-badge coming-soon">
                          <FiClock /> Coming Soon
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </section>

          {/* Iteration 3 Section */}
          <section className="modules-section animate-fade-in" style={{ animationDelay: '300ms' }}>
            <div className="section-header">
              <div className="section-title">
                <span className="iteration-badge iteration-3">
                  <FiClock /> Iteration 3
                </span>
                <h3>Planned</h3>
              </div>
              <p className="section-description">Enterprise features on the roadmap</p>
            </div>
            <div className="modules-grid">
              {modules
                .filter(m => m.iteration === 3)
                .map(module => (
                  <div
                    key={module.id}
                    className="module-card module-coming-soon"
                  >
                    <div className={`module-gradient ${module.gradient} grayscale`}></div>
                    <div className="module-content">
                      <div className="module-icon-wrapper locked">
                        <div className="module-icon">{module.icon}</div>
                      </div>
                      <div className="module-info">
                        <h4>{module.name}</h4>
                        <p>{module.description}</p>
                      </div>
                      <div className="module-footer">
                        <span className="module-status-badge planned">
                          <FiClock /> Planned
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="dashboard-footer">
        <div className="container">
          <div className="footer-content">
            <p>© 2025 Tele-AI Platform • FYP Project</p>
            <p className="footer-version">Version 1.0.0 • Iteration 1</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Dashboard;
