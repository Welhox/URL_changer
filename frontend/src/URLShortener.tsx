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
    <div className="min-h-screen w-full bg-gray-900 flex justify-center pb-16">
      <div className="max-w-2xl px-6 py-8">
        {/* User Info Header */}
        {user && (
          <div className="bg-gray-800 rounded-xl p-4 mb-6 shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{backgroundColor: '#FF7BAC'}}>
                  <User className="w-5 h-5 text-gray-900" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Welcome, {user.username}!</h3>
                  <p className="text-gray-300 text-sm">{user.email}</p>
                </div>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors text-sm"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-xl mb-4" style={{backgroundColor: '#FF7BAC'}}>
            <Link2 className="w-8 h-8 text-gray-900" />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">
            URL Changer
          </h1>
          <p className="text-gray-300 text-lg">
            Transform your URLs and make them trackable
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-gray-800 rounded-xl p-6 mb-6 shadow-lg">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-base font-bold text-white mb-3">
                Enter your long URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/very/long/url/path/to/your/content"
                className="w-full px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg 
                         text-gray-900 text-base placeholder-gray-500 outline-none transition-colors"
                onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                required
              />
            </div>

            <div>
              <label htmlFor="customCode" className="block text-base font-bold text-white mb-3">
                Custom short code (optional)
              </label>
              <input
                type="text"
                id="customCode"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                placeholder="my-awesome-link"
                className="w-full px-4 py-3 bg-gray-100 border-2 border-gray-300 rounded-lg 
                         text-gray-900 text-base placeholder-gray-500 outline-none transition-colors"
                onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                pattern="[a-zA-Z0-9_-]+"
                maxLength={20}
              />
              <p className="text-gray-300 mt-2 text-sm">
                Only letters, numbers, hyphens, and underscores allowed
              </p>
            </div>

            {error && (
              <div className="bg-red-100 border-2 border-red-300 rounded-lg p-4">
                <p className="text-red-800 text-sm font-semibold">
                  {error}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !url.trim()}
              className={clsx(
                'w-full py-3 px-6 rounded-lg font-bold text-base transition-colors shadow-md hover:opacity-90',
                loading || !url.trim()
                  ? 'bg-gray-400 cursor-not-allowed text-gray-600'
                  : 'text-gray-900'
              )}
              style={loading || !url.trim() ? {} : {backgroundColor: '#FF7BAC'}}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-600 border-t-transparent inline-block mr-3"></div>
                  Shortening...
                </>
              ) : (
                'Shorten URL'
              )}
            </button>
          </form>

          {result && (
            <div className="mt-6 p-4 bg-gray-700 border-2 rounded-lg shadow-lg" style={{borderColor: '#FF7BAC'}}>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
                <h3 className="text-lg font-bold text-white">
                  Your shortened URL is ready!
                </h3>
              </div>
              
              <div className="bg-gray-100 rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <input
                    type="text"
                    value={result.short_url}
                    readOnly
                    className="flex-1 px-3 py-2 bg-white border-2 border-gray-300 rounded-lg text-gray-900 
                             text-base font-mono focus:outline-none"
                  />
                  <button
                    onClick={() => copyToClipboard(result.short_url)}
                    className={clsx(
                      'px-4 py-2 rounded-lg font-bold text-sm transition-colors shadow-md',
                      copied 
                        ? 'bg-green-600 text-white' 
                        : 'text-gray-900 hover:opacity-90'
                    )}
                    style={copied ? {} : {backgroundColor: '#FF7BAC'}}
                  >
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                
                <div className="text-gray-700 text-sm">
                  <span className="font-semibold">Original:</span>{' '}
                  <span className="break-all">{result.original_url}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Recent URLs Dropdown */}
        {recentUrls.length > 0 && (
          <div className="bg-gray-800 rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => setShowRecentUrls(!showRecentUrls)}
                className="flex items-center gap-3 text-lg font-bold hover:opacity-80 transition-colors"
                style={{color: '#111827'}}
              >
                Recent URLs ({recentUrls.length})
                {showRecentUrls ? (
                  <ChevronUp className="w-6 h-6" />
                ) : (
                  <ChevronDown className="w-6 h-6" />
                )}
              </button>
              
              {showRecentUrls && (
                <div className="flex gap-3">
                  <button
                    onClick={refreshRecentUrls}
                    className="px-4 py-2 text-gray-900 rounded-lg font-bold transition-colors shadow-md text-sm hover:opacity-90"
                    style={{backgroundColor: '#FF7BAC'}}
                  >
                    Refresh Stats
                  </button>
                  <button
                    onClick={clearRecentUrls}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-colors shadow-md text-sm"
                  >
                    Clear History
                  </button>
                </div>
              )}
            </div>
            
            {showRecentUrls && (
              <div className="space-y-3">
                {recentUrls.map((item) => (
                  <div key={item.id} className="bg-gray-700 border border-gray-600 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-3">
                          <a
                            href={item.short_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-mono text-base font-semibold hover:underline transition-colors hover:opacity-80"
                            style={{color: '#FF7BAC'}}
                          >
                            {item.short_url}
                          </a>
                          <ExternalLink className="w-4 h-4 text-gray-400" />
                        </div>
                        
                        <div className="text-gray-300 mb-3 text-sm break-all">
                          {item.original_url}
                        </div>
                        
                        <div className="flex items-center gap-6 text-gray-400 text-sm">
                          <div className="flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            <span>Created: {new Date(item.created_at).toLocaleDateString()}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-3 h-3" />
                            <span>Clicks: {item.click_count}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => getStats(item.short_code)}
                          className="flex items-center gap-1 px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold transition-colors shadow-md text-xs"
                        >
                          <BarChart3 className="w-3 h-3" />
                          Stats
                        </button>
                        <button
                          onClick={() => copyToClipboard(item.short_url)}
                          className="flex items-center gap-1 px-3 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg font-bold transition-colors shadow-md text-xs"
                        >
                          <Copy className="w-3 h-3" />
                          Copy
                        </button>
                        <button
                          onClick={() => deleteUrl(item.short_code, item.original_url)}
                          className="flex items-center gap-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-colors shadow-md text-xs"
                        >
                          <Trash2 className="w-3 h-3" />
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