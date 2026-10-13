import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet } from '../api';

import './History.css';

import TransactionRow from './TransactionRow';

// const fmt = (value) =>
//   Number(value).toLocaleString('en-NG', { minimumFractionDigits: 2 });

// const LABELS = { deposit: 'Deposit', airtime: 'Airtime', data: 'Data' };

function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError('');
      try {
        const data = await apiGet(`/wallet/transactions/?page=${page}`);
        if (cancelled) return;
        setItems((prev) => (page === 1 ? data.results : [...prev, ...data.results]));
        setHasMore(Boolean(data.next));
      } catch (err) {
        if (cancelled) return;
        if (err.status === 401) navigate('/login');
        else setError('Could not load your transactions. Please try again.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [page, navigate]);

   return (
    <div className="history-page">
      <div className="history-header">
        <button className="history-back" onClick={() => navigate('/dashboard')} aria-label="Back">
          ←
        </button>
        <h2 className="history-title">Transaction History</h2>
      </div>

      {error && <p className="history-error">{error}</p>}
      {!loading && !error && items.length === 0 && (
        <p className="history-empty">No transactions yet.</p>
      )}

      {items.map((t) => (
        <TransactionRow key={t.id} t={t} />
      ))}

      {loading && <p className="history-empty">Loading...</p>}
      {hasMore && !loading && (
        <button className="history-more" onClick={() => setPage((p) => p + 1)}>
          Load more
        </button>
      )}
    </div>
  );
}
export default History;