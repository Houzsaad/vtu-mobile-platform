import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiGet } from '../api';
import './Profile.css';

export default function Profile() {
  const [profile, setProfile] = useState(null);
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

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  if (!profile) return <p className="profile-loading">Loading...</p>;

  return (
    <div className="profile-page">
      <div className="profile-avatar-large">
        {profile.full_name?.charAt(0).toUpperCase()}
      </div>
      <p className="profile-name">{profile.full_name}</p>
      <p className="profile-email">{profile.email}</p>

      <div className="profile-balance-card">
        <p className="profile-balance-label">Wallet balance</p>
      <div className="profile-balance-row">
      <p className="profile-balance-amount">
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
      </div>

      <div className="profile-actions">
        <Link to="/change-password" className="profile-action-item">
          🔒 Change password
        </Link>
        <Link to="/change-pin" className="profile-action-item">
          🔢 Change transaction PIN
        </Link>
        <a
          href="https://wa.me/2348121196405"
          target="_blank"
          rel="noopener noreferrer"
          className="profile-action-item"
        >
          💬 Customer care
        </a>
      </div>

      <button className="profile-logout-btn" onClick={handleLogout}>
        Logout
      </button>

      <nav className="dashboard-nav">
        <Link to="/dashboard" className="nav-item">🏠 Home</Link>
        <span className="nav-item">💳 Fund</span>
        <span className="nav-item">📜 History</span>
        <Link to="/profile" className="nav-item active">👤 Profile</Link>
      </nav>
    </div>
  );
}