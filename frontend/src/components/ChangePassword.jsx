import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';

const BASE_URL = 'http://127.0.0.1:8000/api';

export default function ChangePassword() {
  const [formData, setFormData] = useState({
    current_password: '', new_password: '', confirm_new_password: '',
  });
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setSuccess('');
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch(`${BASE_URL}/accounts/change-password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      if (!response.ok) {
        setErrors(result);
        return;
      }
      setSuccess(result.message);
      setFormData({ current_password: '', new_password: '', confirm_new_password: '' });
    } catch (err) {
      setErrors({ detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-page">
      <div className="change-password-card">
        <p className="change-password-title">Change password</p>
        <form className="change-password-form" onSubmit={handleSubmit}>
          <PasswordInput
            name="current_password"
            placeholder="Current password"
            value={formData.current_password}
            onChange={handleChange}
          />
          <PasswordInput
            name="new_password"
            placeholder="New password"
            value={formData.new_password}
            onChange={handleChange}
          />
          <PasswordInput
            name="confirm_new_password"
            placeholder="Confirm new password"
            value={formData.confirm_new_password}
            onChange={handleChange}
          />
          <button type="submit" className="change-password-submit" disabled={loading}>
            {loading ? 'Updating...' : 'Update password'}
          </button>
        </form>

        {success && <p className="change-password-success">{success}</p>}
        {Object.keys(errors).length > 0 && (
          <div className="change-password-errors">
            {Object.entries(errors).map(([field, msg]) => (
              <p key={field} className="change-password-error">
                {Array.isArray(msg) ? msg.join(', ') : msg}
              </p>
            ))}
          </div>
        )}

        <Link to="/profile" className="change-password-back">← Back to profile</Link>
      </div>
    </div>
  );
}