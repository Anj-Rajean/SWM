import { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { api } from './services/api';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    if (token) {
      api.verify(token).then((res) => {
        if (res.valid) {
          setUser({ email: res.email });
        } else {
          localStorage.removeItem('token');
          setToken(null);
        }
      });
    }
  }, [token]);

  const handleLogin = (newToken, userData) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    setUser(userData);
  };

  const handleLogout = () => {
    const currentToken = localStorage.getItem('token');
    if (currentToken) {
      api.logout(currentToken);
    }
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setShowRegister(false);
    toast.info('Logged out');
  };

  if (!token) {
    return showRegister ? (
      <Register onRegister={(t, u) => handleLogin(t, u)} />
    ) : (
      <Login onShowRegister={() => setShowRegister(true)} />
    );
  }

  return <Dashboard token={token} user={user} onLogout={handleLogout} />;
}

export default App;
