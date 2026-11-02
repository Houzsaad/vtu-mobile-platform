import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';

const BASE_URL = import.meta.env.VITE_API_URL;

async function post(path, body) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const result = await response.json().catch(() => ({}));
  return { ok: response.ok, result };
}

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState(''); 
  const [form, setForm] = useState({ code: '', new_password: '', confirm_new_password: '' });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const requestCode = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setMessage('');
    try {
      const { ok, result } = await post('/accounts/forgot-password/', { email });
      if (!ok) {
        setErrors(result);
        return;
      }
      setMessage(result.message);
      setStep(2);
    } catch {
      setErrors({ detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setMessage('');
    try {
      const { ok, result } = await post('/accounts/forgot-password/confirm/', {
        email,
        ...form,
      });
      if (!ok) {
        setErrors(result);
        return;
      }
      setMessage(result.message);
      setTimeout(() => navigate('/login'), 1500);
    } catch {
      setErrors({ detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-page">
      <div className="change-password-card">
        <p className="change-password-title">Forgot password</p>

        {step === 1 && (
          <form className="change-password-form" onSubmit={requestCode}>
            <input
              type="email"
              className="change-password-input"
              placeholder="Your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit" className="change-password-submit" disabled={loading || !email}>
              {loading ? 'Sending...' : 'Send reset code'}
            </button>
          </form>
        )}

        {step === 2 && (
          <form className="change-password-form" onSubmit={resetPassword}>
            <input
              name="code"
              className="change-password-input"
              inputMode="numeric"
              maxLength={6}
              placeholder="6-digit code"
              value={form.code}
              onChange={(e) =>
                setForm({ ...form, code: e.target.value.replace(/\D/g, '').slice(0, 6) })
              }
              required
            />
            <PasswordInput
              name="new_password"
              placeholder="New password"
              value={form.new_password}
              onChange={handleChange}
            />
            <PasswordInput
              name="confirm_new_password"
              placeholder="Confirm new password"
              value={form.confirm_new_password}
              onChange={handleChange}
            />
            <button type="submit" className="change-password-submit" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset password'}
            </button>
          </form>
        )}

        {message && <p className="change-password-success">{message}</p>}
        {Object.keys(errors).length > 0 && (
          <div className="change-password-errors">
            {Object.entries(errors).map(([field, msg]) => (
              <p key={field} className="change-password-error">
                {Array.isArray(msg) ? msg.join(', ') : msg}
              </p>
            ))}
          </div>
        )}

        <Link to="/login" className="change-password-back">← Back to login</Link>
      </div>
    </div>
  );
}