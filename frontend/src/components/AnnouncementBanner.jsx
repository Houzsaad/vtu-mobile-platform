import { useEffect, useState } from 'react';
import './AnnouncementBanner.css';

const BASE_URL = import.meta.env.VITE_API_URL;
const KEY = 'dismissed_announcements';

function readDismissed() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];
  } catch {
    return [];
  }
}

export default function AnnouncementBanner() {
  const [items, setItems] = useState([]);
  const [dismissed, setDismissed] = useState(readDismissed);

  useEffect(() => {
    let cancelled = false;
    fetch(`${BASE_URL}/announcements/`)
      .then((r) => (r.ok ? r.json() : []))
      .then((list) => { if (!cancelled && Array.isArray(list)) setItems(list); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  const close = (id) => {
    const next = [...dismissed, id];
    setDismissed(next);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
    } catch {
      /* storage blocked: it just returns next visit */
    }
  };

  const visible = items.filter((a) => !dismissed.includes(a.id));
  if (visible.length === 0) return null;

  return (
    <div className="announcements">
      {visible.map((a) => (
        <div key={a.id} className={`announcement ${a.level}`} role="status">
          <div className="announcement-text">
            <strong>{a.title}</strong>
            <span>{a.message}</span>
          </div>
          <button
            type="button"
            className="announcement-close"
            onClick={() => close(a.id)}
            aria-label="Dismiss"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}