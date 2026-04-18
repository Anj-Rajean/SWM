const API_URL = 'http://127.0.0.1:3000';

export const api = {
  async register(email, password) {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(email, password) {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async logout(token) {
    const res = await fetch(`${API_URL}/api/auth/logout?token=${token}`, {
      method: 'POST'
    });
    return res.json();
  },

  async verify(token) {
    const res = await fetch(`${API_URL}/api/auth/verify?token=${token}`);
    return res.json();
  },

  async getVault(token) {
    const res = await fetch(`${API_URL}/api/vault`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  },

  async addEntry(entry, token) {
    const res = await fetch(`${API_URL}/api/vault/entries`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(entry)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add entry');
    }
    return res.json();
  },

  async updateEntry(id, entry, token) {
    const res = await fetch(`${API_URL}/api/vault/entries/${id}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(entry)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to update entry');
    }
    return res.json();
  },

  async deleteEntry(id, token) {
    const res = await fetch(`${API_URL}/api/vault/entries/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  },

  async searchEntries(query, token) {
    const res = await fetch(`${API_URL}/api/vault/entries/search?q=${encodeURIComponent(query)}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  }
};
