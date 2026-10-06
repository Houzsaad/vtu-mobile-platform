import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiGet } from '../api';
import './Dashboard.css';

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const [showBalance, setShowBalance] = useState(
    localStorage.getItem('balance_hidden') !== 'true'
  );

  const toggleBalance = () => {
  const next = !showBalance;
  setShowBalance(next);
    localStorage.setItem('balance_hidden', next ? 'false' : 'true');
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }
    apiGet('/accounts/profile/')
      .then(setProfile)
      .catch(() => {
        localStorage.clear();
        navigate('/login');
      });
  }, [navigate]);

  if (!profile) return <p className="dashboard-loading">Loading...</p>;
  
  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-greeting">Welcome</p>
          <p className="dashboard-name">{profile.full_name}</p>
        </div>
        <div className="dashboard-avatar">
          {profile.full_name?.charAt(0).toUpperCase()}
        </div>
      </header>

      <div className="wallet-card">
        <p className="wallet-label">💰 Wallet balance</p>
        <div className="wallet-amount-row">
          <p className="wallet-amount">
            {showBalance ? `₦${profile.wallet_balance}` : '₦ • • • • • •'}
          </p>
          <button
            type="button"
            className="wallet-toggle"
            onClick={toggleBalance}
            aria-label={showBalance ? 'Hide balance' : 'Show balance'}
          >
            {showBalance ? '👁️' : '🙈'}
          </button>
        </div>
        <button className="wallet-fund-btn">Fund wallet</button>
      </div>

      <section className="services-section">
        <p className="section-title">Services</p>
        <div className="services-grid">
          <div className="service-item">📱 Airtime</div>
          <div className="service-item">🌐 Data</div>
        </div>
      </section>

      <section className="transactions-section">
        <p className="section-title">Recent transactions</p>
        <p className="transactions-empty">No transactions yet.</p>
      </section>

      <nav className="dashboard-nav">
        <Link to="/dashboard" className="nav-item active">🏠 Home</Link>
        <span className="nav-item">💳 Fund</span>
        <span className="nav-item">📜 History</span>
        <Link to="/profile" className="nav-item">👤 Profile</Link>
      </nav>
    </div>
  );
}