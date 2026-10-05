import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { apiPost } from '../api';
import PasswordInput from './PasswordInput';
import './Login.css';

export default function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await apiPost('/accounts/login/', formData);
      localStorage.setItem('access_token', result.access);
      localStorage.setItem('refresh_token', result.refresh);
      localStorage.setItem('full_name', result.full_name);
      localStorage.setItem('username', result.username);
      localStorage.setItem('wallet_balance', result.wallet_balance);
      navigate('/dashboard');
    } catch (err) {
      setError(err.data?.detail || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <p className="login-title">Welcome back</p>
        <form className="login-form" onSubmit={handleSubmit}>
          <input
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleChange}
          />
          <PasswordInput
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
          />
          <div className="login-meta">
            <Link to="/forgot-password">Forgot password?</Link>
          </div>
          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Log in'}
          </button>
        </form>
        {error && <p className="login-error">{error}</p>}
        <p className="auth-switch">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}