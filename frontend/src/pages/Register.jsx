import { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { api } from '../services/api';
import './Register.css';

function PasswordStrength({ password }) {
  const getStrength = () => {
    if (!password) return { level: 0, text: '' };
    
    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    
    if (score <= 1) return { level: 1, text: 'Faible' };
    if (score <= 2) return { level: 2, text: 'Moyen' };
    if (score <= 3) return { level: 3, text: 'Bon' };
    return { level: 4, text: 'Fort' };
  };
  
  const strength = getStrength();
  const colors = ['', '#ff6b6b', '#FFC570', '#4caf50', '#81A6C6'];
  
  return (
    <div className="password-strength">
      <div className="strength-bars">
        {[1, 2, 3, 4].map((level) => (
          <div 
            key={level} 
            className={`strength-bar ${strength.level >= level ? 'active' : ''}`}
            style={{ backgroundColor: strength.level >= level ? colors[strength.level] : '#D2C4B4' }}
          />
        ))}
      </div>
      {password && <span className="strength-text">{strength.text}</span>}
    </div>
  );
}

function Register({ onRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }

    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setLoading(true);

    try {
      const result = await api.register(email, password);
      if (result.token) {
        toast.success('Compte créé avec succès');
        onRegister(result.token, { email });
      }
    } catch (err) {
      setError(err.message || 'Échec de la création du compte');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-page">
      <ToastContainer position="bottom-right" theme="dark" />
      <div className="register-container">
        <h1>Créer un compte</h1>
        <form className="register-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Mot de passe"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <PasswordStrength password={password} />
          <input
            type="password"
            placeholder="Confirmer le mot de passe"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Création...' : 'Créer le compte'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>
      </div>
    </div>
  );
}

export default Register;
