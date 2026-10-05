import { useState } from 'react';
import { apiPost } from '../api';
import './Register.css';
import PasswordInput from './PasswordInput';

export default function Register() {
  const [formData, setFormData] = useState({
    full_name: '', username: '', email: '', phone_number: '',
    password: '', confirm_password: '', pin: '', confirm_pin: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('handleSubmit fired', formData);
    const result = await apiPost('/accounts/register/', formData);
    setLoading(true);
    setErrors({});
    try {
      const result = await apiPost('/accounts/register/', formData);
      console.log('Registered:', result);
    } catch (err) {
      console.log('Error:', err);
      setErrors(err.data || { detail: 'Something went wrong' });
    } finally {
      setLoading(false);
    }
  };

    const handlePhoneChange = (e) => {
    const digitsOnly = e.target.value.replace(/\D/g, '').slice(0, 11);
    setFormData({ ...formData, phone_number: digitsOnly });
  };


  return (
    <div className="register-page">
      <div className="register-card">
        <p className="register-title">Create account</p>
        <p className="register-subtitle">Buy airtime and data in seconds.</p>
        <form className="register-form" onSubmit={handleSubmit}>
          <input name="full_name" placeholder="Full name" onChange={handleChange} />
          <input name="username" placeholder="Username" onChange={handleChange} />
          <input name="email" placeholder="Email" onChange={handleChange} />
          <input name="phone_number" placeholder="Phone number" value={formData.phone_number} onChange={handlePhoneChange} inputMode="numeric" />
          <PasswordInput name="password" placeholder="Password" value={formData.password} onChange={handleChange} />
          <PasswordInput name="confirm_password" placeholder="Confirm password" value={formData.confirm_password} onChange={handleChange} />
          <PasswordInput name="pin" placeholder="4-digit PIN" value={formData.pin} onChange={handleChange} maxLength={4} />
          <PasswordInput name="confirm_pin" placeholder="Confirm PIN" value={formData.confirm_pin} onChange={handleChange} maxLength={4} />
          <button type="submit" className="register-submit" disabled={loading}>
            {loading ? 'Registering...' : 'Create account'}
          </button>
        </form>
        {Object.keys(errors).length > 0 && (
          <div className="register-errors">
            {Object.entries(errors).map(([field, msg]) => (
              <p key={field} className="register-error">
                {field}: {Array.isArray(msg) ? msg.join(', ') : msg}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}