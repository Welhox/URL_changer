import React, { useState, useEffect } from 'react';
import { Link2, Copy, Check, BarChart3, ExternalLink, TrendingUp, ChevronDown, ChevronUp, Trash2, LogOut, User } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from './AuthContext';

interface URLResult {
  id: number;
  original_url: string;
  short_code: string;
  short_url: string;
  created_at: string;
  click_count: number;
}

interface URLStats {
  short_code: string;
  original_url: string;
  click_count: number;
  created_at: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');
const API_KEY = import.meta.env.VITE_API_KEY;

const createApiRequest = (authToken: string | null) => {
  return async (endpoint: string, options: RequestInit = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (import.meta.env.PROD && API_KEY) {
      headers['X-API-Key'] = API_KEY;
    }

    return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  };
};

export default function URLShortener() {
  const [url, setUrl] = useState('');
  const [customCode, setCustomCode] = useState('');
  const [result, setResult] = useState<URLResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [recentUrls, setRecentUrls] = useState<URLResult[]>([]);
  const [showRecentUrls, setShowRecentUrls] = useState(false);

  const { user, token, logout } = useAuth();

  // Load user's URLs from API when authenticated
  useEffect(() => {
    if (token) {
      loadUserUrls();
    }
  }, [token]);

  const loadUserUrls = async () => {
    if (!token) return;
    
    const apiRequest = createApiRequest(token);
    
    try {
      const response = await apiRequest('/api/my-urls');
      if (response.ok) {
        const urls = await response.json();
        setRecentUrls(urls);
        localStorage.setItem('recentUrls', JSON.stringify(urls));
      }
    } catch (err) {
      console.error('Failed to load user URLs:', err);
    }
  };

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && recentUrls.length > 0) {
        refreshRecentUrls();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [recentUrls]);

  const saveToRecent = (newUrl: URLResult) => {
    const updated = [newUrl, ...recentUrls];
    setRecentUrls(updated);
    localStorage.setItem('recentUrls', JSON.stringify(updated));
  };

  const clearRecentUrls = () => {
    setRecentUrls([]);
    localStorage.removeItem('recentUrls');
  };

  const refreshRecentUrls = async () => {
    if (recentUrls.length === 0 || !token) return;
    
    const apiRequest = createApiRequest(token);
    
    try {
      const updatedUrls = await Promise.all(
        recentUrls.map(async (item) => {
          try {
            const response = await apiRequest(`/api/stats/${item.short_code}`);
            if (response.ok) {
              const stats = await response.json();
              return { ...item, click_count: stats.click_count };
            }
          } catch (err) {
            console.error(`Failed to refresh stats for ${item.short_code}:`, err);
          }
          return item;
        })
      );
      
      setRecentUrls(updatedUrls);
      localStorage.setItem('recentUrls', JSON.stringify(updatedUrls));
    } catch (err) {
      console.error('Failed to refresh recent URLs:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !token) return;

    setLoading(true);
    setError('');
    setResult(null);

    const apiRequest = createApiRequest(token);

    try {
      const payload: any = { url: url.trim() };
      if (customCode.trim()) {
        payload.custom_code = customCode.trim();
      }

      const response = await apiRequest('/api/shorten', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to shorten URL');
      }

      const data = await response.json();
      setResult(data);
      saveToRecent(data);
      setUrl('');
      setCustomCode('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getStats = async (shortCode: string) => {
    if (!token) return;
    
    const apiRequest = createApiRequest(token);
    
    try {
      const response = await apiRequest(`/api/stats/${shortCode}`);
      if (response.ok) {
        const stats = await response.json();
        alert(`Stats for ${shortCode}:\nClicks: ${stats.click_count}\nCreated: ${new Date(stats.created_at).toLocaleString()}`);
      }
    } catch (err) {
      console.error('Failed to get stats:', err);
    }
  };

  const deleteUrl = async (shortCode: string, originalUrl: string) => {
    if (!token) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to delete this URL?\n\nShort URL: ${shortCode}\nOriginal: ${originalUrl}\n\nThis action cannot be undone.`
    );
    
    if (!confirmed) return;

    const apiRequest = createApiRequest(token);

    try {
      const response = await apiRequest(`/api/urls/${shortCode}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove from recent URLs list
        const updatedUrls = recentUrls.filter(item => item.short_code !== shortCode);
        setRecentUrls(updatedUrls);
        localStorage.setItem('recentUrls', JSON.stringify(updatedUrls));
        
        // Show success message
        alert('URL deleted successfully!');
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete URL');
      }
    } catch (err) {
      console.error('Failed to delete URL:', err);
      alert(`Failed to delete URL: ${err instanceof Error ? err.message : 'Something went wrong'}`);
    }
  };

  return (
    <div className="min-h-screen w-full bg-teal-100 flex justify-center">
      <div className="max-w-2xl px-6 py-12">
        {/* User Info Header */}
        {user && (
          <div className="bg-white rounded-2xl p-6 mb-8 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-teal-600 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-800">Welcome, {user.username}!</h3>
                  <p className="text-slate-600">{user.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl font-semibold transition-colors"
              >
                <LogOut className="w-5 h-5" />
                Logout
              </button>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-teal-600 rounded-xl mb-8">
            <Link2 className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-6xl font-bold text-slate-800 mb-6">
            URL Changer
          </h1>
          <p className="text-slate-600 text-2xl">
            Transform your URLs and make them trackable
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl p-10 mb-10 shadow-lg">
          <form onSubmit={handleSubmit} className="space-y-8">
            <div>
              <label htmlFor="url" className="block text-xl font-bold text-slate-800 mb-4">
                Enter your long URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/very/long/url/path/to/your/content"
                className="w-full px-6 py-5 bg-slate-50 border-2 border-slate-300 rounded-xl 
                         text-slate-800 text-xl placeholder-slate-500 focus:border-teal-500 
                         outline-none transition-colors"
                required
              />
            </div>

            <div>
              <label htmlFor="customCode" className="block text-xl font-bold text-slate-800 mb-4">
                Custom short code (optional)
              </label>
              <input
                type="text"
                id="customCode"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                placeholder="my-awesome-link"
                className="w-full px-6 py-5 bg-slate-50 border-2 border-slate-300 rounded-xl 
                         text-slate-800 text-xl placeholder-slate-500 focus:border-teal-500 
                         outline-none transition-colors"
                pattern="[a-zA-Z0-9_-]+"
                maxLength={20}
              />
              <p className="text-slate-600 mt-3 text-lg">
                Only letters, numbers, hyphens, and underscores allowed
              </p>
            </div>

            {error && (
              <div className="bg-red-100 border-2 border-red-400 rounded-xl p-6">
                <p className="text-red-800 text-xl font-semibold">
                  {error}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !url.trim()}
              className={clsx(
                'w-full py-6 px-8 rounded-xl font-bold text-2xl transition-colors shadow-lg',
                loading || !url.trim()
                  ? 'bg-slate-400 cursor-not-allowed text-slate-600'
                  : 'bg-teal-600 hover:bg-teal-700 text-white'
              )}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-slate-600 border-t-transparent inline-block mr-4"></div>
                  Shortening...
                </>
              ) : (
                'Shorten URL'
              )}
            </button>
          </form>

          {result && (
            <div className="mt-10 p-8 bg-green-100 border-2 border-green-400 rounded-2xl shadow-lg">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                  <Check className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-green-800">
                  Your shortened URL is ready!
                </h3>
              </div>
              
              <div className="bg-white rounded-xl p-6 border border-slate-200">
                <div className="flex items-center gap-4 mb-4">
                  <input
                    type="text"
                    value={result.short_url}
                    readOnly
                    className="flex-1 px-4 py-4 bg-slate-50 border-2 border-slate-300 rounded-lg text-slate-800 
                             text-xl font-mono focus:outline-none"
                  />
                  <button
                    onClick={() => copyToClipboard(result.short_url)}
                    className={clsx(
                      'px-6 py-4 rounded-lg font-bold text-xl transition-colors shadow-lg',
                      copied 
                        ? 'bg-green-600 text-white' 
                        : 'bg-teal-600 hover:bg-teal-700 text-white'
                    )}
                  >
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                
                <div className="text-slate-700 text-lg">
                  <span className="font-semibold">Original:</span>{' '}
                  <span className="break-all">{result.original_url}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recent URLs Dropdown */}
        {recentUrls.length > 0 && (
          <div className="bg-white rounded-2xl p-8 shadow-lg border border-slate-200">
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={() => setShowRecentUrls(!showRecentUrls)}
                className="flex items-center gap-4 text-2xl font-bold text-slate-800 hover:text-teal-600 transition-colors"
              >
                Recent URLs ({recentUrls.length})
                {showRecentUrls ? (
                  <ChevronUp className="w-8 h-8" />
                ) : (
                  <ChevronDown className="w-8 h-8" />
                )}
              </button>
              
              {showRecentUrls && (
                <div className="flex gap-4">
                  <button
                    onClick={refreshRecentUrls}
                    className="px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold transition-colors shadow-lg"
                  >
                    Refresh Stats
                  </button>
                  <button
                    onClick={clearRecentUrls}
                    className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold transition-colors shadow-lg"
                  >
                    Clear History
                  </button>
                </div>
              )}
            </div>
            
            {showRecentUrls && (
              <div className="space-y-4">
                {recentUrls.map((item) => (
                  <div key={item.id} className="bg-slate-50 border border-slate-200 rounded-xl p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-4">
                          <a
                            href={item.short_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-teal-600 hover:text-teal-700 font-mono text-xl font-semibold hover:underline transition-colors"
                          >
                            {item.short_url}
                          </a>
                          <ExternalLink className="w-5 h-5 text-slate-500" />
                        </div>
                        
                        <div className="text-slate-700 mb-4 text-lg break-all">
                          {item.original_url}
                        </div>
                        
                        <div className="flex items-center gap-8 text-slate-600 text-lg">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span>Created: {new Date(item.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4" />
                            <span>Clicks: {item.click_count}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-4 ml-8">
                        <button
                          onClick={() => getStats(item.short_code)}
                          className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold transition-colors shadow-lg"
                        >
                          <BarChart3 className="w-5 h-5" />
                          Stats
                        </button>
                        <button
                          onClick={() => copyToClipboard(item.short_url)}
                          className="flex items-center gap-2 px-6 py-3 bg-slate-600 hover:bg-slate-700 text-white rounded-xl font-bold transition-colors shadow-lg"
                        >
                          <Copy className="w-5 h-5" />
                          Copy
                        </button>
                        <button
                          onClick={() => deleteUrl(item.short_code, item.original_url)}
                          className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-bold transition-colors shadow-lg"
                        >
                          <Trash2 className="w-5 h-5" />
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}