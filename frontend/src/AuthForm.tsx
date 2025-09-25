import React, { useState } from 'react';
import { User, UserPlus, LogIn, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from './AuthContext';

export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;

    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const success = await login(username, password);
        if (!success) {
          setError('Invalid username or password');
        }
      } else {
        // Validation for registration
        if (password !== confirmPassword) {
          setError('Passwords do not match');
          return;
        }
        if (password.length < 6) {
          setError('Password must be at least 6 characters long');
          return;
        }
        if (username.length < 3) {
          setError('Username must be at least 3 characters long');
          return;
        }

        const success = await register(username, email, password);
        if (!success) {
          setError('Registration failed. Username or email might already be taken.');
        }
      }
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const useDemoCredentials = () => {
    setUsername('default_user');
    setPassword('default123');
    setIsLogin(true);
  };

  return (
    <div className="min-h-screen w-full bg-teal-100 flex justify-center items-start pt-8 pb-16">
      <div className="max-w-md px-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-teal-600 mb-4 rounded-xl">
            <User className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            Welcome to URL Changer
          </h1>
          <p className="text-slate-600 text-lg">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </p>
        </div>

        {/* Demo Credentials Notice */}
        <div className="bg-blue-100 border-2 border-blue-400 p-4 mb-4 w-full max-w-md rounded-xl">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-blue-800 text-base mb-1">Demo Account Available</h3>
              <p className="text-blue-700 mb-3 text-sm">
                You can use the demo account to test the application with existing URLs.
              </p>
              <button
                onClick={useDemoCredentials}
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors rounded-lg"
              >
                Use Demo Account
              </button>
            </div>
          </div>
        </div>

        {/* Auth Form */}
        <div className="bg-white p-6 shadow-lg w-full max-w-md rounded-2xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="username" className="block text-base font-bold text-slate-800 mb-2">
                Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-300 
                         text-slate-800 text-base placeholder-slate-500 focus:border-teal-500 
                         outline-none transition-colors rounded-lg"
                required
              />
            </div>

            {/* Email (Registration only) */}
            {!isLogin && (
              <div>
                <label htmlFor="email" className="block text-base font-bold text-slate-800 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  className="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-300 
                           text-slate-800 text-base placeholder-slate-500 focus:border-teal-500 
                           outline-none transition-colors rounded-lg"
                  required={!isLogin}
                />
              </div>
            )}

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-base font-bold text-slate-800 mb-2">
                Password
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-300 
                         text-slate-800 text-base placeholder-slate-500 focus:border-teal-500 
                         outline-none transition-colors rounded-lg"
                required
              />
            </div>

            {/* Confirm Password (Registration only) */}
            {!isLogin && (
              <div>
                <label htmlFor="confirmPassword" className="block text-base font-bold text-slate-800 mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                  className="w-full px-3 py-2.5 bg-slate-50 border-2 border-slate-300 
                           text-slate-800 text-base placeholder-slate-500 focus:border-teal-500 
                           outline-none transition-colors rounded-lg"
                  required={!isLogin}
                />
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-100 border-2 border-red-400 p-3 rounded-lg">
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
                'w-full py-3 px-4 font-bold text-base transition-colors shadow-md flex items-center justify-center gap-2 rounded-lg',
                loading
                  ? 'bg-slate-400 cursor-not-allowed text-slate-600'
                  : 'bg-teal-600 hover:bg-teal-700 text-white'
              )}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-slate-600 border-t-transparent"></div>
                  {isLogin ? 'Signing In...' : 'Creating Account...'}
                </>
              ) : (
                <>
                  {isLogin ? <LogIn className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
                  {isLogin ? 'Sign In' : 'Create Account'}
                </>
              )}
            </button>

            {/* Switch Mode */}
            <div className="text-center pt-3">
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                  setEmail('');
                  setConfirmPassword('');
                }}
                className="text-teal-600 hover:text-teal-700 font-semibold text-sm"
              >
                {isLogin 
                  ? "Don't have an account? Sign up" 
                  : "Already have an account? Sign in"
                }
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}