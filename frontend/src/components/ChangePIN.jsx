import { useState } from 'react';
import { Link } from 'react-router-dom';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';

const BASE_URL = 'http://127.0.0.1:8000/api';

export default function ChangePin() {
  const [formData, setFormData] = useState({
    current_pin: '', new_pin: '', confirm_new_pin: '',
  });
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePinChange = (e) => {
    const digitsOnly = e.target.value.replace(/\D/g, '').slice(0, 4);
    setFormData({ ...formData, [e.target.name]: digitsOnly });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});
    setSuccess('');
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch(`${BASE_URL}/accounts/change-pin/`, {
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
      setFormData({ current_pin: '', new_pin: '', confirm_new_pin: '' });
    } catch (err) {
      setErrors({ detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-page">
      <div className="change-password-card">
        <p className="change-password-title">Change transaction PIN</p>
        <form className="change-password-form" onSubmit={handleSubmit}>
          <PasswordInput
            name="current_pin"
            placeholder="Current PIN"
            value={formData.current_pin}
            onChange={handlePinChange}
            maxLength={4}
          />
          <PasswordInput
            name="new_pin"
            placeholder="New PIN"
            value={formData.new_pin}
            onChange={handlePinChange}
            maxLength={4}
          />
          <PasswordInput
            name="confirm_new_pin"
            placeholder="Confirm new PIN"
            value={formData.confirm_new_pin}
            onChange={handlePinChange}
            maxLength={4}
          />
          <button type="submit" className="change-password-submit" disabled={loading}>
            {loading ? 'Updating...' : 'Update PIN'}
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