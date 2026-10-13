import './History.css';

const LABELS = { deposit: 'Deposit', airtime: 'Airtime', data: 'Data' };

const fmt = (value) =>
  Number(value).toLocaleString('en-NG', { minimumFractionDigits: 2 });

function TransactionRow({ t }) {
  const isCredit = t.type === 'deposit';
  return (
    <li className="history-item">
      <div>
        <div className="history-type">{LABELS[t.type] || t.type}</div>
        <div className="history-meta">{new Date(t.created_at).toLocaleString()}</div>
        {t.recipient && <div className="history-meta">To: {t.recipient}</div>}
        <div className="history-meta">Ref: {t.reference}</div>
      </div>
      <div className="history-right">
        <div className={`history-amount ${isCredit ? 'credit' : 'debit'}`}>
          {isCredit ? '+' : '−'}₦{fmt(t.amount)}
        </div>
        <div className="history-balance">Balance ₦{fmt(t.balance_after)}</div>
      </div>
    </li>
  );
}

export default TransactionRow;