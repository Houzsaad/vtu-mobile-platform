import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet, apiPost } from '../api';
import './Fund.css';

const QUICK = [500, 1000, 2000, 5000];
const fmt = (v) => Number(v).toLocaleString('en-NG', { minimumFractionDigits: 2 });

function useCountdown(expiresAt) {
  const [left, setLeft] = useState(0);
  useEffect(() => {
    if (!expiresAt) return;
    const tick = () =>
      setLeft(Math.max(0, Math.floor((new Date(expiresAt) - Date.now()) / 1000)));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);
  const m = String(Math.floor(left / 60)).padStart(2, '0');
  const s = String(left % 60).padStart(2, '0');
  return { left, label: `${m}:${s}` };
}

function Fund() {
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [req, setReq] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const { left, label } = useCountdown(req?.expires_at);

  // Poll while waiting for the transfer
  useEffect(() => {
    if (!req || req.status !== 'pending') return;
    const id = setInterval(async () => {
      try {
        const data = await apiGet(`/funding/${req.reference}/`);
        setReq(data);
      } catch {
        /* keep trying */
      }
    }, 5000);
    return () => clearInterval(id);
  }, [req]);

  async function start(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await apiPost('/funding/initiate/', { amount }, { auth: true });
      setReq(data);
    } catch (err) {
      setError(err?.message || 'Could not start funding. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(req.account_number);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* ignore */
    }
  }

  function reset() {
    setReq(null);
    setAmount('');
    setError('');
  }

  return (
    <div className="fund-page">
      <div className="fund-header">
        <button className="fund-back" onClick={() => navigate('/dashboard')} aria-label="Back">
          ←
        </button>
        <h2 className="fund-title">Fund Wallet</h2>
      </div>

      {!req && (
        <form className="fund-card" onSubmit={start}>
          <label className="fund-label" htmlFor="amount">Amount (₦)</label>
          <input
            id="amount"
            className="fund-input"
            type="number"
            inputMode="numeric"
            min="100"
            step="1"
            placeholder="Enter amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            required
          />
          <div className="fund-quick">
            {QUICK.map((q) => (
              <button type="button" key={q} onClick={() => setAmount(String(q))}>
                ₦{q.toLocaleString()}
              </button>
            ))}
          </div>
          {error && <p className="fund-error">{error}</p>}
          <button className="fund-primary" disabled={loading || !amount}>
            {loading ? 'Please wait...' : 'Fund wallet'}
          </button>
          <p className="fund-note">Pay by bank transfer. No fees.</p>
        </form>
      )}

      {req?.status === 'pending' && (
        <div className="fund-card">
          <p className="fund-note">Transfer exactly</p>
          <p className="fund-amount">₦{fmt(req.amount)}</p>
          <div className="fund-row"><span>Bank</span><strong>{req.bank_name}</strong></div>
          <div className="fund-row"><span>Account name</span><strong>{req.account_name}</strong></div>
          <div className="fund-row">
            <span>Account number</span>
            <strong className="fund-acct">{req.account_number}</strong>
          </div>
          <button className="fund-secondary" onClick={copy}>
            {copied ? 'Copied ✓' : 'Copy account number'}
          </button>
          <p className="fund-timer">
            {left > 0 ? `Account expires in ${label}` : 'Checking...'}
          </p>
          <p className="fund-note">
            This account is for this payment only. Send the exact amount and your wallet
            will be credited automatically.
          </p>
        </div>
      )}

      {req?.status === 'success' && (
        <div className="fund-card fund-center">
          <p className="fund-big">✅</p>
          <p className="fund-amount">₦{fmt(req.amount)} added</p>
          <p className="fund-note">Your wallet has been credited.</p>
          <button className="fund-primary" onClick={() => navigate('/dashboard')}>
            Back to home
          </button>
        </div>
      )}

      {(req?.status === 'expired' || req?.status === 'review') && (
        <div className="fund-card fund-center">
          <p className="fund-big">{req.status === 'review' ? '🔎' : '⌛'}</p>
          <p className="fund-amount">
            {req.status === 'review' ? 'Payment under review' : 'Account expired'}
          </p>
          <p className="fund-note">
            {req.status === 'review'
              ? 'We received a payment that needs a quick check. It will be sorted out shortly.'
              : 'If you already sent the money, it will still be credited. Otherwise, start again.'}
          </p>
          <button className="fund-primary" onClick={reset}>
            {req.status === 'review' ? 'Done' : 'Try again'}
          </button>
        </div>
      )}
    </div>
  );
}

export default Fund;