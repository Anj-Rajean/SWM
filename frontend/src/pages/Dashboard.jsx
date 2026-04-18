import { useState, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { api } from '../services/api';
import './Dashboard.css';

function generatePassword(length = 12) {
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset.charAt(Math.floor(Math.random() * charset.length));
  }
  return password;
}

function Dashboard({ token, user, onLogout }) {
  const [entries, setEntries] = useState([]);
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingEntry, setEditingEntry] = useState(null);
  const [formData, setFormData] = useState({ title: '', username: '', password: '', url: '', notes: '' });
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    loadVault();
  }, [token]);

  const loadVault = async () => {
    const data = await api.getVault(token);
    setEntries(data.entries || []);
  };

  const handleSearch = async () => {
    if (search.trim()) {
      const data = await api.searchEntries(search, token);
      setEntries(data.entries || []);
    } else {
      loadVault();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const entryData = {
      title: formData.title,
      username: formData.username,
      password: formData.password,
      url: formData.url || null,
      notes: formData.notes || null
    };
    
    try {
      if (editingEntry) {
        await api.updateEntry(editingEntry.id, entryData, token);
        toast.success('Mot de passe mis à jour');
      } else {
        await api.addEntry(entryData, token);
        toast.success('Mot de passe ajouté');
      }
      setShowModal(false);
      setEditingEntry(null);
      setFormData({ title: '', username: '', password: '', url: '', notes: '' });
      setTimeout(() => loadVault(), 100);
    } catch (err) {
      toast.error('Erreur: ' + err.message);
    }
  };

  const handleEdit = (entry) => {
    setEditingEntry(entry);
    setFormData(entry);
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteEntry(id, token);
      toast.success('Mot de passe supprimé');
      loadVault();
    } catch (err) {
      toast.error('Erreur: ' + err.message);
    }
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(label + ' copié');
  };

  const openAddModal = () => {
    setEditingEntry(null);
    setFormData({ title: '', username: '', password: '', url: '', notes: '' });
    setShowModal(true);
  };

  const generateAndSetPassword = () => {
    setFormData({ ...formData, password: generatePassword() });
    toast.info('Mot de passe généré');
  };

  return (
    <div className="dashboard">
      <ToastContainer position="bottom-right" theme="dark" />
      <header className="dashboard-header">
        <h1>ErgoSecure</h1>
        <button className="logout-btn" onClick={onLogout}>
          Déconnexion
        </button>
      </header>

      <div className="vault-container">
        <div className="vault-controls">
          <input
            type="text"
            className="search-input"
            placeholder="Rechercher..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button className="add-btn" onClick={openAddModal}>
            + Ajouter
          </button>
        </div>

        <div className="password-grid">
          {entries.length === 0 ? (
            <p className="empty-vault">Aucun mot de passe. Ajoutez votre premier!</p>
          ) : (
            entries.map((entry) => (
              <div key={entry.id} className="password-card">
                <h3>{entry.title}</h3>
                <p>Username: {entry.username}</p>
                <p>Password: ••••••••</p>
                {entry.url && <p>URL: {entry.url}</p>}
                <div className="actions">
                  <button onClick={() => copyToClipboard(entry.username, 'Username')}>Copy</button>
                  <button onClick={() => copyToClipboard(entry.password, 'Password')}>Copy</button>
                  <button onClick={() => handleEdit(entry)}>Edit</button>
                  <button onClick={() => handleDelete(entry.id)}>Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingEntry ? 'Modifier' : 'Ajouter un mot de passe'}</h2>
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                placeholder="Titre"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />
              <input
                type="text"
                placeholder="Username"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                required
              />
              <div className="password-input-group">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Mot de passe"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
                <button type="button" onClick={generateAndSetPassword}>Générer</button>
                <button type="button" onClick={() => setShowPassword(!showPassword)}>
                  {showPassword ? 'Masquer' : 'Afficher'}
                </button>
              </div>
              <input
                type="url"
                placeholder="URL (optionnel)"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              />
              <textarea
                placeholder="Notes (optionnel)"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={2}
              />
              <div className="modal-buttons">
                <button type="button" className="cancel-btn" onClick={() => setShowModal(false)}>Annuler</button>
                <button type="submit" className="save-btn">Sauvegarder</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
