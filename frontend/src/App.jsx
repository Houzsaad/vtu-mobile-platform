import { Routes, Route } from 'react-router-dom';
import Register from './components/Register';
import Login from './components/Login';
import Dashboard from './components/Dasboard';
import Profile from './components/Profile';
import ChangePassword from './components/ChangePassword';

function App() {
  return (
    <Routes>
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Register />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/profile" element={<Profile />} />
      
      <Route path="/change-password" element={<ChangePassword />} />
      <Route path="/change-pin" element={<p>Change PIN coming soon</p>} />
      
    </Routes>
  );
}

export default App;