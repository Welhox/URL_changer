import React, { useState, useEffect } from 'react';
import { Link, Copy, Check, BarChart3, ExternalLink } from 'lucide-react';
import { clsx } from 'clsx';

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

export default function URLShortener() {
  const [url, setUrl] = useState('');
  const [customCode, setCustomCode] = useState('');
  const [result, setResult] = useState<URLResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [recentUrls, setRecentUrls] = useState<URLResult[]>([]);

  // Load recent URLs from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('recentUrls');
    if (stored) {
      setRecentUrls(JSON.parse(stored));
    }
  }, []);

  // Save to localStorage
  const saveToRecent = (newUrl: URLResult) => {
    const updated = [newUrl, ...recentUrls.slice(0, 9)]; // Keep last 10
    setRecentUrls(updated);
    localStorage.setItem('recentUrls', JSON.stringify(updated));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const payload: any = { url: url.trim() };
      if (customCode.trim()) {
        payload.custom_code = customCode.trim();
      }

      const response = await fetch(`${API_BASE}/api/shorten`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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
    try {
      const response = await fetch(`${API_BASE}/api/stats/${shortCode}`);
      if (response.ok) {
        const stats = await response.json();
        alert(`Stats for ${shortCode}:\nClicks: ${stats.click_count}\nCreated: ${new Date(stats.created_at).toLocaleString()}`);
      }
    } catch (err) {
      console.error('Failed to get stats:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center justify-center gap-3">
            <Link className="w-8 h-8 text-blue-600" />
            URL Shortener
          </h1>
          <p className="text-gray-600 text-lg">
            Shorten your long URLs with s.casimirlundberg.fi
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your long URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/very/long/url/path"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>

            <div>
              <label htmlFor="customCode" className="block text-sm font-medium text-gray-700 mb-2">
                Custom short code (optional)
              </label>
              <input
                type="text"
                id="customCode"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                placeholder="my-custom-link"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                pattern="[a-zA-Z0-9_-]+"
                maxLength={20}
              />
              <p className="text-sm text-gray-500 mt-1">
                Only letters, numbers, hyphens, and underscores allowed
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !url.trim()}
              className={clsx(
                'w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors',
                loading || !url.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              )}
            >
              {loading ? 'Shortening...' : 'Shorten URL'}
            </button>
          </form>

          {/* Result */}
          {result && (
            <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
              <h3 className="text-lg font-semibold text-green-800 mb-4">
                Your shortened URL is ready!
              </h3>
              <div className="flex items-center gap-3 mb-3">
                <input
                  type="text"
                  value={result.short_url}
                  readOnly
                  className="flex-1 px-3 py-2 bg-white border border-green-300 rounded focus:outline-none"
                />
                <button
                  onClick={() => copyToClipboard(result.short_url)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="text-sm text-green-700">
                Original: <span className="break-all">{result.original_url}</span>
              </div>
            </div>
          )}
        </div>

        {/* Recent URLs */}
        {recentUrls.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Recent URLs</h2>
            <div className="space-y-4">
              {recentUrls.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <a
                        href={item.short_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        s.casimirlundberg.fi/{item.short_code}
                      </a>
                      <ExternalLink className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="text-sm text-gray-600 truncate">
                      {item.original_url}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Created: {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => getStats(item.short_code)}
                      className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors"
                    >
                      <BarChart3 className="w-4 h-4" />
                      Stats
                    </button>
                    <button
                      onClick={() => copyToClipboard(item.short_url)}
                      className="flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      Copy
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}