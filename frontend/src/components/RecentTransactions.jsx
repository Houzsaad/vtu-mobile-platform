import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiGet } from '../api';
import TransactionRow from './TransactionRow';
import './RecentTransactions.css';

function RecentTransactions() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    apiGet('/wallet/transactions/')
      .then((data) => {
        if (!cancelled) setItems(data.results.slice(0, 3));
      })
      .catch(() => {
        if (!cancelled) setError(true);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="recent">
      <div className="recent-header">
        <h3 className="recent-title">Recent Transactions</h3>
        <button className="recent-viewall" onClick={() => navigate('/history')}>
          View all
        </button>
      </div>

      {loading && <p className="recent-empty">Loading...</p>}
      {error && <p className="recent-empty">Could not load transactions.</p>}
      {!loading && !error && items.length === 0 && (
        <p className="recent-empty">No transactions yet.</p>
      )}

      <ul className="history-list">
        {items.map((t) => (
          <TransactionRow key={t.id} t={t} />
        ))}
      </ul>
    </section>
  );
}

export default RecentTransactions;