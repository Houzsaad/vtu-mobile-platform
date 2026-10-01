import { useState } from 'react';
import { apiPost } from '../api';

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
    <form onSubmit={handleSubmit}>
      <input name="full_name" placeholder="Full Name" onChange={handleChange} />
      <input name="username" placeholder="Username" onChange={handleChange} />
      <input name="email" placeholder="Email" onChange={handleChange} />
      <input name="phone_number" placeholder="Phone Number" value={formData.phone_number} onChange={handlePhoneChange} inputMode="numeric" />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} />
      <input name="confirm_password" type="password" placeholder="Confirm Password" onChange={handleChange} />
      <input name="pin" type="password" maxLength={4} placeholder="PIN" onChange={handleChange} />
      <input name="confirm_pin" type="password" maxLength={4} placeholder="Confirm PIN" onChange={handleChange} />
      <button type="submit" disabled={loading}>{loading ? 'Registering...' : 'Register'}</button>
      {Object.entries(errors).map(([field, msg]) => (
        <p key={field} style={{ color: 'red' }}>{field}: {Array.isArray(msg) ? msg.join(', ') : msg}</p>
      ))}
    </form>
  );
}
