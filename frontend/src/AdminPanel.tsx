import React, { useState, useEffect } from 'react';
import { Users, Link2, Plus, Trash2, Shield, User, ExternalLink, Calendar, TrendingUp, ArrowLeft } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from './AuthContext';

interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

interface URL {
  id: number;
  original_url: string;
  short_code: string;
  short_url: string;
  created_at: string;
  click_count: number;
  expires_at?: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

interface AdminPanelProps {
  onBack?: () => void;
}

export default function AdminPanel({ onBack }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<'users' | 'urls' | 'create-user'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [urls, setUrls] = useState<URL[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Create user form state
  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newIsAdmin, setNewIsAdmin] = useState(false);
  const [createUserLoading, setCreateUserLoading] = useState(false);
  
  const { token } = useAuth();

  const createApiRequest = async (endpoint: string, options: RequestInit = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...(options.headers as Record<string, string>),
    };

    return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  };

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await createApiRequest('/api/admin/users');
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        throw new Error('Failed to fetch users');
      }
    } catch (err) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const fetchUrls = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await createApiRequest('/api/admin/urls');
      if (response.ok) {
        const data = await response.json();
        setUrls(data);
      } else {
        throw new Error('Failed to fetch URLs');
      }
    } catch (err) {
      setError('Failed to load URLs');
    } finally {
      setLoading(false);
    }
  };

  const createUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateUserLoading(true);
    setError('');

    try {
      const response = await createApiRequest('/api/admin/users', {
        method: 'POST',
        body: JSON.stringify({
          username: newUsername,
          email: newEmail,
          password: newPassword,
          is_admin: newIsAdmin
        }),
      });

      if (response.ok) {
        setNewUsername('');
        setNewEmail('');
        setNewPassword('');
        setNewIsAdmin(false);
        setActiveTab('users');
        fetchUsers();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create user');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create user');
    } finally {
      setCreateUserLoading(false);
    }
  };

  const deleteUser = async (userId: number, username: string) => {
    if (!confirm(`Are you sure you want to delete user "${username}" and all their URLs? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await createApiRequest(`/api/admin/users/${userId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchUsers();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete user');
    }
  };

  useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'urls') {
      fetchUrls();
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen w-full bg-gray-900 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-xl" style={{backgroundColor: '#FF7BAC'}}>
                <Shield className="w-5 h-5 sm:w-6 sm:h-6 text-gray-900" />
              </div>
              <div className="min-w-0 flex-1">
                <h1 className="text-2xl sm:text-3xl font-bold text-white">Admin Panel</h1>
                <p className="text-gray-300 text-sm sm:text-base">Manage users and URLs</p>
              </div>
            </div>
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors text-sm sm:text-base touch-manipulation flex-shrink-0"
              >
                <ArrowLeft className="w-3 h-3 sm:w-4 sm:h-4" />
                <span className="hidden xs:inline">Back to URL Shortener</span>
                <span className="xs:hidden">Back</span>
              </button>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex flex-wrap gap-1 mb-4 sm:mb-6 bg-gray-800 p-1 rounded-lg">
          <button
            onClick={() => setActiveTab('users')}
            className={clsx(
              'px-3 sm:px-6 py-2 sm:py-3 rounded-md font-semibold text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 touch-manipulation',
              activeTab === 'users' 
                ? 'text-gray-900' 
                : 'text-gray-900 hover:text-gray-700'
            )}
            style={activeTab === 'users' ? {backgroundColor: '#FF7BAC'} : {backgroundColor: 'white'}}
          >
            <Users className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden xs:inline">Users</span>
          </button>
          <button
            onClick={() => setActiveTab('urls')}
            className={clsx(
              'px-3 sm:px-6 py-2 sm:py-3 rounded-md font-semibold text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 touch-manipulation',
              activeTab === 'urls' 
                ? 'text-gray-900' 
                : 'text-gray-900 hover:text-gray-700'
            )}
            style={activeTab === 'urls' ? {backgroundColor: '#FF7BAC'} : {backgroundColor: 'white'}}
          >
            <Link2 className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden xs:inline">All URLs</span>
            <span className="xs:hidden">URLs</span>
          </button>
          <button
            onClick={() => setActiveTab('create-user')}
            className={clsx(
              'px-3 sm:px-6 py-2 sm:py-3 rounded-md font-semibold text-xs sm:text-sm transition-colors flex items-center gap-1 sm:gap-2 touch-manipulation',
              activeTab === 'create-user' 
                ? 'text-gray-900' 
                : 'text-gray-900 hover:text-gray-700'
            )}
            style={activeTab === 'create-user' ? {backgroundColor: '#FF7BAC'} : {backgroundColor: 'white'}}
          >
            <Plus className="w-4 h-4" />
            Create User
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border-2 border-red-300 p-4 rounded-lg mb-6">
            <p className="text-red-800 font-semibold">
              {error}
            </p>
          </div>
        )}

        {/* Content */}
        {activeTab === 'users' && (
          <div className="bg-gray-800 rounded-xl p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">All Users</h2>
            {loading ? (
              <div className="flex items-center justify-center py-8 sm:py-12">
                <div className="animate-spin rounded-full h-6 w-6 sm:h-8 sm:w-8 border-2 border-gray-300 border-t-transparent"></div>
              </div>
            ) : users.length === 0 ? (
              <p className="text-gray-300 text-center py-8 sm:py-12 text-sm sm:text-base">No users found</p>
            ) : (
              <div className="space-y-3 sm:space-y-4">
                {users.map((user) => (
                  <div key={user.id} className="bg-gray-700 border border-gray-600 rounded-lg p-3 sm:p-4">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 sm:gap-3 mb-2">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 sm:w-5 sm:h-5 text-gray-300" />
                            <span className="font-semibold text-white text-sm sm:text-base break-all">{user.username}</span>
                          </div>
                          {user.is_admin && (
                            <div className="px-2 py-1 bg-yellow-600 text-yellow-100 text-xs font-semibold rounded flex-shrink-0">
                              ADMIN
                            </div>
                          )}
                          {!user.is_active && (
                            <div className="px-2 py-1 bg-red-600 text-red-100 text-xs font-semibold rounded flex-shrink-0">
                              INACTIVE
                            </div>
                          )}
                        </div>
                        <p className="text-gray-300 text-xs sm:text-sm mb-2 break-all">{user.email}</p>
                        <div className="flex items-center gap-2 text-gray-400 text-xs sm:text-sm">
                          <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
                          <span>Created: {new Date(user.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => deleteUser(user.id, user.username)}
                          className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors touch-manipulation"
                          title="Delete user"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'urls' && (
          <div className="bg-gray-800 rounded-xl p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">All URLs</h2>
            {loading ? (
              <div className="flex items-center justify-center py-8 sm:py-12">
                <div className="animate-spin rounded-full h-6 w-6 sm:h-8 sm:w-8 border-2 border-gray-300 border-t-transparent"></div>
              </div>
            ) : urls.length === 0 ? (
              <p className="text-gray-300 text-center py-8 sm:py-12 text-sm sm:text-base">No URLs found</p>
            ) : (
              <div className="space-y-4">
                {urls.map((url) => (
                  <div key={url.id} className="bg-gray-700 border border-gray-600 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-3">
                          <a
                            href={url.short_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-mono text-base font-semibold hover:underline transition-colors hover:opacity-80"
                            style={{color: '#FF7BAC'}}
                          >
                            {url.short_url}
                          </a>
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        </div>
                        
                        <div className="text-gray-300 mb-3 text-sm break-all">
                          {url.original_url}
                        </div>
                        
                        <div className="flex items-center gap-6 text-gray-400 text-sm">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-3 h-3" />
                            <span>Created: {new Date(url.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-3 h-3" />
                            <span>Clicks: {url.click_count}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'create-user' && (
          <div className="bg-gray-800 rounded-xl p-4 sm:p-6">
            <h2 className="text-lg sm:text-xl font-bold text-white mb-3 sm:mb-4">Create New User</h2>
            <form onSubmit={createUser} className="space-y-3 sm:space-y-4 max-w-md">
              <div>
                <label htmlFor="newUsername" className="block text-sm font-semibold text-white mb-2">
                  Username
                </label>
                <input
                  type="text"
                  id="newUsername"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Enter username"
                  className="w-full px-3 py-2 bg-gray-100 border-2 border-gray-300 
                           text-gray-900 text-sm placeholder-gray-500 outline-none transition-colors rounded-lg"
                  onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                  onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                  required
                />
              </div>

              <div>
                <label htmlFor="newEmail" className="block text-sm font-semibold text-white mb-2">
                  Email
                </label>
                <input
                  type="email"
                  id="newEmail"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="Enter email"
                  className="w-full px-3 py-2 bg-gray-100 border-2 border-gray-300 
                           text-gray-900 text-sm placeholder-gray-500 outline-none transition-colors rounded-lg"
                  onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                  onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                  required
                />
              </div>

              <div>
                <label htmlFor="newPassword" className="block text-sm font-semibold text-white mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter password (min 6 characters)"
                  className="w-full px-3 py-2 bg-gray-100 border-2 border-gray-300 
                           text-gray-900 text-sm placeholder-gray-500 outline-none transition-colors rounded-lg"
                  onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                  onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                  required
                  minLength={6}
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="newIsAdmin"
                  checked={newIsAdmin}
                  onChange={(e) => setNewIsAdmin(e.target.checked)}
                  className="w-4 h-4 accent-pink-500"
                />
                <label htmlFor="newIsAdmin" className="text-sm font-semibold text-white">
                  Make this user an admin
                </label>
              </div>

              <button
                type="submit"
                disabled={createUserLoading}
                className="px-4 sm:px-6 py-2 sm:py-2 text-gray-900 text-sm font-semibold transition-colors rounded-lg hover:opacity-90 disabled:opacity-50 flex items-center gap-2 touch-manipulation"
                style={{backgroundColor: '#FF7BAC'}}
              >
                {createUserLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-900 border-t-transparent"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4" />
                    Create User
                  </>
                )}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}