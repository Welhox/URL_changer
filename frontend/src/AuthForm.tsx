import React, { useState } from 'react';
import { User, LogIn } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from './AuthContext';

export default function AuthForm() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;

    setError('');
    setLoading(true);

    try {
      const success = await login(username, password);
      if (!success) {
        setError('Invalid username or password');
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-gray-900 flex justify-center items-start pt-4 sm:pt-8 pb-8 sm:pb-16 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 mb-4 rounded-xl" style={{backgroundColor: '#FF7BAC'}}>
            <User className="w-7 h-7 sm:w-8 sm:h-8 text-gray-900" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-white mb-2">
            Welcome to URL Changer
          </h1>
          <p className="text-gray-300 text-base sm:text-lg">
            Sign in to your account
          </p>
        </div>

        {/* Auth Form */}
        <div className="bg-gray-800 border-2 p-4 sm:p-6 shadow-lg w-full rounded-xl sm:rounded-2xl" style={{borderColor: '#FF7BAC'}}>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-base font-bold text-white mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full px-3 py-2.5 bg-gray-100 border-2 border-gray-300 
                         text-gray-900 text-base placeholder-gray-500 outline-none transition-colors rounded-lg"
                onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                required
              />
            </div>



            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-base font-bold text-white mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full px-3 py-2.5 bg-gray-100 border-2 border-gray-300 
                         text-gray-900 text-base placeholder-gray-500 outline-none transition-colors rounded-lg"
                onFocus={(e) => (e.target as HTMLInputElement).style.borderColor = '#FF7BAC'}
                onBlur={(e) => (e.target as HTMLInputElement).style.borderColor = '#d1d5db'}
                required
              />
            </div>



            {/* Error Message */}
            {error && (
              <div className="bg-red-100 border-2 border-red-300 p-3 rounded-lg">
                <p className="text-red-800 text-sm font-semibold">
                  {error}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={clsx(
                'w-full py-3 sm:py-3 px-4 font-bold text-base transition-colors shadow-md flex items-center justify-center gap-2 rounded-lg hover:opacity-90 touch-manipulation',
                loading
                  ? 'bg-gray-400 cursor-not-allowed text-gray-600'
                  : 'text-gray-900'
              )}
              style={loading ? {} : {backgroundColor: '#FF7BAC'}}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-600 border-t-transparent"></div>
                  Signing In...
                </>
              ) : (
                <>
                  <LogIn className="w-4 h-4" />
                  Sign In
                </>
              )}
            </button>
          </form>

          {/* Admin access notice */}
          <div className="text-center mt-6">
            <p className="text-gray-400 text-sm">
              Access is restricted to authorized users only
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}