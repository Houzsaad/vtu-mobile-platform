import { useState } from 'react';

export default function PasswordInput({ name, placeholder, value, onChange, maxLength }) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="password-field">
      <input
        name={name}
        type={visible ? 'text' : 'password'}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        maxLength={maxLength}
      />
      <button
        type="button"
        className="password-toggle"
        onClick={() => setVisible(!visible)}
        aria-label={visible ? 'Hide password' : 'Show password'}
      >
        {visible ? '🙈' : '👁️'}
      </button>
    </div>
  );
}