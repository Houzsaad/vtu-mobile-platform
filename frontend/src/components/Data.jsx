import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, apiPost } from '../api';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';

const NETWORKS = [
  { value: 'mtn', label: 'MTN' },
  { value: 'airtel', label: 'Airtel' },
  { value: 'glo', label: 'Glo' },
  { value: '9mobile', label: '9mobile' },
];

const EMPTY = { phone: '', pin: '' };

export default function Data() {
  const [network, setNetwork] = useState('mtn');
  const [plans, setPlans] = useState([]);
  const [planId, setPlanId] = useState('');
  const [formData, setFormData] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setPlans([]);
    setPlanId('');
    apiGet(`/wallet/data/plans/?network=${network}`)
      .then((list) => { if (!cancelled) setPlans(list); })
      .catch(() => {
        if (!cancelled) setErrors({ detail: 'Could not load plans.' });
      });
    return () => { cancelled = true; };
  }, [network]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const limit = name === 'phone' ? 11 : 4;
    setFormData({ ...formData, [name]: value.replace(/\D/g, '').slice(0, limit) });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading || !planId) return;
    setLoading(true);
    setErrors({});
    setMessage('');

    try {
      const result = await apiPost(
        '/wallet/data/purchase/',
        { plan_id: Number(planId), phone: formData.phone, pin: formData.pin },
        { auth: true }
      );
      if (result.status === 'success') {
        setMessage(`${result.plan} sent to ${result.recipient}.`);
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
        <p className="change-password-title">Buy data</p>
        <form className="change-password-form" onSubmit={handleSubmit}>
          <select value={network} onChange={(e) => setNetwork(e.target.value)}>
            {NETWORKS.map((n) => (
              <option key={n.value} value={n.value}>{n.label}</option>
            ))}
          </select>
          <select value={planId} onChange={(e) => setPlanId(e.target.value)}>
            <option value="">Select a plan</option>
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name.replace(/^N\d+\s*/, '')} - ₦{p.price}
              </option>
            ))}
          </select>
          <input
            name="phone"
            placeholder="Phone number"
            inputMode="numeric"
            value={formData.phone}
            onChange={handleChange}
          />
          <PasswordInput
            name="pin"
            placeholder="Transaction PIN"
            value={formData.pin}
            onChange={handleChange}
            maxLength={4}
          />
          <button
            type="submit"
            className="change-password-submit"
            disabled={loading || !planId}
          >
            {loading ? 'Processing...' : 'Buy data'}
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