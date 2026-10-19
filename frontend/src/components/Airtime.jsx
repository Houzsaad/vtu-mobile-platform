import { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiPost } from '../api';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';

const NETWORKS = [
  { value: 'mtn', label: 'MTN' },
  { value: 'glo', label: 'Glo' },
  { value: 'airtel', label: 'Airtel' },
  { value: '9mobile', label: '9mobile' },
];

const EMPTY = { network: 'mtn', phone: '', amount: '', pin: '' };

export default function Airtime() {
  const [formData, setFormData] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const limits = { phone: 11, amount: 6, pin: 4 };
    const clean = name in limits
      ? value.replace(/\D/g, '').slice(0, limits[name])
      : value;
    setFormData({ ...formData, [name]: clean });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    setErrors({});
    setMessage('');

    try {
      const result = await apiPost(
        '/wallet/airtime/purchase/',
        { ...formData, amount: parseInt(formData.amount, 10) },
        { auth: true }
      );
      if (result.status === 'success') {
        setMessage(`₦${result.amount} airtime sent to ${result.recipient}.`);
      } else if (result.status === 'pending') {
        setMessage('Your purchase is processing. Check History for the final status.');
      } else {
        setMessage('Purchase failed. Your wallet was refunded.');
      }
      setFormData(EMPTY);
    } catch (err) {
      setErrors(err.data || { detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-page">
      <div className="change-password-card">
        <p className="change-password-title">Buy airtime</p>
        <form className="change-password-form" onSubmit={handleSubmit}>
          <select name="network" value={formData.network} onChange={handleChange}>
            {NETWORKS.map((n) => (
              <option key={n.value} value={n.value}>{n.label}</option>
            ))}
          </select>
          <input
            name="phone"
            placeholder="Phone number"
            inputMode="numeric"
            value={formData.phone}
            onChange={handleChange}
          />
          <input
            name="amount"
            placeholder="Amount (₦)"
            inputMode="numeric"
            value={formData.amount}
            onChange={handleChange}
          />
          <PasswordInput
            name="pin"
            placeholder="Transaction PIN"
            value={formData.pin}
            onChange={handleChange}
            maxLength={4}
          />
          <button type="submit" className="change-password-submit" disabled={loading}>
            {loading ? 'Processing...' : 'Buy airtime'}
          </button>
        </form>

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

        <Link to="/dashboard" className="change-password-back">← Back to home</Link>
      </div>
    </div>
  );
}