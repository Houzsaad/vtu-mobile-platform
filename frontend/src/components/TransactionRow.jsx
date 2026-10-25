// import './History.css';

// const LABELS = { deposit: 'Deposit', airtime: 'Airtime', data: 'Data' };

// const fmt = (value) =>
//   Number(value).toLocaleString('en-NG', { minimumFractionDigits: 2 });

// function TransactionRow({ t }) {
//   const isCredit = t.type === 'deposit';
//   return (
//     <li className="history-item">
//       <div>
//         <div className="history-type">{LABELS[t.type] || t.type}</div>
//         <div className="history-meta">{new Date(t.created_at).toLocaleString()}</div>
//         {t.recipient && <div className="history-meta">To: {t.recipient}</div>}
//         <div className="history-meta">Ref: {t.reference}</div>
//       </div>
//       <div className="history-right">
//         <div className={`history-amount ${isCredit ? 'credit' : 'debit'}`}>
//           {isCredit ? '+' : '−'}₦{fmt(t.amount)}
//         </div>
//         <div className="history-balance">Balance ₦{fmt(t.balance_after)}</div>
//       </div>
//     </li>
//   );
// }

// export default TransactionRow;

import './History.css';

const LABELS = { deposit: 'Deposit', airtime: 'Airtime', data: 'Data' };

const fmt = (value) =>
  Number(value).toLocaleString('en-NG', { minimumFractionDigits: 2 });

function getState(t) {
  if (t.refunded) return { key: 'refunded', label: 'Refunded' };
  if (t.status === 'failed') return { key: 'failed', label: 'Failed' };
  if (t.status === 'pending') return { key: 'pending', label: 'Pending' };
  return { key: 'success', label: 'Successful' };
}

function TransactionRow({ t }) {
  const isCredit = t.type === 'deposit';
  const state = getState(t);

  let sign = isCredit ? '+' : '−';
  let amountClass = isCredit ? 'credit' : 'debit';
  if (state.key === 'refunded' || state.key === 'failed') {
    sign = '';
    amountClass = 'muted';
  } else if (state.key === 'pending') {
    sign = '';
    amountClass = 'hold';
  }

  return (
    <li className="history-item">
      <div>
        <div className="history-type">{LABELS[t.type] || t.type}</div>
        <div className="history-meta">{new Date(t.created_at).toLocaleString()}</div>
        {t.recipient && <div className="history-meta">To: {t.recipient}</div>}
        <div className="history-meta">Ref: {t.reference}</div>
      </div>
      <div className="history-right">
        <div className={`history-amount ${amountClass}`}>
          {sign}₦{fmt(t.amount)}
        </div>
        <span className={`history-badge ${state.key}`}>{state.label}</span>
        <div className="history-balance">Balance ₦{fmt(t.balance_after)}</div>
      </div>
    </li>
  );
}

export default TransactionRow;