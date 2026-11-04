import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, apiPost } from '../api';
import PasswordInput from './PasswordInput';
import './ChangePassword.css';
import './Data.css';

const NETWORKS = [
  { value: 'mtn', label: 'MTN' },
  { value: 'airtel', label: 'Airtel' },
  { value: 'glo', label: 'Glo' },
  { value: '9mobile', label: '9mobile' },
];

const EMPTY = { phone: '', pin: '' };

const cleanName = (name) => name.replace(/\s*\([^()]*\)\s*$/, '');

// 08012345678, +2348012345678 and 8012345678 all become 08012345678
function normalizePhone(raw) {
  let d = String(raw).replace(/\D/g, '');
  if (d.startsWith('234') && d.length >= 13) d = '0' + d.slice(3, 13);
  if (d.length === 10) d = '0' + d;
  return d.slice(0, 11);
}

const canPickContact =
  typeof navigator !== 'undefined' && 'contacts' in navigator && 'ContactsManager' in window;

export default function Data() {
  const [step, setStep] = useState('form'); // 'form' | 'confirm'
  const [network, setNetwork] = useState('mtn');
  const [types, setTypes] = useState([]);
  const [typesLoaded, setTypesLoaded] = useState(false);
  const [planType, setPlanType] = useState('');
  const [plans, setPlans] = useState([]);
  const [planId, setPlanId] = useState('');
  const [formData, setFormData] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  // Network changed: load the plan types that have active plans
  useEffect(() => {
    let cancelled = false;
    setTypes([]);
    setTypesLoaded(false);
    setPlanType('');
    setPlans([]);
    setPlanId('');
    setErrors({});
    apiGet(`/wallet/data/plan-types/?network=${network}`)
      .then((list) => {
        if (!cancelled) {
          setTypes(list);
          setTypesLoaded(true);
        }
      })
      .catch(() => {
        if (!cancelled) setErrors({ detail: 'Could not load plan types.' });
      });
    return () => { cancelled = true; };
  }, [network]);

  // Type chosen: load only the plans of that type
  useEffect(() => {
    setPlanId('');
    if (!planType) {
      setPlans([]);
      return;
    }
    let cancelled = false;
    apiGet(`/wallet/data/plans/?network=${network}&plan_type=${encodeURIComponent(planType)}`)
      .then((list) => { if (!cancelled) setPlans(list); })
      .catch(() => {
        if (!cancelled) setErrors({ detail: 'Could not load plans.' });
      });
    return () => { cancelled = true; };
  }, [network, planType]);

  const selectedPlan = plans.find((p) => String(p.id) === planId);
  const networkLabel = NETWORKS.find((n) => n.value === network)?.label;
  const phoneOk = /^0\d{10}$/.test(formData.phone);

  const handleChange = (e) => {
    const { name, value } = e.target;
    const limit = name === 'phone' ? 11 : 4;
    setFormData({ ...formData, [name]: value.replace(/\D/g, '').slice(0, limit) });
  };

  const pickContact = async () => {
    try {
      const [contact] = await navigator.contacts.select(['tel'], { multiple: false });
      if (contact?.tel?.length) {
        setFormData((f) => ({ ...f, phone: normalizePhone(contact.tel[0]) }));
      }
    } catch {
      /* user cancelled or the browser refused: they can still type the number */
    }
  };

  const goToConfirm = (e) => {
    e.preventDefault();
    setErrors({});
    setMessage('');
    if (!selectedPlan) return;
    if (!phoneOk) {
      setErrors({ phone: 'Enter a valid 11-digit phone number.' });
      return;
    }
    setStep('confirm');
  };

  const handleConfirm = async (e) => {
    e.preventDefault();
    if (loading || !selectedPlan || formData.pin.length !== 4) return;
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
      setPlanId('');
      setStep('form');
    } catch (err) {
      // wrong PIN, low balance, etc.: stay on the confirm screen
      setFormData((f) => ({ ...f, pin: '' }));
      setErrors(err.data || { detail: 'Something went wrong.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="change-password-page">
      <div className="change-password-card">
        <p className="change-password-title">Buy data</p>

        {step === 'form' && (
          <form className="change-password-form" onSubmit={goToConfirm}>
            <select value={network} onChange={(e) => setNetwork(e.target.value)}>
              {NETWORKS.map((n) => (
                <option key={n.value} value={n.value}>{n.label}</option>
              ))}
            </select>

            <select value={planType} onChange={(e) => setPlanType(e.target.value)}>
              <option value="">Select plan type</option>
              {types.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            {typesLoaded && types.length === 0 && (
              <p className="change-password-error">No plans available for this network yet.</p>
            )}

            <select value={planId} onChange={(e) => setPlanId(e.target.value)} disabled={!planType}>
              <option value="">Select a plan</option>
              {plans.map((p) => (
                <option key={p.id} value={p.id}>
                  {cleanName(p.name)} - ₦{p.price}
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
            {canPickContact && (
              <button type="button" className="data-contact-btn" onClick={pickContact}>
                📇 Choose from contacts
              </button>
            )}

            <button type="submit" className="change-password-submit" disabled={!planId || !formData.phone}>
              Continue
            </button>
          </form>
        )}

        {step === 'confirm' && selectedPlan && (
          <form className="change-password-form" onSubmit={handleConfirm}>
            <div className="data-summary">
              <div className="data-row"><span>Network</span><strong>{networkLabel}</strong></div>
              <div className="data-row"><span>Plan</span><strong>{cleanName(selectedPlan.name)}</strong></div>
              <div className="data-row"><span>Phone</span><strong>{formData.phone}</strong></div>
              <div className="data-row"><span>Amount</span><strong>₦{selectedPlan.price}</strong></div>
            </div>
            <PasswordInput
              name="pin"
              placeholder="Enter transaction PIN to confirm"
              value={formData.pin}
              onChange={handleChange}
              maxLength={4}
            />
            <button
              type="submit"
              className="change-password-submit"
              disabled={loading || formData.pin.length !== 4}
            >
              {loading ? 'Processing...' : 'Confirm purchase'}
            </button>
            <button
              type="button"
              className="data-secondary"
              onClick={() => { setStep('form'); setErrors({}); setFormData({ ...formData, pin: '' }); }}
              disabled={loading}
            >
              ← Edit details
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

        <Link to="/dashboard" className="change-password-back">← Back to home</Link>
      </div>
    </div>
  );
}